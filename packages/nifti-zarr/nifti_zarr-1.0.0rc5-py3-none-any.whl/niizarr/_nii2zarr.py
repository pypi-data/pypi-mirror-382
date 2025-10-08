import argparse
import io
import json
import math
import re
import sys
from argparse import ArgumentDefaultsHelpFormatter
from typing import (
    Literal, Union, List, Optional, Callable, Generator, Any, Tuple
)

import nibabel as nib
import numpy as np
import zarr.storage
from nibabel.nifti1 import Nifti1Header, Nifti1Image
from nibabel.nifti2 import Nifti2Header, Nifti2Image
from numpy import ndarray
from skimage.transform import pyramid_gaussian, pyramid_laplacian

from ._compat import (
    _make_compressor, _open_zarr, _create_array, _load_nifti_from_stream, pyzarr_version
)
from ._header import (
    UNITS, DTYPES, INTENTS, INTENTS_P, SLICEORDERS, XFORMS,
    bin2nii, get_magic_string, SYS_BYTEORDER, JNIFTI_ZARR,
    SYS_BYTEORDER_SWAPPED
)


def nii2json(header: Union[Nifti1Header, Nifti2Header, ndarray],
             extensions: bool = False) -> dict:
    """
    Convert a nifti header to a JSON serializable dictionary.

    Parameters
    ----------
    header : Nifti1Header | Nifti2Header | ndarray
        Nifti header object.
    extensions : bool, optional
        Whether nifti extensions are present.

    Returns
    -------
    dict
        Nifti header in JSON form following JNIfTI specification.
    """
    if isinstance(header, (Nifti1Header, Nifti2Header)):
        extensions = len(header.extensions) != 0
        header = bin2nii(header.structarr.tobytes())

    header = header.copy()

    ndim = header["dim"][0].item()
    intent_code = INTENTS[header["intent_code"].item()]

    intent_param = header["intent_p"][:INTENTS_P[intent_code]].tolist()
    quatern = header["quatern"].tolist()
    qoffset = header["qoffset"].tolist()
    nii_version = 1 if header["sizeof_hdr"].item() == 348 else 2
    jsonheader = {
        "NIIHeaderSize": header["sizeof_hdr"].item(),
        "DimInfo": {
            "Freq": (header["dim_info"] & 0x03).item(),
            "Phase": ((header["dim_info"] >> 2) & 0x03).item(),
            "Slice": ((header["dim_info"] >> 4) & 0x03).item(),
        },
        "Dim": header["dim"][1:1 + ndim].tolist(),
        "Param1": intent_param[0] if len(intent_param) > 0 else None,
        "Param2": intent_param[1] if len(intent_param) > 1 else None,
        "Param3": intent_param[2] if len(intent_param) > 2 else None,
        "Intent": intent_code,
        "DataType": DTYPES[header["datatype"].item()],
        "BitDepth": header["bitpix"].item(),
        "FirstSliceID": header["slice_start"].item(),
        "VoxelSize": header["pixdim"][1:1 + ndim].tolist(),
        "Orientation": {
            "x": "r" if header["pixdim"][0].item() == 0 else "l",
            "y": "a",
            "z": "s",
        },
        "NIIByteOffset": header["vox_offset"].item(),
        "ScaleSlope": header["scl_slope"].item(),
        "ScaleOffset": header["scl_inter"].item(),
        "LastSliceID": header["slice_end"].item(),
        "SliceType": SLICEORDERS[header["slice_code"].item()],
        "Unit": {
            "L": UNITS[(header["xyzt_units"] & 0x07).item()],
            "T": UNITS[(header["xyzt_units"] & 0x38).item()],
        },
        "MaxIntensity": header["cal_max"].item(),
        "MinIntensity": header["cal_min"].item(),
        "SliceTime": header["slice_duration"].item(),
        "TimeOffset": header["toffset"].item(),
        "Description": header["descrip"].tobytes().decode(),
        "AuxFile": header["aux_file"].tobytes().decode(),
        "QForm": XFORMS[header["qform_code"].item()],
        "SForm": XFORMS[header["sform_code"].item()],
        "Quatern": {
            "b": quatern[0],
            "c": quatern[1],
            "d": quatern[2],
        },
        "QuaternOffset": {
            "x": qoffset[0],
            "y": qoffset[1],
            "z": qoffset[2],
        },
        "Affine": header["sform"].tolist(),
        "Name": header["intent_name"].tobytes().decode(),
        # Strip control characters
        "NIIFormat": get_magic_string(header),
        "NIFTIExtension": [1 if extensions else 0] + [0, 0, 0],
    }
    if not math.isfinite(jsonheader["ScaleSlope"]):
        jsonheader["ScaleSlope"] = 0.0
    if not math.isfinite(jsonheader["ScaleOffset"]):
        jsonheader["ScaleOffset"] = 0.0

    if nii_version == 1:
        unused_fields = {
            "A75DataTypeName": header["datatype"].tobytes().decode(),
            "A75DBName": header["db_name"].tobytes().decode(),
            "A75Extends": header["extents"].item(),
            "A75SessionError": header["session_error"].item(),
            "A75Regular": header["regular"].item(),
            "A75GlobalMax": header["glmax"].item(),
            "A75GlobalMin": header["glmin"].item(),
        }
    else:
        unused_fields = {
            "A75DataTypeName": "",
            "A75DBName": "",
            "A75Extends": 0,
            "A75SessionError": 0,
            "A75Regular": 0,
            "A75GlobalMax": 0,
            "A75GlobalMin": 0,
        }
    jsonheader.update(unused_fields)
    # Remove control characters
    for k, v in jsonheader.items():
        if isinstance(v, str):
            jsonheader[k] = re.sub(r'[\n\r\t\00]*', '', v)

    # Check that the dictionary is serializable
    json.dumps(jsonheader)

    return jsonheader


def _make_pyramid3d(
        data3d: np.ndarray,
        nb_levels: int,
        pyramid_fn: Callable = pyramid_gaussian,
        label: bool = False,
        no_pyramid_axis: Optional[Union[str, int]] = None,
) -> Generator[np.ndarray, None, None]:
    """
    Compute a 3D image pyramid from a given data volume.

    Parameters
    ----------
    data3d : np.ndarray
        3D numpy array representing the volume.
    nb_levels : int
        Number of pyramid levels to compute.
    pyramid_fn : Callable, optional
        Function to generate pyramid levels.
    label : bool, optional
        Whether the data is a label volume.
    no_pyramid_axis : Optional[Union[str, int]], optional
        The axis that should not be downsampled.

    Yields
    ------
    np.ndarray
        The pyramid level as a numpy array.
    """
    no_pyramid_axis = {
        'x': 2,
        'y': 1,
        'z': 0,
    }.get(no_pyramid_axis, no_pyramid_axis)
    if isinstance(no_pyramid_axis, str):
        no_pyramid_axis = int(no_pyramid_axis)

    batch, nxyz = data3d.shape[:-3], data3d.shape[-3:]
    data3d = data3d.reshape((-1, *nxyz))
    max_layer = nb_levels - 1

    def pyramid_values(x):
        return pyramid_fn(x, max_layer, 2, preserve_range=True,
                          channel_axis=no_pyramid_axis)

    def pyramid_labels(x):
        yield x
        labels = np.unique(x)
        pyrmaxprob = list(pyramid_values(x == labels[0]))[1:]
        pyramid = [
            np.zeros_like(level, dtype=x.dtype) for level in pyrmaxprob
        ]
        for label in labels[1:]:
            pyrprob = list(pyramid_values(x == label))[1:]
            for (value, prob, maxprob) in zip(pyramid, pyrprob, pyrmaxprob):
                mask = prob > maxprob
                value[mask] = label
                maxprob[mask] = prob[mask]

        for level in pyramid:
            yield level

    pyramid = pyramid_labels if label else pyramid_values

    for level in zip(*map(pyramid, data3d)):
        yield np.stack(level).reshape(batch + level[0].shape)


def write_ome_metadata(
    omz: zarr.Group,
    axes: List[str],
    space_scale: Union[float, List[float]] = 1.0,
    time_scale: float = 1.0,
    space_unit: str = "micrometer",
    time_unit: str = "second",
    name: str = "",
    pyramid_aligns: Union[str, int, List[str], List[int]] = 2,
    levels: Optional[int] = None,
    no_pool: Optional[int] = None,
    multiscales_type: str = "",
    ome_version: Literal["0.4", "0.5"] = "0.4"
) -> None:
    """
    Write OME metadata into Zarr.

    Parameters
    ----------
    omz : zarr.Group
        Zarr group to write metadata
    axes : list[str]
        Name of each dimension, in Zarr order (t, c, z, y, x)
    space_scale : float | list[float]
        Finest-level voxel size, in Zarr order (z, y, x)
    time_scale : float
        Time scale
    space_unit : str
        Unit of spatial scale (assumed identical across dimensions)
    time_unit : str
        Unit of time scale
    name : str
        Name attribute
    pyramid_aligns : float | list[float] | {"center", "edge"}
        Whether the pyramid construction aligns the edges or the centers
        of the corner voxels. If a (list of) number, assume that a moving
        window of that size was used.
    levels : int
        Number of existing levels. Default: find out automatically.

    """
    # 1) Pull out all pyramid-level shapes
    shapes = []
    lvl = 0
    while True:
        if levels is not None and lvl > levels:
            break
        key = str(lvl)
        if key not in omz:
            break
        shapes.append(omz[key].shape)
        lvl += 1

    if not shapes:
        return  # nothing to do

    # 2) Map axes → types, count spatial vs. others
    axis_to_type = dict(x="space", y="space", z="space", t="time", c="channel")
    types = [axis_to_type[a] for a in axes]
    ndim = len(axes)
    sdim = types.count("space")
    bdim = ndim - sdim

    # 3) Normalize space_scale and pyramid_aligns to length==sdim
    def _normalize(val, length):
        if not isinstance(val, (list, tuple)):
            val = [val]
        if len(val) < length:
            val = [val[0]] * (length - len(val)) + list(val)
        return val[-length:]
    space_scale = _normalize(space_scale, sdim)
    aligns = _normalize(pyramid_aligns, sdim)

    # 4) Precompute base shape
    shape0 = shapes[0]

    # 5) Build the multiscales dict
    space_unit = space_unit or "millimeter"
    time_unit = time_unit or "second"
    ms: dict = {
        "version": ome_version,
        "name": name,
        "type": multiscales_type or f"median window {'x'.join(['2']*sdim)}",
        "axes": [
            dict(name=a, type=t, **({"unit": space_unit} if t=="space" else {"unit": time_unit} if t=="time" else {}))
            for a, t in zip(axes, types)
        ],
        "datasets": [],
    }

    # Helper to compute per-dimension scale/translation
    def _factor(a0, aN, align, n, scale, is_pool):
        if is_pool:
            # no pooling along this axis
            return scale, 0.0
        if isinstance(align, str) and align.lower().startswith("e"):
            factor = (a0 / aN)
            trans = (factor - 1) * 0.5
        elif isinstance(align, str) and align.lower().startswith("c"):
            factor = ((a0 - 1) / (aN - 1))
            trans = 0.0
        else:
            # numeric align: repeated power
            factor = (align ** n)
            trans = (factor - 1) * 0.5
        return factor * scale, trans * scale

    prev_scale_axes = [None] * sdim
    prev_trans_axes = [None] * sdim
    # 7) Populate each pyramid level
    for n, shape in enumerate(shapes):
        # compute scale+translation arrays of length ndim
        scale = [1.0]*bdim + []
        translation = [0.0]*bdim + []
        for i in range(sdim):
            a0 = shape0[bdim+i]
            aN = shape[bdim+i]
            is_pool = (i == no_pool)
            if n > 0 and shapes[n-1][bdim + i] == aN:
                # no change from last level → re‐use
                s, tr = prev_scale_axes[i], prev_trans_axes[i]
            else:
                s, tr = _factor(a0, aN, aligns[i], n, space_scale[i], is_pool)
            scale.append(s)
            translation.append(tr)
            prev_scale_axes[i] = s
            prev_trans_axes[i] = tr

        ms["datasets"].append({
            "path": str(n),
            "coordinateTransformations": [
                {"type":"scale",       "scale": scale},
                {"type":"translation", "translation": translation},
            ]
        })

    # 8) Add global time‐scale transformation
    tscale = [time_scale if t=="time" else 1.0 for t in types]
    ms["coordinateTransformations"] = [{"type":"scale", "scale": tscale}]

    # 9) Write into Zarr attributes
    omz.attrs["multiscales"] = [ms]
    if ome_version == "0.5":
        omz.attrs["ome"] = {"multiscales": [ms]}
    elif ome_version not in {"0.4","0.5"}:
        raise ValueError(f"Unsupported ome_version {ome_version}")


def write_nifti_header(
        omz: zarr.Group,
        header: Union[Nifti1Header, Nifti2Header]
) -> None:
    jsonheader = nii2json(header)
    # Write nifti header (binary)
    stream = io.BytesIO()
    header.write_to(stream)
    bin_data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    # Remove the extension flag if there are no extensions
    if len(header.extensions) == 0:
        bin_data = bin_data[:-4]
    _create_array(
        omz,
        'nifti',
        shape=[len(bin_data)],
        chunks=len(bin_data),
        dtype='u1',
        compressors=None,
        fill_value=None,
        dimension_separator='/',
        overwrite=True,
    )
    omz['nifti'][:] = bin_data

    # Write nifti header (JSON)
    omz['nifti'].attrs.update(jsonheader)
    return


def nii2zarr(
        inp: Union[Nifti1Image, Nifti2Image, Any],
        out: Union[str, Any],
        *,
        chunk: Union[int, Tuple[int]] = 64,
        chunk_channel: int = 1,
        chunk_time: int = 1,
        shard: Optional[Union[int, Tuple[int]]] = None,
        shard_channel: Optional[int] = None,
        shard_time: Optional[int] = None,
        nb_levels: int = -1,
        method: Literal['gaussian', 'laplacian'] = 'gaussian',
        label: Optional[bool] = None,
        no_time: bool = False,
        no_pyramid_axis: Optional[Union[str, int]] = None,
        fill_value: Optional[Union[int, float, complex]] = None,
        compressor: Literal['blosc', 'zlib'] = 'blosc',
        compressor_options: dict = {},
        zarr_version: Literal[2, 3] = 2,
        ome_version: Literal["0.4", "0.5"] = "0.4",
) -> None:
    """
    Convert a nifti file to nifti-zarr.

    Parameters
    ----------
    inp : Nifti1Image | Nifti12mage | file-like
        Input nifti image.
    out : zarr.Store, zarr.Group or path
        Output zarr object/path.
        If object, it must be opened with "w" capability.
    chunk : int or tuple of int, optional
        Chunk size for spatial dimensions.
        The tuple allows different chunk sizes to be used along each dimension.
    chunk_channel : int, optional
        Chunk size of the channel dimension. If 0, combine all channels
        in a single chunk.
    chunk_time : int, optional
        Chunk size for the time dimension. If 0, combine all timepoints
        in a single chunk.
    shard : int or tuple of int, optional
        Shard size for spatial dimensions.
        The tuple allows different shard sizes to be used along each dimension.
    shard_channel : int, optional
        Shard size of the channel dimension. If 0, combine all channels
        in a single shard.
    shard_time : int, optional
        Shard size for the time dimension. If 0, combine all timepoints
        in a single shard.
    nb_levels : int, optional
        Number of pyramid levels to generate.
        If -1, make all possible levels until the level can be fit into
        one chunk.
    method : {'gaussian', 'laplacian'}
        Method used to compute the pyramid.
    label : bool, optional
        Is this is a label volume?  If `None`, guess from intent code.
    no_time : bool, optional
        If True, there is no time dimension so the 4th dimension
        (if it exists) should be interpreted as the channel dimensions.
    no_pyramid_axis : {'x', 'y', 'z'}
        Axis that should not be downsampled. If None, downsample
        across all three dimensions.
    fill_value : number
        Value to use for missing tiles
    compressor : {'blosc', 'zlib'}
        Compression to use
    compressor_options : dict, optional
        Options for the compressor.
    zarr_version : {2, 3}, optional
        Zarr format version.
    ome_version : {"0.4", "0.5"}, optional
        OME-Zarr version.

    Returns
    -------
    None
    """
    # check conflicts in parameters
    if pyzarr_version == 2 and zarr_version == 3:
        raise ValueError("zarr-python >=3.0.0 is required for zarr version 3")
    if shard and zarr_version == 2:
        raise ValueError("Sharding is only supported in zarr version 3")

    # Open nifti image with nibabel
    if not isinstance(inp, (Nifti1Image, Nifti2Image)):
        if hasattr(inp, 'read'):
            inp = _load_nifti_from_stream(inp)
        else:
            inp = nib.load(inp)

    out = _open_zarr(out, zarr_version=zarr_version)

    # If the no_time option is used:
    # - if the 4-th dimension is a singleton, we assume it is the time
    #   dimension, and squeeze it from the array before saving it to zarr.
    # - If the 4-th dimension is not a singleton, we add a singleton
    #   dimension in the header, si that it follows the specification,
    #   but squeeze it from the array before saving it to zarr.

    nbheader = inp.header
    if no_time and len(inp.shape) > 3 and inp.shape[3] != 1:
        # add singleton time dimension
        nbheader = Nifti1Image(
            inp.dataobj[:, :, :, None], inp.affine, inp.header
        ).header

    # nibabel consumed these two values
    if hasattr(inp.dataobj, "_slope") and hasattr(inp.dataobj, "_inter"):
        nbheader.set_slope_inter(inp.dataobj._slope, inp.dataobj._inter)

    # Compute JSON version of the nifti header
    # NOTE
    #   This is not the version that gets written up. This is only
    #   used to obtain well-formatted metadata such as intent, voxel size
    #   or data type.
    jsonheader = nii2json(nbheader)

    if hasattr(inp.dataobj, "get_unscaled"):
        data = np.asarray(inp.dataobj.get_unscaled())
    else:
        data = np.asarray(inp.dataobj)
    if fill_value:
        if np.issubdtype(data.dtype, np.complexfloating):
            fill_value = complex(fill_value)
        elif np.issubdtype(data.dtype, np.floating):
            fill_value = float(fill_value)
        elif np.issubdtype(data.dtype, np.integer):
            fill_value = int(fill_value)
        elif np.issubdtype(data.dtype, np.bool_):
            fill_value = bool(fill_value)

    # Fix array shape
    nbatch = data.ndim - 3
    if data.ndim == 5:
        perm = [3, 4, 2, 1, 0]
        axes = ['t', 'c', 'z', 'y', 'x']
        chunk_tc = (
            chunk_time or data.shape[3],
            chunk_channel or data.shape[4]
        )
        shard_tc = (
            shard_time or data.shape[3],
            shard_channel or data.shape[4]
        )
        if no_time:
            raise ValueError('no_time is not supported for 5D data')
    elif data.ndim == 4:
        perm = [3, 2, 1, 0]
        if no_time:
            axes = ['c', 'z', 'y', 'x']
            chunk_tc = (chunk_channel or data.shape[3],)
            shard_tc = (shard_channel or data.shape[3],)
        else:
            axes = ['t', 'z', 'y', 'x']
            chunk_tc = (chunk_time or data.shape[3],)
            shard_tc = (shard_time or data.shape[3],)
    elif data.ndim == 3:
        perm = [2, 1, 0]
        axes = ['z', 'y', 'x']
        chunk_tc = tuple()
        shard_tc = tuple()
    elif data.ndim > 5:
        raise ValueError('Too few dimensions for conversion to nii.zarr')
    else:
        raise ValueError('Too many dimensions for conversion to nii.zarr')
    ARRAY_DIMENSIONS_MAP = {
        't': 'time',
        'c': 'channel',
        'z': 'z',
        'y': 'y',
        'x': 'x',
    }
    ARRAY_DIMENSIONS = [ARRAY_DIMENSIONS_MAP[axis] for axis in axes]
    data = data.transpose(perm)

    # Compute image pyramid
    if label is None:
        label = jsonheader['Intent'] in ("label", "neuronames")
    pyramid_fn = pyramid_gaussian if method[0] == 'g' else pyramid_laplacian

    chunksize = np.array((chunk,) * 3 if isinstance(chunk, int) else chunk)
    nxyz = np.array(data.shape[-3:])

    if nb_levels == -1:
        default_nb_levels = int(np.ceil(np.log2(np.max(nxyz / chunksize)))) + 1
        default_nb_levels = max(default_nb_levels, 1)
        nb_levels = default_nb_levels

    data = list(_make_pyramid3d(data, nb_levels, pyramid_fn, label,
                                no_pyramid_axis))

    # Fix data type
    # If nifti was swapped when loading it, we want to swapped it back
    # to make it as same as before
    byteorder_swapped = inp.header.endianness != SYS_BYTEORDER
    byteorder = SYS_BYTEORDER_SWAPPED if byteorder_swapped else SYS_BYTEORDER
    data_type = JNIFTI_ZARR[jsonheader['DataType']]
    if isinstance(data_type, tuple):
        data_type = [
            (field, '|' + dtype) for field, dtype in data_type
        ]
    elif data_type.endswith('1'):
        data_type = '|' + data_type
    else:
        data_type = byteorder + data_type

    # Prepare array metadata at each level
    compressor = _make_compressor(compressor, zarr_version=zarr_version,
                                  **compressor_options)

    chunk = tuple(chunk) if isinstance(chunk, (list, tuple)) else (chunk,)
    chunk = chunk + chunk[-1:] * max(0, 3 - len(chunk)) + chunk_tc
    chunk = tuple(chunk[i] for i in perm)

    opts = {
        'chunks': chunk,
        'dimension_separator': '/',
        'order': 'C',
        'dtype': data_type,
        'fill_value': fill_value,
        'compressors': compressor,
    }

    if shard:
        shard = tuple(shard) if isinstance(shard, (list, tuple)) else (shard,)
        shard = shard + shard[-1:] * max(0, 3 - len(shard)) + shard_tc
        shard = tuple(shard[i] for i in perm)
        opts['shards'] = shard

    for i, d in enumerate(data):
        _create_array(out, str(i), shape=d.shape, **opts)
        out[str(i)][:] = d

    # write xarray metadata
    for i in range(len(data)):
        out[str(i)].attrs['_ARRAY_DIMENSIONS'] = ARRAY_DIMENSIONS

    write_ome_metadata(
        out,
        axes=axes,
        space_scale=[jsonheader["VoxelSize"][2],
                     jsonheader["VoxelSize"][1],
                     jsonheader["VoxelSize"][0]],
        time_scale=jsonheader["VoxelSize"][3] if nbatch >= 1 else 1.0,
        space_unit=JNIFTI_ZARR[jsonheader["Unit"]["L"]],
        time_unit=JNIFTI_ZARR[jsonheader["Unit"]["T"]],
        ome_version=ome_version
    )

    write_nifti_header(out, nbheader)
    return


def cli(args=None):
    """    Command-line entrypoint"""
    parser = argparse.ArgumentParser(
        'nii2zarr', description='Convert nifti to nifti-zarr.',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'input', help='Input nifti file.')
    parser.add_argument(
        'output', default=None, nargs="?",
        help='Output zarr directory. '
             'When not specified, write to input directory.')
    parser.add_argument(
        '--chunk', type=int, default=64, help='Spatial chunk size.')
    parser.add_argument(
        '--unchunk-channels', action='store_true',
        help='Save all chanels in a single chunk. '
             'Unchunk if you want to display all channels as a single RGB '
             'layer in neuroglancer. '
             'Chunked by default, unless datatype is RGB.'
    )
    parser.add_argument(
        '--unchunk-time', action='store_true',
        help='Save all timepoints in a single chunk.'
             'Unchunk if you want to display all timepoints as a single RGB '
             'layer in neuroglancer. Chunked by default.')
    parser.add_argument(
        '--shard', type=int, default=None, help='Spatial shard size.')
    parser.add_argument(
        '--unshard-channels', action='store_true',
        help='Save all channels in a single shard.')
    parser.add_argument(
        '--unshard-time', action='store_true',
        help='Save all timepoints in a single shard.')
    parser.add_argument(
        '--levels', type=int, default=-1,
        help='Number of levels in the pyramid. '
             'If -1 (default), use as many levels as possible.')
    parser.add_argument(
        '--method', choices=('gaussian', 'laplacian'), default='gaussian',
        help='Pyramid method.')
    parser.add_argument(
        '--fill', default=None, help='Missing value.')
    parser.add_argument(
        '--compressor', choices=('blosc', 'zlib'), default='blosc',
        help='Compressor.')
    parser.add_argument(
        '--label', action='store_true', default=None,
        help='Segmentation volume.')
    parser.add_argument(
        '--no-label', action='store_false', dest='label',
        help='Not a segmentation volume.')
    parser.add_argument(
        '--no-time', action='store_true',
        help='No time dimension.')
    parser.add_argument(
        '--no-pyramid-axis', choices=('x', 'y', 'z'),
        help='Thick slice axis that should not be downsampled.')
    parser.add_argument(
        '--zarr-version', type=int, default=2, choices=(2, 3),
        help='Zarr format version.')
    parser.add_argument(
        '--ome-version', type=str, default="0.4", choices=("0.4", "0.5"),
        help='OME-Zarr specification version.')

    args = args or sys.argv[1:]
    args = parser.parse_args(args)

    if args.output is None:
        print('Output not specified, using input directory')
        args.output = re.sub(r'\.nii(\.gz)?$', '', args.input) + '.nii.zarr'

    nii2zarr(
        args.input, args.output,
        chunk=args.chunk,
        chunk_channel=0 if args.unchunk_channels else 1,
        chunk_time=0 if args.unchunk_time else 1,
        shard=args.shard,
        shard_channel=0 if args.unshard_channels else 1,
        shard_time=0 if args.unshard_time else 1,
        nb_levels=args.levels,
        method=args.method,
        fill_value=args.fill,
        compressor=args.compressor,
        label=args.label,
        no_time=args.no_time,
        no_pyramid_axis=args.no_pyramid_axis,
        zarr_version=args.zarr_version,
        ome_version=args.ome_version,
    )

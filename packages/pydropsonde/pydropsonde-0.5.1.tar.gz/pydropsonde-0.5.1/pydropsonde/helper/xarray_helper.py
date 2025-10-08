import numpy as np
import xarray as xr
import numcodecs
from pathlib import Path
from zarr.errors import ContainsGroupError
import warnings


def add_ancillary_var(ds, variable, anc_name):
    """
    add ancillary variable to xarray dataset variable
    """
    var_attrs = ds[variable].attrs
    if "ancillary_variables" in var_attrs.keys():
        anc = var_attrs["ancillary_variables"] + f" {anc_name}"
    else:
        anc = "" + f"{anc_name}"
    var_attrs.update({"ancillary_variables": anc})
    ds = ds.assign(
        {
            f"{variable}": (
                ds[variable].dims,
                ds[variable].values,
                var_attrs,
            )
        }
    )
    return ds


def remove_above_alt(ds, variables, alt_dim, maxalt):
    return ds.assign(
        {
            var: (
                ds[var].dims,
                xr.where(
                    (ds[alt_dim] < maxalt) | (np.isnan(ds[alt_dim])), ds[var], np.nan
                ).values,
                ds[var].attrs,
            )
            for var in variables
            if var != alt_dim
        }
    )


# encode and write files
def get_chunks(ds, var, object_dims=("sonde", "circle"), alt_dim="alt"):
    """
    Get standard chunks for one object_dim (like sonde_id or circle) and one height dimension
    """
    chunks = {}
    if all(object_dim not in ds[var].dims for object_dim in object_dims):
        chunks = {
            alt_dim: ds[alt_dim].size,
        }

    elif alt_dim not in ds[var].dims:
        chunks = {object_dim: ds[object_dim].size for object_dim in object_dims}

    else:
        chunks = {
            object_dim: min(750, ds[object_dim].size) for object_dim in object_dims
        }
        chunks.update(
            {
                alt_dim: min(750, ds[alt_dim].size),
            }
        )

    return tuple((chunks[d] for d in ds[var].dims))


def get_time_encoding(ds_time):
    min_time = np.nanmin(ds_time.values)
    max_time = np.nanmax(ds_time.values)
    if np.isnan(min_time):
        min_time = np.datetime64("1970-01-01T00:00:00", "us")
    if (max_time - min_time) > np.timedelta64(2**53 - 1, "us"):
        warnings.warn(
            "your time range is larger than 2**53 microseconds, consider using another encoding for time"
        )
    return {
        "dtype": "int64",
        "units": f"microseconds since {np.datetime_as_string(min_time, unit='us', timezone='UTC')}",
    }


def get_target_dtype(ds, var):
    """
    reduce float dtypes to float32 and properly encode time
    """
    if isinstance(ds[var].values.flat[0], np.floating):
        return {"dtype": "float32"}
    if np.issubdtype(type(ds[var].values.flat[0]), np.datetime64):
        return get_time_encoding(ds[var])
    else:
        return {"dtype": ds[var].values.dtype}


def get_zarr_encoding(ds, var, **kwargs):
    """
    get zarr encoding for dataset
    """
    numcodecs.blosc.set_nthreads(1)  # IMPORTANT FOR DETERMINISTIC CIDs
    codec = numcodecs.Blosc("zstd")
    enc = {
        "compressor": codec,
        "chunks": get_chunks(ds, var, **kwargs),
    }
    enc.update(get_target_dtype(ds, var))
    return enc


def get_nc_encoding(ds, var, **kwargs):
    """
    get netcdf encoding for dataset
    default compression is zlib for compatibility
    """
    if isinstance(ds[var].values.flat[0], str):
        return {}
    else:
        enc = {
            "compression": "zlib",
            "chunksizes": get_chunks(ds, var, **kwargs),
            "fletcher32": True,
        }
        enc.update(get_target_dtype(ds, var))
        return enc


enc_map = {
    "zarr": get_zarr_encoding,
    "nc": get_nc_encoding,
}


def get_encoding(ds, filetype, exclude_vars=None, **kwargs):
    """
    get encoding for a dataset depending on filetype
    """
    enc_fct = enc_map[filetype]
    if exclude_vars is None:
        exclude_vars = []
    enc_var = {
        var: enc_fct(ds, var, **kwargs)
        for var in ds.variables
        if var not in ds.dims
        if var not in exclude_vars
    }
    return enc_var


def open_dataset(path):
    """
    open an xr.dataset from path depending on filetype
    """
    path = Path(path)
    return xr.open_dataset(path)


def to_file(ds, path, filetype, overwrite=True, **kwargs):
    """
    write dataset to file depending on filetype.
    """
    if filetype == "nc":
        ds.to_netcdf(path, **kwargs)
    elif filetype == "zarr":
        try:
            ds.to_zarr(path, zarr_format=2, **kwargs)
        except (ContainsGroupError, FileExistsError):
            if overwrite:
                ds.to_zarr(path, zarr_format=2, mode="w", **kwargs)
            else:
                warnings.warn(f"file {path} already exists. no new file written")
    else:
        raise ValueError("Could not write: unrecognized filetype")


def coarsen_time(ds, target_unit="us"):
    """
    Coarsen the time dimension of the dataset to a specified target unit.
    """
    for var in ds.variables:
        if np.issubdtype(type(ds[var].values.flat[0]), np.datetime64):
            ds = ds.assign({var: ds[var].astype(f"datetime64[{target_unit}]")})
    return ds


def write_ds(ds, dir, filename, **kwargs):
    """
    standardized way to write level files;
    includes determination of filetype and encoding
    """
    Path(dir).mkdir(parents=True, exist_ok=True)
    if ".nc" in filename:
        filetype = "nc"
    elif ".zarr" in filename:
        filetype = "zarr"
    else:
        raise ValueError("filetype unknown")
    ds = coarsen_time(ds)
    encoding = get_encoding(ds, filetype=filetype, **kwargs)
    to_file(
        ds=ds,
        filetype=filetype,
        path=Path(dir, filename),
        encoding=encoding,
    )

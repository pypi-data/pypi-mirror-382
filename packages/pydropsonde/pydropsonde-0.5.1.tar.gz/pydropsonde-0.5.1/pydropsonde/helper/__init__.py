import numpy as np
from . import physics
import xarray as xr
from configparser import NoSectionError

from moist_thermodynamics import functions as mtf
from moist_thermodynamics import saturation_vapor_pressures as mtsvp

# Keys in l2_variables should be variable names in aspen_ds attribute of Sonde object
l2_variables = {
    "u_wind": {
        "rename_to": "u",
        "attributes": {
            "standard_name": "eastward_wind",
            "long_name": "u component of winds",
            "units": "m s-1",
        },
    },
    "v_wind": {
        "rename_to": "v",
        "attributes": {
            "standard_name": "northward_wind",
            "long_name": "v component of winds",
            "units": "m s-1",
        },
    },
    "tdry": {
        "rename_to": "ta",
        "attributes": {
            "standard_name": "air_temperature",
            "long_name": "air temperature",
            "units": "K",
        },
    },
    "pres": {
        "rename_to": "p",
        "attributes": {
            "standard_name": "air_pressure",
            "long_name": "atmospheric pressure",
            "units": "Pa",
        },
    },
    "rh": {
        "rename_to": "rh",
        "attributes": {
            "standard_name": "relative_humidity",
            "long_name": "relative humidity",
            "units": "1",
        },
    },
    "lat": {
        "rename_to": "lat",
        "attributes": {
            "standard_name": "latitude",
            "long_name": "latitude",
            "units": "degrees_north",
            "axis": "Y",
        },
    },
    "lon": {
        "rename_to": "lon",
        "attributes": {
            "standard_name": "longitude",
            "long_name": "longitude",
            "units": "degrees_east",
            "axis": "X",
        },
    },
    "time": {
        "rename_to": "time",
        "attributes": {
            "standard_name": "time",
            "long_name": "time of recorded measurement",
            "axis": "T",
            "time_zone": "UTC",
        },
    },
    "gpsalt": {
        "rename_to": "gpsalt",
        "attributes": {
            "standard_name": "altitude",
            "long_name": "gps reported altitude above MSL",
            "units": "m",
            "axis": "Z",
            "positive": "up",
        },
    },
    "alt": {
        "rename_to": "alt",
        "attributes": {
            "standard_name": "altitude",
            "long_name": "altitude above MSL",
            "units": "m",
            "axis": "Z",
            "positive": "up",
        },
    },
}


l2_flight_attributes_map = {
    "True Air Speed (m/s) =": "true_air_speed_(ms-1)",
    "Ground Speed (m/s) =": "ground_speed_(ms-1)",
    "Software Notes =": "AVAPS_software_notes",
    "Format Notes =": "AVAPS_format_notes",
    "True Heading (deg) =": "true_heading_(deg)",
    "Ground Track (deg) =": "ground_track_(deg)",
    "Longitude (deg) =": "launch_lon_(degrees_east)",
    "Latitude (deg) =": "launch_lat_(degrees_north)",
    "MSL Altitude (m) =": "launch_altitude_(m)",
    "Geopotential Altitude (m) =": "launch_geopotential_altitude_(m)",
}

l3_coords = dict(
    launch_time={"long_name": "dropsonde launch time", "time_zone": "UTC"},
    launch_lon={
        "long_name": "aircraft longitude at launch",
        "standard_name": "deployment_longitude",
        "units": "degrees_east",
        "source": "aircraft measurement",
    },
    launch_lat={
        "long_name": "aircraft latitude at launch",
        "standard_name": "deployment_latitude",
        "units": "degrees_north",
        "source": "aircraft measurement",
    },
    launch_altitude={
        "long_name": "aircraft altitude at launch",
        "units": "m",
        "source": "aircraft measurement",
    },
)


path_to_flight_ids = "{platform}/Level_0"
path_to_l0_files = "{platform}/Level_0/{flight_id}"

l2_filename_template = "{platform}_{flight_id}_{id}_Level_2.nc"

l3_filename = "Level_3.nc"
l4_filename = "Level_4.nc"

es_formular = mtsvp.liq_wagner_pruss
es_name = "Wagner and Pruß 2002 (IAPWS Formulation 1995)"


def get_global_attrs_from_config(config):
    """get global attributes that should be added to each dataset from config
    Input:
        config: configparser
    Returns:
    -------
        global_attrs: dict with global attributes
    """
    try:
        global_attrs = dict(config.items("GLOBAL_ATTRS"))
    except NoSectionError:
        global_attrs = {}
    global_attrs.update(
        dict(
            featureType="trajectoryProfile",
        )
    )

    return {"global": global_attrs}


def get_level_specific_attrs_from_config(config):
    """
    get level specific attributes that should be added to each dataset from config
    """
    attrs = {}
    for i in range(2, 5):
        try:
            attrs[f"l{i}"] = dict(config.items(f"L{i}_ATTRS"))
        except NoSectionError:
            attrs[f"l{i}"] = {}
    return attrs


def get_bool(s):
    if isinstance(s, bool):
        return s
    elif isinstance(s, int):
        return bool(s)
    elif isinstance(s, str):
        lower_s = s.lower()
        if lower_s == "true":
            return True
        elif lower_s == "false":
            return False
        elif lower_s in ["0", "1"]:
            return bool(int(lower_s))
        else:
            raise ValueError(f"Cannot convert {s} to boolean")
    else:
        raise ValueError(f"Cannot convert {s} to boolean")


def convert_rh_to_si(value):
    """convert RH from % to fraction"""
    return value / 100


def convert_p_to_si(value):
    """convert pressure from hPa to Pa"""
    return value * 100


def convert_ta_to_si(value):
    """convert temperature from C to K"""
    return value + 273.15


def get_si_converter_function_based_on_var(var_name):
    """get the function to convert a variable to SI units based on its name"""
    func_name = f"convert_{var_name}_to_si"
    func = globals().get(func_name, None)
    if func is None:
        raise ValueError(f"No function named {func_name} found in the module")
    return func


def calc_q_from_rh_sonde(ds):
    """
    Input :

        ds : Dataset

    Output :

        ds : Dataset with rh added

    Function to estimate specific humidity from the relative humidity, temperature and pressure in the given dataset.
    """
    try:
        q_attrs = ds.q.attrs
        q_attrs.update(
            dict(
                method="calculated from measured RH following Hardy 1998",
            )
        )
    except AttributeError:
        q_attrs = dict(
            standard_name="specific_humidity",
            long_name="specific humidity",
            units="kg kg-1",
            method="calculated from measured RH following Hardy 1998",
        )
    ds = ds.assign(
        q=(
            ds.rh.dims,
            mtf.relative_humidity_to_specific_humidity(
                ds.rh, ds.p, ds.ta, es=mtsvp.liq_hardy
            ).values,
            q_attrs,
        )
    )
    return ds


def calc_q_from_rh(ds):
    """
    Input :

        ds : Dataset

    Output :

        ds : Dataset with rh added

    Function to estimate specific humidity from the relative humidity, temperature and pressure in the given dataset.
    """
    try:
        q_attrs = ds.q.attrs
        q_attrs.update(
            dict(
                method=f"calculated from RH following {es_name}",
            )
        )
    except AttributeError:
        q_attrs = dict(
            standard_name="specific_humidity",
            long_name="specific humidity",
            units="kg kg-1",
            method=f"calculated from RH following {es_name}",
        )
    ds = ds.assign(
        q=(
            ds.rh.dims,
            mtf.relative_humidity_to_specific_humidity(
                ds.rh, ds.p, ds.ta, es=es_formular
            ).values,
            q_attrs,
        )
    )
    return ds


def calc_rh_from_q(ds, alt_dim="altitude"):
    """
    Input :

        ds : Dataset

    Output :

        ds : Dataset with rh added

    Function to estimate relative humidity from the specific humidity, temperature and pressure in the given dataset.
    """
    assert ds.p.attrs["units"] == "Pa"
    try:
        rh_attrs = ds.rh.attrs
        rh_attrs.update(
            dict(
                method=f"recalculated from q following {es_name}",
            )
        )
    except AttributeError:
        rh_attrs = dict(
            standard_name="relative_humidity",
            long_name="relative humidity",
            units="1",
            method=f"recalculated from q following {es_name} after binning in {alt_dim}",
        )
    ds = ds.assign(
        rh=(
            ds.q.dims,
            mtf.specific_humidity_to_relative_humidity(
                ds.q, ds.p, ds.ta, es=es_formular
            ).values,
            rh_attrs,
        )
    )

    return ds


def calc_iwv(ds, sonde_dim="sonde_id", alt_dim="alt", max_gap=300, qc_var=None):
    """
    Input :

        ds : Dataset
        sonde_dim : Dimension name for the sonde identifier
        alt_dim : Dimension name for the altitude
        max_gap : Maximum one-sided gap at the surface to fill for IWV calculation (m)
        qc_var : List of quality control variable names to check for valid data

    Output :

        dataset : Dataset with integrated water vapor

    Function to estimate integrated water vapor in the given dataset. q, p and ta are interpolated before the calculation, and up to max_gap m are extrapolated to the surface. If the gap at the surface is larger than 300m or one of the QC was not passed, Nan is returned.
    """
    if qc_var is not None:
        qc_vals = [ds[var].values for var in qc_var]
    if (qc_var is None) or (qc_vals.count(0) == len(qc_vals)):
        q_interp = ds.q.interpolate_na(dim=alt_dim, method="linear").interpolate_na(
            dim=alt_dim, method="nearest", fill_value="extrapolate", max_gap=max_gap
        )
        log_p = np.log(ds.p)
        p_interp = np.exp(
            log_p.interpolate_na(dim=alt_dim, method="linear").interpolate_na(
                dim=alt_dim, method="linear", fill_value="extrapolate", max_gap=max_gap
            )
        )
        ta_interp = ds.ta.interpolate_na(dim=alt_dim, method="linear").interpolate_na(
            dim=alt_dim, method="linear", fill_value="extrapolate", max_gap=max_gap
        )

        if (
            (np.isnan(q_interp.sel(altitude=0)))
            or (np.isnan(p_interp.sel(altitude=0)))
            or (np.isnan(ta_interp.sel(altitude=0)))
        ):
            iwv = np.nan
        else:
            mask_p = ~np.isnan(p_interp)
            mask_t = ~np.isnan(ta_interp)
            mask_q = ~np.isnan(q_interp)
            mask = mask_p & mask_t & mask_q
            iwv = physics.integrate_water_vapor(
                q=q_interp[mask].values,
                p=p_interp[mask].values,
                T=ta_interp[mask].values,
                z=ds[alt_dim][mask].values,
            )

    else:
        iwv = np.nan

    ds_iwv = xr.DataArray([iwv], dims=[sonde_dim], coords={})
    ds_iwv.name = "iwv"
    ds_iwv.attrs = dict(
        standard_name="atmosphere_mass_content_of_water_vapor",
        units="kg m-2",
        long_name="integrated water vapor",
        description="vertically integrated water vapor up to aircraft altitude",
    )
    ds = xr.merge([ds, ds_iwv])
    return ds


def calc_theta_from_T(ds):
    """
    Input :

        dataset : Dataset

    Output :

        dataset : Dataset with Potential temperature values

    Function to estimate potential temperature from the temperature and pressure in the given dataset.
    """
    assert ds.p.attrs["units"] == "Pa"
    theta = mtf.theta(ds.ta.values, ds.p.values)
    try:
        theta_attrs = ds.theta.attrs
    except AttributeError:
        theta_attrs = dict(
            standard_name="air_potential_temperature",
            long_name="dry potential temperature",
            units="K",
        )
    theta_attrs.update(dict(method="calculated from measured ta and p"))
    ds = ds.assign(theta=(ds.ta.dims, theta, theta_attrs))

    return ds


def calc_T_from_theta(ds, alt_dim="altitude"):
    """
    Input :

        dataset : Dataset

    Output :

        dataset: Dataset with temperature calculated from theta

    Function to estimate potential temperature from the temperature and pressure in the given dataset.
    """
    assert ds.p.attrs["units"] == "Pa"

    try:
        t_attrs = ds.ta.attrs
    except AttributeError:
        t_attrs = dict(
            standard_name="air_temperature",
            long_name="air temperature",
            units="K",
        )

    t_attrs.update(
        dict(method=f"recalculated from theta and p after binning in {alt_dim}")
    )
    ds = ds.assign(ta=(ds.theta.dims, mtf.theta2T(ds.theta, ds.p).values, t_attrs))
    return ds


def calc_theta_e(ds):
    """
    Input :

        dataset : Dataset

    Output :

        dataset: Dataset with theta_e added

    Function to estimate theta_e from the temperature, pressure and q in the given dataset.
    """

    assert ds.p.attrs["units"] == "Pa"
    theta_e = mtf.theta_e(T=ds.ta.values, P=ds.p.values, qt=ds.q.values, es=es_formular)

    ds = ds.assign(
        theta_e=(
            ds.ta.dims,
            theta_e,
            dict(
                standard_name="air_equivalent_potential_temperature",
                long_name="equivalent potential temperature",
                units="K",
            ),
        )
    )
    return ds


def calc_wind_dir_and_speed(ds):
    """
    Input :

        dataset : Dataset

    Output :

        dataset: Dataset wind direction and wind speed

    Calculates wind direction between 0 and 360 according to https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398

    """
    w_dir = (180 + np.arctan2(ds.u.values, ds.v.values) * 180 / np.pi) % 360
    w_spd = np.sqrt(ds.u.values**2 + ds.v.values**2)

    ds = ds.assign(
        wdir=(
            ds.u.dims,
            w_dir,
            dict(
                standard_name="wind_from_direction",
                long_name="wind direction",
                units="degree",
            ),
        )
    )

    ds = ds.assign(
        wspd=(
            ds.u.dims,
            w_spd,
            dict(
                standard_name="wind_speed",
                long_name="wind speed",
                units="m s-1",
            ),
        )
    )
    return ds


def calc_wind_components(ds):
    """
    Input :

        dataset : Dataset

    Output :

        dataset: Dataset with u and v added

    Function to estimate u and v from wind speed and wind direction in the given dataset.
    """

    u = -ds.wspd.values * np.sin(np.deg2rad(ds.wdir.values))
    v = -ds.wspd.values * np.cos(np.deg2rad(ds.wdir.values))

    u_attrs = dict(
        standard_name="eastward_wind",
        long_name="u component of winds",
        units="m s-1",
    )
    u_attrs.update(dict(method="calculated from measured wind speed and direction"))

    v_attrs = dict(
        standard_name="northward_wind",
        long_name="v component of winds",
        units="m s-1",
    )
    v_attrs.update(dict(method="calculated from measured wind speed and direction"))
    ds = ds.assign(v=(ds.wspd.dims, v, v_attrs), u=(ds.wspd.dims, u, u_attrs))

    return ds

from dataclasses import dataclass
import numpy as np
import xarray as xr
import circle_fit as cf
import pydropsonde.helper as hh
import pydropsonde.helper.physics as hp
import pydropsonde.helper.xarray_helper as hx

_no_default = object()


@dataclass(order=True)
class Circle:
    """Class identifying a circle and containing its metadata.

    A `Circle` identifies the circle data for a circle on a given flight
    """

    circle_ds: str
    clon: float
    clat: float
    crad: float
    flight_id: str
    platform_id: str
    segment_id: str
    alt_dim: str
    sonde_dim: str

    def drop_vars(self, variables=None):
        """
        drop m and N variables from level 3 from circle dataset
        """
        data_vars = ["u", "v", "ta", "p", "rh", "theta", "q", "altitude"]
        if variables is None:
            variables = [
                "bin_average_time",
                "interpolated_time",
                "alt_near_gpsalt",
                "alt_source",
                "alt_near_gpsalt_max_diff",
                "altitude_below_aircraft",
                "altitude_source",
            ]
        ds = self.circle_ds
        ds = (
            ds.drop_vars(
                [f"{var}_m_qc" for var in ds.variables],
                errors="ignore",
            )
            .drop_vars(
                [f"{var}_N_qc" for var in ds.variables],
                errors="ignore",
            )
            .drop_vars(
                ["gps_m_qc", "gps_N_qc", "gpspos_N_qc", "gpspos_m_qc"], errors="ignore"
            )
            .drop_vars(
                [f"{var}_qc" for var in data_vars],
                errors="ignore",
            )
            .drop_vars(
                variables,
                errors="ignore",
            )
        )

        for qc_details in [
            "sfc_physics_val",
            "near_surface_count",
            "profile_extent_max",
            "profile_sparsity_fraction",
        ]:
            ds = ds.drop_vars(
                [f"{var}_{qc_details}" for var in data_vars],
                errors="ignore",
            )
        for var in data_vars:
            try:
                del ds[var].attrs["ancillary_variables"]
            except KeyError:
                pass
        self.circle_ds = ds

        return self

    def drop_latlon(self):
        self.circle_ds = self.circle_ds.drop_vars(["lat", "lon"])
        return self

    def get_circle_flight_id(self):
        flight_id = self.circle_ds.flight_id.sel({self.sonde_dim: 0})
        self.circle_ds = self.circle_ds.drop_vars(["flight_id"]).assign(
            flight_id=flight_id
        )
        return self

    def interpolate_position(self, max_alt=300):
        ds = self.circle_ds.sortby(self.alt_dim)

        ds = ds.assign(
            {
                var: (
                    ds[var].dims,
                    ds[var]
                    .interpolate_na(
                        dim=self.alt_dim,
                        method="nearest",
                        max_gap=int(max_alt),
                        fill_value="extrapolate",
                    )
                    .values,
                    ds[var].attrs,
                )
                for var in ["lat", "lon"]
            }
        )
        self.circle_ds = ds
        return self

    def get_xy_coords_for_circles(self):
        """
        Calculate x and y from lat and lon relative to circle center.
        """

        if self.circle_ds[self.sonde_dim].size == 0:
            print(f"Empty segment {self.segment_id}:  No sondes in circle.")
            return None  # or some default value like [], np.array([]), etc.

        x_coor = (
            self.circle_ds.lon * 111.32 * np.cos(np.radians(self.circle_ds.lat)) * 1000
        )
        y_coor = self.circle_ds.lat * 110.574 * 1000

        # converting from lat, lon to coordinates in metre from (0,0).
        if self.clat is None:
            c_xc = np.full(np.size(x_coor, 1), np.nan)
            c_yc = np.full(np.size(x_coor, 1), np.nan)
            c_r = np.full(np.size(x_coor, 1), np.nan)

            for j in range(np.size(x_coor, 1)):
                a = ~np.isnan(x_coor.values[:, j])
                if a.sum() > 4:
                    c_xc[j], c_yc[j], c_r[j], _ = cf.least_squares_circle(
                        [
                            (x, y)
                            for x, y in zip(x_coor.values[:, j], y_coor.values[:, j])
                            if ~np.isnan(x)
                        ]
                    )

            self.clat = np.nanmean(c_yc) / (110.574 * 1000)
            self.clon = np.nanmean(c_xc) / (
                111.32 * np.cos(np.radians(self.clat)) * 1000
            )

            self.crad = np.nanmean(c_r)
            self.method = "circle with central coordinate calculated as average from all sondes in circle."
        else:
            self.method = "circle from flight segmentation"

        yc = self.clat * 110.574 * 1000
        xc = self.clon * (111.32 * np.cos(np.radians(self.clat)) * 1000)

        delta_x = x_coor - xc
        delta_y = y_coor - yc

        delta_x_attrs = {
            "long_name": "x",
            "description": "Distance of sonde longitude to mean circle longitude",
            "units": "m",
        }
        delta_y_attrs = {
            "long_name": "y",
            "description": "Distance of sonde latitude to mean circle latitude",
            "units": "m",
        }

        self.circle_ds = self.circle_ds.assign(
            dict(
                x=([self.sonde_dim, self.alt_dim], delta_x.values, delta_x_attrs),
                y=([self.sonde_dim, self.alt_dim], delta_y.values, delta_y_attrs),
            )
        )

        return self

    def add_circle_variables_to_ds(self):
        """
        Add circle metadata to the circle dataset.
        """
        circle_radius_attrs = {
            "long_name": "circle radius",
            "description": f"Radius of {self.method}",
            "units": "m",
        }
        circle_lon_attrs = {
            "long_name": "circle longitude",
            "description": f"Longitude of {self.method}",
            "units": "degrees_east",
        }
        circle_lat_attrs = {
            "long_name": "circle latitude",
            "description": f"Latitude of {self.method}",
            "units": "degrees_north",
        }
        circle_altitude_attrs = {
            "long_name": "circle altitude",
            "description": "Mean altitude of the aircraft during the circle",
            "units": self.circle_ds[self.alt_dim].attrs["units"],
        }
        circle_time_attrs = {
            "long_name": "circle time",
            "time_zone": "UTC",
            "description": "Mean launch time of first and last sonde in circle",
        }
        self.circle_ds = self.circle_ds.assign(
            dict(
                circle_altitude=(
                    [],
                    self.circle_ds["launch_altitude"].mean().values,
                    circle_altitude_attrs,
                ),
                circle_time=(
                    [],
                    self.circle_ds["launch_time"].isel(sonde=[0, -1]).mean().values,
                    circle_time_attrs,
                ),
                circle_lon=([], self.clon, circle_lon_attrs),
                circle_lat=([], self.clat, circle_lat_attrs),
                circle_radius=([], self.crad, circle_radius_attrs),
            )
        )
        return self

    def add_circle_id_variable(self):
        ds = self.circle_ds
        attrs = {
            "descripion": "unique circle ID from flight segmentation",
            "long_name": "circle identifier",
        }
        ds = ds.assign({"circle_id": self.segment_id})
        ds["circle_id"] = ds["circle_id"].assign_attrs(attrs)
        self.circle_ds = ds
        return self

    def extrapolate_na_sondes(self, max_alt=300):
        """
        CAREFUL: This should be used after interpolate_na_sondes, because of the p interpolation
        """
        ds = self.circle_ds.sortby(self.alt_dim)

        constant_vars = ["u", "v", "q", "theta"]
        ds = ds.assign(
            {
                var: (
                    ds[var].dims,
                    ds[var]
                    .interpolate_na(
                        dim=self.alt_dim,
                        method="nearest",
                        max_gap=int(max_alt),
                        fill_value="extrapolate",
                    )
                    .values,
                    ds[var].attrs,
                )
                for var in constant_vars
            }
        )
        p_log = np.log(
            ds.reset_coords().p.sel({self.alt_dim: slice(0, max_alt + 1000)})
        ).interpolate_na(
            dim=self.alt_dim,
            method="linear",
            max_gap=int(max_alt),
            fill_value="extrapolate",
        )
        ds = ds.assign(
            p=(
                ds.p.dims,
                xr.concat(
                    [
                        np.exp(p_log),
                        ds.reset_coords().p.sel(
                            {self.alt_dim: slice(max_alt + 1001, None)}
                        ),
                    ],
                    dim=self.alt_dim,
                ).values,
                ds.p.attrs,
            )
        )

        self.circle_ds = ds
        return self

    def interpolate_na_sondes(self, method="akima", max_gap=1500, thresh=4):
        if method is not None:
            ds = self.circle_ds.swap_dims({self.sonde_dim: "sonde_id"})
            alt_dim = self.alt_dim
            ds["p"] = np.log(ds["p"])

            for var in [
                var
                for var in ds.variables
                if set([alt_dim, "sonde_id"]).issubset(ds.variables[var].dims)
            ]:
                interp = ds[var].interpolate_na(
                    dim=alt_dim,
                    method=method,
                    max_gap=int(max_gap),
                )
                ds = ds.assign(
                    {
                        var: (
                            ds[var].dims,
                            interp.values,
                            ds[var].attrs,
                        )
                    }
                )
            ds["p"] = np.exp(ds["p"])
            self.circle_ds = ds.swap_dims({"sonde_id": self.sonde_dim})

        return self

    def recalculate_q_ta(self):
        ds = self.circle_ds
        ds = hh.calc_T_from_theta(ds)
        ds = hh.calc_q_from_rh_sonde(ds)
        self.circle_ds = ds
        return self

    def mask_sonde(self, sonde_id=0):
        ds = self.circle_ds
        alt_mask = np.full(ds.u.shape, True)
        alt_mask[int(sonde_id), :] = False

        for var in ["u", "v", "rh", "q", "ta", "theta", "x", "y"]:
            self.circle_ds = self.circle_ds.assign(
                {var: (ds[var].dims, ds[var].where(alt_mask).values, ds[var].attrs)}
            )
        return self

    @staticmethod
    def fit2d(x, y, u, weight=1):
        weight = np.asarray(weight)
        a = np.stack([np.ones_like(x), x, y], axis=-1)

        invalid = np.isnan(u) | np.isnan(x) | np.isnan(y)
        # remove values where fewer than 6 sondes are present. Depending on the application, this might be changed.
        under_constraint = np.sum(~invalid, axis=-1) < 6
        a[invalid] = 0
        sqw = np.where(invalid, 0, np.sqrt(weight))
        wa = sqw[..., np.newaxis] * a
        u_cal = sqw * np.where(invalid, 0, u)

        a_inv = np.linalg.pinv(wa)
        intercept, dux, duy = np.einsum("...rm,...m->r...", a_inv, u_cal)

        intercept[under_constraint] = np.nan
        dux[under_constraint] = np.nan
        duy[under_constraint] = np.nan
        return intercept, dux, duy

    def fit2d_xr(self, x, y, u, weight, sonde_dim="sonde"):
        return xr.apply_ufunc(
            self.__class__.fit2d,  # Call the static method without passing `self`
            x,
            y,
            u,
            weight,
            input_core_dims=[
                [sonde_dim],
                [sonde_dim],
                [sonde_dim],
                [sonde_dim],
            ],  # Specify input dims
            output_core_dims=[(), (), ()],  # Output dimensions as scalars
        )

    def apply_fit2d(self, variables=None):
        if variables is None:
            variables = [
                "u",
                "v",
                "q",
                "ta",
                "p",
                "rh",
                "theta",
                "wdir",
                "wspd",
                "iwv",
            ]
        alt_var = self.alt_dim
        alt_attrs = self.circle_ds[alt_var].attrs

        assign_dict = {}

        for par in variables:
            try:
                long_name = self.circle_ds[par].attrs.get("long_name")
            except KeyError:
                pass
            else:
                standard_name = self.circle_ds[par].attrs.get("standard_name")
                varnames = [
                    par + "_mean",
                    par + "_d" + par + "dx",
                    par + "_d" + par + "dy",
                ]
                var_units = self.circle_ds[par].attrs.get("units", None)
                long_names = [
                    "circle mean of " + long_name,
                    "zonal gradient of " + long_name,
                    "meridional gradient of " + long_name,
                ]
                use_names = [
                    "",
                    "eastward_derivative_of_" + standard_name,
                    "northward_derivative_of_" + standard_name,
                ]
                try:
                    weight = self.circle_ds[f"{par}_weights"]
                except KeyError:
                    weight = xr.ones_like(self.circle_ds[par])

                results = self.fit2d_xr(
                    x=self.circle_ds.x,
                    y=self.circle_ds.y,
                    u=self.circle_ds[par],
                    weight=weight,
                    sonde_dim=self.sonde_dim,
                )

                for varname, result, long_name, use_name in zip(
                    varnames, results, long_names, use_names
                ):
                    if "mean" in varname:
                        assign_dict[varname] = (
                            [alt_var],
                            result.data,
                            {
                                "long_name": long_name,
                                "units": var_units,
                            },
                        )
                    else:
                        assign_dict[varname] = (
                            [alt_var],
                            result.data,
                            {
                                "standard_name": use_name,
                                "long_name": long_name,
                                "units": f"{var_units} m-1",
                            },
                        )

        ds = self.circle_ds.assign(assign_dict)
        ds[alt_var].attrs.update(alt_attrs)

        self.circle_ds = ds
        return self

    def add_regression_stderr(self, variables=None):
        """
        Calculation of regression standard error, following Lenschow, Donald H and Savic-Jovcic,Verica and Stevens, Bjorn 2007

        """
        alt_dim = self.alt_dim
        sonde_dim = self.sonde_dim
        if variables is None:
            variables = ["u", "v", "q", "ta", "p", "rh", "theta"]
        ds = self.circle_ds

        dx_denominator = ((ds.x - ds.x.mean(dim=sonde_dim)) ** 2).sum(dim=sonde_dim)
        dy_denominator = ((ds.y - ds.y.mean(dim=sonde_dim)) ** 2).sum(dim=sonde_dim)

        for var in variables:
            dvardx_name = f"{var}_d{var}dx"
            dvardy_name = f"{var}_d{var}dy"

            var_err = (
                ds[var]
                - (ds[f"{var}_mean"] + ds[dvardx_name] * ds.x + ds[dvardy_name] * ds.y)
            ) ** 2
            nominator = (var_err.sum(dim=sonde_dim)) / (
                var_err.count(dim=sonde_dim) - 3
            )
            se_x = np.sqrt(nominator / dx_denominator)
            se_y = np.sqrt(nominator / dy_denominator)

            dvardx_std_name = ds[dvardx_name].attrs.get("standard_name", "")
            unit = ds[dvardx_name].attrs.get("units", "")
            dvardy_std_name = ds[dvardy_name].attrs.get("standard_name", "")

            ds = ds.assign(
                {
                    f"{dvardx_name}_std_error": (
                        [alt_dim],
                        (se_x.where(~np.isnan(ds[dvardx_name])).values),
                        dict(
                            standard_name=f"{dvardx_std_name} standard_error",
                            units=unit,
                        ),
                    ),
                    f"{dvardy_name}_std_error": (
                        [alt_dim],
                        (se_y.where(~np.isnan(ds[dvardy_name])).values),
                        dict(
                            standard_name=f"{dvardy_std_name} standard_error",
                            units=unit,
                        ),
                    ),
                }
            )
            ds = hx.add_ancillary_var(ds, dvardx_name, f"{dvardx_name}_std_error")
            ds = hx.add_ancillary_var(ds, dvardy_name, f"{dvardy_name}_std_error")
        div_error_name = "div_std_error"
        div_std_name = ds["div"].attrs.get("standard_name", "divergence_of_wind")
        ds = ds.assign(
            {
                div_error_name: (
                    [alt_dim],
                    np.sqrt(ds.u_dudx_std_error**2 + ds.v_dvdy_std_error**2).values,
                    dict(
                        standard_name=f"{div_std_name} standard_error",
                        units=ds.div.attrs.get("units", "s-1"),
                    ),
                )
            }
        )
        vor_std_name = ds["vor"].attrs.get(
            "standard_name", "atmosphere_upward_relative_vorticity"
        )
        ds = ds.assign(
            {
                "vor_std_error": (
                    [alt_dim],
                    np.sqrt(ds.u_dudy_std_error**2 + ds.v_dvdx_std_error**2).values,
                    dict(
                        standard_name=f"{vor_std_name} standard_error",
                        units=ds.vor.attrs.get("units", "s-1"),
                    ),
                )
            }
        )

        ds = hx.add_ancillary_var(ds, "div", "div_std_error")
        ds = hx.add_ancillary_var(ds, "vor", "vor_std_error")
        se_div_nona = ds[div_error_name].dropna(dim=alt_dim)
        wvel_std_name = ds["wvel"].attrs.get("standard_name", "upward_air_velocity")
        ds = ds.assign(
            {
                "wvel_std_error": (
                    ds[div_error_name].dims,
                    (
                        np.sqrt((se_div_nona**2).cumsum(dim=alt_dim))
                        * se_div_nona[alt_dim].diff(dim=alt_dim)
                    )
                    .broadcast_like(ds[div_error_name])
                    .values,
                    dict(
                        standard_name=f"{wvel_std_name} standard_error",
                        units=ds["wvel"].attrs.get("units", "m s-1"),
                    ),
                )
            }
        )
        ds = hx.add_ancillary_var(ds, "wvel", "wvel_std_error")

        omega_std_name = ds["omega"].attrs.get(
            "standard_name", "vertical_air_velocity_expressed_as_tendency_of_pressure"
        )

        ds = ds.assign(
            {
                "omega_std_error": (
                    ds[div_error_name].dims,
                    (
                        np.sqrt((se_div_nona**2).cumsum(dim=alt_dim))
                        * ds.p_mean.sel({alt_dim: se_div_nona[alt_dim]}).diff(
                            dim=alt_dim
                        )
                    )
                    .broadcast_like(ds[div_error_name])
                    .values,
                    dict(
                        standard_name=f"{omega_std_name} standard_error",
                        units=ds["omega"].attrs.get("units", "Pa s-1"),
                    ),
                )
            }
        )
        ds = hx.add_ancillary_var(ds, "omega", "omega_std_error")

        self.circle_ds = ds
        return self

    def drop_dvardxy(self, variables=None):
        if variables is None:
            variables = ["iwv", "wspd", "wdir"]
        self.circle_ds = self.circle_ds.drop_vars(
            [f"{var}_d{var}dx" for var in variables],
            errors="ignore",
        ).drop_vars(
            [f"{var}_d{var}dy" for var in variables],
            errors="ignore",
        )
        if "iwv_mean" in self.circle_ds.variables:
            self.circle_ds = self.circle_ds.assign(
                iwv_mean=(
                    "circle",
                    [self.circle_ds["iwv_mean"].mean("altitude").values],
                    self.circle_ds["iwv_mean"].attrs,
                )
            )
        return self

    def calc_remove_sonde_manipulation(self):
        ds = self.circle_ds.copy()
        remove_sonde_vals = {
            "div": [],
            "vor": [],
            "omega": [],
            "wvel": [],
        }
        for sonde_id in ds.sonde:
            self.get_xy_coords_for_circles()
            self.drop_vars()
            self.mask_sonde(sonde_id=sonde_id)
            self.interpolate_na_sondes()
            self.apply_fit2d()
            self.add_divergence()
            self.add_vorticity()
            self.add_omega()
            self.add_wvel()
            for var in ["div", "vor", "omega", "wvel"]:
                remove_sonde_vals[var].append(self.circle_ds[var])

            self.circle_ds = ds.copy()
        self.remove_sonde_ds = remove_sonde_vals
        return self

    def add_sonde_relevance_to_ds(self):
        ds = self.circle_ds
        for var in ["div", "vor", "omega", "wvel"]:
            var_err = xr.concat(
                [remove_ds - ds[var] for remove_ds in self.remove_sonde_ds[var]],
                dim="sonde",
            )
            var_attr = dict(
                long_name=f"helper variable for {var}",
                description=f"Difference in {var} if this sonde is removed from circle before calculation",
            )
            ds = ds.assign(
                {
                    f"{var}_sonde_relevance": (
                        (self.sonde_dim, self.alt_dim),
                        var_err.values,
                        var_attr,
                    )
                }
            )
            ds = hx.add_ancillary_var(ds, var, f"{var}_sonde_relevance")
        self.circle_ds = ds
        return self

    def add_density(self):
        """
        Calculate and add the density to the circle dataset.

        This method computes each sondes density.
        The result is added to the dataset.

        Returns:
            self: circle object with updated circle_ds
        """
        ds = self.circle_ds
        assert ds.p.attrs["units"] == "Pa"
        assert ds.ta.attrs["units"] == "K"
        density = hp.density_from_q(
            ds.p,
            ds.ta,
            ds.q,
        )
        density_attrs = {
            "standard_name": "air_density",
            "long_name": "Air density (moist)",
            "units": "kg m-3",
        }
        self.circle_ds = ds.assign(
            dict(
                density=(ds.ta.dims, density.values, density_attrs),
            )
        )
        return self

    def add_divergence(self):
        """
        Calculate and add the divergence to the circle dataset.

        This method computes the area-averaged horizontal mass divergence.
        The result is added to the dataset.

        Returns:
            self: circle object with updated circle_ds
        """
        ds = self.circle_ds
        D = ds.u_dudx + ds.v_dvdy
        D_attrs = {
            "standard_name": "divergence_of_wind",
            "long_name": "Area-averaged horizontal mass divergence",
            "units": "s-1",
        }
        self.circle_ds = ds.assign(div=(ds.u_dudx.dims, D.values, D_attrs))
        return self

    def add_vorticity(self):
        """
        Calculate and add the vorticity to the circle dataset.

        This method computes the area-averaged horizontal vorticity.
        The result is added to the dataset.

        Returns:
            self: circle object with updated circle_ds
        """
        ds = self.circle_ds
        vor = ds.v_dvdx - ds.u_dudy
        vor_attrs = {
            "standard_name": "atmosphere_upward_relative_vorticity",
            "long_name": "Area-averaged relative vorticity",
            "units": "s-1",
        }
        self.circle_ds = ds.assign(vor=(ds.u_dudx.dims, vor.values, vor_attrs))
        return self

    def add_omega(self):
        """
        Calculate vertical pressure velocity as
        \int div dp

        This calculates the vertical pressure velocity as described in
        Bony and Stevens 2019

        Returns:
            self: circle object with updated circle_ds
        """
        ds = self.circle_ds
        alt_dim = self.alt_dim
        div = ds.div.where(~np.isnan(ds.div), drop=True).sortby(alt_dim)
        p = ds.p_mean.where(~np.isnan(ds.div), drop=True).sortby(alt_dim)
        zero_vel = xr.DataArray(data=[0], dims=alt_dim, coords={alt_dim: [0]})
        if p.sizes["altitude"] > 0:
            pres_diff = xr.concat([zero_vel, p.diff(dim=alt_dim)], dim=alt_dim)
            del_omega = -div * pres_diff.values
            omega = del_omega.cumsum(dim=alt_dim)
        else:
            omega = xr.DataArray(data=[np.nan], dims=alt_dim, coords={alt_dim: [0]})
        omega_attrs = {
            "standard_name": "vertical_air_velocity_expressed_as_tendency_of_pressure",
            "long_name": "Area-averaged atmospheric pressure velocity (omega)",
            "units": "Pa s-1",
        }
        self.circle_ds = ds.assign(
            dict(omega=(ds.div.dims, omega.broadcast_like(ds.div).values, omega_attrs))
        )
        return self

    def add_wvel(self):
        """
        Calculate vertical velocity as
        - int diff dz

        This calculates the vertical velocity from omega

        Returns:
            self: circle object with updated circle_ds
        """
        ds = self.circle_ds
        alt_dim = self.alt_dim
        div = ds.div.where(~np.isnan(ds.div), drop=True).sortby(alt_dim)
        zero_vel = xr.DataArray(data=[0], dims=alt_dim, coords={alt_dim: [0]})
        if div.sizes["altitude"] > 0:
            height = xr.concat([zero_vel, div[alt_dim]], dim=alt_dim)
            height_diff = height.diff(dim=alt_dim)
            del_w = -div * height_diff.values
            w_vel = del_w.cumsum(dim=alt_dim)
        else:
            w_vel = xr.DataArray(data=[np.nan], dims=alt_dim, coords={alt_dim: [0]})
        wvel_attrs = {
            "standard_name": "upward_air_velocity",
            "long_name": "Area-averaged atmospheric vertical velocity",
            "units": "m s-1",
        }
        self.circle_ds = ds.assign(
            dict(wvel=(ds.omega.dims, w_vel.broadcast_like(ds.div).values, wvel_attrs))
        )
        return self

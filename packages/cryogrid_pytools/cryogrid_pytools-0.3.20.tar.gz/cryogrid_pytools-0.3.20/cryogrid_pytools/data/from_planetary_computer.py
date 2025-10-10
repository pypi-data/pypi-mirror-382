try:
    import rioxarray as _rxr  # noqa
    import stackstac as _stackstac  # noqa
    import pystac_client as _pystac_client
    import planetary_computer as _planetary_computer
    from .. import xr_raster_vector as _xrv  # noqa
    from ..utils import drop_coords_without_dim
except ImportError as e:
    missing_package = str(e).split("'")[1]
    raise ImportError(
        f"Missing optional dependency '{missing_package}'. "
        "Please install it using: pip install 'cryogrid_pytools[data]'"
    )

# if cryogrid_pytools[data] dependencies are not installed,
# then warn the user that this package cannot be imported
import xarray as _xr
from loguru import logger as _logger

from . import utils


def search_stac_items_planetary_computer(collection, bbox, **kwargs) -> list:
    """
    Searches for STAC items from the Planetary Computer.

    Parameters
    ----------
    collection : str
        The name of the collection to search within.
    bbox : list
        The bounding box to search within, specified as [minx, miny, maxx, maxy].
    **kwargs : Additional keyword arguments to pass to the search.

    Returns
    -------
    list
        A list of STAC items matching the search criteria.
    """

    URL_PLANETARY_COMPUTER = "https://planetarycomputer.microsoft.com/api/stac/v1"

    catalog = _pystac_client.Client.open(
        url=URL_PLANETARY_COMPUTER, modifier=_planetary_computer.sign_inplace
    )

    search = catalog.search(collections=[collection], bbox=bbox, **kwargs)

    items = search.item_collection()

    return items


@utils._decorator_dataarray_to_bbox
def get_dem_copernicus(
    bbox_WSEN: list,
    res: int = 30,
    epsg=32643,
    collection="cop-dem-glo-30",
    smoothing_iters=2,
    smoothing_size=3,
) -> _xr.DataArray:
    """
    Download DEM data from the STAC catalog (default is COP DEM Global 30m).

    Parameters
    ----------
    bbox_WSEN : list
        The bounding box of the area of interest in WSEN format.
    res : int
        The resolution of the DEM data in EPSG units.
    epsg : int, optional
        The EPSG code of the projection of the DEM data. Default is
        EPSG:32643 (UTM 43N) for the Pamir region.
    collection : str, optional
        The STAC collection to search for DEM data. Default is "cop-dem-glo-30".
        Also supports "cop-dem-glo-90" for 90m resolution.
    smoothing_iters : int, optional
        The number of iterations to apply the smoothing filter. Default is 2.
        Set to 0 to disable smoothing.
    smoothing_size : int, optional
        The size of the kernel (num pixels) for the smoothing filter. Default is 3.

    Returns
    -------
    xarray.DataArray
        The DEM data as an xarray DataArray with attributes.
    """
    from .utils import check_epsg, smooth_data

    check_epsg(epsg)

    _logger.debug(
        f"Fetching COP DEM Global data from Planetary Computer ({collection} @ {res:.2g})"
    )
    items = search_stac_items_planetary_computer(collection, bbox_WSEN)
    da_dem = _stackstac.stack(
        items=items, bounds_latlon=bbox_WSEN, resolution=res, epsg=epsg
    )

    da_dem = (
        da_dem.mean("time")
        .squeeze()
        .pipe(drop_coords_without_dim)
        .pipe(smooth_data, n_iters=smoothing_iters, kernel_size=smoothing_size)
        .rio.write_crs(f"EPSG:{epsg}")
        .rename(collection)
        .assign_attrs(
            source=items[0].links[0].href,  # collection URL
            bbox_request=bbox_WSEN,
        )
    )

    return da_dem


@utils._decorator_dataarray_to_bbox
def get_esa_land_cover(bbox_WSEN: tuple, res: int = 30, epsg=32643) -> _xr.DataArray:
    """
    Get the ESA World Cover dataset on the target grid and resolution.

    Parameters
    ----------
    bbox_WSEN : tuple
        Bounding box in the format (West, South, East, North).
    res : int, optional
        Resolution in EPSG units. Defaults to 30 (meters for UTM).
    epsg : int, optional
        EPSG code for the coordinate reference system. Defaults to 32643.

    Returns
    -------
    xr.DataArray
        A DataArray with the land cover data on the target grid. Contains
        attributes 'class_values', 'class_descriptions', 'class_colors' for plotting.
    """
    from .utils import _long_string_processor, check_epsg

    def get_land_cover_classes(item):
        """
        Get the land cover class names, and colors from the ESA World Cover dataset

        Args:
            item (pystac.Item): The STAC item containing the land cover data.

        Returns:
            dict: A dictionary with class values, descriptions, and colors.
        """
        import pandas as pd

        classes = item.assets["map"].extra_fields["classification:classes"]
        df = (
            pd.DataFrame(classes)
            .set_index("value")
            .rename(
                columns=lambda s: s.replace("-", "_")
            )  # bug fix for version 2.7.8 (stacstack back compatibility)
        )

        df["color_hint"] = "#" + df["color_hint"]

        out = dict(
            class_values=df.index.values,
            class_descriptions=df["description"].values,
            class_colors=df["color_hint"].values,
        )

        return out

    # make sure epsg is supported
    check_epsg(epsg)

    _logger.debug(
        f"Fetching ESA World Cover (v2.0) data from Planetary Computer (esa-worldcover @ {res}m)"
    )
    items = search_stac_items_planetary_computer(
        collection="esa-worldcover",
        bbox=bbox_WSEN,
        query={"esa_worldcover:product_version": {"eq": "2.0.0"}},
    )

    stac_props = dict(
        items=items, assets=["map"], epsg=epsg, bounds_latlon=bbox_WSEN, resolution=res
    )

    da = (
        _stackstac.stack(**stac_props)
        .max(["band", "time"], keep_attrs=True)  # removing the single band dimension
        .rename("esa_world_cover")
        .assign_attrs(
            **get_land_cover_classes(items[0]),
            description=_long_string_processor(
                """
                The European Space Agency (ESA) WorldCover product provides global land cover maps
                for the years 2020 and 2021 at 10 meter resolution based on the combination of Sentinel-1
                radar data and Sentinel-2 imagery. The discrete classification maps provide 11 classes
                defined using the Land Cover Classification System (LCCS) developed by the
                United Nations (UN) Food and Agriculture Organization (FAO). The map images are
                stored in cloud-optimized GeoTIFF format.
                WorldCover product is developed by a consortium of European service providers and
                research organizations. VITO (Belgium) is the prime contractor of the WorldCover consortium
                together with Brockmann Consult (Germany), CS SI (France), Gamma Remote Sensing AG (Switzerland),
                International Institute for Applied Systems Analysis (Austria),
                and Wageningen University (The Netherlands)."""
            ),
        )
    )

    da = da.pipe(drop_coords_without_dim).rio.write_crs(f"EPSG:{epsg}")

    return da


@utils._decorator_dataarray_to_bbox
def get_esri_land_cover(bbox_WSEN: tuple, res: int = 30, epsg: int = 32643):
    from .utils import _long_string_processor

    items = search_stac_items_planetary_computer(
        collection="io-lulc-9-class",
        bbox=bbox_WSEN,
        datetime="2020-01-01/2020-12-31",
    )

    da = (
        _stackstac.stack(
            items,
            epsg=epsg,
            resolution=res,
            bounds_latlon=bbox_WSEN,
        )
        .mean("time")
        .isel(band=0)
    )

    da = da.rename("land_use_and_cover").assign_attrs(
        long_name="Land use and land cover (LULC) from ESA Sentinel-2",
        class_values={
            0: "No Data",
            1: "Water",
            2: "Trees",
            4: "Flooded vegetation",
            5: "Crops",
            7: "Built area",
            8: "Bare ground",
            9: "Snow/ice",
            10: "Clouds",
            11: "Rangeland",
        },
        link="https://planetarycomputer.microsoft.com/dataset/io-lulc-annual-v02",
        description=_long_string_processor(
            """
            Time series of annual global maps of land use and land cover (LULC). It currently has data from 2017-2023.
            The maps are derived from ESA Sentinel-2 imagery at 10m resolution. Each map is a composite of LULC
            predictions for 9 classes throughout the year in order to generate a representative snapshot of each year.
            This dataset, produced by Impact Observatory, Microsoft, and Esri, displays a global map of land use and
            land cover (LULC) derived from ESA Sentinel-2 imagery at 10 meter resolution for the years 2017 - 2023.
            Each map is a composite of LULC predictions for 9 classes throughout the year in order to generate a
            representative snapshot of each year. This dataset was generated by Impact Observatory, which used billions
            of human-labeled pixels (curated by the National Geographic Society) to train a deep learning model for
            land classification. Each global map was produced by applying this model to the Sentinel-2 annual scene
            collections from the Mircosoft Planetary Computer. Each of the maps has an assessed average accuracy of over 75%.
            These maps have been improved from Impact Observatory's previous release and provide a relative reduction in
            the amount of anomalous change between classes, particularly between “Bare” and any of the vegetative classes
            “Trees,” “Crops,” “Flooded Vegetation,” and “Rangeland”. This updated time series of annual global maps is
            also re-aligned to match the ESA UTM tiling grid for Sentinel-2 imagery.
            All years are available under a Creative Commons BY-4.0."""
        ),
    )

    da = da.pipe(drop_coords_without_dim).rio.write_crs(f"EPSG:{epsg}")
    return da


@utils._decorator_dataarray_to_bbox
def get_sentinel2_data(
    bbox_WSEN: tuple,
    years=range(2018, 2025),
    assets=["SCL"],
    res: int = 30,
    epsg=32643,
    max_cloud_cover=5,
) -> _xr.DataArray:
    """
    Fetches Sentinel-2 data for a given bounding box and time range.

    Parameters
    ----------
    bbox_WSEN : tuple
        Bounding box in the format (West, South, East, North).
    years : range, optional
        Range of years to fetch data for. Defaults to range(2018, 2025).
    assets : list, optional
        List of assets to fetch. Defaults to ['SCL'].
    res : int, optional
        Resolution in EPSG units. Defaults to 30 (meters for UTM).
    epsg : int, optional
        EPSG code for the coordinate reference system. Defaults to 32643.
    max_cloud_cover : int, optional
        Maximum cloud cover percentage. Defaults to 5.

    Returns
    -------
    xr.DataArray
        DataArray containing the fetched Sentinel-2 data.
    """
    from .utils import check_epsg

    check_epsg(epsg)

    da_list = []
    for year in years:
        _logger.debug(
            f"Getting Sentinel-2 SCL granules @{res}m for {year} with max cloud cover = {max_cloud_cover}%"
        )

        t0, t1 = (
            f"{year}-01-01",
            f"{year}-11-15",
        )  # assuming that snow melt is done by mid-November
        items = search_stac_items_planetary_computer(
            collection="sentinel-2-l2a",
            bbox=bbox_WSEN,
            datetime=(t0, t1),
            query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        )

        da_list += (
            _stackstac.stack(
                items=items,
                assets=assets,
                bounds_latlon=bbox_WSEN,
                resolution=res,
                epsg=epsg,
            ),
        )

    da_granules = _xr.concat(da_list, dim="time")
    da = (
        da_granules.groupby("time")  # granules are not grouped by time
        .max()  # take max value to avoid mixing ints
        .squeeze()  # remove the band dimension
        .where(lambda x: x > 0)
    )  # mask null_values so that pixel coverage can be counted

    da.attrs = {}
    da = da.pipe(drop_coords_without_dim).rio.write_crs(f"EPSG:{epsg}")

    return da


@utils._decorator_dataarray_to_bbox
def get_snow_melt_doy(
    bbox_WSEN: tuple, years=range(2018, 2025), res: int = 30, epsg=32643
) -> _xr.DataArray:
    """
    Calculate the snow melt day of year (DOY) from Sentinel-2 SCL data for a given bounding box and years.

    Parameters
    ----------
    bbox_WSEN : tuple
        Bounding box coordinates in the format (West, South, East, North).
    years : range, optional
        Range of years to consider. Defaults to range(2018, 2025).
    res : int, optional
        Spatial resolution in meters. Defaults to 30.
    epsg : int, optional
        EPSG code for the coordinate reference system. Defaults to 32643.

    Returns
    -------
    _xr.DataArray
        DataArray containing the snow melt DOY for each year.
    """

    da = get_sentinel2_data(
        bbox_WSEN, years=years, res=res, epsg=epsg, max_cloud_cover=10
    )

    _logger.debug("Calculating snow melt day of year (DOY) from Sentinel-2 SCL data")
    doy = da.groupby("time.year").apply(_calc_sentinel2_snow_melt_doy)

    return doy


def _calc_sentinel2_snow_melt_doy(da_scl) -> _xr.DataArray:
    """
    Calculates the day of year (DOY) when snow melt occurs based on Sentinel-2 SCL data.

    Parameters
    ----------
    da_scl : xarray.DataArray
        The Sentinel-2 SCL data as an xarray DataArray.

    Returns
    -------
    xarray.DataArray
        The day of year when snow melt occurs as an xarray DataArray.
    """

    def drop_poor_coverage_at_end(da, threshold=0.9):
        """
        Drops the time steps at the end of the time series that
        occur after the last point that meets the threshold req.

        Example
        -------
        [0.4, 0.5, 0.3, 0.7, 0.9, 0.3]
        [keep keep keep keep keep drop]
        """
        counts = da.count(["x", "y"]).compute()
        size = da.isel(time=0).size
        frac = counts / size
        good_cover = (
            frac.bfill("time").where(lambda x: x > threshold).dropna("time").time.values
        )
        return da.sel(time=slice(None, good_cover[-1]))

    def find_time_of_lowest_snow_cover(snow_mask, window=10):
        """
        Returns the time step where the snow cover is the lowest
        """
        window = min(window, snow_mask.sizes["time"])
        filled = snow_mask.rolling(time=window, center=True, min_periods=1).max()
        lowest_cover_time = filled.count(["x", "y"]).idxmin()
        return lowest_cover_time

    def get_only_melt_period(snow_mask):
        """
        Drops time steps after snow starts increasing again
        """
        time_snow_cover_min = find_time_of_lowest_snow_cover(snow_mask)
        snow_melt_period = snow_mask.sel(time=slice(None, time_snow_cover_min))
        return snow_melt_period

    def get_max_day_of_year_from_mask(mask):
        """
        Get the maximum day of the year from a given mask.

        Parameters
        ----------
        mask : xarray.DataArray
            A DataArray with a 'time' dimension and boolean values
            indicating the mask.

        Returns
        -------
        xarray.DataArray
            A DataArray containing the maximum day of the year where the mask is True.

        Raises
        ------
        AssertionError
            If 'time' is not a dimension in the mask.
        AssertionError
            If the mask contains data from more than one year.
        """
        assert "time" in mask.dims, "'time' dimension is required"

        years = set(mask.time.dt.year.values.tolist())
        assert len(years) == 1, "Only one year is supported"

        doy_max = (
            mask.time.dt.dayofyear.where(  # get the day of year
                mask
            )  # broadcast the day of year to the mask shape
            .max("time")  # get the last time step
            .astype("float32")
            .rename("day_of_year")
        )

        return doy_max

    scl = da_scl.compute()
    scl_snow_ice = 11

    # only one year allowed
    assert scl.time.dt.year.to_series().unique().size == 1, "Only one year is allowed"

    # find the last time step with good coverage and drop everything after
    # so that we can back fill the snow cover later
    scl_tail_clipped = drop_poor_coverage_at_end(scl, threshold=0.9)
    # mask snow/ice pixels and set values to 1 instead of 11
    snow_mask = scl_tail_clipped.where(lambda x: x == scl_snow_ice) * 0 + 1

    # find the time step where snow cover is the lowest, and remove anything after
    snow_melt = get_only_melt_period(snow_mask)
    # backfill the snow cover (assuming only melt) and create mask
    snow_mask = snow_melt.bfill("time").notnull()
    # compute the melt date based on a mask
    snow_melt_day = get_max_day_of_year_from_mask(snow_mask)

    return snow_melt_day

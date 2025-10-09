"""
NASA Fire Weather Index
"""
from datetime import datetime, timedelta
from typing import List, Union

import geopandas as gpd
import pandas as pd
import xarray as xr

URL = "https://portal.nccs.nasa.gov/datashare/GlobalFWI/v2.0/fwiCalcs.GEOS-5/Default/GPM.LATE.v5"

# TODO: Add attr to the FWI


def curate_nasa_fwi(ds: xr.Dataset, bounds: List, date: datetime) -> xr.DataArray:
    """
    Curate the NASA FWI data, clipping by the bounds and setting the crs

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset containing the FWI data
    bounds : list
        The bounds of the area of interest
    date : datetime
        The date of the data

    Returns
    -------
    xarray.DataArray
        The curated data array
    """
    fwi = ds["GPM.LATE.v5_FWI"].sel(time=1)
    # Add or remove 0.1 to the bounds to make sure we get all the data
    fwi = fwi.sel(
        lon=slice(bounds[0] - 0.1, bounds[2] + 0.1),
        lat=slice(bounds[1] - 0.1, bounds[3] + 0.1),
    )
    fwi.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    fwi.rio.write_crs("epsg:4326", inplace=True)
    fwi.coords["time"] = pd.to_datetime(date)

    return fwi


def get_nasa_fwi(dates: List, gdf: Union[str, gpd.GeoDataFrame]) -> xr.Dataset:
    """
    Get the NASA FWI data for the given dates and area of interest

    Parameters
    ----------
    dates : list
        The start and end dates of the data
    aoi : str
        The path to the area of interest file

    Returns
    -------
    xarray.Dataset
        The dataset containing the FWI data
    """
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    if isinstance(gdf, str):
        gdf = gpd.read_file(gdf)
    bounds = gdf.total_bounds

    current_date = dates[0]
    data_arrays = []
    while current_date <= dates[1]:
        year = current_date.year
        date_formatted = datetime.strftime(current_date, "%Y%m%d")
        file_url = (
            f"{URL}/{year}/FWI.GPM.LATE.v5.Daily.Default.{date_formatted}.nc#mode=bytes"
        )
        try:
            ds = xr.open_dataset(file_url)
        except OSError:
            current_date += timedelta(days=1)
            continue
        try:
            fwi_data_array = curate_nasa_fwi(ds, bounds, current_date)
        except KeyError:
            current_date += timedelta(days=1)
            continue
        data_arrays.append(fwi_data_array)
        current_date += timedelta(days=1)

    try:
        combined = xr.concat(data_arrays, dim="time").to_dataset(name="fwi")
    except ValueError:
        return None

    combined.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    combined.rio.write_crs("epsg:4326", inplace=True)

    return combined


def download_nasa_fwi(dates: List, aoi: str, storage):
    """
    Download the NASA FWI data for the given dates and area of interest

    Parameters
    ----------
    dates : list
        The start and end dates of the data
    aoi : str
        The path to the area of interest file
    storage : BaseStorage
        The storage object
    """
    fwi = get_nasa_fwi(dates, aoi)
    curated_fwi = fwi["fwi"].to_dataset(name="fwi")
    storage.create_from_zarr(curated_fwi, name="fwi")

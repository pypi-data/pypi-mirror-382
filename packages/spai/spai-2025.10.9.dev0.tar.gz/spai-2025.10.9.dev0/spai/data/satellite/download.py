"""
Download satellite imagery data
"""

from os.path import dirname
from shutil import rmtree
import numpy as np
from typing import List, Union, Optional, Any
from datetime import datetime

from . import DOWNLOADERS

from .stac.STACDownloader import STACDownloader
from .sentinelhub.SHDownloader import SHDownloader

from .load import load_satellite_imagery
from .explore import explore_satellite_imagery

from ...storage import Storage


def download_satellite_imagery(
    storage: Storage,
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    name: Optional[str] = None,
    clip: Optional[bool] = False,
    crs: Optional[str] = "epsg:4326",
    **kwargs,
) -> List[str]:
    """
    Download satellite imagery data from a given area of interest (aoi) and date to a given storage.

    Parameters
    ----------
    storage : Storage
        Storage object to save the data.
    aoi : Any
        Area of interest. It can be a GeoDataFrame, a list of coordinates, a bounding box, etc.
    date : Optional[List[Union[str, datetime]]], optional
        Date of the image, by default None. If None, the last available image will be loaded.
    collection : str, optional
        Satellite collection to download, by default "sentinel-2-l2a"
    clip : Optional[bool], optional
        Clip the data to the area of interest, by default False
    crs : Optional[str], optional
        Coordinate Reference System, by default "epsg:4326"
    kwargs : dict
        Extra parameters to pass to the downloader, such as bands, cloud_cover, vegetation_percentage an so on.   TODO

    Returns
    -------
    None
    """
    if issubclass(DOWNLOADERS[collection], STACDownloader):
        # Download using the STACDownloader
        return download_with_stac(
            storage, aoi, date, collection, name, clip, crs, **kwargs
        )
    elif issubclass(DOWNLOADERS[collection], SHDownloader):
        # Download using the SHDownloader
        return download_with_sentinelhub(
            storage, aoi, date, collection, name, crs, **kwargs
        )


def download_with_stac(
    storage: Storage,
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    name: Optional[str] = None,
    clip: Optional[bool] = False,
    crs: Optional[str] = "epsg:4326",
    **kwargs,
):
    """
    Downloads satellite imagery using the STAC (SpatioTemporal Asset Catalog) protocol.

    This function fetches and downloads satellite images from a specified collection
    based on the area of interest (AOI), date range, and other optional parameters.
    The downloaded images can be optionally clipped to the AOI and stored with a custom name.

    Parameters
    ----------
    storage : Storage
        The storage system where the downloaded images will be saved.
    aoi : Any
        The area of interest which can be specified in various formats (e.g., GeoJSON).
    date : Optional[List[Union[str, datetime]]], optional
        The date range for the satellite imagery query, by default None.
    collection : str, optional
        The name of the satellite imagery collection to query, by default "sentinel-2-l2a".
    name : Optional[str], optional
        Custom name for the saved images, by default None.
    clip : Optional[bool], optional
        Flag to clip the downloaded images to the AOI, by default False.
    crs : Optional[str], optional
        Coordinate reference system to be used for the images, by default "epsg:4326".
    **kwargs
        Additional keyword arguments for the STAC query.

    Returns
    -------
    Union[str, List[str]]
        A string or a list of strings with the paths of the downloaded images.
    """
    data = load_satellite_imagery(aoi, date, collection, clip, crs, **kwargs)
    if not data:
        print("No data available to download")
        return
    data = data.compute()
    paths = []
    for date in data.time.values:
        date = np.datetime_as_string(date, unit="D")
        path = storage.create(
            data.sel(time=date).squeeze(),
            name=name if name else f"{collection}_{date}.tif",
        )
        paths.append(path)
    return paths if len(paths) > 1 else paths[0]


def download_with_sentinelhub(
    storage: Storage,
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    name: Optional[str] = None,
    crs: Optional[str] = "epsg:4326",
    download_folder: Optional[str] = "/tmp/sentinelhub",
    **kwargs,
):
    """
    Downloads satellite imagery using the Sentinel Hub service.

    This function interfaces with the Sentinel Hub service to fetch and download
    satellite images based on the specified area of interest (AOI), date range,
    and collection. The images are stored in the specified storage system, optionally
    with a custom name.

    Parameters
    ----------
    storage : Storage
        The storage system where the downloaded images will be saved.
    aoi : Any
        The area of interest which can be specified in various formats (e.g., GeoJSON).
    date : Optional[List[Union[str, datetime]]], optional
        The date range for the satellite imagery query, by default None.
    collection : str, optional
        The name of the satellite imagery collection to query, by default "sentinel-2-l2a".
    name : Optional[str], optional
        Custom name for the saved images, by default None.
    crs : Optional[str], optional
        Coordinate reference system to be used for the images, by default "epsg:4326".
    download_folder: Optional[str], optional
        Temporary folder where the data is going to be downloaded
    **kwargs
        Additional keyword arguments for the Sentinel Hub query.

    Returns
    -------
    Union[str, List[str]]
        A string or a list of strings with the paths of the downloaded images.
    """
    results = explore_satellite_imagery(aoi, date, collection, crs, **kwargs)
    if not results:
        print(f"No data available to download for {date}")
        return

    downloader = DOWNLOADERS[collection](download_folder)

    # Get the dates of every result
    dates = []
    for result in results:
        date_str = result["date"]
        try:
            # Try to parse the date with milliseconds
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            # If it fails, parse the date without milliseconds
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        date = date_obj.strftime("%Y-%m-%d")
        dates.append(date) if date not in dates else None

    dates.sort()

    # Download the image for every date
    paths = []
    for date in dates:
        path = downloader.download(aoi, date, **kwargs)
        dst_path = storage.create(
            path,
            name=name if name else f"{collection}_{date}.tif",
        )
        paths.append(dst_path)
        rmtree(dirname(path))  # Remove the temporary folder
    return paths if len(paths) > 1 else paths[0]

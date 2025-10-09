"""
Explore satellite imagery data
"""

from typing import List, Union, Optional, Any
from datetime import datetime

from . import DOWNLOADERS, AVAILABLE_COLLECTIONS
from .utils import is_valid_datetime_param
from .sentinelhub import SHExplorer, SHDownloader
from .stac.STACDownloader import STACDownloader

from .utils import (
    create_aoi_geodataframe,
    get_last_month,
    add_item_extra_properties,
)


def explore_satellite_imagery(
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    crs: Optional[str] = "epsg:4326",
    **kwargs,
) -> dict:
    """
    Explore satellite imagery data from a given area of interest (aoi) and date.

    Parameters
    ----------
    aoi : Any
        Area of interest. It can be a GeoDataFrame, a list of coordinates, a bounding box, etc.
    date : Optional[List[Union[str, datetime]]], optional
        Date of the image, by default None. If None, the available images of the last month will be loaded.
    collection : str, optional
        Satellite collection to download, by default "sentinel-2-l2a"
    crs : Optional[str], optional
        Coordinate Reference System, by default "epsg:4326"
    kwargs : dict
        Extra parameters to pass to the downloader, such as bands, cloud_cover, vegetation_percentage an so on.   TODO

    Returns
    -------
    dict
        Information about the available images. If no image is found, it returns None. If any extra parameter is given, it will be added to the output.
    """
    gdf = create_aoi_geodataframe(aoi, crs)
    bbox = gdf.total_bounds

    if collection not in AVAILABLE_COLLECTIONS:
        raise ValueError(
            f"Collection {collection} not available. Available collections are: {AVAILABLE_COLLECTIONS}"
        )

    if not date:
        date = get_last_month()
    else:
        if not is_valid_datetime_param(date):
            raise ValueError("Invalid date parameter. Please provide a valid date.")

    if issubclass(DOWNLOADERS[collection], STACDownloader):
        # Explore using the STAC
        return explore_with_stac(bbox, date, collection, **kwargs)
    elif issubclass(DOWNLOADERS[collection], SHDownloader):
        # Explore using the SentinelHub
        return explore_with_sentinelhub(gdf, date, collection, **kwargs)


def explore_with_stac(
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    **kwargs,
):
    """
    Explores available satellite imagery for a given area of interest (AOI), date range,
    and collection using the STAC (SpatioTemporal Asset Catalog) protocol.

    This function searches for available satellite images within the specified parameters
    and returns a list of metadata for each image found. The metadata includes the image ID,
    datetime, and optionally a thumbnail URL among other properties that can be added based
    on the query.

    Parameters
    ----------
    aoi : Any
        The area of interest for which to search satellite imagery. This can be specified
        in various formats, such as a bounding box or a GeoJSON object.
    date : Union[str, List[str], datetime, List[datetime]]
        The date range for the satellite imagery search. Can be a single date or a list
        representing a range.
    collection : str
        The name of the satellite imagery collection to search within.
    **kwargs : dict
        Additional keyword arguments that can be passed to the STAC search query.

    Returns
    -------
    Optional[List[dict]]
        A list of dictionaries, each containing metadata for a found satellite image.
        Returns None if no images are found.
    """
    downloader = DOWNLOADERS[collection](aoi, date, **kwargs)
    search = downloader.search_stac()

    if not search:
        return None

    search_list = []
    for item in search:
        item_dict = {
            "id": item.id,
            "datetime": item.datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        item_dict["thumbnail"] = (
            item.assets["thumbnail"].href if "thumbnail" in item.assets else None
        )
        # Add extra parameters from the query, such as cloud cover, etc.
        item_dict = add_item_extra_properties(item, item_dict, downloader.query, kwargs)
        search_list.append(item_dict)
    # Sort by datetime
    search_list_sorted = sorted(search_list, key=lambda x: x["datetime"])

    return search_list_sorted


def explore_with_sentinelhub(
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    **kwargs,
):
    """
    Explores available satellite imagery for a given area of interest (AOI), date range,
    and collection using the Sentinel Hub service.

    This function searches for available satellite images but specifically through the Sentinel Hub service.
    It returns a list of metadata for each image found, including the image ID, datetime,
    and potentially a thumbnail URL, among other properties based on the query.

    Parameters
    ----------
    aoi : Any
        The area of interest for which to search satellite imagery. This can be specified
        in various formats, such as a bounding box or a GeoJSON object.
    date : Union[str, List[str], datetime, List[datetime]]
        The date range for the satellite imagery search. Can be a single date or a list
        representing a range.
    collection : str
        The name of the satellite imagery collection to search within.
    **kwargs : dict
        Additional keyword arguments that can be passed to the Sentinel Hub search query.

    Returns
    -------
    Optional[List[dict]]
        A list of dictionaries, each containing metadata for a found satellite image.
        Returns None if no images are found.
    """
    explorer = SHExplorer(date, collection, **kwargs)
    results = explorer.search(aoi)

    return results

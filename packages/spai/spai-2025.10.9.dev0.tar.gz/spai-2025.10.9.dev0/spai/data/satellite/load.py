"""
Load satellite imagery data
"""

from typing import List, Union, Optional, Any
from datetime import datetime

from . import DOWNLOADERS, AVAILABLE_COLLECTIONS, STATIC_COLLECTIONS
from .stac.STACDownloader import STACDownloader
from .utils import create_aoi_geodataframe
from .explore import explore_satellite_imagery


def load_satellite_imagery(
    aoi: Any,
    date: Optional[List[Union[str, datetime]]] = None,
    collection: str = "sentinel-2-l2a",
    clip: Optional[bool] = False,
    crs: Optional[str] = "epsg:4326",
    **kwargs,
):
    """
    Load satellite imagery data from a given area of interest (aoi) and date in memory.

    Parameters
    ----------
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
    xarray.Dataset
        Satellite imagery data in memory.
    """
    gdf = create_aoi_geodataframe(aoi, crs)
    bbox = gdf.total_bounds
    if collection not in AVAILABLE_COLLECTIONS:
        raise ValueError(
            f"Collection {collection} not available. Available collections are: {AVAILABLE_COLLECTIONS}"
        )

    if not issubclass(DOWNLOADERS[collection], STACDownloader):
        # If the collection is not available to be loaded in memory, return None
        print(
            f"The given collection {collection} is not available to be loaded in memory. Please use download_satellite_imagery function instead."
        )
        return

    if not date and collection not in STATIC_COLLECTIONS:
        # If no date given, search for the last available image
        # until a valid image is found
        last_available_image_date = None
        while not last_available_image_date:
            # TODO review this, if the last image is not found, it will loop forever
            search = explore_satellite_imagery(gdf, date, collection, crs, **kwargs)
            if search:
                last_available_image_date = search[-1]["datetime"]
                date = last_available_image_date
            else:
                # TODO continue searching for last date available
                print("Try introducing a date parameter to load a specific image.")
                return

    downloader = DOWNLOADERS[collection](bbox, date, **kwargs)
    data = downloader.load_stac()

    if clip:
        data = downloader.clip_data(data, gdf)

    return data

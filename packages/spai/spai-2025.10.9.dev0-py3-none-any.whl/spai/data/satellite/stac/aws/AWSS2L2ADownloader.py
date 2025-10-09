"""
AWSS2L2ADownloader class to download and load Sentinel-2 L2A data from a STAC API of the AWS Registry of Open Data.
"""

from .AWSDownloader import AWSDownloader

from typing import Optional, List


S2L2A_BANDS = [
    "coastal",
    "blue",
    "green",
    "red",
    "rededge1",
    "rededge2",
    "rededge3",
    "nir",
    "nir08",
    "nir09",
    "swir16",
    "swir22",
]


class AWSS2L2ADownloader(AWSDownloader):
    def __init__(
        self,
        aoi,
        datetime,
        bands: Optional[List[str]] = S2L2A_BANDS,
        resolution: Optional[float] = 0.00009009,
        crs: Optional[str] = "EPSG:4326",
        cloud_cover: Optional[float] = 100,
        vegetation_percentage: Optional[float] = 100,
        cloud_shadow_percentage: Optional[float] = 100,
        water_percentage: Optional[float] = 100,
        not_vegetated_percentage: Optional[float] = 100,
        snow_ice_percentage: Optional[float] = 100,
        nodata_pixel_percentage: Optional[float] = 100,
    ):
        # TODO add filters
        # See filters in https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items
        query = {
            "eo:cloud_cover": {"lt": cloud_cover},
            "s2:vegetation_percentage": {"lt": vegetation_percentage},
            "s2:cloud_shadow_percentage": {"lt": cloud_shadow_percentage},
            "s2:water_percentage": {"lt": water_percentage},
            "s2:not_vegetated_percentage": {"lt": not_vegetated_percentage},
            "s2:snow_ice_percentage": {"lt": snow_ice_percentage},
            "s2:nodata_pixel_percentage": {"lt": nodata_pixel_percentage},
        }
        super().__init__(aoi, datetime, query)
        self.collection = "sentinel-2-l2a"
        self.bands = bands
        self.resolution = resolution
        self.crs = crs

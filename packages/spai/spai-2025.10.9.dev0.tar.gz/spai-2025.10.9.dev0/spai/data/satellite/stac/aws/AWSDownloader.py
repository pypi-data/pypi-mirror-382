"""
AWSDownloader class for downloading data from the AWS STAC API.
"""

from ..STACDownloader import STACDownloader
from typing import Optional


class AWSDownloader(STACDownloader):
    def __init__(self, aoi, datetime, query: Optional[dict] = None):
        self.url = "https://earth-search.aws.element84.com/v1"
        self.modifier = None
        super().__init__(aoi, datetime, query)

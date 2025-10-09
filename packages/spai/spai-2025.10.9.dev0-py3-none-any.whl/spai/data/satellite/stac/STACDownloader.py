"""
STACDownloader class to download and load satellite data from a STAC API.
"""

from datetime import datetime
from typing import List, Union, Optional, TYPE_CHECKING

from .decorators import with_rioxarray, with_geopandas


if TYPE_CHECKING:
    from shapely.geometry import box, Polygon


class STACDownloader:
    def __init__(
        self,
        aoi: str,
        datetime: List[Union[str, datetime]],
        query: Optional[dict] = None,
    ):
        try:
            from odc.stac import configure_rio, load

            self.load = load
        except ImportError:
            raise ImportError(
                "The odc.stac package is required. Please install it with 'pip install odc-stac' and try again."
            )
        try:
            import pystac_client
        except ImportError:
            raise ImportError(
                "The pystac_client package is required. Please install it with 'pip install pystac-client' and try again."
            )
        try:
            
            import geopandas as gpd # noqa: F401
            from shapely.geometry import box, Polygon  # noqa: F401
        except ImportError:
            raise ImportError(
                "The geopandas package is required. Please install it with 'pip install geopandas' and try again."
            )
        configure_rio(cloud_defaults=True, aws={"aws_unsigned": True})

        self.aoi = aoi
        self.datetime = datetime
        self.query = query
        self.geopolygon = box(*aoi)
        self.catalog = pystac_client.Client.open(self.url, modifier=self.modifier)

    def is_fully_covered(self, item):
        aoi_polygon = box(*self.aoi)

        item_polygon = Polygon(item.geometry["coordinates"][0])

        return aoi_polygon.within(item_polygon)

    def search_stac(self):
        items = self.catalog.search(
            bbox=self.aoi,
            datetime=self.datetime,
            collections=self.collection,
            query=self.query,
        ).item_collection()

        # TODO change in Builder
        # items = [item for item in items if self.is_fully_covered(item)]

        if len(items) == 0:
            print(
                f"No images found for {self.datetime} in {self.collection} collection"
            )
            return None

        return items

    def load_stac(
        self,
        groupby: Optional[str] = "solar_day",
        chunks: Optional[dict] = {"time": 1, "x": 2048, "y": 2048},
    ):
        items = self.search_stac()
        if not items:
            return None
        data = self.load(
            items,
            chunks=chunks,
            crs=self.crs,
            bands=self.bands,
            resolution=self.resolution,
            groupby=groupby,
            # bbox=self.aoi,
            geopolygon=self.geopolygon,
        )

        try:
            data = self.add_metadata(data, items)
        except Exception:
            pass

        return data

    @with_geopandas
    def add_metadata(self, data, items):
        import pandas as pd

        metadata = []
        # Extract properties from the item
        for item in items:
            properties = item.properties
            metadata.append(properties)

        df_metadata = pd.DataFrame(metadata)
        # Format the datetime column to ensure match
        df_metadata["time"] = pd.to_datetime(df_metadata.datetime).dt.strftime(
            "%Y-%m-%d"
        )
        df_metadata = df_metadata.set_index("time")
        # Remove duplicated in time
        # TODO: keep the first or last value?
        df_metadata = df_metadata[~df_metadata.index.duplicated(keep="first")]

        for i, time_step in enumerate(data.time.values):
            time = pd.to_datetime(time_step).strftime("%Y-%m-%d")
            matching_row = df_metadata.loc[time]
            for key, value in matching_row.items():
                if key == "time":  # temp fix for time column
                    continue
                # If the coordinate already exists, append the value, otherwise create it
                if key in data.coords:
                    data.coords[key].values[i] = value
                else:
                    # Initialize the coordinate with the correct size and then assign the value
                    data = data.assign_coords(
                        {key: (["time"], [None] * len(data.time))}
                    )
                    data.coords[key].values[i] = value

        return data

    @staticmethod
    @with_rioxarray
    def clip_data(data, gdf):
        return data.rio.clip(gdf.geometry.values, gdf.crs, drop=False)

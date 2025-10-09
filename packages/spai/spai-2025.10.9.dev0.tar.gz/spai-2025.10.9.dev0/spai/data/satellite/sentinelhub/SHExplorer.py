import os


class SHExplorer:
    def __init__(self, time_interval, sensor, **kargs):
        try:
            from sentinelhub import SHConfig
            from sentinelhub.data_collections import DataCollection
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            raise ImportError(
                "The python-dotenv package is required. Please install it with 'pip install python-dotenv' and try again."
            )
        self.query, self.fields = None, {
            "include": ["id", "properties.datetime", "assets.thumbnail.href"],
            "exclude": [],
        }
        self.config = SHConfig()
        try:
            self.config.sh_client_id = os.environ["SH_CLIENT_ID"]
            self.config.sh_client_secret = os.environ["SH_CLIENT_SECRET"]
        except KeyError:
            # There is not SH_CLIENT_ID and SH_CLIENT_SECRET in the environment
            raise KeyError(
                "Please set the SH_CLIENT_ID and SH_CLIENT_SECRET environment variables."
            )
        if sensor == "S1":
            self.data_collection = DataCollection.SENTINEL1
        elif sensor == "S2L1C" or sensor == "S2L2A" or sensor == "sentinel-2-l1c":
            # no thumbnail for S2L2A, use the one for S2L1C
            self.data_collection = DataCollection.SENTINEL2_L1C
            if "cloud_cover" in kargs:
                cloud_cover = kargs["cloud_cover"]
                self.query = f"eo:cloud_cover < {cloud_cover}"
                self.fields["include"].append("properties.eo:cloud_cover")
        elif sensor == "S5P" or sensor == "sentinel-5p":
            self.data_collection = DataCollection.SENTINEL5P
            # self.data_collection = DataCollection.SENTINEL3_OLCI
            self.config.sh_base_url = DataCollection.SENTINEL5P.service_url
            # self.config.sh_base_url = DataCollection.SENTINEL3_OLCI.service_url
        elif sensor == "sentinel-3-olci":
            self.data_collection = DataCollection.SENTINEL3_OLCI
            self.config.sh_base_url = DataCollection.SENTINEL3_OLCI.service_url
        elif sensor == "sentinel-3-slstr":
            self.data_collection = DataCollection.SENTINEL3_SLSTR
            self.config.sh_base_url = DataCollection.SENTINEL3_SLSTR.service_url
        elif "sentinel-5p" in sensor:
            self.data_collection = DataCollection.SENTINEL5P
            self.config.sh_base_url = DataCollection.SENTINEL5P.service_url
        else:
            raise Exception(f"Invalid sensor {sensor}")
        self.time_interval = time_interval
        self.config.save()

    def search(self, gdf):
        from sentinelhub import SentinelHubCatalog, CRS, BBox

        # generate the bbox containing the geometry
        mybbox = BBox(bbox=gdf.total_bounds.tolist(), crs=CRS.WGS84)
        # query (different for each server: pleiades, spot, sentinelhub...)
        catalog = SentinelHubCatalog(config=self.config)
        search_iterator = catalog.search(
            self.data_collection,
            bbox=mybbox,
            time=self.time_interval,
            filter=self.query,
            fields=self.fields,
        )
        _results = list(search_iterator)
        results = []
        for result in _results:
            data = {
                "id": result["id"],
                "thumbnail": (
                    result["assets"]["thumbnail"]["href"]
                    if "assets" in result
                    else None
                ),
                "date": result["properties"]["datetime"],
            }
            if "eo:cloud_cover" in result["properties"]:
                data["cloud_cover"] = result["properties"]["eo:cloud_cover"]
            results.append(data)
        return results

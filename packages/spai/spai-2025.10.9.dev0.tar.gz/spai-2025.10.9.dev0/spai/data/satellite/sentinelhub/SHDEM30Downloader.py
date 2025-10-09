from .SHDownloader import SHDownloader
from sentinelhub import DataCollection


class SHDEM30Downloader(SHDownloader):

    def __init__(self, download_folder='/tmp'):
        super().__init__(download_folder)
        self.data_collection = DataCollection.DEM_COPERNICUS_30
        self.resolution = 30  # mpp
        self.script = """
            //VERSION=3

            function setup() {
                return {
                    input: ["DEM"],
                    output: { id: "default",
                            bands: 1,
                            sampleType: SampleType.FLOAT32
                    },
                }
            }

            function evaluatePixel(sample) {
                return [sample.DEM]
            }
        """

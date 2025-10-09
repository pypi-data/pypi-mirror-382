from .SHDownloader import SHDownloader
from sentinelhub import DataCollection


class SHS1Downloader(SHDownloader):

    def __init__(self, download_folder='/tmp'):
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL1
        self.resolution = 10  # mpp
        self.script = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["VV","VH"],
                        units: "LINEAR_POWER"
                    }],
                    output: {
                        bands: 2,
                        sampleType: "INT16"
                    }
                };
            }

            function evaluatePixel(sample) {
                return [sample.VV,
                        sample.VH];
            }
        """
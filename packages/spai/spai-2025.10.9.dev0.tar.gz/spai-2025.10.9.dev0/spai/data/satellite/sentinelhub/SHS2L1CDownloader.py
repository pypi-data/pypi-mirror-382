from .SHS2Downloader import SHS2Downloader


class SHS2L1CDownloader(SHS2Downloader):
    def __init__(self, download_folder):
        try:
            from sentinelhub import DataCollection
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL2_L1C
        self.script = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                        units: "DN"
                    }],
                    output: {
                        bands: 13,
                        sampleType: "INT16"
                    }
                };
            }

            function evaluatePixel(sample) {
                return [sample.B01,
                        sample.B02,
                        sample.B03,
                        sample.B04,
                        sample.B05,
                        sample.B06,
                        sample.B07,
                        sample.B08,
                        sample.B8A,
                        sample.B09,
                        sample.B10,
                        sample.B11,
                        sample.B12];
            }
        """

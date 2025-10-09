from .SHDownloader import SHDownloader


class SHS3OLCIDownloader(SHDownloader):
    def __init__(self, download_folder):
        try:
            from sentinelhub import DataCollection
        except ImportError:
            raise ImportError(
                "The sentinelhub package is required. Please install it with 'pip install sentinelhub' and try again."
            )
        super().__init__(download_folder)
        self.data_collection = DataCollection.SENTINEL3_OLCI
        self.resolution = 300
        self.script = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                    bands: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21"],
                    units: "REFLECTANCE"
                    }],
                    output: {
                        bands: 21,
                        sampleType: "UINT16" //floating point values are automatically rounded to the nearest integer by the service.
                    }
                };
            }

            function evaluatePixel(sample) {
                return [sample.B01, sample.B02, sample.B03, sample.B04, sample.B05, sample.B06, sample.B07, sample.B08, sample.B09, sample.B10, sample.B11, sample.B12, sample.B13, sample.B14, sample.B15, sample.B16, sample.B17, sample.B18, sample.B19, sample.B20, sample.B21]
            }
            """

# from .download import download_satellite_image, download_dem, download_cloud_mask
# from .explore import explore_satellite_images

from .stac import (
    AWSS2L2ADownloader,
    PCS1GRDDownloader,
    PCS1RTCDownloader,
    AWSDEM30Downloader,
    AWSDEM90Downloader,
    PCESAWCDownloader,
    PCLandsat8Downloader,
    PCModisBurnedDownloader,
    PCModisSnow8Downloader,
    PCModisSnowDayDownloader,
    PCAlosPalsarAnnualDownloader,
)

from .sentinelhub import (
    SHS2L1CDownloader,
    SHS3OLCIDownloader,
    SHS3SLSTRDownloader,
    SHS5PCH4Downloader,
    SHS5PCODownloader,
    SHS5PO3Downloader,
    SHS5PNO2Downloader,
    SHS5PSO2Downloader,
    SHS5HCHODownloader,
)


DOWNLOADERS = {
    "sentinel-1-grd": PCS1GRDDownloader,
    "sentinel-1-rtc": PCS1RTCDownloader,
    "sentinel-2-l1c": SHS2L1CDownloader,
    "sentinel-2-l2a": AWSS2L2ADownloader,
    "sentinel-3-olci": SHS3OLCIDownloader,
    "sentinel-3-slstr": SHS3SLSTRDownloader,
    "sentinel-5p-ch4": SHS5PCH4Downloader,
    "sentinel-5p-co": SHS5PCODownloader,
    "sentinel-5p-no2": SHS5PNO2Downloader,
    "sentinel-5p-o3": SHS5PO3Downloader,
    "sentinel-5p-so2": SHS5PSO2Downloader,
    "sentinel-5p-hcho": SHS5HCHODownloader,
    "cop-dem-glo-30": AWSDEM30Downloader,
    "cop-dem-glo-90": AWSDEM90Downloader,
    "esa-worldcover": PCESAWCDownloader,
    "landsat-8-c2-l2": PCLandsat8Downloader,
    "modis-burned-areas": PCModisBurnedDownloader,
    "modis-snow-cover-8": PCModisSnow8Downloader,
    "modis-snow-cover-daily": PCModisSnowDayDownloader,
    "alos-palsar-mosaic": PCAlosPalsarAnnualDownloader,
}
AVAILABLE_COLLECTIONS = list(DOWNLOADERS.keys())
STATIC_COLLECTIONS = [
    "cop-dem-glo-30",
    "cop-dem-glo-90",
    "esa-worldcover",
    "alos-palsar-mosaic",
]

# need to be at the bottom to avoid circular imports
from .download import download_satellite_imagery # noqa: E402
from .explore import explore_satellite_imagery # noqa: E402
from .load import load_satellite_imagery # noqa: E402


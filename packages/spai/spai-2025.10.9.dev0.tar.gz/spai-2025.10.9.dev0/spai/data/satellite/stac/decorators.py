"""
Decorators for the STAC module.
"""


def with_rioxarray(func):
    def wrapper(self, *args, **kwargs):
        try:
            import rioxarray as rxr

        except ImportError:
            raise ImportError(
                "The rioxarray and dask diagnostics packages are required. Please install them with 'pip install rioxarray dask[diagnostics]' and try again."
            )

        return func(self, *args, **kwargs)

    return wrapper


def with_geopandas(func):
    def wrapper(self, *args, **kwargs):
        try:
            import geopandas as gpd
        except ImportError:
            raise ImportError(
                "The geopandas package is required. Please install it with 'pip install geopandas' and try again."
            )
        return func(self, *args, **kwargs)

    return wrapper


def with_geojson(func):
    def wrapper(self, *args, **kwargs):
        try:
            import geojson
        except ImportError:
            raise ImportError(
                "The geojson package is required. Please install it with 'pip install geojson' and try again."
            )
        return func(self, *args, **kwargs)

    return wrapper


def with_requests(func):
    def wrapper(self, *args, **kwargs):
        try:
            import requests
        except ImportError:
            raise ImportError(
                "The requests package is required. Please install it with 'pip install requests' and try again."
            )
        return func(self, *args, **kwargs)

    return wrapper

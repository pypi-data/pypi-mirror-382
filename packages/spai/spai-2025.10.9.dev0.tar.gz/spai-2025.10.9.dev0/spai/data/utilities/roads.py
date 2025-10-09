from typing import Optional, Any

import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_roads(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "highway": ["motorway", "trunk", "primary", "secondary", "tertiary"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load road elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default {'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']}

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the road geometries
    """
    gdf = create_aoi_geodataframe(aoi, crs)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["LineString", "MultiLineString"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_roads(
    storage,
    aoi: Any,
    name: Optional[str] = "roads.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "highway": ["motorway", "trunk", "primary", "secondary", "tertiary"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download road elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store road geometries, by default "roads.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default {'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']}
    """
    final_roads_gdf = load_roads(aoi, source, query, crs)
    if not final_roads_gdf.empty:
        storage.create(final_roads_gdf, name=name)

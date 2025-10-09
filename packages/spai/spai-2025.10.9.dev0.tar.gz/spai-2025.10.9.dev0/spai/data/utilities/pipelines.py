from typing import Optional, Any

import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_pipelines(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "man_made": ["pipeline"],
        "pipeline": ["oil", "gas", "water", "sewage", "heat"],
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load pipeline elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes pipelines for oil, gas, water, sewage, and heat.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the pipeline geometries
    """
    gdf = create_aoi_geodataframe(aoi, crs)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["LineString", "MultiLineString"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_pipelines(
    storage,
    aoi: Any,
    name: Optional[str] = "pipelines_lines.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "man_made": ["pipeline"],
        "pipeline": ["oil", "gas", "water", "sewage", "heat"],
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download pipeline elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store line geometries, by default "pipelines_lines.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes pipelines for oil, gas, water, sewage, and heat.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    lines_gdf = load_pipelines(aoi, source, query, crs)
    lines_gdf = lines_gdf.applymap(lambda x: x if not isinstance(x, list) else str(x))
    if not lines_gdf.empty:
        storage.create(lines_gdf, name=name)

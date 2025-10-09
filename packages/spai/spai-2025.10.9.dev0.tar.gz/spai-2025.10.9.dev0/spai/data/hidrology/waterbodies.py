from typing import Optional, Any
import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_waterbodies(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "natural": ["water"],
        "water": ["lake", "pond", "reservoir", "lagoon"],
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load water body elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes lakes, ponds, reservoirs, and lagoons.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the water body geometries
    """
    gdf = create_aoi_geodataframe(aoi)

    if source == "osm":
        return load_osm_data(
            gdf, query, geometry_types=["Polygon", "MultiPolygon"], crs=crs
        )
    else:
        raise ValueError("Unsupported source")


def download_waterbodies(
    storage,
    aoi: Any,
    name: Optional[str] = "water_bodies.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "natural": ["water"],
        "water": ["lake", "pond", "reservoir", "lagoon"],
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download water body elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store water body geometries, by default "water_bodies.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes lakes, ponds, reservoirs, and lagoons.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_water_bodies_gdf = load_waterbodies(aoi, source, query, crs)
    if not final_water_bodies_gdf.empty:
        storage.create(final_water_bodies_gdf, name=name)

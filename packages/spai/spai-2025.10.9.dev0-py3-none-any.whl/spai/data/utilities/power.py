from typing import Optional, Any

import geopandas as gpd
from ..sources.osm import load_osm_data
from ..satellite.utils import create_aoi_geodataframe


def load_power_networks(
    aoi: Any,
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "power": ["line", "cable", "substation", "plant", "transformer"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load power network elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes power lines, cables, substations, plants, and transformers.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing the power network geometries
    """
    gdf = create_aoi_geodataframe(aoi, crs)

    if source == "osm":
        return load_osm_data(gdf, query, crs=crs)
    else:
        raise ValueError("Unsupported source")


def download_power_networks(
    storage,
    aoi: Any,
    line_name: Optional[str] = "power_lines.geojson",
    point_name: Optional[str] = "power_points.geojson",
    polygon_name: Optional[str] = "power_polygons.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "power": ["line", "cable", "substation", "plant", "transformer"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download power network elements from OpenStreetMap for the given area of interest and separate them by geometry type.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    line_name : str, optional
        The name of the file to store line geometries, by default "power_lines.geojson"
    point_name : str, optional
        The name of the file to store point geometries, by default "power_points.geojson"
    polygon_name : str, optional
        The name of the file to store polygon geometries, by default "power_polygons.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes power lines, cables, substations, plants, and transformers.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_power_networks_gdf = load_power_networks(aoi, source, query, crs)

    lines_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("LineString", "MultiLineString"))
    ]
    points_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("Point", "MultiPoint"))
    ]
    polygons_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("Polygon", "MultiPolygon"))
    ]

    lines_gdf = lines_gdf.applymap(lambda x: x if not isinstance(x, list) else str(x))
    points_gdf = points_gdf.applymap(lambda x: x if not isinstance(x, list) else str(x))
    polygons_gdf = polygons_gdf.applymap(
        lambda x: x if not isinstance(x, list) else str(x)
    )

    if not lines_gdf.empty:
        storage.create(lines_gdf, name=line_name)
    if not points_gdf.empty:
        storage.create(points_gdf, name=point_name)
    if not polygons_gdf.empty:
        storage.create(polygons_gdf, name=polygon_name)

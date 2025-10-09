from dataclasses import dataclass


@dataclass
class AreaOfInterest:
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    def __post_init__(self):
        # Validate longitude range
        if not (-180 <= self.xmin <= 180 and -180 <= self.xmax <= 180):
            raise ValueError("Coordinate values indicate GeoJSON file is not WGS84")

        # Validate latitude range
        if not (-90 <= self.ymin <= 90 and -90 <= self.ymax <= 90):
            raise ValueError("Coordinate values indicate GeoJSON file is not WGS84")

    @classmethod
    def from_geodataframe(cls, gdf) -> "AreaOfInterest":
        bounds = gdf.total_bounds
        return cls(xmin=bounds[0], ymin=bounds[1], xmax=bounds[2], ymax=bounds[3])

    @classmethod
    def from_global(cls) -> "AreaOfInterest":
        return cls(xmin=-180.0, xmax=180.0, ymin=-90.0, ymax=90.0)

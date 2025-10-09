import math
from typing import Tuple


def to_cartesian(lat: float, lon: float) -> Tuple[float, float, float]:
    """
    Convert a lat/lon pair to Cartesian coordinates.

    Args:
        lat (float): Latitude of the location in degrees.
        lon (float): Longitude of the location in degrees.

    Returns:
        Tuple[float, float, float]: The Cartesian coordinates (x, y, z).
    """
    R = 6371  # Earth's radius in kilometers
    x = R * math.cos(math.radians(lat)) * math.cos(math.radians(lon))
    y = R * math.cos(math.radians(lat)) * math.sin(math.radians(lon))
    z = R * math.sin(math.radians(lat))
    return x, y, z


def from_cartesian(x: float, y: float, z: float) -> Tuple[float, float]:
    """
    Convert Cartesian coordinates back to lat/lon.

    Args:
        x (float): The x-coordinate in Cartesian coordinates.
        y (float): The y-coordinate in Cartesian coordinates.
        z (float): The z-coordinate in Cartesian coordinates.

    Returns:
        Tuple[float, float]: The latitude and longitude in degrees.
    """
    lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return math.degrees(lat), math.degrees(lon)

# no_fly.py
"""
No-fly zone generation utilities. Produces shapely Polygons for use with path_planner.
"""
from shapely.geometry import Polygon
from typing import Tuple, List
import random, math

def generate_circular_nofly(center: Tuple[float,float], radius_m: float, n_points: int = 36) -> Polygon:
    lat, lon = center
    pts = []
    for i in range(n_points):
        ang = 2*math.pi*i/n_points
        dlat = (radius_m * math.cos(ang)) / 111000.0
        dlon = (radius_m * math.sin(ang)) / (111000.0 * math.cos(math.radians(lat)))
        pts.append((lon + dlon, lat + dlat))  # shapely uses lon,lat
    return Polygon(pts)

def random_no_fly_areas(center: Tuple[float,float], count: int = 2, max_radius: int = 800) -> List[Polygon]:
    out = []
    for _ in range(count):
        r = random.uniform(200, max_radius)
        dlat = random.uniform(-0.02, 0.02)
        dlon = random.uniform(-0.02, 0.02)
        out.append(generate_circular_nofly((center[0]+dlat, center[1]+dlon), r))
    return out
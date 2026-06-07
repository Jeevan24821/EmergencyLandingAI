# adsb_simulator.py
"""
Synthetic ADS-B traffic generator.
"""
import random
from typing import List, Dict

def generate_adsb_traffic(center_lat: float, center_lon: float, count: int = 8, radius_km: float = 10) -> List[Dict]:
    traffic = []
    for i in range(count):
        lat = center_lat + random.uniform(-radius_km/111.0, radius_km/111.0)
        lon = center_lon + random.uniform(-radius_km/111.0, radius_km/111.0)
        traffic.append({
            "hex": f"T{i+1000}",
            "lat": lat,
            "lon": lon,
            "alt": random.randint(200,12000),
            "speed": random.randint(40,260),
            "heading": random.randint(0,359)
        })
    return traffic
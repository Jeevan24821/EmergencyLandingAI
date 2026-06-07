# terrain_profile.py
"""
Elevation profile wrapper using Open-Elevation as fallback.
Cache with st.cache_data when used in Streamlit.
"""
from typing import List, Tuple
import requests

def profile_along_route(points: List[Tuple[float,float]]) -> List[float]:
    try:
        url = "https://api.open-elevation.com/api/v1/lookup"
        locations = [{"latitude":lat,"longitude":lon} for lat,lon in points]
        r = requests.post(url, json={"locations": locations}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [p["elevation"] for p in data["results"]]
    except Exception:
        return [0.0]*len(points)
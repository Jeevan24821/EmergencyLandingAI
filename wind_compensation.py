# wind_compensation.py
"""
Wind compensation helper: computes required heading and resulting ground speed
to maintain a desired course in the presence of wind.
"""
import math
from typing import Tuple

def compensate_heading(aircraft_speed_mps: float, desired_course_deg: float, wind_speed_mps: float, wind_dir_deg: float) -> Tuple[float,float]:
    """
    Returns (required_heading_deg, resulting_ground_speed_mps)
    wind_dir_deg: meteorological (where wind is coming from). Output heading is nav (0=N).
    """
    # Convert to rad; treat both as nav degrees (0=N clockwise)
    course = math.radians(desired_course_deg)
    wind_to = (wind_dir_deg + 180) % 360  # convert 'from' to 'to'
    wind_to_rad = math.radians(wind_to)
    wx = wind_speed_mps * math.sin(wind_to_rad)
    wy = wind_speed_mps * math.cos(wind_to_rad)
    vx = aircraft_speed_mps * math.sin(course)
    vy = aircraft_speed_mps * math.cos(course)
    ax = vx - wx
    ay = vy - wy
    required_heading = (math.degrees(math.atan2(ax, ay)) + 360) % 360
    ground_speed = math.hypot(ax, ay)
    return required_heading, ground_speed
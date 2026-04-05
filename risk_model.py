import math

def calculate_score(zone):
    score = 0

    # Area score (bigger = better)
    score += zone["area"] / 200

    # Wind penalty
    score -= zone["wind"] * 2

    # Obstacle scoring
    if zone["obstacles"] == "Low":
        score += 20
    elif zone["obstacles"] == "Medium":
        score += 10
    else:
        score -= 20

    # Terrain type
    if zone["type"] == "Field":
        score += 30
    elif zone["type"] == "Highway":
        score += 20
    elif zone["type"] == "Water":
        score -= 30
    elif zone["type"] == "Urban":
        score -= 40

    # Visibility bonus
    if zone.get("visibility") == "Clear":
        score += 10
    elif zone.get("visibility") == "Hazy":
        score += 3
    else:
        score -= 10

    # Surface bonus
    surface_map = {"Concrete": 15, "Grass": 10, "Gravel": 5, "Sand": 0}
    score += surface_map.get(zone.get("surface", "Grass"), 0)

    return round(score)


def get_risk_level(score):
    if score >= 80:
        return "SAFE", "#00ff9d"
    elif score >= 55:
        return "MODERATE", "#00d4ff"
    elif score >= 30:
        return "CAUTION", "#ffb800"
    else:
        return "DANGER", "#ff3d71"


def get_factor_scores(zone):
    """Return normalized 0-100 factor scores for radar chart."""
    obs_score  = {"Low": 92, "Medium": 55, "High": 18}.get(zone["obstacles"], 50)
    type_score = {"Field": 95, "Highway": 70, "Water": 20, "Urban": 14}.get(zone["type"], 50)
    area_score = min(100, zone["area"] / 150)
    wind_score = max(0, 100 - zone["wind"] * 9)
    vis_score  = {"Clear": 95, "Hazy": 60, "Foggy": 25}.get(zone.get("visibility", "Clear"), 60)
    surf_score = {"Concrete": 95, "Grass": 75, "Gravel": 55, "Sand": 35}.get(zone.get("surface", "Grass"), 60)
    return {
        "Surface":     round(type_score),
        "Clearance":   round(obs_score),
        "Area":        round(area_score),
        "Wind":        round(wind_score),
        "Visibility":  round(vis_score),
        "Landing Sfc": round(surf_score),
    }
import random

def get_aircraft_data():
    return {
        "latitude":  12.9716 + random.uniform(-0.01, 0.01),
        "longitude": 77.5946 + random.uniform(-0.01, 0.01),
        "altitude":  random.randint(5000, 12000),
        "speed":     random.randint(180, 300),
        "heading":   random.randint(0, 359),
        "fuel":      random.choice(["LOW", "CRITICAL"]),
        "emergency": random.choice([
            "Engine Failure", "Fuel Loss",
            "Hydraulic Failure", "Bird Strike", "Fire Warning"
        ]),
        "passengers": random.randint(80, 220),
        "crew":       random.randint(4, 8),
    }

def generate_zones(lat, lon):
    zones = []
    for i in range(5):
        zones.append({
            "name":      f"Zone {chr(65+i)}",
            "lat":       lat + random.uniform(-0.05, 0.05),
            "lon":       lon + random.uniform(-0.05, 0.05),
            "type":      random.choice(["Field", "Highway", "Water", "Urban"]),
            "area":      random.randint(5000, 15000),
            "wind":      random.randint(1, 10),
            "obstacles": random.choice(["Low", "Medium", "High"]),
            "visibility": random.choice(["Clear", "Hazy", "Foggy"]),
            "surface":   random.choice(["Grass", "Concrete", "Gravel", "Sand"]),
        })
    return zones

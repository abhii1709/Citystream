import json
import random
from datetime import datetime, timedelta
import math

RECORD_COUNT = 10000  # Change to desired number
LOCATIONS = {
    "McLeod Ganj": {"base_traffic": 300, "tourist_ratio": 0.8},
    "Bhagsu Nag": {"base_traffic": 200, "tourist_ratio": 0.7},
    "Dharamkot": {"base_traffic": 150, "tourist_ratio": 0.6},
    "Sidhpur": {"base_traffic": 100, "tourist_ratio": 0.3},
    "Naddi": {"base_traffic": 180, "tourist_ratio": 0.5},
    "Education Board": {"base_traffic": 80, "tourist_ratio": 0.9},
    "Dal Lake": {"base_traffic": 120, "tourist_ratio": 0.4},
    "Kachehri Chowk": {"base_traffic": 90, "tourist_ratio": 0.85},
    "Sakoh": {"base_traffic": 60, "tourist_ratio": 0.4},
    "Dari": {"base_traffic": 110, "tourist_ratio": 0.6}
}

WEATHER_PROFILES = {
    "Sunny": {"speed_mod": 1.0, "accident_risk": 0.1, "frequency": 0.5},
    "Rainy": {"speed_mod": 0.7, "accident_risk": 0.4, "frequency": 0.2},
    "Cloudy": {"speed_mod": 0.9, "accident_risk": 0.2, "frequency": 0.15},
    "Foggy": {"speed_mod": 0.6, "accident_risk": 0.3, "frequency": 0.1},
    "Snowy": {"speed_mod": 0.4, "accident_risk": 0.5, "frequency": 0.05}
}

def get_time_features(timestamp):
    """Calculate time-based features"""
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return {
        "hour": dt.hour,
        "weekday": dt.weekday(),  # 0=Monday
        "month": dt.month,
        "is_weekend": dt.weekday() >= 5,
        "is_holiday": random.random() < 0.05  # 5% chance of holiday
    }

def generate_timestamp():
    """Generate timestamp with seasonal variation"""
    year = 2025
    # Weight months for tourism season (March-June, Sept-Nov)
    month = random.choices(
        [1,2,3,4,5,6,7,8,9,10,11,12],
        weights=[0.7, 0.8, 1.2, 1.5, 1.5, 1.2, 0.9, 0.8, 1.3, 1.4, 1.2, 0.9]
    )[0]
    
    day = random.randint(1, 28)  # Keep simple for demo
    hour = random.choices(
        range(24),
        weights=[0.3,0.2,0.1,0.1,0.1,0.2,0.8,1.2,1.5,1.3,1.1,1.0,
                 1.1,1.0,0.9,0.9,1.1,1.3,1.5,1.4,1.2,0.9,0.6,0.4]
    )[0]
    
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(year, month, day, hour, minute, second).strftime("%Y-%m-%d %H:%M:%S")

def calculate_congestion(hour, location, is_holiday):
    """Determine congestion level based on time and location"""
    # Base congestion probabilities
    if 7 <= hour <= 10 or 17 <= hour <= 20:
        base_weights = [0.1, 0.3, 0.6]  # Low, Medium, High
    else:
        base_weights = [0.6, 0.3, 0.1]

    # Tourist location modifier
    tourist_mod = LOCATIONS[location]["tourist_ratio"]
    if is_holiday:
        tourist_mod *= 1.5

    # Adjust weights based on tourism factor
    adjusted_weights = [
        base_weights[0] * (1 - tourist_mod*0.3),
        base_weights[1] * (1 + tourist_mod*0.2),
        base_weights[2] * (1 + tourist_mod*0.5)
    ]
    
    return random.choices(["Low", "Medium", "High"], weights=adjusted_weights)[0]

def generate_record():
    timestamp = generate_timestamp()
    time_features = get_time_features(timestamp)
    location = random.choice(list(LOCATIONS.keys()))
    
    # Base traffic calculation
    base_traffic = LOCATIONS[location]["base_traffic"]
    
    # Time modifiers
    if time_features["is_weekend"] or time_features["is_holiday"]:
        traffic_mod = 1.3 + (0.2 * LOCATIONS[location]["tourist_ratio"])
    else:
        traffic_mod = 1.0
        
    if time_features["hour"] in [8,9,18,19]:
        traffic_mod *= 1.4
        
    vehicle_count = base_traffic * traffic_mod * random.uniform(0.9, 1.1)
    
    # Weather selection with seasonal variation
    weather = random.choices(
        list(WEATHER_PROFILES.keys()),
        weights=[w["frequency"] for w in WEATHER_PROFILES.values()]
    )[0]
    
    # Calculate congestion
    congestion = calculate_congestion(
        time_features["hour"],
        location,
        time_features["is_holiday"]
    )
    
    # Speed calculation
    base_speed = 45  # km/h
    speed = base_speed * WEATHER_PROFILES[weather]["speed_mod"]
    speed *= random.uniform(0.9, 1.1)
    
    # Congestion speed reduction
    if congestion == "Medium":
        speed *= 0.7
    elif congestion == "High":
        speed *= 0.4
        
    # Accident calculation
    accident_prob = (
        WEATHER_PROFILES[weather]["accident_risk"] *
        (1.5 if congestion == "High" else 1.0) *
        (1.2 if time_features["is_holiday"] else 1.0))
    
    accidents = min(5, math.floor(random.expovariate(accident_prob * 2)))

    return {
        "timestamp": timestamp,
        "location": location,
        "vehicle_count": str(round(vehicle_count)),
        "avg_speed_kmph": f"{max(5, min(45, speed)):.2f}",
        "congestion_level": congestion,
        "weather": weather,
        "accidents_reported": str(accidents)
    }

# Generate and save data
print(f"Generating {RECORD_COUNT} records...")
data = [generate_record() for _ in range(RECORD_COUNT)]

print("Saving to file...")
with open("realistic_traffic_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Done! File saved as realistic_traffic_data.json")
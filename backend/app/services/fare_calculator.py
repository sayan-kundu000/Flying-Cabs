import math
from typing import List, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

TIERS_CONFIG = [
    {
        "tier_id": "auto",
        "name": "Ola Auto / Uber Auto",
        "car_model": "Bajaj RE EV Auto (Green-Yellow)",
        "car_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Manjunath Gowda",
        "driver_photo": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.92,
        "license_plate": "KA-02-AU-7711",
        "icon": "🛺",
        "description": "Iconic Indian 3-wheeler auto rickshaw. Nimble, economical, beats tight street traffic.",
        "base_fare": 35.00,
        "per_km": 12.00,
        "per_min": 1.50,
        "avg_speed_kmh": 24.0,
        "capacity": 3,
        "speed_factor": 1.1,
        "eta_mins": 2
    },
    {
        "tier_id": "micro",
        "name": "Ola Micro / UberGo",
        "car_model": "Tata Tiago EV / Maruti WagonR",
        "car_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Deepak Rao",
        "driver_photo": "https://images.unsplash.com/photo-1528892952291-009c663ce843?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.89,
        "license_plate": "KA-04-MC-3344",
        "icon": "🚗",
        "description": "Pocket-friendly compact AC hatchback for daily budget city commute.",
        "base_fare": 50.00,
        "per_km": 13.50,
        "per_min": 2.00,
        "avg_speed_kmh": 26.0,
        "capacity": 4,
        "speed_factor": 1.0,
        "eta_mins": 3
    },
    {
        "tier_id": "standard",
        "name": "Ola Mini / UberX",
        "car_model": "Tata Tigor EV Prime / Dzire",
        "car_image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Rajesh Kumar",
        "driver_photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.94,
        "license_plate": "KA-05-EV-4242",
        "icon": "🚖",
        "description": "Standard comfortable AC sedan with dependable top drivers and extra boot space.",
        "base_fare": 80.00,
        "per_km": 16.00,
        "per_min": 2.50,
        "avg_speed_kmh": 28.0,
        "capacity": 4,
        "speed_factor": 1.05,
        "eta_mins": 3
    },
    {
        "tier_id": "luxury",
        "name": "Ola Prime / Uber Premier",
        "car_model": "Mercedes-Benz E-Class Prime Limousine",
        "car_image": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Capt. Priya Sen (Executive Chauffeur)",
        "driver_photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.98,
        "license_plate": "MH-01-LUX-777",
        "icon": "⚡",
        "description": "Spacious premium flagship sedan with quiet EV cabin, bottled water & 5-star chauffeurs.",
        "base_fare": 150.00,
        "per_km": 24.00,
        "per_min": 3.50,
        "avg_speed_kmh": 30.0,
        "capacity": 4,
        "speed_factor": 1.2,
        "eta_mins": 4
    },
    {
        "tier_id": "bike",
        "name": "Ola Bike / Uber Moto",
        "car_model": "Ather 450X EV Bike Taxi",
        "car_image": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Sunil Gowda",
        "driver_photo": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.91,
        "license_plate": "KA-01-BK-8899",
        "icon": "🏍️",
        "description": "Fastest two-wheeler bike taxi with sanitized helmet to weave through peak-hour street congestion.",
        "base_fare": 25.00,
        "per_km": 8.00,
        "per_min": 1.00,
        "avg_speed_kmh": 35.0,
        "capacity": 1,
        "speed_factor": 1.4,
        "eta_mins": 1
    },
    {
        "tier_id": "flying",
        "name": "Ola Air / Uber Elevate (VTOL)",
        "car_model": "AeroVTOL Sky-X7 (Air Garuda)",
        "car_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
        "driver_name": "Capt. Vikram Rathore (DGCA Certified)",
        "driver_photo": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
        "driver_rating": 4.99,
        "license_plate": "KA-01-AERO-007",
        "icon": "🛸",
        "description": "Next-gen eVTOL sky corridor transit bypassing all ground traffic. 3.5x cruising speed.",
        "base_fare": 450.00,
        "per_km": 38.00,
        "per_min": 5.00,
        "avg_speed_kmh": 120.0,
        "capacity": 4,
        "speed_factor": 3.5,
        "eta_mins": 2
    }
]

def calculate_fare_options(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    if distance < 0.5:
        distance = 0.5

    options = []
    base_duration = max(4, int(round((distance / 26.0) * 60)))

    for cfg in TIERS_CONFIG:
        travel_hours = distance / cfg["avg_speed_kmh"]
        duration_mins = max(2, int(round(travel_hours * 60)))
        fare = cfg["base_fare"] + (distance * cfg["per_km"]) + (duration_mins * cfg["per_min"])
        # Round fare to whole rupee for Indian market conventions
        fare = float(round(fare))

        options.append({
            "tier_id": cfg["tier_id"],
            "name": cfg["name"],
            "icon": cfg["icon"],
            "description": cfg["description"],
            "fare": fare,
            "duration_mins": duration_mins,
            "distance_km": distance,
            "speed_factor": cfg["speed_factor"],
            "capacity": cfg["capacity"],
            "car_model": cfg.get("car_model"),
            "car_image": cfg.get("car_image"),
            "driver_name": cfg.get("driver_name"),
            "driver_photo": cfg.get("driver_photo"),
            "driver_rating": cfg.get("driver_rating", 4.9),
            "license_plate": cfg.get("license_plate"),
            "eta_mins": cfg.get("eta_mins", 3)
        })

    return {
        "distance_km": distance,
        "base_duration_mins": base_duration,
        "options": options
    }

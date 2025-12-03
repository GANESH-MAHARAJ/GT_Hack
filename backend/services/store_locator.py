import math
from typing import List, Dict, Any, Optional


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distance in meters between two lat/lng pairs.
    """
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_nearby_stores(
    lat: Optional[float],
    lng: Optional[float],
    intents: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    For now: mock 2–3 stores, compute distance from given lat/lng if present.
    Later you can replace with Google Places / other APIs.
    """
    # Demo store catalog (pretend Bangalore)
    stores = [
        {
            "id": "store_101",
            "name": "Starbucks MG Road",
            "lat": 12.9717,
            "lng": 77.5948,
            "opening_hours": "08:00-22:00",
            "is_open_now": True,
            "rating": 4.4,
            "review_count": 892,
        },
        {
            "id": "store_102",
            "name": "Third Wave Coffee Church Street",
            "lat": 12.9730,
            "lng": 77.6050,
            "opening_hours": "09:00-23:00",
            "is_open_now": False,
            "rating": 4.6,
            "review_count": 650,
        },
    ]

    # Add distance_m if lat/lng provided
    for s in stores:
        if lat is not None and lng is not None:
            s["distance_m"] = _haversine_distance_m(lat, lng, s["lat"], s["lng"])
        else:
            s["distance_m"] = 0.0

    # Sort by distance
    stores.sort(key=lambda x: x["distance_m"])
    return stores

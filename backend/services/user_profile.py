import os
import json
from typing import Dict, Any


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")


def _load_users() -> Dict[str, Any]:
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback stub
    return {
        "demo_user": {
            "user_id": "demo_user",
            "name": "Demo User",
            "loyalty_tier": "Gold",
            "favorite_tags": ["coffee", "hot drinks"],
        }
    }


def get_user_profile_light(user_id: str) -> Dict[str, Any]:
    users = _load_users()
    profile = users.get(user_id)

    if not profile:
        # Default anonymous-ish profile
        profile = {
            "user_id": user_id,
            "name": "Guest",
            "loyalty_tier": "Bronze",
            "favorite_tags": [],
        }

    # Light profile is just what we need for LLM context
    return {
        "user_id": profile.get("user_id", user_id),
        "name": profile.get("name", "Guest"),
        "loyalty_tier": profile.get("loyalty_tier", "Bronze"),
        "favorite_tags": profile.get("favorite_tags", []),
    }

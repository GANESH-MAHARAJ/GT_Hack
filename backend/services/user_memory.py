# backend/services/user_memory.py

from typing import Dict, Any, List

# In-memory store; for hackathon this is perfect.
USER_MEMORY: Dict[str, Dict[str, Any]] = {}

def get_user_profile(user_id: str) -> Dict[str, Any]:
    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = {
            "preferences": {
                "favorite_drinks": [],
                "dislikes": [],
                "allergies": [],
            },
            "loyalty_tier": "Bronze",
            "history": [],
            "last_seen_store": None,
            "last_order": None,
        }
    return USER_MEMORY[user_id]

def update_conversation_history(user_id: str, user_message: str, bot_reply: str):
    profile = get_user_profile(user_id)
    history = profile["history"]
    history.append({"user": user_message, "bot": bot_reply})
    # keep only last 20 for speed
    if len(history) > 20:
        history.pop(0)

def store_preference(user_id: str, key: str, value: str):
    profile = get_user_profile(user_id)
    profile["preferences"].setdefault(key, [])
    if value not in profile["preferences"][key]:
        profile["preferences"][key].append(value)

def set_last_order(user_id: str, order: Dict[str, Any]):
    profile = get_user_profile(user_id)
    profile["last_order"] = order

def set_last_seen_store(user_id: str, store_info: Dict[str, Any]):
    profile = get_user_profile(user_id)
    profile["last_seen_store"] = store_info

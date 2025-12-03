from typing import Dict, Any, List


def get_intents(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent-1 stub:
    Generates top-5 intents based on simple heuristics.
    Later: replace this with llama3.1 call + JSON parsing.
    """
    message = (payload.get("user_message") or "").lower()

    intents: List[Dict[str, Any]] = []

    # Very naive keyword-based example
    if "coffee" in message or "cold" in message:
        intents.append(
            {
                "name": "FIND_NEARBY_COFFEE_SHOP",
                "confidence": 0.9,
                "reason": "User mentioned coffee/cold which suggests a warm drink at a nearby shop.",
                "required_data": ["nearby_stores", "opening_hours", "distance", "offers"],
                "category": "store_discovery",
            }
        )
        intents.append(
            {
                "name": "SUGGEST_WARM_DRINK",
                "confidence": 0.85,
                "reason": "User is cold; warm beverages are relevant.",
                "required_data": ["menu_items", "user_favorites", "offers"],
                "category": "personalized_recommendation",
            }
        )
    elif "order" in message or "where is my" in message:
        intents.append(
            {
                "name": "TRACK_ORDER_STATUS",
                "confidence": 0.9,
                "reason": "User is asking about order status.",
                "required_data": ["order_status"],
                "category": "order_support",
            }
        )
    else:
        intents.append(
            {
                "name": "GENERAL_QUERY",
                "confidence": 0.5,
                "reason": "Default fallback intent.",
                "required_data": [],
                "category": "generic",
            }
        )

    # Fill up to 5 with dummy low-confidence intents
    while len(intents) < 5:
        intents.append(
            {
                "name": f"FILLER_INTENT_{len(intents)+1}",
                "confidence": 0.1,
                "reason": "Low-confidence filler intent.",
                "required_data": [],
                "category": "fallback",
            }
        )

    return {"intents": intents[:5]}

from typing import Dict, Any, List, Optional


def _choose_best_store(stores: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Simple heuristic: prefer open + nearest; else nearest.
    """
    if not stores:
        return None

    open_stores = [s for s in stores if s.get("is_open_now")]
    if open_stores:
        open_stores.sort(key=lambda x: x.get("distance_m", 0.0))
        return open_stores[0]

    stores.sort(key=lambda x: x.get("distance_m", 0.0))
    return stores[0]


def get_final_response(context_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent-2 stub:
    Uses heuristics instead of LLM for now.
    Later: swap to llama3.1 for natural language response generation.
    """
    user_msg = context_bundle.get("user_message_masked", "")
    intents = context_bundle.get("intents", [])
    stores = context_bundle.get("candidate_stores", [])
    user_profile = context_bundle.get("user_profile_light", {})
    offers = context_bundle.get("offers", [])

    name = user_profile.get("name", "there")

    # Pick best intent (highest confidence)
    primary_intent = None
    if intents:
        primary_intent = max(intents, key=lambda i: i.get("confidence", 0.0))

    primary_intent_name = primary_intent.get("name") if primary_intent else None

    best_store = _choose_best_store(stores)
    selected_store_id = best_store.get("id") if best_store else None

    # Find an offer for that store
    offer_text = ""
    if best_store:
        for o in offers:
            if o.get("store_id") == best_store["id"]:
                offer_text = f" You also have a coupon: {o['description']} (code: {o['coupon_code']})."
                break

    # Construct reply based on primary intent
    if primary_intent_name == "FIND_NEARBY_COFFEE_SHOP" and best_store:
        reply = (
            f"Hi {name}, you're close to {best_store['name']} "
            f"({int(best_store.get('distance_m', 0))} meters away). "
            f"It's currently {'open' if best_store.get('is_open_now') else 'closed'}. "
        )
        if best_store.get("is_open_now"):
            reply += "You can step inside to warm up with a hot drink."
        else:
            reply += "It will open later according to its schedule."
        reply += offer_text
    else:
        # generic fallback
        reply = (
            f"Hi {name}, I received your message: '{user_msg}'. "
            "I’m still improving my understanding, but I can help you find nearby stores or track orders."
        )

    return {
        "selected_intent": primary_intent_name,
        "selected_store_id": selected_store_id,
        "reply": reply,
        "reasoning": primary_intent.get("reason") if primary_intent else "No primary intent detected.",
    }

from typing import Optional, List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

from backend.privacy.masking import mask_pii, safe_unmask
from backend.services.user_profile import get_user_profile_light
from backend.services.store_locator import get_nearby_stores
from backend.services.offers import get_offers_for_stores
from backend.llm.agent_intent import get_intents
from backend.llm.agent_response import get_final_response


app = FastAPI(title="GroundTruth Concierge API")


class ChatRequest(BaseModel):
    user_id: str
    message: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class StoreSummary(BaseModel):
    id: str
    name: str
    distance_m: float
    rating: Optional[float] = None
    is_open_now: Optional[bool] = None


class ChatResponse(BaseModel):
    reply: str
    selected_intent: Optional[str] = None
    selected_store: Optional[StoreSummary] = None
    debug: Optional[Dict[str, Any]] = None  # you can disable/remove this for prod


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    Main chat entrypoint:
    - Mask PII
    - Agent-1: get intents
    - Fetch store + offer context
    - Agent-2: compose response
    - Optional safe unmask
    """
    user_id = payload.user_id
    message = payload.message
    lat = payload.lat
    lng = payload.lng

    # 1) Get lightweight user profile
    user_profile = get_user_profile_light(user_id)

    # 2) Mask PII in the user message
    masked_message, pii_map = mask_pii(message)

    # 3) Agent-1: generate intents
    intent_input = {
        "user_message": masked_message,
        "user_profile": user_profile,
        "location": {"lat": lat, "lng": lng},
    }
    intents_result = get_intents(intent_input)
    intents = intents_result.get("intents", [])

    # 4) Fetch store context based on location + intents
    candidate_stores = get_nearby_stores(lat, lng, intents=intents)

    # 5) Fetch offers for those stores
    offers = get_offers_for_stores(user_id, candidate_stores)

    # 6) Bundle context for Agent-2
    context_bundle = {
        "user_message_masked": masked_message,
        "intents": intents,
        "location": {"lat": lat, "lng": lng},
        "candidate_stores": candidate_stores,
        "user_profile_light": user_profile,
        "offers": offers,
    }

    response_result = get_final_response(context_bundle)

    reply_text = response_result.get("reply", "")
    selected_intent = response_result.get("selected_intent")
    selected_store_id = response_result.get("selected_store_id")

    # 7) Safe unmask (currently unmask everything; you can restrict kinds later)
    reply_unmasked = safe_unmask(reply_text, pii_map)

    # 8) Build selected_store summary
    store_summary_obj: Optional[StoreSummary] = None
    if selected_store_id and candidate_stores:
        for s in candidate_stores:
            if s.get("id") == selected_store_id:
                store_summary_obj = StoreSummary(
                    id=s["id"],
                    name=s.get("name", "Unknown Store"),
                    distance_m=s.get("distance_m", 0.0),
                    rating=s.get("rating"),
                    is_open_now=s.get("is_open_now"),
                )
                break

    return ChatResponse(
        reply=reply_unmasked,
        selected_intent=selected_intent,
        selected_store=store_summary_obj,
        debug={
            "intents": intents,
            "candidate_stores": candidate_stores,
            "offers": offers,
            "raw_response": response_result,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

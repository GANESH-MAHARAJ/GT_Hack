from typing import Optional, List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from pydantic import BaseModel

from backend.privacy.masking import mask_pii, safe_unmask
from backend.services.user_profile import get_user_profile_light
from backend.services.store_locator import get_nearby_stores
from backend.services.offers import get_offers_for_stores
from backend.llm.agent_intent import get_intents
from backend.llm.agent_response import get_final_response
from backend.services.user_memory import (
    get_user_profile,
    update_conversation_history,
    set_last_seen_store,
    reset_user,
    reset_all,
)




app = FastAPI(title="GroundTruth Concierge API")

# Allow frontend (e.g., http://localhost:5500 or file:// origin in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon demo; in prod, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

    # 1) Get profiles
    # Persistent profile (preferences, history, last order, etc.)
    persistent_profile = get_user_profile(user_id)
    # Lightweight profile (for LLM context, from users.json)
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

    # ---- Decide if this looks like a FAQ / policy question ----
    user_lower = masked_message.lower()
    heuristic_faq = any(
        kw in user_lower
        for kw in [
            "return", "refund", "return policy", "shipping",
            "delivery", "loyalty", "membership", "points",
            "allergen", "allergy", "wifi", "wi-fi", "terms"
        ]
    )

    # If Agent-1 explicitly asks for FAQ data, respect that too
    explicit_faq = any(
        "faq_answer" in (i.get("required_data") or [])
        for i in intents
    )

    needs_faq = heuristic_faq or explicit_faq

    # 4) Fetch store context based on location + intents
    candidate_stores = get_nearby_stores(lat, lng, intents=intents)

    # 5) Fetch offers for those stores
    offers = get_offers_for_stores(user_id, candidate_stores)

    # 6) RAG: if this is FAQ-ish, query vector store
    rag_snippets = []
    if needs_faq:
        from backend.services.rag_service import rag_query  # import here to avoid cycles
        rag_snippets = rag_query(masked_message, top_k=3)
        # For FAQ/policy questions, we usually don't want store recommendations
        candidate_stores = []

    # 7) Bundle context for Agent-2
    context_bundle = {
        "user_message_masked": masked_message,
        "intents": intents,
        "location": {"lat": lat, "lng": lng},
        "candidate_stores": candidate_stores,
        "user_profile_light": user_profile,
        "user_profile_persistent": persistent_profile,
        "offers": offers,
        "rag_snippets": rag_snippets,
    }



    response_result = get_final_response(context_bundle)

    reply_text = response_result.get("reply", "")
    selected_intent = response_result.get("selected_intent")
    selected_store_id = response_result.get("selected_store_id")

    # 7) Safe unmask (currently unmask everything; you can restrict kinds later)
    reply_unmasked = safe_unmask(reply_text, pii_map)

    update_conversation_history(user_id, message, reply_unmasked)

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
    
    # 9) Update user memory (conversation history + last seen store)
    update_conversation_history(user_id, message, reply_unmasked)

    if store_summary_obj is not None:
        # store a slim version of the selected store
        set_last_seen_store(
            user_id,
            {
                "id": store_summary_obj.id,
                "name": store_summary_obj.name,
                "distance_m": store_summary_obj.distance_m,
                "rating": store_summary_obj.rating,
                "is_open_now": store_summary_obj.is_open_now,
            },
        )




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

@app.post("/reset_user/{user_id}")
def reset_user_endpoint(user_id: str):
    reset_user(user_id)
    return {"status": "ok", "user_id": user_id}


@app.post("/reset_all")
def reset_all_endpoint():
    reset_all()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

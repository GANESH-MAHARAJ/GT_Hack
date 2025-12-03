import json
from typing import Dict, Any, List, Optional

import ollama


MODEL_NAME = "llama3.1"  # same as Agent-1; keep consistent


RESPONSE_SYSTEM_PROMPT = """
You are a hyper-personalized customer support assistant for retail and coffee shops.

You will receive a JSON object with:
- user_message_masked
- intents
- location
- candidate_stores
- user_profile_light: basic profile (name, simple preferences)
- user_profile_persistent: richer memory, e.g.:
  {
    "preferences": {
      "favorite_drinks": [...],
      "dislikes": [...],
      "allergies": [...]
    },
    "loyalty_tier": "Bronze | Silver | Gold",
    "history": [...last 20 turns...],
    "last_seen_store": {...},
    "last_order": {...}
  }
- offers: coupons tagged with loyalty_tier
- rag_snippets: optional FAQ/policy chunks

Your tasks:
1. Choose the single most relevant primary intent.
2. If rag_snippets clearly answer the user's question (policies, shipping, loyalty, Wi-Fi, allergens),
   base your reply on those snippets and summarize accurately.
3. For store / visit / drink related queries:
   - Use user_profile_persistent to personalize recommendations.
   - If the user has favorite_drinks, prefer suggesting those.
   - If the user has allergies, avoid recommending risky drinks and mention warnings if relevant.
   - If the user is Silver or Gold tier, explicitly mention their benefits (e.g., higher discount).
   - If last_seen_store exists and is still relevant, you may reference it as a familiar option.
4. Use offers to mention concrete discounts when helpful, aligned with the user's loyalty tier.
5. Do NOT hallucinate information that is not in the JSON. Use only the data provided.
6. Reply in a friendly but concise tone.

You MUST reply in VALID JSON ONLY with this schema:
{
  "selected_intent": "STRING_OR_NULL",
  "selected_store_id": "STRING_OR_NULL",
  "reasoning": "STRING",
  "reply": "STRING"
}
No backticks, no prose outside JSON.
"""


INTENT_SYSTEM_PROMPT = """
... existing text ...

Some example intent names you can use:
- FIND_NEARBY_COFFEE_SHOP
- SUGGEST_WARM_DRINK
- CHECK_STORE_OPEN_STATUS
- TRACK_ORDER_STATUS
- CHECK_PRODUCT_AVAILABILITY
- ASK_RETURN_POLICY
- ASK_SHIPPING_POLICY
- ASK_LOYALTY_BENEFITS
- ASK_WIFI_TERMS
- ASK_ALLERGEN_INFO

If the question is about policies, returns, shipping, loyalty benefits, Wi-Fi rules, or allergens,
set required_data to include "faq_answer" so that the orchestrator can fetch FAQ snippets.
"""



def _heuristic_choose_store(stores: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Small local heuristic used to propose a 'best' store to the model.
    Not strictly required, but we can suggest one in context if helpful.
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
    Agent-2: call llama3.1 with the context bundle,
    ask it to select intent + store + craft final message.
    """
    # Optionally, we can add a small heuristic hint about best_store
    candidate_stores: List[Dict[str, Any]] = context_bundle.get("candidate_stores", []) or []
    best_store = _heuristic_choose_store(candidate_stores)
    context_bundle["best_store_hint"] = best_store  # purely advisory for the model

    # Call llama via Ollama
    resp = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(context_bundle, ensure_ascii=False),
            },
        ],
        options={
            "temperature": 0.3,  # a bit more creative but still stable
        },
    )

    content = resp["message"]["content"].strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: if model fails JSON, construct basic reply using heuristics
        primary_intent_name = None
        if context_bundle.get("intents"):
            primary_intent = max(
                context_bundle["intents"], key=lambda i: i.get("confidence", 0.0)
            )
            primary_intent_name = primary_intent.get("name")

        if best_store:
            fallback_reply = (
                f"You're close to {best_store['name']} "
                f"({int(best_store.get('distance_m', 0))} meters away). "
                f"It's currently {'open' if best_store.get('is_open_now') else 'closed'}."
            )
            selected_store_id = best_store.get("id")
        else:
            fallback_reply = (
                "I couldn't find a suitable nearby store, but I can still help with general support."
            )
            selected_store_id = None

        return {
            "selected_intent": primary_intent_name,
            "selected_store_id": selected_store_id,
            "reasoning": "JSON parsing failed; used local heuristic fallback.",
            "reply": fallback_reply,
        }

    # Minimal safety: ensure keys exist
    return {
        "selected_intent": data.get("selected_intent"),
        "selected_store_id": data.get("selected_store_id"),
        "reasoning": data.get("reasoning", ""),
        "reply": data.get("reply", ""),
    }

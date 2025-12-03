import json
from typing import Dict, Any

import ollama


MODEL_NAME = "llama3.1"  # make sure you've pulled this in Ollama


INTENT_SYSTEM_PROMPT = """
You are an Intent Classification and Task Routing engine for a hyper-personalized retail assistant.

You will receive:
- the user's MASKED message (no raw PII),
- light user profile,
- user location (lat/lng may be null).

Your job:
1. Infer up to FIVE candidate intents that the assistant might handle.
2. For each intent, provide:
   - name: SHORT_MACHINE_FRIENDLY (e.g., "FIND_NEARBY_COFFEE_SHOP")
   - confidence: float between 0.0 and 1.0
   - reason: brief human-readable explanation
   - required_data: list of data keys needed from tools/services
   - category: high-level group (e.g., "store_discovery", "order_support", "personalized_recommendation")

CRITICAL RULES:
- You MUST respond with VALID JSON ONLY. No backticks, no extra text.
- Response schema:
{
  "intents": [
    {
      "name": "STRING",
      "confidence": 0.95,
      "reason": "STRING",
      "required_data": ["STRING", ...],
      "category": "STRING"
    },
    ...
  ]
}
- If you are unsure, still provide at least one low-confidence fallback intent.
"""


def get_intents(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent-1: call llama3.1 to get top-N intents as JSON.
    payload:
      {
        "user_message": str,
        "user_profile": {...},
        "location": {"lat": float | None, "lng": float | None}
      }
    """
    user_message = payload.get("user_message", "")
    user_profile = payload.get("user_profile", {})
    location = payload.get("location", {})

    user_prompt = {
        "user_message_masked": user_message,
        "user_profile_light": user_profile,
        "location": location,
    }

    # Call llama3.1 via Ollama
    resp = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(user_prompt, ensure_ascii=False),
            },
        ],
        options={
            "temperature": 0.2,  # more deterministic
        },
    )

    content = resp["message"]["content"].strip()

    # Try to parse JSON robustly
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Last-ditch fallback: wrap in a default if something goes wrong
        # so the rest of the pipeline doesn't break.
        return {
            "intents": [
                {
                    "name": "FALLBACK_GENERIC",
                    "confidence": 0.3,
                    "reason": "Model returned non-JSON content.",
                    "required_data": [],
                    "category": "fallback",
                }
            ]
        }

    # Minimal safety checks
    intents = data.get("intents") or []
    if not isinstance(intents, list) or len(intents) == 0:
        intents = [
            {
                "name": "FALLBACK_GENERIC",
                "confidence": 0.3,
                "reason": "No intents returned.",
                "required_data": [],
                "category": "fallback",
            }
        ]

    # Always limit to 5
    data["intents"] = intents[:5]
    return data

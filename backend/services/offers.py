# backend/services/offers.py

from typing import List, Dict, Any

from backend.services.user_memory import get_user_profile


def _discount_for_tier(tier: str) -> int:
    tier = (tier or "").lower()
    if tier == "gold":
        return 15
    if tier == "silver":
        return 10
    return 5  # bronze / default


def get_offers_for_stores(user_id: str, stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Loyalty-aware offers:
    - Bronze: 5% off
    - Silver: 10% off
    - Gold: 15% off

    Applies to hot beverages by default.
    """
    profile = get_user_profile(user_id)
    tier = profile.get("loyalty_tier", "Bronze")
    discount = _discount_for_tier(tier)

    offers: List[Dict[str, Any]] = []
    for idx, s in enumerate(stores):
        offers.append(
            {
                "store_id": s["id"],
                "coupon_code": f"HOT{discount}_{idx+1}",
                "description": f"{discount}% off hot beverages",
                "valid_till": "2025-12-31",
                "loyalty_tier": tier,
            }
        )
    return offers

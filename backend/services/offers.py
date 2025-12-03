from typing import List, Dict, Any


def get_offers_for_stores(user_id: str, stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Stub: return one fake coupon per nearest store for demo.
    Later, attach real coupon logic / user-tier logic.
    """
    offers = []
    for idx, s in enumerate(stores):
        offers.append(
            {
                "store_id": s["id"],
                "coupon_code": f"HOT10_{idx+1}",
                "description": "10% off hot beverages",
                "valid_till": "2025-12-31",
            }
        )
    return offers

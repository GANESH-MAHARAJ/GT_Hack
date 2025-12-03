# backend/services/rag_service.py

import os
from typing import List, Dict, Any

import chromadb

# ---- ChromaDB setup ----

CHROMA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "rag",
    "vector_store"
)

_client = chromadb.PersistentClient(path=CHROMA_DIR)

COLLECTION_NAME = "customer_faqs"


def get_collection():
    return _client.get_or_create_collection(name=COLLECTION_NAME)


# ---- Static "PDF" contents for hackathon RAG ----
# These represent the content you *intended* to load from PDFs.

STATIC_DOCS = [
    {
        "id": "return_policy_1",
        "text": (
            "Return & Refund Policy — GroundTruth Coffee Stores. "
            "Customers may return eligible products within 30 days of purchase. "
            "Perishables such as baked items or fresh beverages must be reported within 24 hours. "
            "Items must be unopened, unused, and in their original packaging. "
            "Gift cards and promotional items are non-refundable. "
            "Refunds are issued to the original mode of payment and may take 2–5 business days. "
            "Online orders can be returned via the Order History section. "
            "Customized beverages, discounted merchandise, opened food items, "
            "and free promotional products are not eligible for return."
        ),
        "metadata": {"category": "return_policy", "source_file": "return_policy.pdf"},
    },
    {
        "id": "shipping_policy_1",
        "text": (
            "Shipping & Delivery Guidelines — GroundTruth Coffee. "
            "Standard delivery takes 2–4 business days. "
            "Express delivery takes 1–2 business days. "
            "Same-day delivery is available in select metro cities for orders placed before 2 PM. "
            "Standard delivery is free on orders above ₹499, otherwise a ₹49 fee applies. "
            "Express delivery costs ₹99 and same-day delivery costs ₹149. "
            "Every order includes a tracking ID that can be used in the Track My Order section. "
            "Delays may occur due to weather, holidays, high seasonal demand, or incorrect address. "
            "Lost or damaged packages are eligible for refund or replacement."
        ),
        "metadata": {"category": "shipping_policy", "source_file": "shipping_policy.pdf"},
    },
    {
        "id": "wifi_terms_1",
        "text": (
            "In-Store Wi-Fi Terms & Usage Policy — GroundTruth Coffee. "
            "Free Wi-Fi is provided to customers with a valid purchase receipt. "
            "Maximum session duration is 2 hours with a bandwidth limit of 5 Mbps per user. "
            "Downloading files larger than 200 MB is not allowed. "
            "Customers must not visit illegal or harmful websites, perform network attacks, "
            "or stream pirated content. "
            "GroundTruth does not record browsing history but logs session metadata such as time connected and device MAC ID. "
            "Use of Wi-Fi is at the customer's own risk; the company is not responsible for external threats."
        ),
        "metadata": {"category": "wifi_terms", "source_file": "wifi_terms.pdf"},
    },
    {
        "id": "loyalty_benefits_1",
        "text": (
            "GroundTruth Loyalty Program — Benefits Overview. "
            "Bronze members earn 1 point per ₹10 spent and get a birthday beverage at 10% discount. "
            "Silver members earn 1.5 points per ₹10, receive a free pastry during their birthday month, "
            "and get early access to new menu items. "
            "Gold members earn 2 points per ₹10, receive one free beverage every month, "
            "get an exclusive 10% discount on hot beverages, and have priority customer support. "
            "Points can be redeemed at participating stores or via the mobile app. "
            "Points expire 12 months after issuance; tier status is valid for the calendar year."
        ),
        "metadata": {"category": "loyalty", "source_file": "loyalty_benefits.pdf"},
    },
    {
        "id": "allergen_guide_1",
        "text": (
            "GroundTruth Coffee — Allergen & Ingredient Guide. "
            "Common allergens in menu items include milk, soy, wheat or gluten, nuts such as almond, cashew and hazelnut, "
            "chocolate, and artificial sweeteners. "
            "Hot Chocolate contains milk and soy. "
            "Caramel Latte contains dairy and may contain traces of gluten. "
            "Mocha Latte contains milk and chocolate. "
            "Cold Brew is typically allergen-free unless flavored syrups are added. "
            "Blueberry Muffin contains wheat, eggs, and milk. "
            "Chocolate Croissant contains wheat, milk, and chocolate. "
            "The Vegan Sandwich is dairy-free and egg-free. "
            "Cross-contamination may occur in shared kitchens, so customers with severe allergies should inform staff."
        ),
        "metadata": {"category": "allergen", "source_file": "allergen_guide.pdf"},
    },
]


def _bootstrap_static_docs():
    """
    Initialize the Chroma collection with static docs if it's empty.
    This replaces the need for PDF ingestion during a hackathon.
    """
    col = get_collection()
    try:
        if col.count() > 0:
            # Already populated, don't duplicate
            return
    except Exception:
        # If count() fails, just try to add docs
        pass

    ids = [d["id"] for d in STATIC_DOCS]
    docs = [d["text"] for d in STATIC_DOCS]
    metas = [d["metadata"] for d in STATIC_DOCS]

    col.add(ids=ids, documents=docs, metadatas=metas)


# Run bootstrap at import time
_bootstrap_static_docs()


def rag_query(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Query the vector store for relevant chunks.
    Returns a list of {text, metadata}.
    """
    col = get_collection()

    try:
        if col.count() == 0:
            return []
    except Exception:
        return []

    res = col.query(query_texts=[question], n_results=top_k)

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    snippets: List[Dict[str, Any]] = []
    for d, m in zip(docs, metas):
        snippets.append({"text": d, "metadata": m})

    return snippets

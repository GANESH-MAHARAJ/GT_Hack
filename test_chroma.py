from backend.services.rag_service import rag_query
print(rag_query("What is your return policy?", top_k=2))

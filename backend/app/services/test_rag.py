from backend.app.services.rag_service import PaymentRAG


rag = PaymentRAG()


query = """
Payment failed because Gateway_A produced a BANK_TIMEOUT.
What recovery action should be taken?
"""


results = rag.retrieve(query, k=3)


print("\n" + "=" * 60)
print("RAG RETRIEVAL TEST")
print("=" * 60)


for i, result in enumerate(results, start=1):

    print(f"\nResult {i}")
    print(f"Similarity: {result['score']:.4f}")
    print(result["document"])
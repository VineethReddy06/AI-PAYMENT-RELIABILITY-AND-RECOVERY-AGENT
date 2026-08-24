from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class PaymentRAG:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        docs_path = (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "payment_recovery_policies.txt"
        )

        self.documents = self.load_documents(docs_path)

        embeddings = self.model.encode(
            self.documents,
            normalize_embeddings=True
        )

        embeddings = np.array(
            embeddings,
            dtype="float32"
        )

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

    def load_documents(self, path):

        text = path.read_text(
            encoding="utf-8"
        )

        documents = [
            section.strip()
            for section in text.split("--------------------------------------------------")
            if section.strip()
        ]

        return documents

    def retrieve(self, query, k=3):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        query_embedding = np.array(
            query_embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            min(k, len(self.documents))
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):
            results.append({
                "score": float(score),
                "document": self.documents[index]
            })

        return results
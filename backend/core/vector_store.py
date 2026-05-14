<![CDATA["""
Thought Collision Engine — ChromaDB Vector Store

Manages concept embeddings for semantic similarity and distance calculations.
"""

from __future__ import annotations

from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger

from config import settings


class VectorStore:
    """ChromaDB vector store for concept embeddings."""

    def __init__(self):
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None

    def connect(self):
        """Connect to ChromaDB."""
        try:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "ChromaDB connected — collection '{}' ({} items)",
                settings.chroma_collection,
                self._collection.count(),
            )
        except Exception as e:
            logger.warning("ChromaDB connection failed, using in-memory fallback: {}", e)
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )

    def is_healthy(self) -> bool:
        """Check if ChromaDB is reachable."""
        if not self._client:
            return False
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False

    def add_embedding(
        self,
        concept_id: str,
        embedding: list[float],
        name: str = "",
        domain: str = "",
        metadata: dict = None,
    ):
        """Store a concept embedding."""
        if not self._collection:
            return

        meta = {"name": name, "domain": domain}
        if metadata:
            meta.update({k: str(v) for k, v in metadata.items()})

        self._collection.upsert(
            ids=[concept_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[name],
        )

    def query_similar(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict = None,
    ) -> list[dict]:
        """Find concepts with similar embeddings."""
        if not self._collection:
            return []

        kwargs = {
            "query_embeddings": [embedding],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        items = []
        if results and results["ids"]:
            for i, concept_id in enumerate(results["ids"][0]):
                items.append({
                    "id": concept_id,
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })
        return items

    def get_embedding(self, concept_id: str) -> Optional[list[float]]:
        """Get the embedding for a concept."""
        if not self._collection:
            return None

        result = self._collection.get(ids=[concept_id], include=["embeddings"])
        if result and result["embeddings"]:
            return result["embeddings"][0]
        return None

    def get_all_embeddings(self) -> dict[str, list[float]]:
        """Get all embeddings keyed by concept ID."""
        if not self._collection:
            return {}

        result = self._collection.get(include=["embeddings"])
        if result and result["ids"]:
            return dict(zip(result["ids"], result["embeddings"]))
        return {}

    def compute_distance(self, id_a: str, id_b: str) -> float:
        """Compute cosine distance between two concepts."""
        emb_a = self.get_embedding(id_a)
        emb_b = self.get_embedding(id_b)

        if not emb_a or not emb_b:
            return 1.0  # Max distance if missing

        # Cosine distance = 1 - cosine_similarity
        import numpy as np
        a = np.array(emb_a)
        b = np.array(emb_b)
        cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
        return float(1.0 - cos_sim)

    def count(self) -> int:
        """Get the number of stored embeddings."""
        if not self._collection:
            return 0
        return self._collection.count()


# Singleton instance
vector_store = VectorStore()
]]>

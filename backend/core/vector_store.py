<![CDATA["""
Thought Collision Engine — Qdrant Vector Store
Manages concept embeddings for semantic similarity and distance calculations.
Replaces ChromaDB for improved scalability and async support.
"""
from __future__ import annotations
from typing import Optional
from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from config import settings

class VectorStore:
    """Qdrant vector store for concept embeddings."""

    def __init__(self):
        self._client: Optional[AsyncQdrantClient] = None
        self._collection_name = settings.qdrant_collection
        self._vector_size = 384 # all-MiniLM-L6-v2 size

    async def connect(self):
        """Connect to Qdrant and initialize collection."""
        try:
            self._client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
            
            # Check if collection exists, create if not
            collections = await self._client.get_collections()
            exists = any(c.name == self._collection_name for c in collections.collections)
            
            if not exists:
                await self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection '{self._collection_name}'.")
            else:
                count = (await self._client.get_collection(self._collection_name)).vectors_count
                logger.info(f"Qdrant connected — collection '{self._collection_name}' ({count} items)")
                
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            self._client = None

    async def is_healthy(self) -> bool:
        """Check if Qdrant is reachable."""
        if not self._client:
            return False
        try:
            # simple ping
            await self._client.get_collections()
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
        """Store a concept embedding (Synchronous wrapper for Graph Builder)."""
        import asyncio
        if not self._client:
            return
            
        meta = {"name": name, "domain": domain}
        if metadata:
            meta.update(metadata)
            
        # We need a proper UUID format or int for Qdrant IDs, but Qdrant accepts UUID strings.
        # If concept_id is just a hash string, Qdrant will fail. 
        # For Thought Collision, concept_id is usually a UUID. We will hash it to int to be safe.
        point_id = hash(concept_id) & ((1<<63)-1) 

        point = PointStruct(id=point_id, vector=embedding, payload=meta)
        
        # Fire and forget or block if in async context
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._client.upsert(
                collection_name=self._collection_name,
                points=[point]
            ))
        except RuntimeError:
            asyncio.run(self._client.upsert(
                collection_name=self._collection_name,
                points=[point]
            ))

    async def get_embedding(self, concept_id: str) -> Optional[list[float]]:
        """Get the embedding for a concept."""
        if not self._client:
            return None
            
        point_id = hash(concept_id) & ((1<<63)-1)
        points = await self._client.retrieve(
            collection_name=self._collection_name,
            ids=[point_id],
            with_vectors=True
        )
        if points and points[0].vector:
            return points[0].vector
        return None

    def search(self, embedding: list[float], top_k: int = 10) -> list[dict]:
        """Synchronous wrapper to find concepts with similar embeddings."""
        import asyncio
        if not self._client:
            return []

        async def _search():
            hits = await self._client.search(
                collection_name=self._collection_name,
                query_vector=embedding,
                limit=top_k,
            )
            items = []
            for hit in hits:
                items.append({
                    "id": str(hit.id), # Not perfect translation from hash but payload contains name
                    "score": hit.score,
                    "metadata": hit.payload
                })
            return items
            
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(_search())
        except RuntimeError:
            return asyncio.run(_search())

vector_store = VectorStore()
]]>

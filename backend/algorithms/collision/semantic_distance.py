<![CDATA["""
Collision Algorithms — Semantic Distance Scorer
Evaluates the conceptual distance using the "Sweet Spot" Bell Curve model.
"""
import math
from typing import Optional
from core.vector_store import VectorStore

class SemanticDistanceScorer:
    def __init__(self, vector_store: VectorStore):
        self.vs = vector_store
        # The sweet spot where concepts are distant enough to be novel, 
        # but related enough to make sense.
        self.sweet_spot_min = 0.4
        self.sweet_spot_max = 0.7

    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """
        Calculates the Bell Curve Novelty Score based on Cosine Similarity.
        Similarity > 0.8 -> Low Score (Too obvious)
        Similarity < 0.3 -> Low Score (No coherent relation)
        Similarity ~0.55 -> High Score 1.0 (The Sweet Spot)
        """
        # Retrieve embeddings
        vec_a = self.vs.get_embedding(concept_a_id)
        vec_b = self.vs.get_embedding(concept_b_id)

        if not vec_a or not vec_b:
            return 0.0

        # Calculate Cosine Similarity
        import numpy as np
        from numpy.linalg import norm
        a, b = np.array(vec_a), np.array(vec_b)
        n_a, n_b = norm(a), norm(b)
        
        if n_a == 0 or n_b == 0:
            return 0.0
            
        similarity = np.dot(a, b) / (n_a * n_b)
        
        return self._bell_curve_score(similarity)

    def _bell_curve_score(self, similarity: float) -> float:
        """Apply gaussian bell curve centered around 0.55."""
        if similarity < 0.1:
            return 0.0 # Complete noise
            
        mean = 0.55
        std_dev = 0.15
        
        # Standard Normal Distribution Formula
        score = math.exp(-0.5 * ((similarity - mean) / std_dev) ** 2)
        return round(score, 3)

    async def get_sweet_spot_candidates(self, concept_id: str, top_k: int = 50) -> list[dict]:
        """Use Vector Store to directly fetch candidates in the sweet spot."""
        vec = self.vs.get_embedding(concept_id)
        if not vec:
            return []
            
        results = self.vs.search(vec, top_k=top_k * 2) # Fetch extra to filter
        
        candidates = []
        for r in results:
            if r["id"] == concept_id:
                continue
                
            sim = r.get("score", 0.0)
            if self.sweet_spot_min <= sim <= self.sweet_spot_max:
                candidates.append({
                    "id": r["id"],
                    "name": r["metadata"].get("name", "Unknown"),
                    "domain": r["metadata"].get("domain", ""),
                    "similarity": sim,
                    "semantic_score": self._bell_curve_score(sim)
                })
        return candidates[:top_k]
]]>

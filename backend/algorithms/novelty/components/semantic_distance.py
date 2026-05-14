<![CDATA["""
Semantic Distance Component for Novelty Scoring.
Reuses the bell-curve logic from the Collision Engine.
"""
from core.vector_store import VectorStore
from algorithms.collision.semantic_distance import SemanticDistanceScorer

class SemanticDistanceComponent:
    name = "semantic_distance"
    
    def __init__(self, vector_store: VectorStore):
        self.scorer = SemanticDistanceScorer(vector_store)
        
    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """Returns novelty score (0.0 to 1.0) based on Sweet Spot similarity."""
        return await self.scorer.score(concept_a_id, concept_b_id)
        
    def explain(self, score: float) -> str:
        if score > 0.8:
            return "Sit perfectly in the semantic 'sweet spot'—distant enough to be novel, but related enough to be useful."
        elif score > 0.5:
            return "Have a moderate, intriguing semantic relationship."
        else:
            return "Are semantically disjoint or overly obvious."
]]>

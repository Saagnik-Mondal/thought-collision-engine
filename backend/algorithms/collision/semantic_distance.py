<![CDATA["""
Semantic Distance Scoring — Score based on embedding distance.
"""
from core.vector_store import VectorStore

class SemanticDistanceScorer:
    name = "semantic_distance"

    def score(self, vector_store: VectorStore, id_a: str, id_b: str) -> float:
        """Score based on semantic distance — moderate distance is ideal.
        
        Too similar = obvious connection (low score)
        Too different = no meaningful connection (low score)
        Sweet spot = distant but with hidden similarity (high score)
        """
        distance = vector_store.compute_distance(id_a, id_b)
        # Bell curve scoring: peak novelty at distance ~0.5-0.7
        if distance < 0.3:
            return distance / 0.3 * 0.5  # Too similar
        elif distance < 0.7:
            return 0.5 + (distance - 0.3) / 0.4 * 0.5  # Sweet spot
        else:
            return max(0.3, 1.0 - (distance - 0.7) / 0.3 * 0.7)  # Too different
]]>

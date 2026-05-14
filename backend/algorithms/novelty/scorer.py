<![CDATA["""
Modular Novelty Scorer — Combines all mathematical novelty factors.
Provides Human-Readable Explainability.
"""
from core.neo4j_client import Neo4jClient
from core.vector_store import VectorStore
from algorithms.novelty.components.semantic_distance import SemanticDistanceComponent
from algorithms.novelty.components.rarity import RarityComponent
from algorithms.novelty.components.graph_separation import GraphSeparationComponent
from algorithms.novelty.components.citation_uniqueness import CitationUniquenessComponent
from algorithms.novelty.components.concept_diversity import ConceptDiversityComponent
from algorithms.novelty.config import DEFAULT_WEIGHTS, validate_weights

class NoveltyScorer:
    def __init__(self, neo4j: Neo4jClient, vector_store: VectorStore, weights: dict = None):
        self.weights = validate_weights(weights or DEFAULT_WEIGHTS)
        
        # Initialize the 5 components
        self.components = {
            "semantic_distance": SemanticDistanceComponent(vector_store),
            "rarity": RarityComponent(neo4j),
            "graph_separation": GraphSeparationComponent(neo4j),
            "citation_uniqueness": CitationUniquenessComponent(neo4j),
            "concept_diversity": ConceptDiversityComponent(neo4j)
        }

    async def evaluate(self, concept_a_id: str, concept_b_id: str) -> dict:
        """Evaluate the collision and return scores and explainability."""
        scores = {}
        total = 0.0
        
        for name, component in self.components.items():
            weight = self.weights.get(name, 0.2)
            score = await component.score(concept_a_id, concept_b_id)
            scores[name] = score
            total += weight * score
            
        final_score = round(min(1.0, max(0.0, total)), 3)
        explanation = self._generate_explanation(scores)
        
        return {
            "novelty_score": final_score,
            "components": scores,
            "explanation": explanation
        }

    def _generate_explanation(self, scores: dict) -> str:
        """Translate mathematical scores into human-readable rationale."""
        sentences = ["This collision is notable because the concepts:"]
        
        for name, score in scores.items():
            component = self.components[name]
            reason = component.explain(score)
            sentences.append(f"- {reason}")
            
        return "\n".join(sentences)
]]>

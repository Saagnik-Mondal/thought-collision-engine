<![CDATA["""
Modular Novelty Scorer — Combines all novelty components.

Novelty = semantic_distance × rarity × graph_separation × citation_uniqueness × concept_diversity

Each component is modular and independently configurable.
"""
from algorithms.novelty.components.semantic_distance import SemanticDistanceComponent
from algorithms.novelty.components.rarity import RarityComponent
from algorithms.novelty.components.graph_separation import GraphSeparationComponent
from algorithms.novelty.components.citation_uniqueness import CitationUniquenessComponent
from algorithms.novelty.components.concept_diversity import ConceptDiversityComponent
from algorithms.novelty.config import DEFAULT_WEIGHTS, validate_weights

class NoveltyScorer:
    def __init__(self, weights: dict = None):
        self.weights = validate_weights(weights or DEFAULT_WEIGHTS)
        self.components = [
            SemanticDistanceComponent(),
            RarityComponent(),
            GraphSeparationComponent(),
            CitationUniquenessComponent(),
            ConceptDiversityComponent(),
        ]

    def score(self, collision: dict) -> float:
        """Compute the overall novelty score (0-100)."""
        total = 0.0
        for component in self.components:
            weight = self.weights.get(component.name, component.weight)
            component_score = component.score(collision)
            total += weight * component_score
        return round(min(100, max(0, total)), 1)

    def score_breakdown(self, collision: dict) -> dict:
        """Get individual component scores."""
        return {c.name: round(c.score(collision), 1) for c in self.components}
]]>

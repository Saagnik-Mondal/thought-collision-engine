<![CDATA["""
Novelty Engine Configuration.
Defines default weights for the 5 novelty factors.
"""

DEFAULT_WEIGHTS = {
    "semantic_distance": 0.30,
    "rarity": 0.15,
    "graph_separation": 0.20,
    "citation_uniqueness": 0.15,
    "concept_diversity": 0.20
}

def validate_weights(weights: dict) -> dict:
    """Ensure weights sum to 1.0 (approximately)."""
    total = sum(weights.values())
    if total == 0:
        return DEFAULT_WEIGHTS
    return {k: v / total for k, v in weights.items()}
]]>

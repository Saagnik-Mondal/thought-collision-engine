<![CDATA["""
Novelty Score Configuration — Define weights for scoring components.
"""
DEFAULT_WEIGHTS = {
    "semantic_distance": 0.25,
    "rarity": 0.15,
    "graph_separation": 0.25,
    "citation_uniqueness": 0.15,
    "concept_diversity": 0.20,
}

def validate_weights(weights: dict) -> dict:
    """Validate and normalize scoring weights."""
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        return {k: v / total for k, v in weights.items()}
    return weights
]]>

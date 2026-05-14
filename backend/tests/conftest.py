<![CDATA["""Test configuration and fixtures."""
import pytest

@pytest.fixture
def sample_collision():
    return {
        "concept_a": {"id": "a1", "name": "ant colony optimization", "domain": "biology"},
        "concept_b": {"id": "b1", "name": "network routing", "domain": "computer_science"},
        "domain_a": "biology", "domain_b": "computer_science",
        "semantic_distance": 0.65, "graph_distance": 0.8, "bridge_score": 0.7,
        "reasoning": "Both involve distributed pathfinding with local decisions",
    }

@pytest.fixture
def sample_concepts():
    return [
        {"name": "neural plasticity", "type": "concept", "confidence": 0.9},
        {"name": "blockchain consensus", "type": "concept", "confidence": 0.85},
        {"name": "immune response", "type": "concept", "confidence": 0.88},
    ]
]]>

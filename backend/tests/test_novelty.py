<![CDATA["""
Tests for Novelty Scoring Components
"""
import pytest
from algorithms.novelty.components.concept_diversity import ConceptDiversityComponent
from algorithms.novelty.config import validate_weights, DEFAULT_WEIGHTS

# Mock Neo4j Client for Diversity Testing
class MockNeo4j:
    async def execute_read(self, query, params):
        if "ConceptDiversity" in self.__class__.__name__ or "domain" in query:
            if params["id"] == "a":
                return [{"domains": ["AI", "CS", "Math"]}]
            if params["id"] == "b":
                return [{"domains": ["Biology", "Chemistry", "CS"]}]
        return []

@pytest.fixture
def mock_neo4j():
    return MockNeo4j()

def test_weight_validation():
    # Should normalize
    weights = {"a": 10, "b": 10}
    norm = validate_weights(weights)
    assert norm["a"] == 0.5
    assert norm["b"] == 0.5
    
    # Empty should return default
    assert validate_weights({}) == DEFAULT_WEIGHTS

@pytest.mark.asyncio
async def test_concept_diversity(mock_neo4j):
    comp = ConceptDiversityComponent(mock_neo4j)
    
    # Neighborhood A: AI, CS, Math
    # Neighborhood B: Biology, Chemistry, CS
    # Intersection: CS (1)
    # Union: AI, CS, Math, Biology, Chemistry (5)
    # Jaccard Index = 1/5 = 0.2
    # Jaccard Distance (Diversity Score) = 1 - 0.2 = 0.8
    
    score = await comp.score("a", "b")
    assert score == 0.8
    
    explanation = comp.explain(score)
    assert "partially overlapping" in explanation.lower() or "distinct" in explanation.lower()
]]>

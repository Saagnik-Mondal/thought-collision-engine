<![CDATA["""
Tests for Collision Discovery Algorithms
"""
import pytest
from algorithms.collision.semantic_distance import SemanticDistanceScorer
from algorithms.graph_algorithms.shortest_paths import ShortestPathAlgorithm

# Mock Vector Store
class MockVectorStore:
    def get_embedding(self, cid):
        if cid == "a": return [1.0, 0.0, 0.0]
        if cid == "b": return [0.5, 0.5, 0.0]  # Sim ~0.7
        if cid == "c": return [1.0, 0.0, 0.0]  # Sim 1.0
        if cid == "d": return [0.0, 1.0, 0.0]  # Sim 0.0
        return None

# Mock Neo4j Client
class MockNeo4j:
    async def execute_read(self, query, params):
        if "shortestPath" in query:
            if params["source_id"] == "a" and params["target_id"] == "b":
                return [{"distance": 1}]
            if params["source_id"] == "a" and params["target_id"] == "d":
                return [] # No path
        return None

@pytest.mark.asyncio
async def test_semantic_bell_curve():
    vs = MockVectorStore()
    scorer = SemanticDistanceScorer(vs)
    
    # Same vector -> Similarity 1.0 -> Bad novelty
    score_identical = await scorer.score("a", "c")
    assert score_identical < 0.2
    
    # Orthogonal vector -> Similarity 0.0 -> Complete noise -> Bad novelty
    score_orthogonal = await scorer.score("a", "d")
    assert score_orthogonal == 0.0
    
    # Sweet spot vector -> Similarity ~0.7 -> High novelty
    score_sweet = await scorer.score("a", "b")
    assert score_sweet > 0.5

@pytest.mark.asyncio
async def test_structural_novelty():
    neo = MockNeo4j()
    scorer = ShortestPathAlgorithm()
    
    # Direct neighbors = 0.0 structural novelty
    score_neighbor = await scorer.score_novelty(neo, "a", "b", max_depth=6)
    assert score_neighbor == 0.0
    
    # Disconnected = 1.0 structural novelty
    score_disconnected = await scorer.score_novelty(neo, "a", "d", max_depth=6)
    assert score_disconnected == 1.0
]]>

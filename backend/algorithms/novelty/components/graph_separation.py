<![CDATA["""
Graph Separation Component for Novelty Scoring.
Evaluates the structural distance between nodes.
"""
from core.neo4j_client import Neo4jClient
from algorithms.graph_algorithms.shortest_paths import ShortestPathAlgorithm

class GraphSeparationComponent:
    name = "graph_separation"
    
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j
        self.scorer = ShortestPathAlgorithm()
        
    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """Returns novelty score (0.0 to 1.0) based on Shortest Path."""
        return await self.scorer.score_novelty(self.neo4j, concept_a_id, concept_b_id, max_depth=6)

    def explain(self, score: float) -> str:
        if score == 1.0:
            return "Are completely disconnected structurally, meaning no known literature links them."
        elif score > 0.6:
            return "Are structurally distant, requiring multiple indirect logical leaps to connect."
        else:
            return "Are closely connected in the existing literature."
]]>

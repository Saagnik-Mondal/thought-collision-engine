<![CDATA["""
Rarity Component for Novelty Scoring.
Evaluates how rarely these concepts are discussed in the global graph.
"""
from core.neo4j_client import Neo4jClient

class RarityComponent:
    name = "rarity"
    
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j
        
    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """
        Returns novelty score (0.0 to 1.0). 
        Calculated as the inverse of their average PageRank or Degree.
        Lower popularity = Higher rarity score.
        """
        query = """
        MATCH (c:Concept)
        WHERE c.id IN [$id_a, $id_b]
        RETURN avg(coalesce(c.pagerank, 0.5)) AS avg_pr
        """
        result = await self.neo4j.execute_read(query, {"id_a": concept_a_id, "id_b": concept_b_id})
        
        if not result or result[0]["avg_pr"] is None:
            return 1.0 # Extremely rare (no pagerank)
            
        avg_pr = result[0]["avg_pr"]
        
        # Heuristic inversion: PR usually is between 0.15 and ~10.0+ depending on graph size.
        # We cap PR at 5.0 for normalization.
        normalized_pr = min(1.0, avg_pr / 5.0)
        rarity = 1.0 - normalized_pr
        return round(max(0.0, rarity), 3)

    def explain(self, score: float) -> str:
        if score > 0.8:
            return "Are highly obscure concepts rarely discussed in the knowledge base."
        elif score > 0.4:
            return "Have moderate visibility across the graph."
        else:
            return "Are ubiquitous, mainstream concepts."
]]>

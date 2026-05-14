<![CDATA["""
Graph Algorithms — Shortest Paths
Calculates the structural distance between two nodes. High distance = high novelty.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class ShortestPathAlgorithm:
    async def get_distance(self, neo4j: Neo4jClient, source_id: str, target_id: str, max_depth: int = 6) -> int:
        """
        Calculate structural distance.
        Returns distance. If no path within max_depth, returns max_depth (high novelty).
        """
        query = """
        MATCH path = shortestPath(
            (a:Concept {id: $source_id})-[*1..$max_depth]-(b:Concept {id: $target_id})
        )
        RETURN length(path) AS distance
        """
        result = await neo4j.execute_read(query, {
            "source_id": source_id, 
            "target_id": target_id, 
            "max_depth": max_depth
        })
        
        if not result:
            return max_depth  # No path found = maximum structural novelty
        
        return result[0]["distance"]

    async def score_novelty(self, neo4j: Neo4jClient, source_id: str, target_id: str, max_depth: int = 6) -> float:
        """Convert structural distance into a normalized novelty score (0.0 to 1.0)."""
        dist = await self.get_distance(neo4j, source_id, target_id, max_depth)
        # Distance 1 (direct neighbor) = 0.0 novelty
        # Distance >= max_depth = 1.0 novelty
        if dist <= 1:
            return 0.0
        return min(1.0, dist / max_depth)
]]>

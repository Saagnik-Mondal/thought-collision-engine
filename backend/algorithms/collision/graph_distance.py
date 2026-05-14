<![CDATA["""
Graph Distance Scoring — Score collisions by graph separation.
"""
from core.neo4j_client import Neo4jClient

class GraphDistanceScorer:
    name = "graph_distance"

    async def score(self, neo4j: Neo4jClient, id_a: str, id_b: str) -> float:
        """Score based on graph distance — higher distance = more novel."""
        result = await neo4j.get_shortest_path(id_a, id_b)
        if not result or result[0].get("distance", -1) == -1:
            return 1.0  # No path = maximum separation
        distance = result[0]["distance"]
        # Normalize: longer paths → higher score (0-1)
        return min(1.0, distance / 10.0)
]]>

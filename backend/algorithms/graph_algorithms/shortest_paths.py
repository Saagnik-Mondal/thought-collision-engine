<![CDATA["""
Shortest Paths — Find shortest paths between concept nodes.
"""
from core.neo4j_client import Neo4jClient

class ShortestPaths:
    name = "shortest_paths"

    async def find(self, neo4j: Neo4jClient, source_id: str, target_id: str) -> dict:
        """Find shortest path between two concepts."""
        result = await neo4j.get_shortest_path(source_id, target_id)
        if result:
            return {"path": result[0].get("path_nodes", []), "distance": result[0].get("distance", -1)}
        return {"path": [], "distance": -1}

    async def all_pairs_distances(self, neo4j: Neo4jClient, node_ids: list[str]) -> dict:
        """Compute pairwise distances for a set of nodes."""
        distances = {}
        for i, id_a in enumerate(node_ids):
            for id_b in node_ids[i+1:]:
                result = await neo4j.get_shortest_path(id_a, id_b)
                dist = result[0].get("distance", -1) if result else -1
                distances[(id_a, id_b)] = dist
        return distances
]]>

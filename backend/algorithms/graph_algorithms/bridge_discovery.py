<![CDATA["""
Bridge Node Discovery — Find nodes that connect different communities.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class BridgeDiscovery:
    name = "bridge_discovery"

    async def find_bridges(self, neo4j: Neo4jClient, top_n: int = 20) -> list[dict]:
        """Find nodes that bridge different communities."""
        query = """
        MATCH (c:Concept)-[r]-(neighbor:Concept)
        WHERE c.community_id IS NOT NULL AND neighbor.community_id IS NOT NULL
              AND c.community_id <> neighbor.community_id
        WITH c, count(DISTINCT neighbor.community_id) AS bridge_count,
             collect(DISTINCT neighbor.community_id) AS connected_communities
        WHERE bridge_count >= 2
        RETURN c.id AS id, c.name AS name, c.domain AS domain,
               bridge_count, connected_communities
        ORDER BY bridge_count DESC
        LIMIT $top_n
        """
        result = await neo4j.execute_read(query, {"top_n": top_n})
        logger.info("Found {} bridge nodes", len(result))
        return result
]]>

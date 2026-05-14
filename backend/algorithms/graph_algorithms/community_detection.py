<![CDATA["""
Community Detection — Louvain-based community detection.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class CommunityDetection:
    name = "community_detection"

    async def detect(self, neo4j: Neo4jClient) -> dict:
        """Detect communities using Louvain algorithm."""
        try:
            await neo4j.execute_write("""
                CALL gds.graph.project('community_graph', 'Concept', {
                    SEMANTIC: {orientation: 'UNDIRECTED'},
                    CO_OCCURRENCE: {orientation: 'UNDIRECTED'}
                })
            """)
            result = await neo4j.execute_write("""
                CALL gds.louvain.write('community_graph', {writeProperty: 'community_id'})
                YIELD communityCount, modularity
                RETURN communityCount, modularity
            """)
            await neo4j.execute_write("CALL gds.graph.drop('community_graph')")
            info = result[0] if result else {}
            logger.info("Detected {} communities (modularity: {})",
                info.get("communityCount", 0), info.get("modularity", 0))
            return info
        except Exception as e:
            logger.info("GDS not available, using label propagation fallback: {}", e)
            return await self._simple_communities(neo4j)

    async def _simple_communities(self, neo4j: Neo4jClient) -> dict:
        """Assign communities based on domain grouping."""
        await neo4j.execute_write("""
            MATCH (c:Concept)
            WITH c.domain AS domain, collect(c) AS nodes
            UNWIND range(0, size(nodes)-1) AS idx
            WITH nodes[idx] AS node, domain
            SET node.community_id = CASE WHEN domain <> '' THEN abs(apoc.util.md5([domain])) % 100 ELSE -1 END
        """)
        return {"communityCount": 0, "modularity": 0, "method": "domain_fallback"}
]]>

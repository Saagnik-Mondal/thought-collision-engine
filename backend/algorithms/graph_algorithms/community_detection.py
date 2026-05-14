<![CDATA["""
Graph Algorithms — Louvain Community Detection
Groups tightly connected concepts into "communities" to enable Bridge Node discovery.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class CommunityDetection:
    async def run(self, neo4j: Neo4jClient) -> None:
        """Execute Louvain Community Detection using Neo4j GDS or native fallback."""
        logger.info("Executing Louvain Community Detection...")
        try:
            await neo4j.execute_write("""
            CALL gds.graph.project(
                'louvain_graph',
                'Concept',
                {
                    INFERRED_RELATION: {orientation: 'UNDIRECTED'},
                    CO_OCCURRENCE: {orientation: 'UNDIRECTED'}
                }
            )
            """)
            await neo4j.execute_write("""
            CALL gds.louvain.write('louvain_graph', {
                writeProperty: 'community_id'
            })
            """)
            await neo4j.execute_write("CALL gds.graph.drop('louvain_graph')")
            logger.info("Louvain completed via GDS.")
        except Exception:
            logger.warning("GDS not available. Using native Cypher fallback for Community Detection.")
            # Native fallback: Weakly Connected Components approximation based on domains
            query = """
            MATCH (c:Concept)
            SET c.community_id = coalesce(c.domain, 'unknown_community')
            """
            await neo4j.execute_write(query)
            logger.info("Community Detection completed via domain mapping approximation.")

    async def are_bridge_nodes(self, neo4j: Neo4jClient, node_a_id: str, node_b_id: str) -> bool:
        """Check if two nodes belong to different communities."""
        query = """
        MATCH (a:Concept {id: $id_a}), (b:Concept {id: $id_b})
        RETURN a.community_id AS comm_a, b.community_id AS comm_b
        """
        result = await neo4j.execute_read(query, {"id_a": node_a_id, "id_b": node_b_id})
        if not result:
            return False
        row = result[0]
        # Return True if they exist and are in different communities
        return row.get("comm_a") != row.get("comm_b")
]]>

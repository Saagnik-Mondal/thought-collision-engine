<![CDATA["""
Centrality Analysis — Betweenness and closeness centrality.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class CentralityAnalysis:
    name = "centrality"

    async def compute_betweenness(self, neo4j: Neo4jClient) -> list[dict]:
        """Compute betweenness centrality."""
        try:
            await neo4j.execute_write("CALL gds.graph.project('centrality_graph', 'Concept', '*')")
            await neo4j.execute_write("""
                CALL gds.betweenness.write('centrality_graph', {writeProperty: 'centrality'})
            """)
            await neo4j.execute_write("CALL gds.graph.drop('centrality_graph')")
            logger.info("Betweenness centrality computed via GDS")
        except Exception:
            logger.info("GDS not available for centrality, using degree-based fallback")
            await neo4j.execute_write("""
                MATCH (c:Concept)
                OPTIONAL MATCH (c)-[r]-()
                WITH c, count(r) AS degree
                SET c.centrality = toFloat(degree)
            """)
        result = await neo4j.execute_read("""
            MATCH (c:Concept) WHERE c.centrality IS NOT NULL
            RETURN c.id AS id, c.name AS name, c.centrality AS centrality
            ORDER BY c.centrality DESC LIMIT 20
        """)
        return result
]]>

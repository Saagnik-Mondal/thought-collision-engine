<![CDATA["""
PageRank — Compute importance of concept nodes.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class PageRankAlgorithm:
    name = "pagerank"

    async def compute(self, neo4j: Neo4jClient, damping: float = 0.85, iterations: int = 20) -> dict:
        """Compute PageRank for all concept nodes."""
        # Try Neo4j GDS first
        try:
            await neo4j.execute_write("""
                CALL gds.graph.project('concept_graph', 'Concept', {
                    SEMANTIC: {orientation: 'UNDIRECTED'},
                    CO_OCCURRENCE: {orientation: 'UNDIRECTED'},
                    INFERRED: {orientation: 'UNDIRECTED'}
                })
            """)
            result = await neo4j.execute_write("""
                CALL gds.pageRank.write('concept_graph', {
                    dampingFactor: $damping, maxIterations: $iterations,
                    writeProperty: 'pagerank'
                }) YIELD nodePropertiesWritten
                RETURN nodePropertiesWritten
            """, {"damping": damping, "iterations": iterations})
            await neo4j.execute_write("CALL gds.graph.drop('concept_graph')")
            logger.info("PageRank computed via GDS: {} nodes updated", result[0].get("nodePropertiesWritten", 0) if result else 0)
        except Exception as e:
            logger.info("GDS not available, using simple PageRank: {}", e)
            await self._simple_pagerank(neo4j, damping, iterations)

    async def _simple_pagerank(self, neo4j: Neo4jClient, damping: float, iterations: int):
        """Simplified PageRank using Cypher."""
        # Initialize
        await neo4j.execute_write("MATCH (c:Concept) SET c.pagerank = 1.0")
        for _ in range(iterations):
            await neo4j.execute_write("""
                MATCH (c:Concept)
                OPTIONAL MATCH (c)<-[r]-(neighbor:Concept)
                WITH c, collect(neighbor) AS neighbors, count(neighbor) AS degree
                OPTIONAL MATCH (c)-[r2]->(out:Concept)
                WITH c, neighbors, degree, count(out) AS out_degree
                SET c.pagerank = $base + $damping * REDUCE(s = 0.0, n IN neighbors |
                    s + COALESCE(n.pagerank, 1.0) / CASE WHEN degree > 0 THEN degree ELSE 1 END)
            """, {"damping": damping, "base": 1.0 - damping})
        logger.info("Simple PageRank completed ({} iterations)", iterations)
]]>

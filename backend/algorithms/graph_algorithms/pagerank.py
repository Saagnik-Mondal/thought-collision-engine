<![CDATA["""
Graph Algorithms — PageRank (Centrality)
Assigns importance scores to concept nodes based on their graph connectivity.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class PageRankAlgorithm:
    async def run(self, neo4j: Neo4jClient) -> None:
        """Execute PageRank using Neo4j GDS or fallback to native Cypher."""
        logger.info("Executing PageRank algorithm...")
        try:
            # Check if GDS is available
            await neo4j.execute_read("CALL gds.graph.exists('concept_graph')")
            
            # Use GDS PageRank
            await neo4j.execute_write("""
            CALL gds.graph.project(
                'concept_graph',
                'Concept',
                ['INFERRED_RELATION', 'CO_OCCURRENCE', 'HAS_CONCEPT']
            )
            """)
            await neo4j.execute_write("""
            CALL gds.pageRank.write('concept_graph', {
                maxIterations: 20,
                dampingFactor: 0.85,
                writeProperty: 'pagerank'
            })
            """)
            await neo4j.execute_write("CALL gds.graph.drop('concept_graph')")
            logger.info("PageRank completed via GDS.")
            
        except Exception:
            logger.warning("GDS not available. Using native Cypher fallback for PageRank approximation.")
            # Fallback approximation based on degree centrality
            query = """
            MATCH (c:Concept)
            OPTIONAL MATCH (c)-[r]-()
            WITH c, count(r) AS degree
            SET c.pagerank = degree * 0.1 + 0.15
            """
            await neo4j.execute_write(query)
            logger.info("PageRank completed via native Cypher approximation.")

    async def get_top_concepts(self, neo4j: Neo4jClient, limit: int = 50) -> list[dict]:
        """Retrieve the concepts with the highest PageRank score."""
        query = """
        MATCH (c:Concept)
        WHERE c.pagerank IS NOT NULL
        RETURN c.id AS id, c.name AS name, c.domain AS domain, c.pagerank AS pagerank
        ORDER BY c.pagerank DESC
        LIMIT $limit
        """
        return await neo4j.execute_read(query, {"limit": limit})
]]>

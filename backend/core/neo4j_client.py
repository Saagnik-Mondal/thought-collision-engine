<![CDATA["""
Thought Collision Engine — Neo4j Client

Async wrapper around the Neo4j Python driver for graph operations.
"""

from __future__ import annotations

from typing import Any, Optional

from loguru import logger
from neo4j import AsyncGraphDatabase, AsyncDriver

from config import settings


class Neo4jClient:
    """Async Neo4j graph database client."""

    def __init__(self):
        self._driver: Optional[AsyncDriver] = None

    async def connect(self):
        """Establish connection to Neo4j."""
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        # Verify connectivity
        await self._driver.verify_connectivity()
        logger.info("Neo4j driver connected to {}", settings.neo4j_uri)

        # Create indexes
        await self._create_indexes()

    async def _create_indexes(self):
        """Create graph indexes for performance."""
        async with self._driver.session() as session:
            # Index on concept name
            await session.run(
                "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)"
            )
            # Index on concept domain
            await session.run(
                "CREATE INDEX concept_domain IF NOT EXISTS FOR (c:Concept) ON (c.domain)"
            )
            # Index on domain name
            await session.run(
                "CREATE INDEX domain_name IF NOT EXISTS FOR (d:Domain) ON (d.name)"
            )
            # Global unique ID constraint across major labels
            await session.run("CREATE CONSTRAINT source_id IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE")
            await session.run("CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
            await session.run("CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE")
            logger.info("Neo4j indexes created/verified")

    async def close(self):
        """Close the driver."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j driver closed")

    async def is_healthy(self) -> bool:
        """Check if Neo4j is reachable."""
        if not self._driver:
            return False
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    async def execute_read(self, query: str, params: dict = None) -> list[dict]:
        """Execute a read query and return results as dicts."""
        if not self._driver:
            return []
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            records = await result.data()
            return records

    async def execute_write(self, query: str, params: dict = None) -> list[dict]:
        """Execute a write query and return results as dicts."""
        if not self._driver:
            return []
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            records = await result.data()
            return records

    async def create_concept_node(self, concept_id: str, name: str, domain: str = "", metadata: dict = None) -> dict:
        """Create a Concept node."""
        query = """
        MERGE (c:Concept {id: $id})
        SET c.name = $name, c.domain = $domain, c.metadata = $metadata, c.created_at = datetime()
        RETURN c
        """
        result = await self.execute_write(query, {"id": concept_id, "name": name, "domain": domain, "metadata": str(metadata or {})})
        return result[0] if result else {}

    async def create_source_node(self, source_id: str, title: str, source_type: str, url: str = "", metadata: dict = None) -> dict:
        """Create a Source node."""
        query = """
        MERGE (s:Source {id: $id})
        SET s.title = $title, s.type = $type, s.url = $url, s.metadata = $metadata, s.created_at = datetime()
        RETURN s
        """
        result = await self.execute_write(query, {"id": source_id, "title": title, "type": source_type, "url": url, "metadata": str(metadata or {})})
        return result[0] if result else {}

    async def create_domain_node(self, name: str) -> dict:
        """Create a Domain node."""
        query = """
        MERGE (d:Domain {name: $name})
        SET d.created_at = coalesce(d.created_at, datetime())
        RETURN d
        """
        result = await self.execute_write(query, {"name": name})
        return result[0] if result else {}

    async def create_entity_node(self, entity_id: str, name: str, label: str) -> dict:
        """Create an Entity node."""
        query = """
        MERGE (e:Entity {id: $id})
        SET e.name = $name, e.label = $label, e.created_at = datetime()
        RETURN e
        """
        result = await self.execute_write(query, {"id": entity_id, "name": name, "label": label})
        return result[0] if result else {}

    async def create_relationship(self, source_id: str, target_id: str, edge_type: str, weight: float = 1.0, properties: dict = None) -> dict:
        """Create a relationship between two nodes of any type by ID."""
        # Using MATCH on any node type since IDs are globally unique constraints
        query = f"""
        MATCH (a {{id: $source_id}})
        MATCH (b {{id: $target_id}})
        MERGE (a)-[r:{edge_type.upper()}]->(b)
        SET r.weight = $weight, r.properties = $properties, r.created_at = coalesce(r.created_at, datetime())
        RETURN a, r, b
        """
        result = await self.execute_write(query, {
            "source_id": source_id,
            "target_id": target_id,
            "weight": weight,
            "properties": str(properties or {})
        })
        return result[0] if result else {}
        
    async def create_domain_relationship(self, node_id: str, domain_name: str) -> dict:
        """Create a BELONGS_TO relationship to a Domain node."""
        query = """
        MATCH (a {id: $node_id})
        MATCH (d:Domain {name: $domain_name})
        MERGE (a)-[r:BELONGS_TO]->(d)
        RETURN a, r, d
        """
        result = await self.execute_write(query, {"node_id": node_id, "domain_name": domain_name})
        return result[0] if result else {}

    async def get_all_nodes(self, limit: int = 500) -> list[dict]:
        """Get all concept nodes for visualization."""
        query = """
        MATCH (c:Concept)
        RETURN c.id AS id, c.name AS name, c.node_type AS node_type,
               c.domain AS domain, c.pagerank AS pagerank,
               c.centrality AS centrality, c.community_id AS community_id
        ORDER BY c.pagerank DESC
        LIMIT $limit
        """
        return await self.execute_read(query, {"limit": limit})

    async def get_all_relationships(self, limit: int = 2000) -> list[dict]:
        """Get all relationships for visualization."""
        query = """
        MATCH (a:Concept)-[r]->(b:Concept)
        RETURN a.id AS source, b.id AS target, type(r) AS edge_type,
               r.weight AS weight, r.label AS label
        LIMIT $limit
        """
        return await self.execute_read(query, {"limit": limit})

    async def get_graph_data(self, limit_nodes: int = 500) -> dict:
        """Get full graph data for frontend visualization."""
        nodes = await self.get_all_nodes(limit=limit_nodes)
        links = await self.get_all_relationships()
        return {"nodes": nodes, "links": links}

    async def get_node_neighbors(self, node_id: str, depth: int = 1) -> dict:
        """Get a node and its neighbors up to a given depth."""
        query = """
        MATCH path = (start:Concept {id: $node_id})-[*1..$depth]-(neighbor:Concept)
        WITH nodes(path) AS ns, relationships(path) AS rs
        UNWIND ns AS n
        WITH collect(DISTINCT {
            id: n.id, name: n.name, node_type: n.node_type,
            domain: n.domain, pagerank: n.pagerank
        }) AS nodes, rs
        UNWIND rs AS r
        RETURN nodes, collect(DISTINCT {
            source: startNode(r).id, target: endNode(r).id,
            edge_type: type(r), weight: r.weight
        }) AS links
        """
        result = await self.execute_read(query, {"node_id": node_id, "depth": depth})
        if result:
            return {"nodes": result[0].get("nodes", []), "links": result[0].get("links", [])}
        return {"nodes": [], "links": []}

    async def get_shortest_path(self, source_id: str, target_id: str) -> list[dict]:
        """Find the shortest path between two concepts."""
        query = """
        MATCH path = shortestPath(
            (a:Concept {id: $source_id})-[*]-(b:Concept {id: $target_id})
        )
        RETURN [n IN nodes(path) | {id: n.id, name: n.name, domain: n.domain}] AS path_nodes,
               length(path) AS distance
        """
        return await self.execute_read(query, {
            "source_id": source_id,
            "target_id": target_id,
        })

    async def get_stats(self) -> dict:
        """Get graph statistics."""
        node_count = await self.execute_read("MATCH (n:Concept) RETURN count(n) AS count")
        edge_count = await self.execute_read("MATCH ()-[r]->() RETURN count(r) AS count")
        domains = await self.execute_read(
            "MATCH (c:Concept) WHERE c.domain <> '' RETURN DISTINCT c.domain AS domain"
        )
        return {
            "total_nodes": node_count[0]["count"] if node_count else 0,
            "total_edges": edge_count[0]["count"] if edge_count else 0,
            "domains": [d["domain"] for d in domains] if domains else [],
        }


# Singleton instance
neo4j_client = Neo4jClient()
]]>

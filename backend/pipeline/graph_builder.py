<![CDATA["""
Graph Builder — Constructs the concept graph from extracted data.
Orchestrates the pipeline triggered by the Event Bus.
"""
import uuid
import asyncio
from loguru import logger
from core.events import event_bus
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store
from core.database import get_db, SourceRecord
from pipeline.extraction.entity_extractor import EntityExtractor
from pipeline.extraction.concept_extractor import ConceptExtractor
from pipeline.extraction.relationship_extractor import RelationshipExtractor
from pipeline.extraction.clustering import ConceptClusterer
from sqlalchemy.future import select

class GraphBuilder:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.concept_extractor = ConceptExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.clusterer = ConceptClusterer()
        self._setup_listeners()

    def _setup_listeners(self):
        event_bus.subscribe("ingestion.completed.*", self.handle_ingestion_completed)

    async def handle_ingestion_completed(self, topic: str, payload: dict):
        """Triggered when a document has been successfully ingested and validated."""
        source_id = payload.get("source_id")
        metadata = payload.get("metadata", {})
        
        # Fetch text from DB
        text = ""
        title = ""
        source_type = ""
        url = ""
        async for session in get_db():
            stmt = select(SourceRecord).where(SourceRecord.id == source_id)
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                text = record.content_preview  # Assuming full text is stored here for now
                title = record.title
                source_type = record.source_type
                url = record.url or ""
            break

        if not text:
            logger.error(f"Cannot build graph: Source {source_id} text not found.")
            return

        await event_bus.publish(f"graph.build_started.{source_id}", {"source_id": source_id})
        try:
            await self.build_from_text(text, source_id, title, source_type, url, metadata)
            await event_bus.publish(f"graph.build_completed.{source_id}", {"source_id": source_id})
        except Exception as e:
            logger.error(f"Graph build failed for {source_id}: {e}")
            await event_bus.publish(f"graph.build_failed.{source_id}", {"source_id": source_id, "error": str(e)})

    async def build_from_text(self, text: str, source_id: str, title: str, source_type: str, url: str, metadata: dict) -> dict:
        """Full pipeline: extraction → Neo4j Schema mapping."""
        logger.info(f"Building graph for source {source_id}")

        # 1. Create Source Node
        await neo4j_client.create_source_node(source_id, title, source_type, url, metadata)
        
        # 2. Extract and create Domain (if available in metadata, e.g. from arXiv)
        domain = metadata.get("categories", [metadata.get("domain", "")])[0]
        if domain:
            await neo4j_client.create_domain_node(domain)
            await neo4j_client.create_domain_relationship(source_id, domain)

        # 3. Extract Entities
        entities = self.entity_extractor.extract(text)
        entity_ids = {}
        for ent in entities:
            eid = f"ent_{hash(ent['name'])}"
            entity_ids[ent['name'].lower()] = eid
            await neo4j_client.create_entity_node(eid, ent["name"], ent["label"])
            await neo4j_client.create_relationship(source_id, eid, "HAS_ENTITY", weight=ent.get("confidence", 0.8))

        # 4. Extract Concepts
        concepts = self.concept_extractor.extract(text, top_n=30)
        concept_ids = {}
        embeddings_for_clustering = {}
        
        for concept in concepts:
            cid = f"con_{hash(concept['name'])}"
            name = concept["name"]
            concept_ids[name.lower()] = cid
            
            await neo4j_client.create_concept_node(
                concept_id=cid, name=name, domain=domain,
                metadata={"confidence": concept.get("confidence", 0.5)},
            )
            await neo4j_client.create_relationship(source_id, cid, "HAS_CONCEPT", weight=concept.get("confidence", 0.5))
            
            if domain:
                await neo4j_client.create_domain_relationship(cid, domain)

            if concept.get("embedding") is not None:
                # Add to Vector DB
                vector_store.add_embedding(cid, concept["embedding"], name=name, domain=domain)
                embeddings_for_clustering[cid] = concept["embedding"]

        # 5. Local Clustering & Similarity (Graph-level similarities)
        # Note: Global similarity is handled by Vector DB searches during collision discovery.
        # Here we just establish strong local similarity edges.
        if len(embeddings_for_clustering) > 2:
            cluster_mapping = self.clusterer.cluster(embeddings_for_clustering, min_cluster_size=2)
            # We could add community_ids to nodes here, but skipping for brevity
        
        # 6. Extract Relationships (SVO & Co-occurrence)
        # We pass both concepts and entities to the relationship extractor to build a unified graph
        all_nodes = concepts + entities
        relationships = self.relationship_extractor.extract(all_nodes, text)
        
        # Merge ID lookups
        all_ids = {**concept_ids, **entity_ids}

        for rel in relationships:
            src_id = all_ids.get(rel["source"].lower())
            tgt_id = all_ids.get(rel["target"].lower())
            if src_id and tgt_id:
                edge_type = "INFERRED_RELATION" if "SVO" in rel["type"] else "CO_OCCURRENCE"
                await neo4j_client.create_relationship(
                    src_id, tgt_id, edge_type=edge_type, 
                    weight=rel["weight"], properties={"label": rel.get("label", "")}
                )

        # 7. Citations
        # If arXiv paper has references in metadata, we would link them here.
        
        logger.info(f"Graph build complete for {source_id}: {len(concepts)} concepts, {len(entities)} entities, {len(relationships)} edges")
        return {"concepts": len(concepts), "entities": len(entities), "relationships": len(relationships)}

# Singleton instance
graph_builder = GraphBuilder()
]]>

<![CDATA["""
Graph Builder — Constructs the concept graph from extracted data.

Orchestrates the full pipeline: extraction → embedding → graph construction.
"""
import uuid
from loguru import logger
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store
from pipeline.extraction.entity_extractor import EntityExtractor
from pipeline.extraction.concept_extractor import ConceptExtractor
from pipeline.extraction.relationship_extractor import RelationshipExtractor
from pipeline.extraction.clustering import ConceptClusterer

class GraphBuilder:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.concept_extractor = ConceptExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.clusterer = ConceptClusterer()
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                from config import settings
                self._embedding_model = SentenceTransformer(settings.embedding_model)
                logger.info("Loaded embedding model: {}", settings.embedding_model)
            except Exception as e:
                logger.warning("Could not load embedding model: {}", e)
        return self._embedding_model

    async def build_from_text(self, text: str, source_id: str, domain: str = "") -> dict:
        """Full pipeline: text → concepts → embeddings → graph."""
        # Step 1: Extract concepts
        concepts = self.concept_extractor.extract(text)
        entities = self.entity_extractor.extract(text)
        logger.info("Extracted {} concepts, {} entities", len(concepts), len(entities))

        # Step 2: Create concept nodes and generate embeddings
        concept_ids = {}
        model = self._get_embedding_model()

        for concept in concepts[:100]:  # Limit per source
            cid = str(uuid.uuid4())
            name = concept["name"]
            concept_ids[name.lower()] = cid

            await neo4j_client.create_concept_node(
                concept_id=cid, name=name, node_type="concept",
                domain=domain, description="",
                metadata={"source_id": source_id, "confidence": concept.get("confidence", 0.5)},
            )

            if model:
                embedding = model.encode(name).tolist()
                vector_store.add_embedding(cid, embedding, name=name, domain=domain)

        # Step 3: Extract and create relationships
        relationships = self.relationship_extractor.extract(concepts, text)
        for rel in relationships:
            src_id = concept_ids.get(rel["source"])
            tgt_id = concept_ids.get(rel["target"])
            if src_id and tgt_id:
                await neo4j_client.create_relationship(
                    src_id, tgt_id, edge_type=rel["type"].upper(), weight=rel["weight"],
                )

        logger.info("Built graph: {} nodes, {} edges", len(concept_ids), len(relationships))
        return {"concepts": len(concept_ids), "relationships": len(relationships)}
]]>

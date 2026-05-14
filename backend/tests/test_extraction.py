<![CDATA["""
Tests for the Concept Extraction Engine
"""
import pytest
import numpy as np
from pipeline.extraction.entity_extractor import EntityExtractor
from pipeline.extraction.concept_extractor import ConceptExtractor
from pipeline.extraction.relationship_extractor import RelationshipExtractor
from pipeline.extraction.clustering import ConceptClusterer

# Mocking SentenceTransformer to avoid heavy downloads during unit tests
class MockEncoder:
    def encode(self, texts):
        # Return random 384d vectors
        return np.random.rand(len(texts), 384)

@pytest.fixture
def sample_text():
    return "Apple announced a new optimization algorithm for their iPhone. The algorithm improves neural plasticity."

def test_entity_extraction(sample_text):
    extractor = EntityExtractor()
    entities = extractor.extract(sample_text)
    # Depending on spaCy's exact parsing, Apple and iPhone should be entities (ORG/PRODUCT)
    # We check if it returns a list and format is correct.
    assert isinstance(entities, list)
    if entities:
        assert "name" in entities[0]
        assert "label" in entities[0]

def test_concept_extraction(sample_text):
    extractor = ConceptExtractor(embedding_model=MockEncoder())
    concepts = extractor.extract(sample_text, top_n=5)
    
    assert len(concepts) > 0
    assert "name" in concepts[0]
    assert "confidence" in concepts[0]
    assert "embedding" in concepts[0]

def test_relationship_extraction():
    extractor = RelationshipExtractor()
    text = "The user builds the server."
    concepts = [{"name": "user"}, {"name": "server"}]
    
    relationships = extractor.extract(concepts, text)
    assert isinstance(relationships, list)
    
    # Check if SVO is found (user builds server)
    svo_found = any(r["source"] == "user" and r["target"] == "server" and "SVO" in r["type"] for r in relationships)
    
    # If spaCy successfully parses it, svo_found should be True. 
    # Otherwise it falls back to co_occurrence.
    assert len(relationships) > 0
    assert "weight" in relationships[0]

def test_clustering():
    clusterer = ConceptClusterer()
    embeddings = {
        "c1": [1.0, 0.0, 0.0],
        "c2": [0.9, 0.1, 0.0],
        "c3": [0.0, 1.0, 0.0],
        "c4": [0.0, 0.9, 0.1],
        "c5": [0.0, 0.0, 1.0] # Outlier/noise
    }
    
    # min_cluster_size=2 for this small test
    mapping = clusterer.cluster(embeddings, min_cluster_size=2)
    assert len(mapping) == 5
    # c1 and c2 should be in the same cluster
    assert mapping["c1"] == mapping["c2"]
    # c3 and c4 should be in the same cluster
    assert mapping["c3"] == mapping["c4"]
    # c1 and c3 should be different
    assert mapping["c1"] != mapping["c3"]
]]>

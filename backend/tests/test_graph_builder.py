<![CDATA["""
Tests for the Graph Builder Pipeline
"""
import pytest
import asyncio
from core.events import event_bus
from pipeline.graph_builder import GraphBuilder

# Mock Neo4j Client
class MockNeo4jClient:
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    async def create_source_node(self, *args, **kwargs):
        self.nodes.append(("Source", args[0]))
        
    async def create_domain_node(self, name):
        self.nodes.append(("Domain", name))
        
    async def create_entity_node(self, eid, name, label):
        self.nodes.append(("Entity", eid))
        
    async def create_concept_node(self, concept_id, name, **kwargs):
        self.nodes.append(("Concept", concept_id))
        
    async def create_relationship(self, src, tgt, edge_type, **kwargs):
        self.edges.append((src, edge_type, tgt))
        
    async def create_domain_relationship(self, node_id, domain_name):
        self.edges.append((node_id, "BELONGS_TO", domain_name))

@pytest.fixture
def mock_neo4j(monkeypatch):
    client = MockNeo4jClient()
    monkeypatch.setattr("pipeline.graph_builder.neo4j_client", client)
    return client

@pytest.mark.asyncio
async def test_graph_builder_pipeline(mock_neo4j):
    builder = GraphBuilder()
    
    text = "Apple released a new smartphone optimization algorithm in artificial intelligence."
    metadata = {"categories": ["cs.AI"]}
    
    # We directly test the build_from_text method to bypass DB dependencies in test
    result = await builder.build_from_text(
        text=text,
        source_id="src_123",
        title="Test Document",
        source_type="text",
        url="",
        metadata=metadata
    )
    
    # Check if correct Nodes were created
    node_types = [n[0] for n in mock_neo4j.nodes]
    assert "Source" in node_types
    assert "Domain" in node_types
    assert "Concept" in node_types
    
    # Check if correct Edges were created
    edge_types = [e[1] for e in mock_neo4j.edges]
    assert "HAS_CONCEPT" in edge_types
    assert "BELONGS_TO" in edge_types
    
    # Ensure it found relationships or entities
    assert result["concepts"] > 0
]]>

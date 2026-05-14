<![CDATA["""
Tests for the Event-Driven Document Ingestion Pipeline
"""
import pytest
import asyncio
from core.events import event_bus
from pipeline.ingestion.queue import IngestionQueue
from pipeline.ingestion.text_connector import TextConnector

@pytest.fixture
def queue():
    return IngestionQueue()

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    events_received = []
    
    async def handler(topic, payload):
        events_received.append((topic, payload))
        
    event_bus.subscribe("test.topic", handler)
    await event_bus.publish("test.topic", {"data": "test"})
    
    assert len(events_received) == 1
    assert events_received[0][0] == "test.topic"
    assert events_received[0][1]["data"] == "test"

@pytest.mark.asyncio
async def test_event_bus_wildcard_subscribe():
    events_received = []
    
    async def handler(topic, payload):
        events_received.append(topic)
        
    event_bus.subscribe("ingestion.*", handler)
    await event_bus.publish("ingestion.started.123", {})
    await event_bus.publish("ingestion.completed.123", {})
    
    assert len(events_received) == 2
    assert "ingestion.started.123" in events_received
    assert "ingestion.completed.123" in events_received

@pytest.mark.asyncio
async def test_text_connector_validation():
    connector = TextConnector()
    
    # Test valid text
    valid_text = "This is a sufficiently long text document for testing."
    meta = await connector.extract_metadata(valid_text)
    is_valid, msg = connector.validate(valid_text, meta)
    assert is_valid is True
    assert meta["word_count"] == 9
    
    # Test invalid text
    invalid_text = "short"
    meta = await connector.extract_metadata(invalid_text)
    is_valid, msg = connector.validate(invalid_text, meta)
    assert is_valid is False
    assert "too short" in msg
]]>

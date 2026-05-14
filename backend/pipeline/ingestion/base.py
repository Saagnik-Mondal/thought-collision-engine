<![CDATA["""
Thought Collision Engine — Base Ingestion Plugin Interface
"""
from abc import abstractmethod
from typing import Any, Tuple
from plugins.interfaces import IngestionPlugin

class BaseConnector(IngestionPlugin):
    """Abstract base class for ingestion connectors acting as plugins."""
    name: str = "base"
    description: str = "Base connector interface"
    supported_types: list[str] = []

    @abstractmethod
    async def ingest(self, source: Any, **kwargs) -> str:
        """Extract main text content from source."""
        pass

    @abstractmethod
    async def extract_metadata(self, source: Any, **kwargs) -> dict:
        """Extract rich metadata (author, date, etc.) from source."""
        pass

    def validate(self, text: str, metadata: dict) -> Tuple[bool, str]:
        """Validate the extracted content and metadata."""
        if not text or len(text.strip()) < 10:
            return False, "Extracted text is too short or empty."
        return True, "Valid"
]]>

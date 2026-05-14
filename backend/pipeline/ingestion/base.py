<![CDATA["""
Base ingestion connector interface — all connectors inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Any

class BaseConnector(ABC):
    """Abstract base class for ingestion connectors."""
    name: str = "base"
    supported_types: list[str] = []

    @abstractmethod
    async def ingest(self, source: Any) -> dict:
        """Ingest a source and return extracted text + metadata."""
        pass
]]>

<![CDATA["""
Plugin Interfaces — Define what plugins must implement.
"""
from abc import ABC, abstractmethod
from typing import Any

class GraphAlgorithmPlugin(ABC):
    name: str
    description: str
    @abstractmethod
    async def execute(self, neo4j_client: Any, **kwargs) -> Any: pass

class CollisionAlgorithmPlugin(ABC):
    name: str
    description: str
    @abstractmethod
    async def discover(self, **kwargs) -> list[dict]: pass

class EmbeddingPlugin(ABC):
    name: str
    description: str
    @abstractmethod
    def encode(self, texts: list[str]) -> Any: pass

class IngestionPlugin(ABC):
    name: str
    description: str
    supported_types: list[str]
    @abstractmethod
    async def ingest(self, source: Any) -> dict: pass

class ScoringPlugin(ABC):
    name: str
    description: str
    weight: float = 0.2
    @abstractmethod
    def score(self, collision: dict) -> float: pass
]]>

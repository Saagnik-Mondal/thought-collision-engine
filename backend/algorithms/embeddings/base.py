<![CDATA["""
Base Embedding Provider Interface.
"""
from abc import ABC, abstractmethod
import numpy as np

class BaseEmbeddingProvider(ABC):
    name: str = "base"

    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        pass

    @abstractmethod
    def encode_single(self, text: str) -> list[float]:
        """Encode a single text into an embedding vector."""
        pass
]]>

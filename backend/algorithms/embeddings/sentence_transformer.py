<![CDATA["""
Sentence Transformer Embedding Provider.
"""
import numpy as np
from loguru import logger
from algorithms.embeddings.base import BaseEmbeddingProvider

class SentenceTransformerProvider(BaseEmbeddingProvider):
    name = "sentence_transformer"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = None
        self._model_name = model_name

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            logger.info("Loaded SentenceTransformer: {}", self._model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        self._load()
        return self._model.encode(texts, show_progress_bar=False)

    def encode_single(self, text: str) -> list[float]:
        self._load()
        return self._model.encode(text).tolist()
]]>

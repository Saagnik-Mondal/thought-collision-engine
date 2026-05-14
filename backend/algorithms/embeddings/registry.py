<![CDATA["""
Embedding Provider Registry — Manage pluggable embedding providers.
"""
from algorithms.embeddings.base import BaseEmbeddingProvider
from algorithms.embeddings.sentence_transformer import SentenceTransformerProvider

class EmbeddingRegistry:
    def __init__(self):
        self._providers: dict[str, BaseEmbeddingProvider] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(SentenceTransformerProvider())

    def register(self, provider: BaseEmbeddingProvider):
        self._providers[provider.name] = provider

    def get(self, name: str) -> BaseEmbeddingProvider:
        if name not in self._providers:
            raise ValueError(f"Unknown embedding provider: {name}")
        return self._providers[name]

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

embedding_registry = EmbeddingRegistry()
]]>

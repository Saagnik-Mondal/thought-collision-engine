<![CDATA["""
Thought Collision Engine — Custom Exceptions
"""


class TCEError(Exception):
    """Base exception for the Thought Collision Engine."""
    pass


class IngestionError(TCEError):
    """Raised when document ingestion fails."""
    pass


class ExtractionError(TCEError):
    """Raised when concept extraction fails."""
    pass


class GraphError(TCEError):
    """Raised when graph operations fail."""
    pass


class CollisionError(TCEError):
    """Raised when collision discovery fails."""
    pass


class PluginError(TCEError):
    """Raised when a plugin fails to load or execute."""
    pass


class VectorStoreError(TCEError):
    """Raised when vector store operations fail."""
    pass
]]>

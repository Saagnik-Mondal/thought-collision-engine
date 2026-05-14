<![CDATA["""
Base Algorithm Interface — All algorithms inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Any

class BaseAlgorithm(ABC):
    """Abstract base for all pluggable algorithms."""
    name: str = "base"
    description: str = ""
    version: str = "0.1.0"

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the algorithm."""
        pass

    def get_info(self) -> dict:
        return {"name": self.name, "description": self.description, "version": self.version}
]]>

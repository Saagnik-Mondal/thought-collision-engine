<![CDATA["""
Thought Collision Engine — Plugins API Routes
"""
from fastapi import APIRouter
from plugins.manager import plugin_manager

router = APIRouter()

@router.get("/")
async def list_plugins():
    """List all registered plugins."""
    return plugin_manager.list_plugins()

@router.get("/types")
async def list_plugin_types():
    """List available plugin types."""
    return ["graph_algorithm", "collision_algorithm", "embedding_provider", "ingestion_connector", "scoring_component"]

@router.post("/reload")
async def reload_plugins():
    """Reload all plugins from the contrib directory."""
    plugin_manager.reload()
    return {"status": "reloaded", "plugins": plugin_manager.list_plugins()}
]]>

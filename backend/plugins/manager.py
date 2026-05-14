<![CDATA["""
Plugin Manager — Discovers, loads, and manages plugins.
"""
import importlib, os
from pathlib import Path
from loguru import logger

class PluginManager:
    def __init__(self):
        self._plugins: dict[str, dict] = {}
        self._contrib_dir = Path(__file__).parent / "contrib"

    def reload(self):
        """Reload plugins from the contrib directory."""
        self._plugins.clear()
        if not self._contrib_dir.exists():
            return
        for f in self._contrib_dir.glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(f.stem, f)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    plugin_info = mod.register()
                    self._plugins[plugin_info["name"]] = plugin_info
                    logger.info("Loaded plugin: {}", plugin_info["name"])
            except Exception as e:
                logger.error("Failed to load plugin {}: {}", f.name, e)

    def list_plugins(self) -> list[dict]:
        return [{"name": k, **v} for k, v in self._plugins.items()]

    def get_plugin(self, name: str):
        return self._plugins.get(name)

plugin_manager = PluginManager()
]]>

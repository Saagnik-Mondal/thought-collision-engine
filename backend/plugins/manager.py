<![CDATA["""
Plugin Manager — Discovers, loads, and manages algorithms and connectors.
"""
import importlib, os
from pathlib import Path
from loguru import logger
import inspect

class PluginManager:
    """
    Handles dynamic discovery and instantiation of plugins dropped into the 'contrib' folder.
    Ensures that plugins implement the expected interface.
    """
    def __init__(self):
        self._plugins: dict[str, dict] = {}
        self._contrib_dir = Path(__file__).parent / "contrib"

    def reload(self):
        """
        Reload plugins from the contrib directory.
        Iterates over all python files, looking for a 'register' method.
        """
        self._plugins.clear()
        if not self._contrib_dir.exists():
            logger.warning(f"Contrib directory {self._contrib_dir} not found.")
            return

        for f in self._contrib_dir.glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                # Dynamically load the module
                spec = importlib.util.spec_from_file_location(f.stem, f)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                
                if hasattr(mod, "register"):
                    # Basic validation of the register method
                    if not inspect.isroutine(mod.register):
                        logger.error(f"Plugin {f.name} 'register' is not a callable routine.")
                        continue
                        
                    plugin_info = mod.register()
                    
                    if "name" not in plugin_info or "instance" not in plugin_info:
                        logger.error(f"Plugin {f.name} returned invalid metadata. Missing 'name' or 'instance'.")
                        continue
                        
                    self._plugins[plugin_info["name"]] = plugin_info
                    logger.info(f"Successfully loaded plugin: {plugin_info['name']}")
                else:
                    logger.debug(f"File {f.name} ignored: No 'register' method found.")
            except Exception as e:
                logger.error(f"Failed to load plugin {f.name} due to an exception: {e}")

    def list_plugins(self) -> list[dict]:
        """Return a list of all currently loaded plugins and their metadata."""
        return [{"name": k, **v} for k, v in self._plugins.items()]

    def get_plugin(self, name: str):
        """Retrieve a specific plugin's metadata by name."""
        return self._plugins.get(name)

plugin_manager = PluginManager()
]]>

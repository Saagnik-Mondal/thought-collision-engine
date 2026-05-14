<![CDATA[# Plugin Contributions

Place your plugin files here. Each plugin should be a `.py` file with a `register()` function.

## Example Plugin

```python
# my_algorithm.py

from plugins.interfaces import GraphAlgorithmPlugin

class MyCustomAlgorithm(GraphAlgorithmPlugin):
    name = "my_algorithm"
    description = "A custom graph algorithm"

    async def execute(self, neo4j_client, **kwargs):
        # Your algorithm here
        pass

def register():
    return {
        "name": "my_algorithm",
        "type": "graph_algorithm",
        "description": "A custom graph algorithm",
        "instance": MyCustomAlgorithm(),
    }
```
]]>

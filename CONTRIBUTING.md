<![CDATA[# Contributing to Thought Collision Engine

Thank you for contributing! We actively welcome PRs for new Ingestion Connectors, Discovery Algorithms, and UI components.

## Local Development Setup
1. Clone the repository.
2. Ensure Docker Desktop is running.
3. Run `docker-compose up -d` to spin up Neo4j, PostgreSQL, Qdrant, and the Python Backend.
4. The API will be available at `http://localhost:8000/docs`.

## Adding a New Ingestion Plugin
You can add support for new data sources (e.g., Notion, Slack, Obsidian) by creating a plugin in `backend/plugins/contrib/`.

1. Create a class that inherits from `backend.pipeline.ingestion.base.BaseConnector`.
2. Implement `ingest(source)` and `extract_metadata(source)`.
3. Provide a module-level `register()` method that returns your class instance.

Example:
```python
from pipeline.ingestion.base import BaseConnector

class NotionConnector(BaseConnector):
    name = "notion"
    supported_types = ["notion_url"]

    async def ingest(self, source, **kwargs):
        return "Extract text from notion API here"

    async def extract_metadata(self, source, **kwargs):
        return {"author": "Workspace User"}

def register():
    return {"name": "notion_connector", "instance": NotionConnector()}
```

## Adding a New Discovery Algorithm
If you want to test a new way of discovering collisions (e.g., Jaccard Similarity on Sub-graphs):
1. Create your algorithm in `backend/algorithms/graph_algorithms/`.
2. Modify `backend/experiments/runner.py` to include your algorithm in the benchmarking pipeline.
3. Run `python backend/experiments/runner.py` to see if your algorithm produces more novel collisions than the current composite engine!

## Pull Request Guidelines
- All new algorithms must include `pytest` unit tests in `backend/tests/`.
- Do not introduce synchronous blocking code into the FastAPI routes or EventBus listeners.
- Keep ML models local. Do not add paid API dependencies (e.g., OpenAI) without providing an open-source fallback.
]]>

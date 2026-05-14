<![CDATA["""
Thought Collision Engine — Root API Router

Aggregates all route modules into a single router.
"""

from fastapi import APIRouter

from api.routes import ingest, concepts, collisions, hypotheses, graph, experiments, plugins

api_router = APIRouter()

api_router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
api_router.include_router(concepts.router, prefix="/concepts", tags=["Concepts"])
api_router.include_router(collisions.router, prefix="/collisions", tags=["Collisions"])
api_router.include_router(hypotheses.router, prefix="/hypotheses", tags=["Hypotheses"])
api_router.include_router(graph.router, prefix="/graph", tags=["Graph"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])
]]>

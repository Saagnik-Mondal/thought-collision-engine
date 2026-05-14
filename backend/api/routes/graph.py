<![CDATA["""
Thought Collision Engine — Graph API Routes
"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_neo4j
from core.neo4j_client import Neo4jClient
from core.models import GraphData, GraphNode, GraphLink

router = APIRouter()

DOMAIN_COLORS = {
    "biology": "#10b981", "computer_science": "#3b82f6", "physics": "#8b5cf6",
    "mathematics": "#f59e0b", "chemistry": "#ef4444", "engineering": "#06b6d4",
    "economics": "#f97316", "philosophy": "#ec4899", "medicine": "#14b8a6",
    "psychology": "#a855f7", "neuroscience": "#6366f1", "ecology": "#22c55e",
}

@router.get("/data", response_model=GraphData)
async def get_graph_data(limit: int = Query(300, ge=1, le=1000), neo4j: Neo4jClient = Depends(get_neo4j)):
    """Get full graph data for visualization."""
    data = await neo4j.get_graph_data(limit_nodes=limit)
    nodes = [GraphNode(id=n["id"], name=n["name"], node_type=n.get("node_type","concept"),
        domain=n.get("domain",""), val=max(1, (n.get("pagerank",0) or 0) * 100),
        color=DOMAIN_COLORS.get(n.get("domain",""), "#64748b"),
        community_id=n.get("community_id"), pagerank=n.get("pagerank",0) or 0) for n in data["nodes"]]
    links = [GraphLink(source=l["source"], target=l["target"],
        edge_type=l.get("edge_type",""), weight=l.get("weight",1) or 1,
        label=l.get("label","")) for l in data["links"]]
    stats = await neo4j.get_stats()
    return GraphData(nodes=nodes, links=links, stats=stats)

@router.get("/neighbors/{node_id}")
async def get_neighbors(node_id: str, depth: int = Query(1, ge=1, le=3), neo4j: Neo4jClient = Depends(get_neo4j)):
    """Get subgraph around a node."""
    return await neo4j.get_node_neighbors(node_id, depth=depth)

@router.get("/path")
async def get_shortest_path(source_id: str, target_id: str, neo4j: Neo4jClient = Depends(get_neo4j)):
    """Find shortest path between two concepts."""
    return await neo4j.get_shortest_path(source_id, target_id)

@router.get("/stats")
async def get_graph_stats(neo4j: Neo4jClient = Depends(get_neo4j)):
    """Get graph statistics."""
    return await neo4j.get_stats()
]]>

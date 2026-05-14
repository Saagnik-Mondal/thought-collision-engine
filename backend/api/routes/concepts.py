<![CDATA["""
Thought Collision Engine — Concepts API Routes

CRUD and search for concept nodes in the knowledge graph.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from api.deps import get_neo4j, get_vector_store
from core.models import Concept, ConceptCreate, PaginatedResponse
from core.neo4j_client import Neo4jClient
from core.vector_store import VectorStore

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_concepts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str = Query("", description="Filter by domain"),
    search: str = Query("", description="Search by name"),
    neo4j: Neo4jClient = Depends(get_neo4j),
):
    """List concepts with pagination and filtering."""
    skip = (page - 1) * page_size

    # Build query
    where_clauses = []
    params = {"skip": skip, "limit": page_size}

    if domain:
        where_clauses.append("c.domain = $domain")
        params["domain"] = domain

    if search:
        where_clauses.append("toLower(c.name) CONTAINS toLower($search)")
        params["search"] = search

    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    MATCH (c:Concept) {where}
    RETURN c.id AS id, c.name AS name, c.node_type AS node_type,
           c.domain AS domain, c.description AS description,
           c.pagerank AS pagerank, c.centrality AS centrality,
           c.community_id AS community_id
    ORDER BY c.pagerank DESC
    SKIP $skip LIMIT $limit
    """
    concepts = await neo4j.execute_read(query, params)

    count_query = f"MATCH (c:Concept) {where} RETURN count(c) AS total"
    count_result = await neo4j.execute_read(count_query, params)
    total = count_result[0]["total"] if count_result else 0

    items = [
        Concept(
            id=c["id"],
            name=c["name"],
            node_type=c.get("node_type", "concept"),
            domain=c.get("domain", ""),
            description=c.get("description", ""),
            pagerank=c.get("pagerank", 0) or 0,
            centrality=c.get("centrality", 0) or 0,
            community_id=c.get("community_id"),
        )
        for c in concepts
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/domains", response_model=list[str])
async def list_domains(neo4j: Neo4jClient = Depends(get_neo4j)):
    """List all unique domains."""
    result = await neo4j.execute_read(
        "MATCH (c:Concept) WHERE c.domain <> '' RETURN DISTINCT c.domain AS domain ORDER BY domain"
    )
    return [r["domain"] for r in result]


@router.get("/search")
async def search_concepts(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    neo4j: Neo4jClient = Depends(get_neo4j),
):
    """Full-text search for concepts."""
    query = """
    MATCH (c:Concept)
    WHERE toLower(c.name) CONTAINS toLower($search)
       OR toLower(c.description) CONTAINS toLower($search)
    RETURN c.id AS id, c.name AS name, c.node_type AS node_type,
           c.domain AS domain, c.description AS description
    LIMIT $limit
    """
    results = await neo4j.execute_read(query, {"search": q, "limit": limit})
    return results


@router.get("/{concept_id}")
async def get_concept(
    concept_id: str,
    neo4j: Neo4jClient = Depends(get_neo4j),
):
    """Get a single concept by ID."""
    query = """
    MATCH (c:Concept {id: $id})
    RETURN c.id AS id, c.name AS name, c.node_type AS node_type,
           c.domain AS domain, c.description AS description,
           c.pagerank AS pagerank, c.centrality AS centrality,
           c.community_id AS community_id
    """
    result = await neo4j.execute_read(query, {"id": concept_id})
    if not result:
        raise HTTPException(status_code=404, detail="Concept not found")
    return result[0]


@router.get("/{concept_id}/neighbors")
async def get_concept_neighbors(
    concept_id: str,
    depth: int = Query(1, ge=1, le=3),
    neo4j: Neo4jClient = Depends(get_neo4j),
):
    """Get a concept and its neighboring nodes."""
    return await neo4j.get_node_neighbors(concept_id, depth=depth)


@router.get("/{concept_id}/similar")
async def get_similar_concepts(
    concept_id: str,
    limit: int = Query(10, ge=1, le=50),
    vs: VectorStore = Depends(get_vector_store),
):
    """Find semantically similar concepts using embeddings."""
    embedding = vs.get_embedding(concept_id)
    if not embedding:
        raise HTTPException(status_code=404, detail="No embedding found for this concept")

    similar = vs.query_similar(embedding, n_results=limit + 1)
    # Filter out the concept itself
    return [s for s in similar if s["id"] != concept_id][:limit]
]]>

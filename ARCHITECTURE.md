<![CDATA[# Thought Collision Engine — Architecture

## Overview
The Thought Collision Engine is an event-driven system designed to discover highly novel, "weakly connected" concepts between distant domains. 
It ingests diverse documents, maps them structurally into Neo4j and semantically into Qdrant, and runs heavy graph and math algorithms to benchmark novel collisions.

## Core Pipelines

### 1. Event-Driven Ingestion
Documents (PDFs, URLs, arXiv IDs, GitHub Repos) hit the FastAPI endpoints, which immediately respond with `202 Pending` and offload the task to the `IngestionQueue`.
The Queue invokes `IngestionPlugins` to extract raw text and rich metadata, publishing status events to the asynchronous `EventBus`.

### 2. Extraction Engine
Triggered by `ingestion.completed.*`. The text is processed:
- **Entity Extractor:** Uses `spaCy` NER to find specific real-world nouns.
- **Concept Extractor:** Uses `spaCy` Noun Chunks + `SentenceTransformers` to pull "Keywords" via Cosine Similarity against the document.
- **Relationship Extractor:** Uses `spaCy` Dependency Parsing to find explicit Subject-Verb-Object (SVO) logical links.
- **Clustering:** Uses `HDBSCAN` on the generated vectors to group connected concepts.

### 3. Graph Construction
Outputs from extraction are mapped to specific Graph Schemas:
- **Neo4j:** Nodes (`Source`, `Concept`, `Entity`, `Domain`). Edges (`HAS_CONCEPT`, `HAS_ENTITY`, `INFERRED_RELATION`, `CO_OCCURRENCE`).
- **Qdrant:** Dense 384-dimensional vectors stored for semantic retrieval.

### 4. Collision Discovery
Replaces naive $O(n^2)$ pairing with a scalable seed strategy:
1. **Centrality Seeding:** Neo4j PageRank algorithm runs in the background. The engine picks top concepts.
2. **Semantic Candidates:** Qdrant is queried for "Sweet Spot" semantic matches (Cosine similarity 0.4 - 0.7).
3. **Graph Evaluation:** Candidates are scored on structural distance (Shortest Path) and reachability (Random Walks).
4. **Bridge Detection:** Louvain Community detection checks if the candidates cross a major knowledge divide.

### 5. Novelty Score Engine
The final analytical layer that breaks down a collision into 5 explicit metrics:
- **Semantic Distance**
- **Rarity** (Inverse PageRank)
- **Graph Separation** (Shortest Path)
- **Citation Uniqueness** (Shared Source nodes)
- **Concept Diversity** (Jaccard Distance of 1-hop Domain Neighborhoods)

It then translates these math scores into human-readable explainability text.
]]>

<![CDATA[# 🧠 Thought Collision Engine

> Discover hidden relationships between ideas across unrelated domains. Generate novel hypotheses, startup concepts, research directions, and algorithmic insights.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)

---

## What is This?

This is **NOT** a chatbot, RAG app, recommendation system, or "chat with PDFs."

The Thought Collision Engine identifies **unexpected conceptual collisions** between distant fields and ranks them by **novelty** and **usefulness**.

### Example Output

```
🔬 Collision Candidate

Domain A: Immune Systems
Domain B: Distributed Networks

Reasoning:
Immune systems detect and isolate failures dynamically.
Distributed systems struggle with self-healing and fault detection.

💡 Novel Hypothesis:
Build adaptive node trust systems inspired by biological immune responses.

Novelty Score:  92/100  ████████████████████░░
Confidence:     78/100  ███████████████░░░░░░░
```

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│   FastAPI     │────▶│   Neo4j     │
│  React + TS  │     │   Backend    │     │  Graph DB   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼────┐  ┌─────▼──────┐
              │ ChromaDB  │  │ PostgreSQL │
              │ Vectors   │  │ Metadata   │
              └──────────┘  └────────────┘
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/thought-collision-engine.git
cd thought-collision-engine

# Start all services
docker-compose up -d

# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

---

## Features

- 📥 **Multi-source Ingestion** — PDFs, arXiv papers, URLs, GitHub repos, text documents
- 🧬 **Concept Extraction** — NLP-powered entity, concept, and relationship extraction
- 🕸️ **Dynamic Knowledge Graph** — Interactive force-directed graph visualization
- 💥 **Collision Discovery** — Find hidden connections between distant domains
- 📊 **Novelty Scoring** — Modular, configurable scoring system
- 💡 **Hypothesis Generation** — Startup ideas, research hypotheses, cross-domain insights
- 🧪 **Experiment System** — Compare algorithms, embeddings, and scoring methods
- 🔌 **Plugin Architecture** — Extend everything: algorithms, connectors, embeddings, scorers

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| Frontend | React 19, TypeScript, Vite |
| Visualization | react-force-graph, D3.js |
| Backend | Python, FastAPI, Pydantic v2 |
| Graph DB | Neo4j |
| Vector DB | ChromaDB |
| Relational DB | PostgreSQL |
| NLP | spaCy, Sentence-Transformers |
| Containers | Docker, docker-compose |

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.
]]>

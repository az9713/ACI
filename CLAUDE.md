# CLAUDE.md - Instructions for Claude Code

This file provides context and instructions for Claude Code when working with this project.

## Project Overview

ACI (Agent-Computer-Interaction) is an MCP server that provides a scientific knowledge graph. It allows AI agents to:
- Store and retrieve scientific propositions (atomic units)
- Build relationships between concepts
- Search semantically across the knowledge base
- Trace intellectual lineages between ideas
- Detect contradictions in accumulated knowledge

## Tech Stack

- **Python 3.10+** - Primary language
- **MCP SDK** (`mcp`) - Protocol for Claude integration using FastMCP
- **LanceDB** - Vector database for semantic search (stored in `data/atomic_graph.lance/`)
- **NetworkX** - In-memory directed graph for pathfinding
- **OpenAI API** - For generating text embeddings (text-embedding-ada-002)
- **Pydantic** - Data validation and serialization

## Project Structure

```
ACI/
├── src/
│   ├── __init__.py       # Package marker
│   ├── server.py         # MCP server with 7 tools (entry point)
│   ├── model.py          # Pydantic models (AtomicUnit, Relation, responses)
│   ├── graph_engine.py   # KnowledgeGraph class (LanceDB + NetworkX)
│   └── persistence.py    # JSON persistence for relations and idempotency
├── data/                 # Runtime data directory
│   ├── atomic_graph.lance/  # LanceDB vector storage
│   ├── relations.json       # Graph edges
│   └── idempotency.json     # Idempotency key cache
├── docs/                 # Documentation
├── .mcp.json            # Project-scope MCP configuration
├── .env                 # Environment variables (OPENAI_API_KEY)
└── pyproject.toml       # Python project configuration
```

## Key Files

### src/server.py
The MCP server entry point. Defines 7 tools:
- `ingest_hypothesis` - Add new propositions
- `connect_propositions` - Create relationships
- `semantic_search` - Vector similarity search
- `find_scientific_lineage` - Path finding between concepts
- `find_contradictions` - Conflict detection
- `list_propositions` - Browse knowledge base
- `get_unit` - Get single unit details

### src/graph_engine.py
Core `KnowledgeGraph` class that:
- Manages LanceDB table for vector storage
- Maintains NetworkX DiGraph for relationships
- Handles embedding generation via OpenAI
- Provides search, pathfinding, and conflict detection

### src/model.py
Pydantic models:
- `AtomicUnit` - Core proposition with content, source, confidence, vector
- `Relation` - Edge with source_id, target_id, type, reasoning
- Response models with HATEOAS `available_actions`

### src/persistence.py
`PersistenceManager` for:
- Relations storage (`relations.json`)
- Idempotency cache (`idempotency.json`)
- Load/save with datetime handling

## Development Commands

```bash
# Install dependencies
uv sync

# Run the server directly
uv run python src/server.py

# Test imports
uv run python -c "from src.server import mcp; print(mcp.name)"

# Add to Claude Code
claude mcp add --transport stdio atomic-graph -- uv run python src/server.py
```

## Architecture Patterns

### HATEOAS for Agents
All responses include `available_actions` suggesting what the agent can do next:
```python
{
    "result": {...},
    "available_actions": [
        {"tool": "semantic_search", "description": "Find related concepts"},
        {"tool": "connect_propositions", "description": "Link to another unit"}
    ]
}
```

### Idempotency Keys
Write operations accept `idempotency_key` to prevent duplicate actions on retry:
```python
ingest_hypothesis("claim", source="paper", idempotency_key="unique-key-123")
```

### Lazy Graph Initialization
The `KnowledgeGraph` is initialized lazily via `get_graph()` to allow environment setup.

## Common Development Tasks

### Adding a New Tool
1. Add the function in `src/server.py` with `@mcp.tool()` decorator
2. Write a comprehensive docstring (Claude uses this to decide when to use the tool)
3. Return dict with `status`, result data, and `available_actions`

### Adding a New Model
1. Define Pydantic model in `src/model.py`
2. Add to response models if needed
3. Update graph engine if it needs to store/retrieve

### Modifying the Graph Schema
1. Update `AtomicUnit` model in `src/model.py`
2. Update LanceDB schema in `graph_engine._init_table()`
3. Update serialization in `add_proposition()` and retrieval methods

## Testing

Currently no automated tests. To test manually:
1. Set `OPENAI_API_KEY` environment variable
2. Run server: `uv run python src/server.py`
3. Use MCP Inspector or Claude Desktop to test tools

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings |

## Known Limitations

1. **No batch operations** - Each proposition is ingested individually
2. **In-memory graph** - NetworkX graph is rebuilt from JSON on startup
3. **Single embedding model** - Hard-coded to text-embedding-ada-002
4. **No authentication** - Designed for local/personal use

## Future Enhancement Ideas

1. Add batch ingestion for papers
2. Add graph visualization endpoint
3. Support multiple embedding models
4. Add unit tests with mocked embeddings
5. Add export/import functionality
6. Add tagging/categorization

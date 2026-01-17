# ACI - Agent-Computer-Interaction Knowledge Graph

A headless MCP (Model Context Protocol) server that enables AI agents like Claude to read, write, and reason over a knowledge graph of scientific propositions. Think of it as a "second brain" for research that Claude can directly interact with.

## What Does This Project Do?

ACI allows you to:
- **Store scientific claims** as atomic units in a searchable knowledge graph
- **Find relationships** between concepts using semantic (meaning-based) search
- **Trace intellectual lineages** - how one idea led to another
- **Detect contradictions** - find where new claims conflict with existing knowledge
- **Build a research graph** - connect related ideas with explicit reasoning

## Who Is This For?

- **Researchers** who want Claude to help manage their knowledge base
- **Students** building literature reviews or thesis research
- **Anyone** who accumulates scientific knowledge and wants AI-assisted organization

## Quick Start (5 Minutes)

### Prerequisites

Before you begin, you need:
1. **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
2. **uv** (Python package manager) - Install with: `pip install uv`
3. **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
4. **Claude Code** or **Claude Desktop** - For interacting with the MCP server

### Step 1: Clone or Download This Project

```bash
# If using git:
git clone <repository-url>
cd ACI

# Or download and extract the ZIP file, then:
cd path/to/ACI
```

### Step 2: Set Your OpenAI API Key

Create a `.env` file in the project root:

```bash
# Windows (PowerShell)
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env

# Windows (Command Prompt)
echo OPENAI_API_KEY=sk-your-actual-api-key-here > .env

# Linux/Mac
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
```

Replace `sk-your-actual-api-key-here` with your actual OpenAI API key.

### Step 3: Install Dependencies

```bash
uv sync
```

This downloads and installs all required Python packages.

### Step 4: Add to Claude Code

```bash
claude mcp add --transport stdio atomic-graph -- uv run python src/server.py
```

### Step 5: Start Using!

Start a Claude Code session by running:

```bash
claude
```

Then try:
```
"Ingest a hypothesis that transformer attention mechanisms scale quadratically with sequence length"
```

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | 12 hands-on use cases to learn the system |
| [Advanced Examples](docs/ADVANCED_EXAMPLES.md) | 15 power-user scenarios: discover hidden connections, generate hypotheses, uncover "new facts" |
| [User Guide](docs/USER_GUIDE.md) | Complete user documentation |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | For developers extending the system |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [CLAUDE.md](CLAUDE.md) | Instructions for Claude Code |

## Available Tools

Once configured, Claude can use these tools:

| Tool | Purpose |
|------|---------|
| `ingest_hypothesis` | Add a new scientific claim to the knowledge graph |
| `connect_propositions` | Create relationships between claims |
| `semantic_search` | Find related concepts by meaning |
| `find_scientific_lineage` | Trace how one idea connects to another |
| `find_contradictions` | Check if a claim conflicts with existing knowledge |
| `list_propositions` | Browse all stored claims |
| `get_unit` | Get details of a specific claim |
| `delete_unit` | Remove a claim and its connections (requires confirmation) |

## Project Structure

```
ACI/
├── src/
│   ├── __init__.py       # Package marker
│   ├── server.py         # MCP server entry point (8 tools)
│   ├── model.py          # Pydantic data models
│   ├── graph_engine.py   # Knowledge graph logic (LanceDB + NetworkX)
│   └── persistence.py    # JSON persistence for relations and idempotency
├── tests/
│   ├── test_quick_start.py      # 12 use cases from Quick Start guide
│   └── test_advanced_examples.py # 8 advanced scenarios
├── data/                 # Stored knowledge (auto-created)
│   ├── atomic_graph.lance/  # LanceDB vector storage
│   ├── relations.json       # Graph edges
│   └── idempotency.json     # Idempotency cache
├── docs/                 # Documentation
├── .env                  # API keys (create this - see below)
├── .mcp.json            # MCP configuration
└── pyproject.toml       # Python dependencies
```

## Testing

ACI includes comprehensive automated tests that verify all documented functionality:

```bash
# Run Quick Start use cases (12 tests)
uv run python tests/test_quick_start.py

# Run Advanced Examples (8 scenarios)
uv run python tests/test_advanced_examples.py
```

### Test Results Summary

**Quick Start Tests** (12/12 passing):
- Hypothesis ingestion with sources
- Knowledge cluster building
- Semantic connections
- Natural language search
- Unit exploration
- Intellectual lineage tracing
- Contradiction detection
- Cross-domain knowledge linking

**Advanced Examples Tests** (8/8 passing):
- Hidden connection discovery (Sleep → Creativity)
- Hypothesis generation (Drug repurposing)
- Research gap identification (Climate feedback)
- Implicit contradiction uncovering (Economics)
- Cross-domain innovation (Biology → Cybersecurity)
- Emergent pattern discovery (Power laws)
- "Aha!" moment generation (Urban resilience)
- Historical idea archaeology (Internet origins)

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See the `/docs` folder for detailed guides

## License

[Add your license here]

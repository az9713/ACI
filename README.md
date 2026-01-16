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

Open Claude Code and try:
```
"Ingest a hypothesis that transformer attention mechanisms scale quadratically with sequence length"
```

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | 10 hands-on use cases to learn the system |
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

## Project Structure

```
ACI/
├── src/
│   ├── server.py         # MCP server entry point
│   ├── model.py          # Data models
│   ├── graph_engine.py   # Knowledge graph logic
│   └── persistence.py    # Data storage
├── data/                 # Stored knowledge (auto-created)
├── docs/                 # Documentation
├── .mcp.json            # MCP configuration
└── pyproject.toml       # Python dependencies
```

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See the `/docs` folder for detailed guides

## License

[Add your license here]

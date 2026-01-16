# Architecture Overview

This document explains how ACI works at both a high level and in technical detail. It's designed for developers with traditional programming backgrounds (C, C++, Java) who may be new to Python, vector databases, and AI integration.

## Table of Contents

1. [Big Picture](#big-picture)
2. [Core Concepts](#core-concepts)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Storage Architecture](#storage-architecture)
6. [MCP Protocol](#mcp-protocol)
7. [Design Patterns](#design-patterns)

---

## Big Picture

### What Problem Does ACI Solve?

When you're researching a topic, you accumulate knowledge from many sources:
- Research papers
- Experiments
- Conversations
- Your own hypotheses

This knowledge has **relationships**:
- Paper A supports Paper B's findings
- Your hypothesis contradicts an established claim
- One idea extends another

ACI provides a structured way to store this knowledge and lets Claude reason over it.

### The Architecture in One Sentence

ACI is an **MCP server** that stores scientific claims in a **vector database** (for semantic search) and a **graph database** (for relationship traversal), accessed by Claude through **7 tools**.

### Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLAUDE (AI Agent)                          │
│                                                                     │
│  "Find concepts related to attention mechanisms"                    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ MCP Protocol (stdio)
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                         MCP SERVER (server.py)                      │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   ingest_   │  │  semantic_  │  │   find_     │                 │
│  │ hypothesis  │  │   search    │  │ lineage     │  ... 4 more    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH (graph_engine.py)                │
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────┐        │
│  │       LanceDB           │    │       NetworkX          │        │
│  │   (Vector Storage)      │    │    (Graph Storage)      │        │
│  │                         │    │                         │        │
│  │  • Atomic Units         │    │  • Nodes (unit IDs)     │        │
│  │  • Embeddings           │    │  • Edges (relations)    │        │
│  │  • Similarity Search    │    │  • Path Finding         │        │
│  └─────────────────────────┘    └─────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    PERSISTENCE (persistence.py)                     │
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────┐        │
│  │    relations.json       │    │   idempotency.json      │        │
│  │   (Graph Edges)         │    │   (Duplicate Prevention)│        │
│  └─────────────────────────┘    └─────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### What is an Atomic Unit?

An **Atomic Unit** is a single, indivisible scientific claim or proposition. Think of it like a single "fact" or "statement."

**Example Atomic Units:**
- "Attention mechanisms scale quadratically with sequence length"
- "Dropout reduces overfitting in neural networks"
- "The Earth orbits the Sun"

Each unit has:
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (UUID) |
| `content` | string | The proposition text |
| `source_doi` | string | Where this came from (optional) |
| `confidence` | float | How confident (0.0 to 1.0) |
| `vector` | float[] | Embedding for semantic search |

### What is a Relation?

A **Relation** connects two Atomic Units with meaning. It's like an edge in a graph.

**Relation Types:**
| Type | Meaning | Example |
|------|---------|---------|
| `supports` | A provides evidence for B | "Study A supports the hypothesis in Study B" |
| `refutes` | A contradicts B | "New findings refute the old theory" |
| `extends` | A builds upon B | "This work extends the original framework" |
| `implies` | A logically leads to B | "If A is true, then B must be true" |
| `contradicts` | A and B cannot both be true | "These two claims are mutually exclusive" |

### What is an Embedding?

An **embedding** is a list of numbers (a vector) that represents the *meaning* of text. Similar meanings have similar numbers.

**Why do we need embeddings?**
- Traditional search: "dog" only matches "dog"
- Semantic search: "dog" also matches "puppy", "canine", "pet"

**How it works:**
1. Text goes to OpenAI's embedding API
2. API returns 1536 numbers representing meaning
3. We store these numbers with the text
4. To search, we embed the query and find similar vectors

```
"attention mechanism" → [0.023, -0.145, 0.892, ...] (1536 numbers)
"self-attention"      → [0.021, -0.142, 0.889, ...] (very similar!)
"banana"              → [-0.567, 0.234, -0.123, ...] (very different)
```

### What is MCP?

**MCP (Model Context Protocol)** is a standard way for AI models like Claude to interact with external tools and data sources.

**Analogy:** Think of MCP like a USB standard for AI:
- USB lets any device connect to any computer
- MCP lets any AI model connect to any tool

**In this project:**
- We create an MCP "server" that provides tools
- Claude is an MCP "client" that uses those tools
- Communication happens over stdio (standard input/output)

---

## System Components

### 1. MCP Server (`src/server.py`)

**Responsibility:** Expose tools to Claude and handle requests.

**Key Elements:**
```python
# Create the server
mcp = FastMCP("Atomic Graph Researcher", instructions="...")

# Define a tool
@mcp.tool()
def ingest_hypothesis(hypothesis: str, source: str = "") -> dict:
    """Docstring that Claude reads to understand when to use this tool."""
    # Implementation
    return {"status": "success", "unit_id": "...", "available_actions": [...]}

# Run the server
mcp.run()
```

**What each tool does:**

| Tool | Input | Output | Side Effects |
|------|-------|--------|--------------|
| `ingest_hypothesis` | claim text, source | unit ID | Creates unit in DB |
| `connect_propositions` | two IDs, relation type | relation details | Creates edge |
| `semantic_search` | query text | ranked results | None (read-only) |
| `find_scientific_lineage` | start/end concepts | path | None (read-only) |
| `find_contradictions` | claim text | conflicts | None (read-only) |
| `list_propositions` | limit | unit list | None (read-only) |
| `get_unit` | unit ID | unit details | None (read-only) |

### 2. Knowledge Graph Engine (`src/graph_engine.py`)

**Responsibility:** Core logic for storing and querying knowledge.

**Key Class: `KnowledgeGraph`**

```python
class KnowledgeGraph:
    def __init__(self, data_dir, openai_api_key=None):
        # Initialize OpenAI client for embeddings
        # Connect to LanceDB for vector storage
        # Create NetworkX graph for relationships
        # Load existing relations from disk

    def add_proposition(self, content, source, confidence) -> AtomicUnit:
        # 1. Generate embedding via OpenAI
        # 2. Store in LanceDB table
        # 3. Add node to NetworkX graph
        # 4. Return the created unit

    def semantic_search(self, query, limit) -> list[(AtomicUnit, score)]:
        # 1. Generate embedding for query
        # 2. Search LanceDB for similar vectors
        # 3. Return ranked results

    def find_path(self, start_concept, end_concept) -> list[LineageStep]:
        # 1. Semantic search to find matching nodes
        # 2. Use NetworkX shortest_path algorithm
        # 3. Return path with relations
```

### 3. Data Models (`src/model.py`)

**Responsibility:** Define data structures with validation.

**Why Pydantic?**

Pydantic is like a "struct with superpowers":
- Automatic type checking
- Default values
- Serialization to/from JSON
- Validation rules

```python
# Traditional Python
class Unit:
    def __init__(self, id, content, confidence):
        self.id = id
        self.content = content
        self.confidence = confidence
        # No type checking, no validation

# Pydantic
class AtomicUnit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)  # Must be 0-1
    # Automatic type checking, validation, serialization
```

### 4. Persistence Layer (`src/persistence.py`)

**Responsibility:** Save/load relations and idempotency cache to JSON files.

**Why not store relations in LanceDB?**

- LanceDB is optimized for vector search, not graph queries
- JSON is simple and human-readable for debugging
- NetworkX needs edges in memory anyway

**Idempotency Cache:**

Prevents duplicate operations when Claude retries:
```python
# First call
ingest_hypothesis("claim", idempotency_key="abc123")
# → Creates unit, stores result with key "abc123"

# Retry with same key
ingest_hypothesis("claim", idempotency_key="abc123")
# → Returns cached result, no duplicate created
```

---

## Data Flow

### Flow 1: Ingesting a Hypothesis

```
User: "Ingest hypothesis that attention scales quadratically"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude calls: ingest_hypothesis(                            │
│   hypothesis="Attention scales quadratically...",           │
│   source="Vaswani 2017",                                    │
│   idempotency_key="user-session-123"                        │
│ )                                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ server.py: ingest_hypothesis()                              │
│   1. Check idempotency cache → Not found, proceed           │
│   2. Call graph.add_proposition()                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ graph_engine.py: add_proposition()                          │
│   1. Call OpenAI API to get embedding                       │
│   2. Create AtomicUnit with UUID                            │
│   3. Insert into LanceDB table                              │
│   4. Add node to NetworkX graph                             │
│   5. Return AtomicUnit                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ server.py: Build response                                   │
│   1. Create result dict with unit_id, content, etc.         │
│   2. Add available_actions for HATEOAS                      │
│   3. Store in idempotency cache                             │
│   4. Return to Claude                                       │
└─────────────────────────────────────────────────────────────┘
```

### Flow 2: Semantic Search

```
User: "Find concepts related to transformers"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude calls: semantic_search(query="transformers", limit=5)│
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ graph_engine.py: semantic_search()                          │
│   1. Generate embedding for "transformers"                  │
│   2. LanceDB vector search (cosine similarity)              │
│   3. Return top 5 most similar units with scores            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Results:                                                    │
│   1. "Transformers use self-attention" (0.92 similarity)    │
│   2. "BERT is a transformer model" (0.89 similarity)        │
│   3. "Attention mechanisms in NLP" (0.85 similarity)        │
│   ...                                                       │
└─────────────────────────────────────────────────────────────┘
```

### Flow 3: Finding Lineage

```
User: "How does attention connect to GPT?"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude calls: find_scientific_lineage(                      │
│   start_concept="attention mechanism",                      │
│   end_concept="GPT"                                         │
│ )                                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ graph_engine.py: find_path()                                │
│   1. Semantic search for "attention mechanism" → Node A     │
│   2. Semantic search for "GPT" → Node B                     │
│   3. NetworkX shortest_path(A, B) on undirected graph       │
│   4. Build path with relations                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Result:                                                     │
│   [Attention] --extends--> [Transformer] --implies--> [GPT] │
└─────────────────────────────────────────────────────────────┘
```

---

## Storage Architecture

### LanceDB (Vector Database)

**What is LanceDB?**

LanceDB is a vector database - it stores both regular data AND embeddings, enabling similarity search.

**Schema:**
```
Table: units
├── id: string (primary key)
├── content: string
├── source_doi: string
├── confidence: float64
├── created_at: string (ISO timestamp)
└── vector: float32[1536] (embedding)
```

**Why LanceDB?**
- Embedded (no separate server needed)
- Fast vector search
- Supports filtering alongside vector search
- Stores as files (easy to backup/share)

**Location:** `data/atomic_graph.lance/`

### NetworkX (Graph Database)

**What is NetworkX?**

NetworkX is a Python library for graph operations. We use it as an in-memory graph database.

**Structure:**
```
DiGraph (Directed Graph)
├── Nodes: {unit_id: {"content": "..."}}
└── Edges: {(source_id, target_id): {"type": "supports", "reasoning": "..."}}
```

**Why NetworkX?**
- Simple to use
- Powerful pathfinding algorithms
- In-memory (fast)
- Persisted via JSON for durability

### JSON Persistence

**relations.json:**
```json
[
  {
    "source_id": "uuid-1",
    "target_id": "uuid-2",
    "type": "supports",
    "reasoning": "Both discuss attention mechanisms",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

**idempotency.json:**
```json
{
  "unique-key-123": {
    "status": "success",
    "unit_id": "uuid-1",
    "content": "..."
  }
}
```

---

## MCP Protocol

### How Communication Works

```
┌─────────┐     stdio      ┌─────────────┐
│  Claude │ ◄────────────► │  MCP Server │
└─────────┘                └─────────────┘
     │                           │
     │  1. Request (JSON)        │
     │ ──────────────────────►   │
     │                           │
     │  2. Execute tool          │
     │                           │
     │  3. Response (JSON)       │
     │ ◄──────────────────────   │
     │                           │
```

### Message Format

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "semantic_search",
    "arguments": {
      "query": "attention",
      "limit": 5
    }
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"status\": \"success\", \"results\": [...]}"
    }
  ]
}
```

### Tool Discovery

Claude reads the tool list and descriptions to decide which tool to use:

```python
@mcp.tool()
def semantic_search(query: str, limit: int = 5) -> dict:
    """
    Finds atomic units semantically similar to the query.

    Use this when:
    - Exploring what's in the knowledge graph
    - Finding related concepts to a topic
    """
```

Claude sees:
- Tool name: `semantic_search`
- Parameters: `query` (required), `limit` (optional, default 5)
- Description: When and how to use it

---

## Design Patterns

### 1. HATEOAS (Hypermedia as the Engine of Application State)

Every response includes suggestions for what to do next:

```python
{
    "status": "success",
    "unit_id": "abc123",
    "available_actions": [
        {"tool": "connect_propositions", "description": "Link to another unit"},
        {"tool": "semantic_search", "description": "Find related concepts"}
    ]
}
```

**Why?** Claude can discover available operations without prior knowledge.

### 2. Idempotency Keys

Write operations accept optional keys to prevent duplicates:

```python
# First call creates the unit
ingest_hypothesis("claim", idempotency_key="key1") → {"unit_id": "abc"}

# Retry returns cached result (no duplicate)
ingest_hypothesis("claim", idempotency_key="key1") → {"unit_id": "abc"}
```

**Why?** AI agents sometimes retry requests. This prevents data corruption.

### 3. Lazy Initialization

The graph is created on first use, not at import time:

```python
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph(DATA_DIR)
    return _graph
```

**Why?** Allows environment variables to be set before initialization.

### 4. Rich Tool Descriptions

Detailed docstrings help Claude understand when to use each tool:

```python
@mcp.tool()
def find_contradictions(claim: str) -> dict:
    """
    Checks if a claim contradicts existing knowledge in the graph.

    Use this when:
    - Validating a new hypothesis against existing knowledge
    - Looking for papers/claims that disagree
    - Ensuring consistency in your knowledge base

    Example: find_contradictions("Attention is linear in sequence length")
    """
```

---

## Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Interface | MCP/FastMCP | Connect Claude to our tools |
| Tools | Python functions | Define operations Claude can perform |
| Logic | KnowledgeGraph | Combine vector search + graph traversal |
| Vector Storage | LanceDB | Store embeddings, enable semantic search |
| Graph Storage | NetworkX | Store relations, enable pathfinding |
| Persistence | JSON files | Durability for relations and cache |
| Embeddings | OpenAI API | Convert text to vectors |

The architecture separates concerns cleanly:
- **server.py** - Interface (what tools exist)
- **graph_engine.py** - Logic (how tools work)
- **model.py** - Data (what data looks like)
- **persistence.py** - Storage (how data persists)

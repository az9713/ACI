# Developer Guide

This guide is for developers who want to understand, modify, or extend the ACI codebase. It assumes you have experience with traditional programming languages (C, C++, Java) but may be new to Python, web development patterns, and AI integration.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Python Primer for C/C++/Java Developers](#python-primer)
3. [Understanding the Codebase](#understanding-the-codebase)
4. [Making Changes](#making-changes)
5. [Adding New Features](#adding-new-features)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Common Tasks](#common-tasks)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Step 1: Install Python 3.10+

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Verify: Open Command Prompt, type `python --version`

**Mac:**
```bash
brew install python@3.10
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### Step 2: Install uv (Package Manager)

`uv` is a fast Python package manager (like npm for Node.js or Maven for Java).

```bash
pip install uv
```

**Why uv instead of pip?**
- Faster dependency resolution
- Better reproducibility
- Manages virtual environments automatically

### Step 3: Clone and Setup the Project

```bash
# Get the code
git clone <repository-url>
cd ACI

# Install all dependencies
uv sync

# This creates:
# - .venv/ folder (virtual environment, like a sandbox)
# - Downloads all required packages
```

### Step 4: Configure Environment

```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**What is a .env file?**

It's a text file containing environment variables. The application reads these at startup. It's not committed to git (security).

### Step 5: Verify Setup

```bash
# Test that imports work
uv run python -c "from src.server import mcp; print('Setup OK')"

# You should see: "Setup OK"
```

### IDE Setup (VS Code Recommended)

1. Install VS Code
2. Install Python extension
3. Open the ACI folder
4. VS Code will detect the virtual environment in `.venv/`
5. Select it as your Python interpreter (bottom-left of VS Code)

---

## Python Primer

### For C/C++ Developers

| C/C++ | Python | Notes |
|-------|--------|-------|
| `int x = 5;` | `x = 5` | No type declarations needed |
| `int* ptr = &x;` | N/A | No pointers in Python |
| `#include <stdio.h>` | `import os` | Imports instead of includes |
| `class Foo { public: int x; };` | `class Foo: x = 0` | Classes are simpler |
| `new Foo()` | `Foo()` | No `new` keyword |
| Memory management | Automatic | Python has garbage collection |

**Key Differences:**
- **Indentation matters**: Python uses indentation instead of braces `{}`
- **No semicolons**: Line endings end statements
- **Dynamic typing**: Variables can change types
- **Everything is an object**: Even functions and classes

### For Java Developers

| Java | Python | Notes |
|------|--------|-------|
| `public class Foo {}` | `class Foo:` | No access modifiers |
| `public static void main` | `if __name__ == "__main__":` | Entry point |
| `ArrayList<String>` | `list` | No generics needed |
| `HashMap<String, Integer>` | `dict` | Built-in dictionary |
| `interface Foo {}` | `class Foo(Protocol):` | Protocols for interfaces |
| `@Override` | N/A | Duck typing instead |

**Key Differences:**
- **No compilation**: Python is interpreted
- **Duck typing**: "If it walks like a duck..."
- **Multiple inheritance**: Python supports it
- **No checked exceptions**: All exceptions are unchecked

### Essential Python Syntax

```python
# Variables
name = "Alice"        # String
count = 42            # Integer
price = 19.99         # Float
items = [1, 2, 3]     # List (like ArrayList)
data = {"key": "value"}  # Dict (like HashMap)

# Functions
def greet(name: str) -> str:
    """Docstring: This function greets someone."""
    return f"Hello, {name}!"

# Classes
class Person:
    def __init__(self, name: str):
        self.name = name  # Instance variable

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

# Type hints (optional but recommended)
def add(a: int, b: int) -> int:
    return a + b

# List comprehension (common pattern)
squares = [x**2 for x in range(10)]  # [0, 1, 4, 9, 16, ...]

# With statement (automatic cleanup, like try-with-resources)
with open("file.txt", "r") as f:
    content = f.read()
# File automatically closed here
```

### Understanding `async/await`

The MCP server uses async code. Here's a quick primer:

```python
# Synchronous (blocking)
def get_data():
    result = slow_network_call()  # Waits here
    return result

# Asynchronous (non-blocking)
async def get_data():
    result = await slow_network_call()  # Can do other things while waiting
    return result
```

**For this project:** The MCP framework handles async internally. Your tool functions can be regular (synchronous) functions.

---

## Understanding the Codebase

### File-by-File Walkthrough

#### `pyproject.toml` - Project Configuration

```toml
[project]
name = "aci-knowledge-graph"
version = "0.1.0"
dependencies = [
    "mcp[cli]>=1.0.0",   # MCP server framework
    "lancedb>=0.6.0",    # Vector database
    "networkx>=3.0",     # Graph library
    "pydantic>=2.0",     # Data validation
    "openai>=1.0.0",     # Embeddings API
]
```

**This is like:**
- `pom.xml` in Maven (Java)
- `CMakeLists.txt` in CMake (C++)
- `package.json` in npm (Node.js)

#### `src/model.py` - Data Models

```python
from pydantic import BaseModel, Field

class AtomicUnit(BaseModel):
    """A single scientific proposition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    confidence: float = Field(1.0, ge=0.0, le=1.0)
```

**Pydantic BaseModel is like:**
- A struct (C) with validation
- A POJO with Bean Validation (Java)
- A data class with contracts

**What `Field` does:**
- `default_factory`: Generates default value (like a constructor)
- `ge=0.0, le=1.0`: Validation (greater-equal 0, less-equal 1)

#### `src/persistence.py` - Data Storage

```python
class PersistenceManager:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.relations_file = self.data_dir / "relations.json"
        self._relations = []
        self._load()

    def _load(self):
        if self.relations_file.exists():
            with open(self.relations_file, "r") as f:
                self._relations = json.load(f)
```

**Key patterns:**
- `Path` objects (like `java.nio.file.Path`)
- JSON serialization (like Jackson in Java)
- Private methods prefixed with `_`

#### `src/graph_engine.py` - Core Logic

```python
class KnowledgeGraph:
    def __init__(self, data_dir: Path, openai_api_key: str = None):
        # Initialize OpenAI
        self.openai_client = OpenAI(api_key=api_key)

        # Initialize LanceDB
        self.db = lancedb.connect(str(self.data_dir / "atomic_graph.lance"))

        # Initialize NetworkX
        self.graph = nx.DiGraph()
```

**Three systems working together:**
1. **OpenAI client**: Makes API calls for embeddings
2. **LanceDB**: Stores vectors, enables similarity search
3. **NetworkX**: Stores graph structure, enables pathfinding

#### `src/server.py` - MCP Interface

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Atomic Graph Researcher")

@mcp.tool()
def ingest_hypothesis(hypothesis: str, source: str = "") -> dict:
    """Tool description that Claude reads."""
    graph = get_graph()
    unit = graph.add_proposition(hypothesis, source)
    return {"status": "success", "unit_id": unit.id}
```

**The `@mcp.tool()` decorator:**
- Registers the function as an MCP tool
- Extracts parameter types and docstring
- Makes it callable by Claude

---

## Making Changes

### Modifying an Existing Tool

**Example: Add a parameter to `semantic_search`**

1. **Find the tool in `src/server.py`:**

```python
@mcp.tool()
def semantic_search(query: str, limit: int = 5) -> dict:
```

2. **Add the new parameter:**

```python
@mcp.tool()
def semantic_search(
    query: str,
    limit: int = 5,
    min_score: float = 0.0,  # NEW: minimum similarity score
) -> dict:
```

3. **Update the docstring:**

```python
    """
    Finds atomic units semantically similar to the query.

    Args:
        query: Search text
        limit: Maximum results (default: 5)
        min_score: Minimum similarity score 0.0-1.0 (default: 0.0)
    """
```

4. **Update the implementation:**

```python
    results = graph.semantic_search(query, limit=limit)

    # Filter by minimum score
    filtered = [(unit, score) for unit, score in results if score >= min_score]
```

5. **Test:**

```bash
uv run python -c "
from src.server import semantic_search
# This would need a real graph, but syntax check is good
print('Import OK')
"
```

### Adding a New Field to AtomicUnit

1. **Update `src/model.py`:**

```python
class AtomicUnit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    source_doi: Optional[str] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)  # NEW FIELD
```

2. **Update LanceDB schema in `src/graph_engine.py`:**

```python
def _init_table(self) -> None:
    if "units" not in self.db.table_names():
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("source_doi", pa.string()),
            pa.field("confidence", pa.float64()),
            pa.field("created_at", pa.string()),
            pa.field("tags", pa.list_(pa.string())),  # NEW FIELD
            pa.field("vector", pa.list_(pa.float32(), self.EMBEDDING_DIM)),
        ])
```

3. **Update `add_proposition`:**

```python
def add_proposition(
    self,
    content: str,
    source_doi: Optional[str] = None,
    confidence: float = 1.0,
    tags: list[str] = None,  # NEW PARAMETER
) -> AtomicUnit:
    unit = AtomicUnit(
        content=content,
        source_doi=source_doi,
        confidence=confidence,
        tags=tags or [],
        vector=vector,
    )

    self.table.add([{
        "id": unit.id,
        "content": unit.content,
        "source_doi": unit.source_doi or "",
        "confidence": unit.confidence,
        "created_at": unit.created_at.isoformat(),
        "tags": unit.tags,  # NEW FIELD
        "vector": unit.vector,
    }])
```

4. **Update retrieval methods to include the new field.**

**Note:** Existing data won't have the new field. You'll need to handle migration or recreate the database.

---

## Adding New Features

### Adding a New Tool

**Example: Add a `delete_unit` tool**

1. **Add to `src/server.py`:**

```python
@mcp.tool()
def delete_unit(unit_id: str, confirm: bool = False) -> dict:
    """
    Deletes an atomic unit from the knowledge graph.

    Use this when:
    - Removing incorrect or outdated information
    - Cleaning up the knowledge base

    Args:
        unit_id: The ID of the unit to delete
        confirm: Must be True to actually delete (safety check)

    Returns:
        Deletion status
    """
    if not confirm:
        return {
            "status": "error",
            "message": "Set confirm=True to delete. This action cannot be undone."
        }

    graph = get_graph()

    # Check if unit exists
    unit = graph.get_unit(unit_id)
    if not unit:
        return {"status": "error", "message": f"Unit not found: {unit_id}"}

    # Delete from LanceDB
    graph.delete_unit(unit_id)

    return {
        "status": "success",
        "deleted_id": unit_id,
        "deleted_content": unit.content,
    }
```

2. **Add method to `src/graph_engine.py`:**

```python
def delete_unit(self, unit_id: str) -> bool:
    """Delete a unit from the graph."""
    # Delete from LanceDB
    self.table.delete(f"id = '{unit_id}'")

    # Remove from NetworkX
    if self.graph.has_node(unit_id):
        self.graph.remove_node(unit_id)

    # Note: Related edges in persistence would need cleanup too
    return True
```

### Adding a New Relation Type

1. **Update `src/model.py`:**

```python
RelationType = Literal[
    "supports",
    "refutes",
    "extends",
    "implies",
    "contradicts",
    "requires",  # NEW: B requires A to be true
]
```

2. **Update validation in `connect_propositions` tool:**

```python
valid_relations = ["supports", "refutes", "extends", "implies", "contradicts", "requires"]
```

3. **Update any logic that handles relation types (e.g., in `get_conflicts`).**

---

## Testing

### Manual Testing

Since there are no automated tests yet, test manually:

```bash
# Start Python interpreter
uv run python

# In Python:
>>> from src.graph_engine import KnowledgeGraph
>>> from pathlib import Path
>>> import os

# Set API key
>>> os.environ["OPENAI_API_KEY"] = "sk-your-key"

# Create graph
>>> graph = KnowledgeGraph(Path("./test_data"))

# Test adding a unit
>>> unit = graph.add_proposition("Test hypothesis", "Test source")
>>> print(f"Created: {unit.id}")

# Test search
>>> results = graph.semantic_search("test")
>>> for unit, score in results:
...     print(f"{score:.2f}: {unit.content}")

# Clean up test data
>>> import shutil
>>> shutil.rmtree("./test_data")
```

### Writing Automated Tests

Create `tests/test_graph_engine.py`:

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.model import AtomicUnit
from src.graph_engine import KnowledgeGraph


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph class."""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI API to avoid real API calls."""
        with patch("src.graph_engine.OpenAI") as mock:
            # Return fake embedding
            mock.return_value.embeddings.create.return_value.data = [
                Mock(embedding=[0.1] * 1536)
            ]
            yield mock

    @pytest.fixture
    def graph(self, mock_openai, tmp_path):
        """Create a test graph with mocked OpenAI."""
        return KnowledgeGraph(tmp_path, openai_api_key="fake-key")

    def test_add_proposition(self, graph):
        """Test adding a proposition."""
        unit = graph.add_proposition("Test content", "Test source")

        assert unit.content == "Test content"
        assert unit.source_doi == "Test source"
        assert len(unit.vector) == 1536

    def test_get_unit(self, graph):
        """Test retrieving a unit."""
        unit = graph.add_proposition("Test", "Source")
        retrieved = graph.get_unit(unit.id)

        assert retrieved is not None
        assert retrieved.content == "Test"
```

Run tests:
```bash
uv run pytest tests/ -v
```

---

## Debugging

### Common Issues and Solutions

#### "OPENAI_API_KEY not set"

```python
# Error
ValueError: OPENAI_API_KEY must be set in environment or passed explicitly

# Solution 1: Set environment variable
export OPENAI_API_KEY=sk-your-key  # Linux/Mac
set OPENAI_API_KEY=sk-your-key     # Windows

# Solution 2: Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env
```

#### "Module not found"

```python
# Error
ModuleNotFoundError: No module named 'lancedb'

# Solution: Install dependencies
uv sync
```

#### "Table already exists with different schema"

```python
# Error when you've changed the schema
# Solution: Delete the old database
import shutil
shutil.rmtree("data/atomic_graph.lance")
```

### Adding Debug Logging

```python
import logging

# In src/graph_engine.py
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def add_proposition(self, content, source=None):
        logger.debug(f"Adding proposition: {content[:50]}...")

        vector = self._get_embedding(content)
        logger.debug(f"Got embedding of length {len(vector)}")

        # ... rest of method
```

Run with debug output:
```bash
uv run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.server import mcp
"
```

### Using Python Debugger

```python
# Add this line where you want to stop
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

**Debugger commands:**
- `n` - next line
- `s` - step into function
- `c` - continue
- `p variable` - print variable
- `q` - quit

---

## Common Tasks

### Task: Update Dependencies

```bash
# Add a new dependency
uv add requests

# Update all dependencies
uv sync --upgrade

# Remove a dependency
uv remove requests
```

### Task: Reset the Database

```bash
# Delete all data (start fresh)
rm -rf data/

# Or in Python
import shutil
shutil.rmtree("data/", ignore_errors=True)
```

### Task: Export Data

```python
import json
from src.graph_engine import KnowledgeGraph
from pathlib import Path

graph = KnowledgeGraph(Path("data"))

# Export all units
units = graph.list_propositions(limit=1000)
export = [{"id": u.id, "content": u.content, "source": u.source_doi} for u in units]

with open("export.json", "w") as f:
    json.dump(export, f, indent=2)
```

### Task: View MCP Server Logs

```bash
# Run server with verbose output
uv run python src/server.py 2>&1 | tee server.log
```

---

## Best Practices

### Code Style

Follow PEP 8 (Python style guide):

```python
# Good
def calculate_score(query: str, limit: int = 10) -> float:
    """Calculate search score."""
    pass

# Bad
def CalculateScore(Query,Limit=10):
    pass
```

### Type Hints

Always use type hints for function signatures:

```python
# Good
def add_proposition(
    self,
    content: str,
    source: Optional[str] = None,
    confidence: float = 1.0,
) -> AtomicUnit:

# Bad
def add_proposition(self, content, source=None, confidence=1.0):
```

### Error Handling

Return structured errors, don't raise exceptions in tools:

```python
# Good
def my_tool(param: str) -> dict:
    if not param:
        return {"status": "error", "message": "param is required"}
    try:
        result = do_something(param)
        return {"status": "success", "result": result}
    except SomeException as e:
        return {"status": "error", "message": str(e)}

# Bad
def my_tool(param: str) -> dict:
    result = do_something(param)  # May raise exception
    return result
```

### Documentation

Every function should have a docstring:

```python
def semantic_search(self, query: str, limit: int = 5) -> list[tuple[AtomicUnit, float]]:
    """
    Find atomic units semantically similar to query.

    Args:
        query: The search text to find similar content for
        limit: Maximum number of results to return

    Returns:
        List of (unit, similarity_score) tuples, sorted by score descending

    Raises:
        ValueError: If query is empty

    Example:
        >>> results = graph.semantic_search("attention", limit=3)
        >>> for unit, score in results:
        ...     print(f"{score:.2f}: {unit.content[:50]}")
    """
```

---

## Troubleshooting

### Issue: Server Won't Start

```bash
# Check for syntax errors
uv run python -m py_compile src/server.py

# Check imports
uv run python -c "from src.server import mcp"

# Check environment
uv run python -c "import os; print(os.environ.get('OPENAI_API_KEY', 'NOT SET'))"
```

### Issue: Can't Connect from Claude

1. **Check MCP configuration:**
```bash
claude mcp list
```

2. **Re-add the server:**
```bash
claude mcp remove atomic-graph
claude mcp add --transport stdio atomic-graph -- uv run python src/server.py
```

3. **Test server manually:**
```bash
uv run python src/server.py
# Should hang waiting for MCP input (Ctrl+C to exit)
```

### Issue: Search Returns No Results

1. **Check if there's data:**
```python
from src.graph_engine import KnowledgeGraph
from pathlib import Path

graph = KnowledgeGraph(Path("data"))
units = graph.list_propositions()
print(f"Total units: {len(units)}")
```

2. **Check vector table:**
```python
print(f"Table rows: {graph.table.count_rows()}")
```

### Issue: Embedding API Errors

```python
# Test OpenAI connection
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
response = client.embeddings.create(
    input="test",
    model="text-embedding-ada-002"
)
print(f"Embedding length: {len(response.data[0].embedding)}")
```

---

## Next Steps

After reading this guide, you should be able to:

1. Set up your development environment
2. Understand the codebase structure
3. Make modifications to existing tools
4. Add new features
5. Debug common issues

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).
For user-facing documentation, see [USER_GUIDE.md](USER_GUIDE.md).

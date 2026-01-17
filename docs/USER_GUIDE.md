# User Guide

> **Prototype / Experimental**
>
> This project is in early development with a raw, command-line interface. Some rough edges are expected.

This guide teaches you how to use Knowledge Graph CLI to build and query a scientific knowledge graph with Claude's help. No programming knowledge is required.

## Table of Contents

1. [What is Knowledge Graph CLI?](#what-is-knowledge-graph-cli)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Using the Tools](#using-the-tools)
5. [Building Your Knowledge Graph](#building-your-knowledge-graph)
6. [Searching and Exploring](#searching-and-exploring)
7. [Finding Connections](#finding-connections)
8. [Detecting Contradictions](#detecting-contradictions)
9. [Tips and Best Practices](#tips-and-best-practices)
10. [Frequently Asked Questions](#faq)

---

## What is Knowledge Graph CLI?

### The Problem

When you research a topic, you gather information from many sources:
- Research papers
- Books and articles
- Experiments
- Conversations with experts
- Your own ideas

Over time, this knowledge becomes hard to manage:
- "Where did I read that claim about X?"
- "Does this new finding contradict what I learned before?"
- "How does concept A relate to concept B?"

### The Solution

Knowledge Graph CLI gives Claude the ability to:
1. **Store** your scientific claims in a searchable database
2. **Connect** related ideas with explicit relationships
3. **Search** by meaning, not just keywords
4. **Trace** how ideas connect to each other
5. **Detect** contradictions in your accumulated knowledge

Think of it as a "second brain" that Claude can access and reason over.

---

## Installation

### What You'll Need

1. **A computer** (Windows, Mac, or Linux)
2. **An internet connection** (for OpenAI API)
3. **An OpenAI API key** (costs money per use, but very cheap)
4. **Claude Code or Claude Desktop**

### Step-by-Step Installation

#### Step 1: Install Python

Python is a programming language. You don't need to write code, but it needs to be installed.

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.x.x"
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH"
5. Click "Install Now"

**Mac:**
1. Open Terminal (press Cmd+Space, type "Terminal")
2. Type: `brew install python`
3. Press Enter

**Linux:**
1. Open Terminal
2. Type: `sudo apt install python3 python3-pip`
3. Press Enter

#### Step 2: Install uv

uv is a tool that manages Python packages.

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```
pip install uv
```

#### Step 3: Get the Code

**Option A: Download ZIP**
1. Download the ZIP file
2. Extract it to a folder you can find (e.g., `Downloads/knowledge-graph-cli`)

**Option B: Using git**
```
git clone <repository-url>
```

#### Step 4: Install Dependencies

1. Open your terminal
2. Navigate to the project folder:
   - Windows: `cd C:\Users\YourName\Downloads\knowledge-graph-cli`
   - Mac/Linux: `cd ~/Downloads/knowledge-graph-cli`
3. Run: `uv sync`

This downloads all the required software. It may take a minute.

#### Step 5: Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Step 6: Configure Your API Key

Create a file called `.env` in the project folder with this content:

```
OPENAI_API_KEY=sk-your-key-here
```

Replace `sk-your-key-here` with your actual key.

**Windows (using Notepad):**
1. Open Notepad
2. Type: `OPENAI_API_KEY=sk-your-key-here`
3. Save as `.env` in the project folder (choose "All Files" as file type)

#### Step 7: Connect to Claude Code

Run this command to register the MCP server (only needed once):

```
claude mcp add --transport stdio atomic-graph -- uv run python src/server.py
```

#### Step 8: Verify It Works

Start a Claude Code session:

```
claude
```

Then type:

```
List propositions in my knowledge graph
```

Claude should respond that the knowledge graph is empty (or show existing entries if you have any).

---

## Basic Concepts

### Atomic Units

An **atomic unit** is a single scientific claim or proposition. Think of it as one "fact" or "statement."

**Good atomic units:**
- "Attention mechanisms allow models to focus on relevant parts of input"
- "The speed of light is approximately 299,792 km/s"
- "BERT uses bidirectional transformer encoders"

**Bad atomic units (too complex):**
- "Attention mechanisms, which were introduced in 2015, allow models to focus on relevant parts of input and have been used in many applications including translation, summarization, and image processing"

Keep each unit simple and focused on ONE claim.

### Relations

A **relation** connects two atomic units and describes HOW they're connected.

**Types of relations:**

| Type | What it means | Example |
|------|---------------|---------|
| **supports** | A provides evidence for B | "Experiment results support the hypothesis" |
| **refutes** | A contradicts or disproves B | "New data refutes the old theory" |
| **extends** | A builds upon B | "This work extends the original framework" |
| **implies** | If A is true, B must be true | "Universal grammar implies language is innate" |
| **contradicts** | A and B cannot both be true | "These two claims are mutually exclusive" |

### Semantic Search

Traditional search finds exact words:
- Search for "dog" → only finds "dog"

Semantic search finds meaning:
- Search for "dog" → finds "dog", "puppy", "canine", "pet"

Knowledge Graph CLI uses semantic search, so you can find related concepts even if they use different words.

---

## Using the Tools

Knowledge Graph CLI provides 8 tools that Claude can use. Here's how to use each one:

### 1. Ingest Hypothesis

**Purpose:** Add a new scientific claim to your knowledge graph.

**How to use:**
```
"Ingest the hypothesis that transformer models use self-attention for sequence processing, from Vaswani et al. 2017"
```

**What Claude does:**
1. Creates a new atomic unit
2. Generates an embedding (for semantic search)
3. Stores it in the database
4. Returns the unit ID

**Tips:**
- Be specific about the claim
- Include the source when possible
- Keep claims atomic (one idea per unit)

### 2. Connect Propositions

**Purpose:** Create a relationship between two existing claims.

**How to use:**
```
"Connect the attention mechanism unit to the transformer architecture unit with a 'supports' relationship, because attention is a core component of transformers"
```

**What Claude does:**
1. Finds both units
2. Creates an edge in the graph
3. Stores your reasoning

**Tips:**
- Explain WHY they're connected
- Choose the right relation type
- Make sure both units exist first

### 3. Semantic Search

**Purpose:** Find claims related to a topic.

**How to use:**
```
"Search for concepts related to neural network optimization"
```

**What Claude does:**
1. Converts your query to an embedding
2. Finds similar units by meaning
3. Returns ranked results with similarity scores

**Tips:**
- Use natural language, not keywords
- Try different phrasings if results aren't good
- The score shows how similar (0.0-1.0)

### 4. Find Scientific Lineage

**Purpose:** Trace how one idea connects to another.

**How to use:**
```
"Find the intellectual lineage from attention mechanisms to GPT models"
```

**What Claude does:**
1. Finds units matching start and end concepts
2. Traces the path through connected units
3. Shows each step with relationships

**Tips:**
- Works best when units are well-connected
- May return partial paths if not fully connected
- Use broad concepts for better matching

### 5. Find Contradictions

**Purpose:** Check if a claim conflicts with existing knowledge.

**How to use:**
```
"Check if the claim 'attention is linear in sequence length' contradicts anything"
```

**What Claude does:**
1. Finds semantically similar units
2. Checks for 'refutes' or 'contradicts' relations
3. Reports potential conflicts

**Tips:**
- Use before accepting new claims
- Helps maintain consistency
- May find false positives (high similarity isn't always contradiction)

### 6. List Propositions

**Purpose:** Browse all claims in your knowledge graph.

**How to use:**
```
"List all propositions in my knowledge graph"
```

**What Claude does:**
1. Retrieves recent units
2. Shows their content and sources

**Tips:**
- Use to get an overview
- Set a limit if you have many units
- Useful for finding units to connect

### 7. Get Unit

**Purpose:** See details of a specific claim and its connections.

**How to use:**
```
"Get details for unit abc123"
```

**What Claude does:**
1. Retrieves the unit
2. Shows all its connections
3. Shows available actions

**Tips:**
- Use unit IDs from other commands
- Great for exploring the graph
- See what each unit connects to

### 8. Delete Unit

**Purpose:** Remove incorrect or outdated claims from your knowledge graph.

**How to use:**
```
"Delete unit abc123"
```

**What Claude does:**
1. Shows you what will be deleted (content, connections)
2. Asks for confirmation
3. If confirmed, permanently removes:
   - The unit from the database
   - All connections involving that unit

**Safety features:**
- Requires explicit confirmation (you must confirm the deletion)
- Shows exactly what will be removed before deleting
- Cannot be undone once confirmed

**Tips:**
- Review the confirmation carefully before confirming
- Consider adding a correcting claim with "refutes" relation instead
- Use to clean up mistakes or outdated information

---

## Building Your Knowledge Graph

### Getting Started

Start by adding a few related claims. Here's an example workflow:

**1. Add your first claim:**
```
"Ingest the hypothesis that neural networks are composed of layers of interconnected nodes"
```

**2. Add related claims:**
```
"Ingest that deep learning refers to neural networks with many layers"

"Ingest that each layer transforms its input and passes it to the next layer"
```

**3. Connect them:**
```
"Connect the deep learning definition to the neural network composition claim, showing that deep learning extends the basic neural network concept"
```

### Best Practices for Building

**Keep units atomic:**
- One claim per unit
- Split complex ideas into multiple units
- Connect them with relations

**Be consistent:**
- Use similar phrasing for similar concepts
- Include sources when possible
- Document your reasoning in connections

**Build incrementally:**
- Start with core concepts
- Add supporting details
- Connect as you go

### Example: Building a Topic

Let's build knowledge about "Transformers in NLP":

```
1. "Ingest: Transformers are a neural network architecture introduced in 2017"

2. "Ingest: Transformers use self-attention mechanisms, from Vaswani et al."

3. "Ingest: Self-attention allows each position to attend to all positions"

4. "Connect unit 2 to unit 1 as 'supports' - attention is a key feature"

5. "Connect unit 3 to unit 2 as 'extends' - explaining how attention works"

6. "Ingest: BERT uses transformer encoders for language understanding"

7. "Connect BERT to transformers as 'extends' - BERT builds on transformers"
```

---

## Searching and Exploring

### Finding What You Have

**Basic search:**
```
"Search for concepts about machine learning"
```

**Specific search:**
```
"Search for claims about the limitations of recurrent neural networks"
```

**Exploring results:**
```
"Get more details on unit [id from search results]"
```

### Understanding Search Scores

Results include a similarity score from 0.0 to 1.0:

| Score | Meaning |
|-------|---------|
| 0.90+ | Very closely related |
| 0.80-0.90 | Clearly related |
| 0.70-0.80 | Somewhat related |
| 0.60-0.70 | Loosely related |
| Below 0.60 | Probably not relevant |

### Tips for Better Searches

1. **Use natural language:** "concepts about how transformers process sequences"
2. **Try synonyms:** If "neural network" doesn't work, try "deep learning"
3. **Be specific:** "attention mechanism in NLP" vs just "attention"
4. **Iterate:** Start broad, then narrow down

---

## Finding Connections

### Tracing Lineages

When you want to understand how ideas connect:

```
"Find the intellectual lineage from word embeddings to large language models"
```

Claude will show the path:
```
Word embeddings → Neural language models → Attention mechanisms → Transformers → Large language models
```

### Building Better Paths

Lineage finding works best when:
- Units are connected
- Connections are meaningful
- The graph has enough coverage

If paths are incomplete:
1. Add missing intermediate concepts
2. Connect existing units
3. Try different start/end concepts

---

## Detecting Contradictions

### Checking New Claims

Before accepting a new claim, check for conflicts:

```
"Before I add this: check if 'RNNs are better than transformers for long sequences' contradicts anything"
```

### Understanding Conflicts

When contradictions are found, Claude reports:
- The conflicting unit
- The relationship (if any)
- An explanation

**Types of conflicts:**
1. **Explicit contradiction:** Units connected with "refutes" or "contradicts"
2. **Implicit conflict:** Highly similar units that seem to disagree

### Resolving Contradictions

When you find a contradiction:
1. **Evaluate both claims** - which is more credible?
2. **Check sources** - is one more recent or authoritative?
3. **Add nuance** - maybe both are true in different contexts?
4. **Update the graph** - remove incorrect claims or add clarifying connections

---

## Tips and Best Practices

### For Research

1. **Ingest as you read:** Add claims while reading papers
2. **Connect immediately:** Link new claims to existing knowledge
3. **Note contradictions:** They're valuable for understanding debates
4. **Include sources:** Makes claims credible and traceable

### For Learning

1. **Build from basics:** Start with foundational concepts
2. **Add incrementally:** Build complexity over time
3. **Test understanding:** Use lineage tracing to verify connections
4. **Review regularly:** List and review your knowledge

### For Writing

1. **Use as outline:** Search for topics, use results to structure
2. **Find connections:** Lineage tracing shows how to connect ideas
3. **Verify consistency:** Check for contradictions before citing
4. **Export for reference:** List relevant units for your bibliography

---

## Frequently Asked Questions

### General Questions

**Q: How much does it cost to use?**

A: Each operation costs a small amount through OpenAI's API:
- Ingesting a claim: ~$0.0001 (fraction of a cent)
- Searching: ~$0.0001
- Typical session: a few cents

**Q: Where is my data stored?**

A: Everything is stored locally in the `data/` folder:
- Vector database: `data/atomic_graph.lance/`
- Relations: `data/relations.json`
- Idempotency cache: `data/idempotency.json`

**Q: Can I share my knowledge graph?**

A: Yes! Copy the entire `data/` folder to share with others.

**Q: What happens if I lose my data?**

A: Back up the `data/` folder regularly. There's no cloud sync currently.

### Technical Questions

**Q: Why does the first operation take longer?**

A: The system initializes on first use:
- Connects to the database
- Loads the graph into memory
- Subsequent operations are faster

**Q: Why does search sometimes miss relevant content?**

A: Semantic search isn't perfect:
- Try different phrasings
- The content might use very different terminology
- Lower the similarity threshold in your mental model

**Q: Can I edit or delete units?**

A: You can delete units using the `delete_unit` tool:
```
"Delete unit [unit-id]"
```
Claude will show you what will be deleted and ask for confirmation. This permanently removes the unit and all its connections.

For editing, there's no direct edit function. Instead:
- Delete the incorrect unit
- Add a corrected version with `ingest_hypothesis`
- Or add a clarifying unit connected with "refutes" relation

### Troubleshooting

**Q: Claude says the tool isn't available**

A: The MCP server might not be running:
1. Restart Claude Code/Desktop
2. Re-add the server: `claude mcp add --transport stdio atomic-graph -- uv run python src/server.py`

**Q: I get "OPENAI_API_KEY not set"**

A: Create a `.env` file with your key:
1. Open the project folder
2. Create a file named `.env`
3. Add: `OPENAI_API_KEY=sk-your-key`

**Q: Search returns no results**

A: Either:
- Your knowledge graph is empty (ingest some claims first)
- No claims match your query (try different wording)

**Q: Connection fails - "Unit not found"**

A: The unit ID might be wrong:
1. Use `list_propositions` to see available units
2. Copy the exact ID
3. Try the connection again

---

## Next Steps

Now that you understand the basics:

1. **Start small:** Add 5-10 claims from a paper you know well
2. **Connect them:** Build relationships between the claims
3. **Search:** Practice finding your claims with different queries
4. **Expand:** Gradually add more knowledge
5. **Explore:** Use lineage tracing to discover connections

### Learning Resources

| Resource | Description |
|----------|-------------|
| [Quick Start Guide](QUICK_START.md) | 12 hands-on use cases to learn the basics |
| [Advanced Examples](ADVANCED_EXAMPLES.md) | 15 power-user scenarios: discover hidden connections, generate hypotheses, uncover "new facts" |
| [Architecture](ARCHITECTURE.md) | How the system works internally |
| [Developer Guide](DEVELOPER_GUIDE.md) | For those who want to extend the system |

### Verify Your Setup

After installation, you can run the automated tests to make sure everything works:

```bash
# Run 12 use cases from the Quick Start guide
uv run python tests/test_quick_start.py

# Run 8 advanced scenarios
uv run python tests/test_advanced_examples.py
```

All tests should pass (20/20 total). If any fail, check your API key and dependencies.

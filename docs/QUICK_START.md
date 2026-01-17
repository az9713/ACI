# Quick Start Guide: 12 Hands-On Use Cases

Welcome! This guide will teach you Knowledge Graph CLI through practical examples. Each use case builds on previous ones, so follow in order for the best experience.

## Before You Begin

Make sure you have:
1. Knowledge Graph CLI installed and configured (see [README](../README.md))
2. Claude Code or Claude Desktop running
3. The MCP server added

Test your setup by asking Claude:
```
"List propositions in my knowledge graph"
```

Claude should respond (empty graph is fine for now).

---

## Use Case 1: Your First Hypothesis

**Goal:** Add your first scientific claim to the knowledge graph.

**Try this:**
```
"Ingest the hypothesis that water boils at 100 degrees Celsius at sea level"
```

**What happens:**
- Claude creates an atomic unit with your claim
- Generates an embedding (for semantic search)
- Returns the unit ID

**Expected response:**
```
Successfully ingested hypothesis:
- Unit ID: abc123-...
- Content: "Water boils at 100 degrees Celsius at sea level"
```

**Congratulations!** You've added your first piece of knowledge.

---

## Use Case 2: Adding a Source

**Goal:** Add a claim with attribution to its source.

**Try this:**
```
"Ingest the hypothesis that the speed of light is approximately 299,792 kilometers per second, from Einstein's theory of special relativity"
```

**What happens:**
- Claude adds the claim with source information
- The source helps you remember where the claim came from

**Why this matters:**
When your knowledge graph grows, sources help you:
- Verify claims
- Find original papers
- Build bibliographies

---

## Use Case 3: Multiple Related Claims

**Goal:** Add several claims about one topic to build a knowledge cluster.

**Try these (one at a time):**
```
"Ingest: Neural networks are computational models inspired by biological brains"
```

```
"Ingest: Neural networks consist of interconnected nodes organized in layers"
```

```
"Ingest: Deep learning refers to neural networks with many hidden layers"
```

```
"Ingest: Each layer in a neural network transforms its input before passing to the next"
```

**What you've built:**
Four related claims about neural networks, ready to be connected.

---

## Use Case 4: Connecting Ideas

**Goal:** Create a relationship between two claims.

**First, find your units:**
```
"List propositions in my knowledge graph"
```

Note the IDs of the neural network claims.

**Then connect them:**
```
"Connect the claim about neural networks being inspired by brains to the claim about interconnected nodes, with a 'supports' relationship. The reasoning is: the node structure mimics how neurons connect in biological brains."
```

**What happens:**
- Claude creates an edge in the graph
- Your reasoning is stored with the connection

**Try another:**
```
"Connect the deep learning definition to the neural network layers claim, with an 'extends' relationship. The reasoning is: deep learning is a specific case of neural networks with many layers."
```

---

## Use Case 5: Your First Search

**Goal:** Find knowledge using natural language.

**Try this:**
```
"Search for concepts related to how brains inspire computing"
```

**What happens:**
- Claude converts your query to meaning (embedding)
- Finds similar claims by semantic similarity
- Returns ranked results

**Expected results:**
Your neural network claims should appear, even though you searched for "brains" and "computing" instead of "neural networks."

**Try variations:**
```
"Search for information about deep learning"
```

```
"Search for concepts about layered computational structures"
```

Notice how different phrasings find relevant content.

---

## Use Case 6: Exploring a Unit

**Goal:** See all details and connections for a specific claim.

**Try this:**
```
"Get details for unit [paste an ID from your list]"
```

**What you'll see:**
- The full claim text
- Its source (if provided)
- All connections (incoming and outgoing)
- Suggested next actions

**Why this matters:**
This helps you navigate your knowledge graph, following connections to explore related ideas.

---

## Use Case 7: Building a Research Topic

**Goal:** Build a comprehensive knowledge cluster about transformers.

**Add these claims:**
```
"Ingest: The Transformer architecture was introduced in the paper 'Attention Is All You Need' in 2017, from Vaswani et al."
```

```
"Ingest: Transformers use self-attention mechanisms to process sequences in parallel"
```

```
"Ingest: Self-attention allows each position in a sequence to attend to all other positions"
```

```
"Ingest: BERT (Bidirectional Encoder Representations from Transformers) uses transformer encoders for language understanding, from Devlin et al. 2018"
```

```
"Ingest: GPT (Generative Pre-trained Transformer) uses transformer decoders for text generation, from OpenAI"
```

**Connect them:**
```
"Connect the self-attention claim to the Transformer architecture claim, as 'supports'. Reasoning: Self-attention is the core mechanism that makes transformers work."
```

```
"Connect BERT to the Transformer architecture as 'extends'. Reasoning: BERT builds on the transformer encoder architecture."
```

```
"Connect GPT to the Transformer architecture as 'extends'. Reasoning: GPT builds on the transformer decoder architecture."
```

---

## Use Case 8: Finding Intellectual Lineage

**Goal:** Trace how one concept connects to another.

**Try this:**
```
"Find the scientific lineage from neural networks to GPT"
```

**What happens:**
- Claude finds claims matching "neural networks" and "GPT"
- Traces the path through your connected claims
- Shows each step with the relationship

**Expected path:**
```
Neural networks → Deep learning → Transformers → GPT
```

(Path depends on what you've ingested and connected)

**Try another:**
```
"Find the intellectual lineage from biological brains to modern language models"
```

---

## Use Case 9: Checking for Contradictions

**Goal:** Verify that a new claim doesn't conflict with existing knowledge.

**First, add a claim:**
```
"Ingest: Recurrent neural networks (RNNs) process sequences one step at a time"
```

**Now check a potentially conflicting claim:**
```
"Check if the claim 'RNNs process entire sequences in parallel' contradicts anything in my knowledge graph"
```

**What happens:**
- Claude searches for related claims
- Checks for conflicts
- Reports potential contradictions

**Why this matters:**
Before accepting new information, you can verify it doesn't contradict your established knowledge.

---

## Use Case 10: Building a Contradiction

**Goal:** Explicitly mark when claims conflict.

**Add conflicting claims:**
```
"Ingest: Larger language models always perform better than smaller ones"
```

```
"Ingest: Some smaller, specialized models outperform larger general-purpose models on specific tasks, from various benchmark studies"
```

**Connect them as contradiction:**
```
"Connect the claim about smaller specialized models to the claim about larger models always being better, with a 'contradicts' relationship. Reasoning: Benchmark results show that the 'bigger is always better' claim is oversimplified."
```

**Now search:**
```
"Find contradictions related to model size and performance"
```

You'll see both claims and their conflicting relationship.

---

## Use Case 11: Building a Literature Review

**Goal:** Use Knowledge Graph CLI to organize knowledge for a paper.

**Scenario:** You're writing about attention mechanisms.

**Step 1: Add key papers**
```
"Ingest: Attention mechanisms were first applied to sequence-to-sequence models for machine translation, from Bahdanau et al. 2014"
```

```
"Ingest: The Transformer replaced recurrence with self-attention for improved parallelization, from Vaswani et al. 2017"
```

```
"Ingest: Multi-head attention allows the model to attend to information from different representation subspaces, from Vaswani et al. 2017"
```

**Step 2: Connect the evolution**
```
"Connect the Transformer paper to the Bahdanau attention paper as 'extends'. Reasoning: Transformers generalized the attention concept from the earlier work."
```

**Step 3: Search for your topic**
```
"Search for concepts about attention in neural networks"
```

**Step 4: Trace the history**
```
"Find the lineage from early attention mechanisms to multi-head attention"
```

**You now have:**
- Organized claims from papers
- Connected timeline of developments
- Searchable knowledge base for writing

---

## Use Case 12: Cross-Domain Knowledge

**Goal:** Build knowledge spanning multiple fields and find unexpected connections.

**Add claims from different domains:**

**Physics:**
```
"Ingest: Entropy measures the disorder or randomness in a system, from thermodynamics"
```

**Information Theory:**
```
"Ingest: Information entropy measures the average information content in a message, from Shannon 1948"
```

**Machine Learning:**
```
"Ingest: Cross-entropy loss measures the difference between predicted and true probability distributions"
```

**Connect across domains:**
```
"Connect information entropy to thermodynamic entropy as 'extends'. Reasoning: Shannon explicitly drew on thermodynamic entropy when formulating information entropy."
```

```
"Connect cross-entropy loss to information entropy as 'extends'. Reasoning: Cross-entropy in ML is a direct application of Shannon's information entropy."
```

**Search across domains:**
```
"Search for concepts related to measuring disorder or uncertainty"
```

**Find the lineage:**
```
"Find the intellectual lineage from thermodynamics to machine learning loss functions"
```

**This demonstrates:**
How Knowledge Graph CLI can reveal connections across different fields that might not be obvious.

---

## Practice Exercises

Try these on your own:

### Exercise 1: Your Research Area
Add 5 key claims from your own field of study. Connect them. Search for them.

### Exercise 2: Book Summary
Take a chapter from a textbook. Extract 3-5 key claims. Add them with the book as source.

### Exercise 3: Debate Mapping
Find a scientific debate (e.g., nature vs. nurture). Add claims from both sides. Mark contradictions.

### Exercise 4: Concept Genealogy
Pick a modern technology. Trace its intellectual ancestors. Build the lineage in your knowledge graph.

### Exercise 5: Paper Reading
Read a research paper. Extract the main claims. Add them with proper attribution. Connect to existing knowledge.

---

## What's Next?

You've learned to:
- [x] Add claims (atomic units)
- [x] Include sources
- [x] Build knowledge clusters
- [x] Connect related ideas
- [x] Search semantically
- [x] Explore individual units
- [x] Find intellectual lineages
- [x] Detect contradictions
- [x] Build cross-domain knowledge

**Suggested next steps:**

1. **Build your personal knowledge graph** - Start adding claims from your daily reading
2. **Try Advanced Examples** - [ADVANCED_EXAMPLES.md](ADVANCED_EXAMPLES.md) for 15 power-user scenarios that showcase discovering hidden connections, generating new hypotheses, and uncovering "new facts"
3. **Read the full User Guide** - [USER_GUIDE.md](USER_GUIDE.md) for complete documentation
4. **Explore advanced patterns** - Try complex queries and lineage tracing
5. **Contribute** - If you're a developer, see the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

## Quick Reference

| What you want | What to say |
|---------------|-------------|
| Add a claim | "Ingest the hypothesis that [claim]" |
| Add with source | "Ingest [claim], from [source]" |
| Connect claims | "Connect [unit A] to [unit B] with [relation]. Reasoning: [why]" |
| Search | "Search for concepts about [topic]" |
| Get details | "Get details for unit [id]" |
| Find path | "Find the lineage from [concept A] to [concept B]" |
| Check conflicts | "Check if [claim] contradicts anything" |
| Browse all | "List propositions in my knowledge graph" |
| Delete a claim | "Delete unit [id]" (requires confirmation) |

**Relation types:**
- `supports` - A provides evidence for B
- `refutes` - A contradicts/disproves B
- `extends` - A builds upon B
- `implies` - If A then B
- `contradicts` - A and B are mutually exclusive

---

## Troubleshooting

**"Tool not found"**
- Restart Claude Code/Desktop
- Re-add the MCP server

**"OPENAI_API_KEY not set"**
- Create `.env` file with your key
- Restart the application

**"Unit not found"**
- Use `list_propositions` to see available IDs
- Copy the exact ID

**Search returns nothing**
- Try different wording
- Check if you have any data (`list_propositions`)

**Lineage returns only start and end**
- The concepts might not be connected
- Add intermediate claims and connections

---

## Automated Testing

All 12 use cases in this guide are covered by automated tests. You can run them to verify your setup works correctly:

```bash
# Run all Quick Start use cases
uv run python tests/test_quick_start.py
```

**Expected output:**
```
[START] KNOWLEDGE GRAPH CLI QUICK START TEST SUITE
...
[END] TEST RESULTS SUMMARY
   UC1: [OK] PASS  Your First Hypothesis
   UC2: [OK] PASS  Adding a Source
   ...
   UC12: [OK] PASS Cross-Domain Knowledge
[SUMMARY] Total: 12/12 use cases passed
[SUCCESS] ALL TESTS PASSED!
```

The tests:
- Ingest real claims using the OpenAI API
- Create connections between units
- Perform semantic searches
- Trace intellectual lineages
- Verify all documented functionality works

If any tests fail, check:
1. Your `OPENAI_API_KEY` is set correctly in `.env`
2. You've run `uv sync` to install dependencies
3. Your internet connection is working

---

Happy knowledge building!

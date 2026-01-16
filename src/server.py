"""MCP Server for Agent-Computer-Interaction Knowledge Graph."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

from .model import (
    AtomicUnit,
    Relation,
    RelationType,
    AvailableAction,
    UnitResponse,
    ConnectionResponse,
    SearchResult,
    SearchResponse,
    LineageResponse,
    ConflictResponse,
    get_unit_actions,
)
from .graph_engine import KnowledgeGraph


# Initialize MCP server with instructions for Claude
mcp = FastMCP(
    "Atomic Graph Researcher",
    instructions="""
    Use this server for scientific knowledge management:
    - Ingesting hypotheses and claims from papers
    - Finding intellectual lineages between concepts
    - Detecting contradictions in accumulated knowledge
    - Semantic search across your research graph

    Best practices:
    - Use ingest_hypothesis for new scientific claims
    - Use connect_propositions to build relationships
    - Use find_scientific_lineage to trace idea evolution
    - Use find_contradictions before accepting new claims
    - Use semantic_search to explore related concepts
    """,
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"

# Lazy initialization of graph (to allow OPENAI_API_KEY to be set)
_graph: Optional[KnowledgeGraph] = None


def get_graph() -> KnowledgeGraph:
    """Get or initialize the knowledge graph."""
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph(DATA_DIR)
    return _graph


@mcp.tool()
def ingest_hypothesis(
    hypothesis: str,
    source: str = "",
    confidence: float = 1.0,
    idempotency_key: Optional[str] = None,
) -> dict:
    """
    Ingests a new scientific claim/hypothesis into the knowledge graph.

    Use this when:
    - The user states a new scientific fact or finding
    - Summarizing key claims from a paper
    - Recording your own research hypotheses

    Args:
        hypothesis: The scientific claim or proposition to ingest
        source: DOI or source reference (e.g., "Vaswani et al. 2017")
        confidence: Confidence score from 0.0 to 1.0 (default: 1.0)
        idempotency_key: Optional key to prevent duplicate ingestion on retry

    Example: ingest_hypothesis("Attention scales quadratically with sequence length", "Vaswani et al. 2017")

    Returns the created unit ID and available follow-up actions.
    """
    graph = get_graph()

    # Check idempotency
    if idempotency_key:
        cached = graph.persistence.check_idempotency(idempotency_key)
        if cached:
            return cached

    # Add the proposition
    unit = graph.add_proposition(
        content=hypothesis,
        source_doi=source if source else None,
        confidence=confidence,
    )

    result = {
        "status": "success",
        "unit_id": unit.id,
        "content": unit.content,
        "source": unit.source_doi,
        "confidence": unit.confidence,
        "available_actions": [
            {"tool": "connect_propositions", "description": "Link to another unit", "suggested_args": {"id_a": unit.id}},
            {"tool": "semantic_search", "description": "Find related concepts"},
            {"tool": "find_contradictions", "description": "Check for conflicts with this claim", "suggested_args": {"claim": unit.content}},
        ],
    }

    # Cache for idempotency
    if idempotency_key:
        graph.persistence.store_idempotency(idempotency_key, result)

    return result


@mcp.tool()
def connect_propositions(
    id_a: str,
    id_b: str,
    relation: str,
    reasoning: str,
    idempotency_key: Optional[str] = None,
) -> dict:
    """
    Creates a relationship between two atomic units in the knowledge graph.

    Use this when:
    - One claim supports or refutes another
    - An idea extends or implies another
    - You identify intellectual dependencies between concepts

    Args:
        id_a: ID of the source unit
        id_b: ID of the target unit
        relation: Type of relationship - one of: supports, refutes, extends, implies, contradicts
        reasoning: Explanation for why this relation exists
        idempotency_key: Optional key to prevent duplicate connection on retry

    Example: connect_propositions("unit_123", "unit_456", "supports", "Both discuss attention mechanisms")

    Returns connection details and available follow-up actions.
    """
    graph = get_graph()

    # Validate relation type
    valid_relations = ["supports", "refutes", "extends", "implies", "contradicts"]
    if relation not in valid_relations:
        return {
            "status": "error",
            "message": f"Invalid relation type. Must be one of: {valid_relations}",
        }

    # Check idempotency
    if idempotency_key:
        cached = graph.persistence.check_idempotency(idempotency_key)
        if cached:
            return cached

    try:
        rel = graph.connect_concepts(
            source_id=id_a,
            target_id=id_b,
            relation_type=relation,
            reasoning=reasoning,
        )

        source_unit = graph.get_unit(id_a)
        target_unit = graph.get_unit(id_b)

        result = {
            "status": "success",
            "relation": {
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "type": rel.type,
                "reasoning": rel.reasoning,
            },
            "source_content": source_unit.content if source_unit else None,
            "target_content": target_unit.content if target_unit else None,
            "available_actions": [
                {"tool": "find_scientific_lineage", "description": "Trace the intellectual path"},
                {"tool": "find_contradictions", "description": "Check for conflicts"},
                {"tool": "semantic_search", "description": "Find related concepts"},
            ],
        }

        # Cache for idempotency
        if idempotency_key:
            graph.persistence.store_idempotency(idempotency_key, result)

        return result

    except ValueError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def find_scientific_lineage(
    start_concept: str,
    end_concept: str,
) -> dict:
    """
    Traces the intellectual dependency path between two concepts.

    Use this when:
    - Understanding how one idea led to another
    - Tracing the evolution of a scientific concept
    - Finding the chain of reasoning between related claims

    Args:
        start_concept: Natural language description of the starting concept
        end_concept: Natural language description of the ending concept

    Example: find_scientific_lineage("attention mechanism", "transformer architecture")

    Returns the chain of units with their relationships and reasoning.
    """
    graph = get_graph()

    try:
        steps = graph.find_path(start_concept, end_concept)

        path_data = []
        for step in steps:
            step_dict = {
                "unit_id": step.unit.id,
                "content": step.unit.content,
                "source": step.unit.source_doi,
            }
            if step.relation_to_next:
                step_dict["relation_to_next"] = {
                    "type": step.relation_to_next.type,
                    "reasoning": step.relation_to_next.reasoning,
                }
            path_data.append(step_dict)

        return {
            "status": "success",
            "start_concept": start_concept,
            "end_concept": end_concept,
            "path_length": len(steps),
            "path": path_data,
            "available_actions": [
                {"tool": "get_unit", "description": "Get details of any unit in the path"},
                {"tool": "connect_propositions", "description": "Add more connections to the lineage"},
            ],
        }

    except ValueError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def find_contradictions(claim: str) -> dict:
    """
    Checks if a claim contradicts existing knowledge in the graph.

    Use this when:
    - Validating a new hypothesis against existing knowledge
    - Looking for papers/claims that disagree
    - Ensuring consistency in your knowledge base

    Args:
        claim: The claim to check for contradictions

    Example: find_contradictions("Attention is linear in sequence length")

    Returns conflicts found with explanations.
    """
    graph = get_graph()

    conflicts = graph.get_conflicts(claim)

    conflict_data = []
    for c in conflicts:
        conflict_dict = {
            "unit_id": c.conflicting_unit.id,
            "content": c.conflicting_unit.content,
            "source": c.conflicting_unit.source_doi,
            "explanation": c.explanation,
        }
        if c.relation:
            conflict_dict["relation"] = {
                "type": c.relation.type,
                "reasoning": c.relation.reasoning,
            }
        conflict_data.append(conflict_dict)

    return {
        "status": "success",
        "claim": claim,
        "conflicts_found": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicts": conflict_data,
        "available_actions": [
            {"tool": "ingest_hypothesis", "description": "Add this claim despite conflicts"},
            {"tool": "connect_propositions", "description": "Create explicit contradiction relationship"},
            {"tool": "semantic_search", "description": "Find more related concepts"},
        ],
    }


@mcp.tool()
def semantic_search(query: str, limit: int = 5) -> dict:
    """
    Finds atomic units semantically similar to the query.

    Use this when:
    - Exploring what's in the knowledge graph
    - Finding related concepts to a topic
    - Looking for prior art on a hypothesis

    Args:
        query: Natural language search query
        limit: Maximum number of results (default: 5, max: 20)

    Example: semantic_search("transformer attention mechanisms", limit=10)

    Returns ranked results with similarity scores.
    """
    graph = get_graph()

    # Cap limit
    limit = min(limit, 20)

    results = graph.semantic_search(query, limit=limit)

    result_data = []
    for unit, score in results:
        result_data.append({
            "unit_id": unit.id,
            "content": unit.content,
            "source": unit.source_doi,
            "confidence": unit.confidence,
            "similarity_score": round(score, 4),
            "available_actions": get_unit_actions(unit.id),
        })

    return {
        "status": "success",
        "query": query,
        "total_found": len(results),
        "results": result_data,
    }


@mcp.tool()
def list_propositions(limit: int = 20) -> dict:
    """
    Lists recent propositions in the knowledge graph.

    Use this when:
    - Browsing the knowledge base
    - Getting an overview of stored claims
    - Finding units to connect

    Args:
        limit: Maximum number of results (default: 20, max: 50)

    Returns list of propositions with their metadata.
    """
    graph = get_graph()

    # Cap limit
    limit = min(limit, 50)

    units = graph.list_propositions(limit=limit)

    unit_data = []
    for unit in units:
        unit_data.append({
            "unit_id": unit.id,
            "content": unit.content,
            "source": unit.source_doi,
            "confidence": unit.confidence,
        })

    return {
        "status": "success",
        "count": len(units),
        "propositions": unit_data,
        "available_actions": [
            {"tool": "ingest_hypothesis", "description": "Add a new proposition"},
            {"tool": "semantic_search", "description": "Search for specific concepts"},
        ],
    }


@mcp.tool()
def get_unit(unit_id: str) -> dict:
    """
    Retrieves a single atomic unit by ID with its connections.

    Use this when:
    - Getting full details of a specific unit
    - Examining a unit's relationships
    - Following up on search results

    Args:
        unit_id: The ID of the unit to retrieve

    Returns the unit with its connections and available actions.
    """
    graph = get_graph()

    unit = graph.get_unit(unit_id)
    if not unit:
        return {"status": "error", "message": f"Unit not found: {unit_id}"}

    connections = graph.get_unit_connections(unit_id)

    connection_data = []
    for rel in connections:
        conn = {
            "type": rel.type,
            "reasoning": rel.reasoning,
        }
        if rel.source_id == unit_id:
            conn["direction"] = "outgoing"
            conn["connected_to"] = rel.target_id
            other_unit = graph.get_unit(rel.target_id)
            if other_unit:
                conn["connected_content"] = other_unit.content
        else:
            conn["direction"] = "incoming"
            conn["connected_from"] = rel.source_id
            other_unit = graph.get_unit(rel.source_id)
            if other_unit:
                conn["connected_content"] = other_unit.content
        connection_data.append(conn)

    return {
        "status": "success",
        "unit": {
            "id": unit.id,
            "content": unit.content,
            "source": unit.source_doi,
            "confidence": unit.confidence,
        },
        "connections": connection_data,
        "connection_count": len(connections),
        "available_actions": get_unit_actions(unit_id),
    }


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

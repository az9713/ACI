"""Data models for the ACI Knowledge Graph."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


RelationType = Literal["supports", "refutes", "extends", "implies", "contradicts"]


class AtomicUnit(BaseModel):
    """Core proposition/claim model - the atomic unit of knowledge."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., description="The proposition text")
    source_doi: Optional[str] = Field(None, description="DOI or source reference")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(default_factory=datetime.now)
    vector: list[float] = Field(default_factory=list, description="Embedding vector")


class Relation(BaseModel):
    """Edge model representing relationships between atomic units."""

    source_id: str = Field(..., description="ID of the source unit")
    target_id: str = Field(..., description="ID of the target unit")
    type: RelationType = Field(..., description="Type of relationship")
    reasoning: str = Field(..., description="Explanation for why this relation exists")
    created_at: datetime = Field(default_factory=datetime.now)


class AvailableAction(BaseModel):
    """HATEOAS action suggestion for agents."""

    tool: str = Field(..., description="Tool name to invoke")
    description: str = Field(..., description="What this action does")
    suggested_args: Optional[dict] = Field(None, description="Suggested arguments")


class UnitResponse(BaseModel):
    """Response model for unit operations with HATEOAS actions."""

    unit: AtomicUnit
    available_actions: list[AvailableAction] = Field(default_factory=list)


class ConnectionResponse(BaseModel):
    """Response model for connection operations."""

    relation: Relation
    source_unit: AtomicUnit
    target_unit: AtomicUnit
    available_actions: list[AvailableAction] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Single search result with relevance score."""

    unit: AtomicUnit
    score: float = Field(..., description="Similarity score")
    available_actions: list[AvailableAction] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response model for semantic search."""

    query: str
    results: list[SearchResult]
    total_found: int


class LineageStep(BaseModel):
    """A step in an intellectual lineage path."""

    unit: AtomicUnit
    relation_to_next: Optional[Relation] = None


class LineageResponse(BaseModel):
    """Response model for lineage tracing."""

    start_concept: str
    end_concept: str
    path: list[LineageStep]
    path_length: int
    available_actions: list[AvailableAction] = Field(default_factory=list)


class ConflictResult(BaseModel):
    """A contradiction/conflict found in the knowledge graph."""

    conflicting_unit: AtomicUnit
    relation: Optional[Relation] = None
    explanation: str


class ConflictResponse(BaseModel):
    """Response model for contradiction detection."""

    claim: str
    conflicts_found: bool
    conflicts: list[ConflictResult]
    available_actions: list[AvailableAction] = Field(default_factory=list)


def get_unit_actions(unit_id: str) -> list[AvailableAction]:
    """Generate standard HATEOAS actions for a unit."""
    return [
        AvailableAction(
            tool="connect_propositions",
            description="Link this unit to another proposition",
            suggested_args={"id_a": unit_id}
        ),
        AvailableAction(
            tool="semantic_search",
            description="Find related concepts"
        ),
        AvailableAction(
            tool="find_contradictions",
            description="Check for conflicts with this claim"
        ),
        AvailableAction(
            tool="get_unit",
            description="Get full details of this unit",
            suggested_args={"unit_id": unit_id}
        ),
    ]

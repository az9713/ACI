"""Knowledge Graph engine combining LanceDB vectors with NetworkX graph."""

import os
from pathlib import Path
from typing import Optional

import lancedb
import networkx as nx
from openai import OpenAI
import pyarrow as pa

from .model import (
    AtomicUnit,
    Relation,
    RelationType,
    LineageStep,
    ConflictResult,
    get_unit_actions,
)
from .persistence import PersistenceManager


class KnowledgeGraph:
    """Core knowledge graph combining vector search with graph traversal."""

    EMBEDDING_MODEL = "text-embedding-ada-002"
    EMBEDDING_DIM = 1536

    def __init__(self, data_dir: Path, openai_api_key: Optional[str] = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenAI client
        api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly")
        self.openai_client = OpenAI(api_key=api_key)

        # Initialize LanceDB
        self.db = lancedb.connect(str(self.data_dir / "atomic_graph.lance"))
        self._init_table()

        # Initialize NetworkX graph
        self.graph = nx.DiGraph()

        # Initialize persistence
        self.persistence = PersistenceManager(self.data_dir)

        # Load existing relations into graph
        self._load_graph_from_persistence()

    def _init_table(self) -> None:
        """Initialize LanceDB table if it doesn't exist."""
        if "units" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("content", pa.string()),
                pa.field("source_doi", pa.string()),
                pa.field("confidence", pa.float64()),
                pa.field("created_at", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), self.EMBEDDING_DIM)),
            ])
            self.db.create_table("units", schema=schema)

        self.table = self.db.open_table("units")

    def _load_graph_from_persistence(self) -> None:
        """Load all relations from persistence into NetworkX graph."""
        relations = self.persistence.get_all_relations()
        for relation in relations:
            self.graph.add_edge(
                relation.source_id,
                relation.target_id,
                type=relation.type,
                reasoning=relation.reasoning,
            )

    def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.EMBEDDING_MODEL,
        )
        return response.data[0].embedding

    def add_proposition(
        self,
        content: str,
        source_doi: Optional[str] = None,
        confidence: float = 1.0,
        unit_id: Optional[str] = None,
    ) -> AtomicUnit:
        """Create a new atomic unit, embed it, and store in LanceDB."""
        # Generate embedding
        vector = self._get_embedding(content)

        # Create unit
        unit = AtomicUnit(
            content=content,
            source_doi=source_doi,
            confidence=confidence,
            vector=vector,
        )

        if unit_id:
            unit.id = unit_id

        # Store in LanceDB
        self.table.add([{
            "id": unit.id,
            "content": unit.content,
            "source_doi": unit.source_doi or "",
            "confidence": unit.confidence,
            "created_at": unit.created_at.isoformat(),
            "vector": unit.vector,
        }])

        # Add node to graph
        self.graph.add_node(unit.id, content=unit.content)

        return unit

    def get_unit(self, unit_id: str) -> Optional[AtomicUnit]:
        """Retrieve a unit by ID."""
        results = self.table.search().where(f"id = '{unit_id}'", prefilter=True).limit(1).to_list()
        if not results:
            return None

        row = results[0]
        return AtomicUnit(
            id=row["id"],
            content=row["content"],
            source_doi=row["source_doi"] if row["source_doi"] else None,
            confidence=row["confidence"],
            vector=row["vector"],
        )

    def connect_concepts(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        reasoning: str,
    ) -> Relation:
        """Create a relationship between two atomic units."""
        # Verify both units exist
        source = self.get_unit(source_id)
        target = self.get_unit(target_id)

        if not source:
            raise ValueError(f"Source unit not found: {source_id}")
        if not target:
            raise ValueError(f"Target unit not found: {target_id}")

        # Create relation
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            type=relation_type,
            reasoning=reasoning,
        )

        # Add to graph
        self.graph.add_edge(
            source_id,
            target_id,
            type=relation_type,
            reasoning=reasoning,
        )

        # Persist
        self.persistence.add_relation(relation)

        return relation

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[AtomicUnit, float]]:
        """Find atomic units semantically similar to query."""
        query_vector = self._get_embedding(query)

        results = (
            self.table.search(query_vector)
            .metric("cosine")
            .limit(limit)
            .to_list()
        )

        units_with_scores = []
        for row in results:
            unit = AtomicUnit(
                id=row["id"],
                content=row["content"],
                source_doi=row["source_doi"] if row["source_doi"] else None,
                confidence=row["confidence"],
                vector=row["vector"],
            )
            # LanceDB returns _distance for cosine, convert to similarity
            score = 1 - row.get("_distance", 0)
            units_with_scores.append((unit, score))

        return units_with_scores

    def find_path(
        self,
        start_concept: str,
        end_concept: str,
    ) -> list[LineageStep]:
        """Find intellectual lineage path between two concepts.

        Uses semantic search to find nodes matching the concepts,
        then graph traversal to find the shortest path.
        """
        # Find nodes matching start concept
        start_results = self.semantic_search(start_concept, limit=3)
        if not start_results:
            raise ValueError(f"No units found matching: {start_concept}")

        # Find nodes matching end concept
        end_results = self.semantic_search(end_concept, limit=3)
        if not end_results:
            raise ValueError(f"No units found matching: {end_concept}")

        # Try to find path between best matches
        best_path = None
        best_path_length = float("inf")

        for start_unit, _ in start_results:
            for end_unit, _ in end_results:
                if start_unit.id == end_unit.id:
                    continue

                try:
                    # Try undirected path first
                    path = nx.shortest_path(
                        self.graph.to_undirected(),
                        start_unit.id,
                        end_unit.id,
                    )
                    if len(path) < best_path_length:
                        best_path = path
                        best_path_length = len(path)
                except nx.NetworkXNoPath:
                    continue

        if not best_path:
            # Return start and end as disconnected
            return [
                LineageStep(unit=start_results[0][0], relation_to_next=None),
                LineageStep(unit=end_results[0][0], relation_to_next=None),
            ]

        # Build lineage steps
        steps = []
        for i, node_id in enumerate(best_path):
            unit = self.get_unit(node_id)
            if not unit:
                continue

            relation = None
            if i < len(best_path) - 1:
                next_id = best_path[i + 1]
                # Check for edge in either direction
                if self.graph.has_edge(node_id, next_id):
                    edge_data = self.graph.edges[node_id, next_id]
                    relation = Relation(
                        source_id=node_id,
                        target_id=next_id,
                        type=edge_data["type"],
                        reasoning=edge_data["reasoning"],
                    )
                elif self.graph.has_edge(next_id, node_id):
                    edge_data = self.graph.edges[next_id, node_id]
                    relation = Relation(
                        source_id=next_id,
                        target_id=node_id,
                        type=edge_data["type"],
                        reasoning=edge_data["reasoning"],
                    )

            steps.append(LineageStep(unit=unit, relation_to_next=relation))

        return steps

    def get_conflicts(self, claim: str) -> list[ConflictResult]:
        """Find units that may contradict the given claim.

        Searches for semantically similar units and checks for
        'refutes' or 'contradicts' relations.
        """
        # Find similar units
        similar = self.semantic_search(claim, limit=10)
        conflicts = []

        for unit, score in similar:
            # Skip low similarity
            if score < 0.5:
                continue

            # Check if this unit has any refutes/contradicts relations
            relations = self.persistence.get_relations_for_unit(unit.id)

            for rel in relations:
                if rel.type in ("refutes", "contradicts"):
                    conflicts.append(ConflictResult(
                        conflicting_unit=unit,
                        relation=rel,
                        explanation=f"This unit has a '{rel.type}' relationship: {rel.reasoning}",
                    ))
                    break
            else:
                # No explicit contradiction, but high similarity might indicate conflict
                if score > 0.85:
                    conflicts.append(ConflictResult(
                        conflicting_unit=unit,
                        relation=None,
                        explanation=f"Highly similar (score: {score:.2f}) but potentially conflicting content",
                    ))

        return conflicts

    def list_propositions(self, limit: int = 20) -> list[AtomicUnit]:
        """List recent propositions in the graph."""
        results = self.table.search().limit(limit).to_list()

        units = []
        for row in results:
            unit = AtomicUnit(
                id=row["id"],
                content=row["content"],
                source_doi=row["source_doi"] if row["source_doi"] else None,
                confidence=row["confidence"],
                vector=row["vector"],
            )
            units.append(unit)

        return units

    def get_unit_connections(self, unit_id: str) -> list[Relation]:
        """Get all relations connected to a unit."""
        return self.persistence.get_relations_for_unit(unit_id)

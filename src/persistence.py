"""Persistence layer for relations and idempotency cache."""

import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from .model import Relation


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def datetime_decoder(dct: dict) -> dict:
    """Decode datetime strings back to datetime objects."""
    for key in ["created_at"]:
        if key in dct and isinstance(dct[key], str):
            try:
                dct[key] = datetime.fromisoformat(dct[key])
            except ValueError:
                pass
    return dct


class PersistenceManager:
    """Manages JSON-based persistence for relations and idempotency keys."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.relations_file = self.data_dir / "relations.json"
        self.idempotency_file = self.data_dir / "idempotency.json"

        self._relations: list[dict] = []
        self._idempotency_cache: dict[str, Any] = {}

        self._load()

    def _load(self) -> None:
        """Load relations and idempotency cache from disk."""
        if self.relations_file.exists():
            with open(self.relations_file, "r") as f:
                self._relations = json.load(f, object_hook=datetime_decoder)

        if self.idempotency_file.exists():
            with open(self.idempotency_file, "r") as f:
                self._idempotency_cache = json.load(f)

    def _save_relations(self) -> None:
        """Save relations to disk."""
        with open(self.relations_file, "w") as f:
            json.dump(self._relations, f, indent=2, cls=DateTimeEncoder)

    def _save_idempotency(self) -> None:
        """Save idempotency cache to disk."""
        with open(self.idempotency_file, "w") as f:
            json.dump(self._idempotency_cache, f, indent=2, cls=DateTimeEncoder)

    def get_all_relations(self) -> list[Relation]:
        """Get all stored relations."""
        return [Relation(**r) for r in self._relations]

    def add_relation(self, relation: Relation) -> None:
        """Add a new relation and persist."""
        self._relations.append(relation.model_dump())
        self._save_relations()

    def get_relations_for_unit(self, unit_id: str) -> list[Relation]:
        """Get all relations involving a specific unit."""
        return [
            Relation(**r)
            for r in self._relations
            if r["source_id"] == unit_id or r["target_id"] == unit_id
        ]

    def relation_exists(self, source_id: str, target_id: str, relation_type: str) -> bool:
        """Check if a specific relation already exists."""
        for r in self._relations:
            if (
                r["source_id"] == source_id
                and r["target_id"] == target_id
                and r["type"] == relation_type
            ):
                return True
        return False

    def check_idempotency(self, key: str) -> Optional[Any]:
        """Check if an idempotency key exists and return cached result."""
        return self._idempotency_cache.get(key)

    def store_idempotency(self, key: str, result: Any) -> None:
        """Store result for an idempotency key."""
        self._idempotency_cache[key] = result
        self._save_idempotency()

    def clear_idempotency_cache(self) -> int:
        """Clear all idempotency keys. Returns count of cleared keys."""
        count = len(self._idempotency_cache)
        self._idempotency_cache = {}
        self._save_idempotency()
        return count

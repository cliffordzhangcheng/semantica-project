#!/usr/bin/env python3
"""Evidence validator - validate evidence for entities and relationships"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class EvidenceValidationError(Exception):
    """Raised when evidence validation fails"""


class EvidenceValidator:
    """Validate evidence objects against schema requirements"""

    REQUIRED_EVIDENCE_FIELDS = {
        "evidence_id",
        "source_id",
        "source_document_id",
        "locator",
        "text_basis",
        "extractor",
    }

    def validate_evidence(self, evidence: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        missing = self.REQUIRED_EVIDENCE_FIELDS - set(evidence.keys())
        if missing:
            errors.append(f"Evidence missing required fields: {sorted(missing)}")
        if evidence.get("evidence_id") == "" or evidence.get("source_id") == "":
            errors.append("evidence_id and source_id must be non-empty")
        return errors

    def validate_entity_evidence(self, entity: dict[str, Any]) -> list[str]:
        errors = self.validate_evidence(entity.get("provenance", {}))
        if not entity.get("id"):
            errors.append("Entity missing id")
        if not entity.get("name"):
            errors.append("Entity missing name")
        return errors

    def validate_relationship_evidence(
        self, relationship: dict[str, Any]
    ) -> list[str]:
        errors = self.validate_evidence(relationship.get("provenance", {}))
        if not relationship.get("source"):
            errors.append("Relationship missing source")
        if not relationship.get("target"):
            errors.append("Relationship missing target")
        return errors

    def validate_graph(self, graph: dict[str, Any]) -> dict[str, list[str]]:
        entity_errors: list[str] = []
        rel_errors: list[str] = []
        for entity in graph.get("entities", []):
            entity_errors.extend(self.validate_entity_evidence(entity))
        for rel in graph.get("relationships", []):
            rel_errors.extend(self.validate_relationship_evidence(rel))
        return {"entity_errors": entity_errors, "relationship_errors": rel_errors}

    @classmethod
    def from_file(cls, path: Path) -> dict[str, list[str]]:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls().validate_graph(data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: evidence_validator.py <graph.json>", file=sys.stderr)
        sys.exit(1)
    results = EvidenceValidator.from_file(Path(sys.argv[1]))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    if results["entity_errors"] or results["relationship_errors"]:
        sys.exit(1)

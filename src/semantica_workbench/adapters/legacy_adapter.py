#!/usr/bin/env python3
"""Legacy adapter - convert old formats to canonical graph"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class LegacyAdapter:
    """Convert legacy node/edge format to canonical entities/relationships"""

    SUPPORTED_FORMATS = {"nodes_edges", "akos"}

    def convert(self, data: dict[str, Any], source_format: str) -> dict[str, Any]:
        if source_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unknown legacy format: {source_format}")
        if source_format == "nodes_edges":
            return self._convert_nodes_edges(data)
        if source_format == "akos":
            return self._convert_akos(data)
        raise NotImplementedError(source_format)  # pragma: no cover

    def _convert_nodes_edges(self, data: dict[str, Any]) -> dict[str, Any]:
        entities = []
        for node in data.get("nodes", []):
            entity = {
                "id": node.get("id"),
                "type": node.get("type", "Unknown"),
                "name": node.get("name"),
                "properties": node.get("properties", {}),
                "provenance": node.get("provenance", {}),
            }
            entities.append(entity)
        relationships = []
        for edge in data.get("edges", []):
            relationship = {
                "source": edge.get("source"),
                "target": edge.get("target"),
                "type": edge.get("type", "RELATED_TO"),
                "properties": edge.get("properties", {}),
                "provenance": edge.get("provenance", {}),
            }
            relationships.append(relationship)
        return {"entities": entities, "relationships": relationships}

    def _convert_akos(self, data: dict[str, Any]) -> dict[str, Any]:
        # akos format is already canonical, just validate structure
        if "entities" not in data and "relationships" not in data:
            raise ValueError("Invalid AKOS format: missing entities/relationships")
        return data

    @classmethod
    def from_file(cls, path: Path, source_format: str | None = None) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        fmt = source_format or cls._detect_format(data)
        return cls().convert(data, fmt)

    @staticmethod
    def _detect_format(data: dict[str, Any]) -> str:
        if "nodes" in data and "edges" in data:
            return "nodes_edges"
        if "entities" in data or "relationships" in data:
            return "akos"
        raise ValueError(f"Cannot detect format from keys: {list(data.keys())}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: legacy_adapter.py <input.json> <format>", file=sys.stderr)
        sys.exit(1)
    result = LegacyAdapter.from_file(Path(sys.argv[1]), sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))

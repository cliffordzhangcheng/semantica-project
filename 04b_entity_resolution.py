"""Entity Resolution — Mention → Canonical Entity → Ontology Class

Distinguishes three layers:
1. Mention: raw extraction occurrence with provenance
2. Canonical Entity: stable ID, merged across mentions
3. Ontology Class: schema-defined type from akos_domain_ontology.yaml

High-risk merges (ownership/funding/contract/payment/legal) require
human review — never auto-merge.
"""
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, ".")
from akos_adapter import write_audit, make_context

RISKY_CLASSES = {
    "CapitalProvider", "ProjectSPV", "ContainerOwner", "Carrier",
    "ContainerAgent", "Lessee", "Manufacturer", "Operator", "Founder",
    "CapitalCommitment", "PurchaseContract", "LeaseContract", "OneWayContract",
    "PLAContract", "InvoicePayment", "DecisionCard", "PUCMargin",
    "OffHireCondition", "DefaultChain",
}

HIGH_RISK_RELATIONS = {
    "funds", "owns", "commits", "purchased_under", "leased_under",
    "leased_to", "charters_under", "intermediates", "earns", "sells_to",
    "guarantees", "generates", "governs", "subject_to",
}


@dataclass
class Mention:
    mention_id: str
    text: str
    label: str
    doc_id: str
    start_char: int
    end_char: int
    confidence: float
    source_id: str
    extraction_method: str


@dataclass
class CanonicalEntity:
    entity_id: str
    canonical_type: str
    canonical_name: str
    mentions: list = field(default_factory=list)
    aliases: set = field(default_factory=set)
    properties: dict = field(default_factory=dict)
    risk_level: str = "low"
    review_required: bool = False
    merged_by: str = "exact"
    created_at: str = ""
    updated_at: str = ""


def load_ontology_schema(path: str = "config/akos_domain_ontology.yaml") -> dict:
    """Load canonical ontology schema. Returns {class_name: {aliases, ...}}."""
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    schema = {}
    for cls_name, cls_def in (data.get("classes") or {}).items():
        aliases = set(cls_def.get("aliases", []))
        aliases.add(cls_name)
        schema[cls_name] = {
            "aliases": aliases,
            "deprecated": set(cls_def.get("deprecated", [])),
            "identity_key": cls_def.get("identity_key", "name"),
            "required": cls_def.get("required", []),
            "provenance_required": cls_def.get("provenance_required", False),
        }
    return schema


def resolve_label(label: str, schema: dict) -> str:
    """Map an extracted label to its canonical class name."""
    for canonical, info in schema.items():
        if label in info["aliases"]:
            return canonical
        if label in info["deprecated"]:
            return canonical
    return label


def resolve_entities(
    mentions: list, schema: dict
) -> tuple:
    """Resolve mentions into canonical entities.
    Returns (canonical_entities, unresolved, audit_events).
    """
    canonical_map = {}  # entity_id -> CanonicalEntity
    unresolved = []
    audit_events = []

    # Group mentions by (canonical_type, normalized_text)
    groups = defaultdict(list)
    for m in mentions:
        ctype = resolve_label(m.label, schema)
        norm = _normalize(m.text)
        groups[(ctype, norm)].append(m)

    for (ctype, norm), group_mentions in groups.items():
        risk = "high" if ctype in RISKY_CLASSES else "low"
        review_required = risk == "high"
        entity_id = hashlib.sha1(f"{ctype}:{norm}".encode()).hexdigest()[:16]

        canonical = CanonicalEntity(
            entity_id=entity_id,
            canonical_type=ctype,
            canonical_name=group_mentions[0].text,
            mentions=group_mentions,
            aliases={m.text for m in group_mentions if m.text != group_mentions[0].text},
            risk_level=risk,
            review_required=review_required,
            merged_by="exact" if len(group_mentions) == 1 else "normalized",
            created_at=group_mentions[0].source_id if hasattr(group_mentions[0], 'source_id') else "",
        )

        # Audit high-risk merges
        if review_required and len(group_mentions) > 1:
            ctx = make_context("entity-resolution", "akos-governance")
            write_audit(
                "entity_merge",
                entity_id,
                "pending_review",
                ctx,
                {"type": ctype, "mentions": len(group_mentions), "risk": risk},
            )

        canonical_map[entity_id] = canonical

    return list(canonical_map.values()), unresolved, audit_events


def _normalize(text: str) -> str:
    """Normalize text for entity matching."""
    t = text.strip().lower()
    t = re.sub(r"[\s\-_]+", "", t)
    return t


def run_resolution(graph_path: str = "outputs/06_graph.json") -> dict:
    """Run entity resolution on graph output."""
    with open(graph_path) as f:
        g = json.load(f)

    schema = load_ontology_schema()

    # Build mentions from graph nodes
    mentions = []
    for n in g.get("nodes", []):
        m = Mention(
            mention_id=n.get("id", ""),
            text=n.get("text", ""),
            label=n.get("label", "UNKNOWN"),
            doc_id=n.get("doc_id", n.get("source_id", "")),
            start_char=n.get("start_char", 0),
            end_char=n.get("end_char", 0),
            confidence=n.get("confidence", 0.5),
            source_id=n.get("source_id", ""),
            extraction_method=n.get("metadata", {}).get("extraction_method", "unknown"),
        )
        mentions.append(m)

    canonical, unresolved, audit = resolve_entities(mentions, schema)

    # Build resolution report
    type_counts = defaultdict(int)
    for c in canonical:
        type_counts[c.canonical_type] += 1

    report = {
        "total_mentions": len(mentions),
        "canonical_entities": len(canonical),
        "unresolved": len(unresolved),
        "by_type": dict(type_counts),
        "high_risk": sum(1 for c in canonical if c.risk_level == "high"),
        "review_required": sum(1 for c in canonical if c.review_required),
        "schema_version": "1.0",
    }

    # Write outputs
    with open("outputs/entity_resolution.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open("outputs/canonical_entities.jsonl", "w") as f:
        for c in canonical:
            f.write(json.dumps({
                "entity_id": c.entity_id,
                "canonical_type": c.canonical_type,
                "canonical_name": c.canonical_name,
                "aliases": list(c.aliases),
                "risk_level": c.risk_level,
                "review_required": c.review_required,
                "merged_by": c.merged_by,
                "mention_count": len(c.mentions),
            }, ensure_ascii=False) + "\n")

    print(f"Entity Resolution: {len(mentions)} mentions → {len(canonical)} canonical entities")
    print(f"  High-risk: {report['high_risk']}, Review required: {report['review_required']}")
    print(f"  Types: {dict(type_counts)}")
    return report


if __name__ == "__main__":
    run_resolution()
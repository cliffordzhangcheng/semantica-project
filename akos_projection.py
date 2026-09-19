"""AKOS Projection Package — P0-5 Canonical Truth Boundary

Semantica graph is NOT AKOS truth source.
This module generates a gated projection package that AKOS Portal
can safely consume.

Projection status: exploration | candidate | validated | production_projection
source_of_truth: false (always)
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECTION_DIR = Path("akos_projection")
METRICS_FILE = Path("akos_metrics.json")  # R01: 从文件读取真实指标


def compute_hash(data) -> str:
    """Compute SHA256 hash of data."""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def load_actual_metrics() -> dict:
    """R01: 加载实际计算的指标，而非硬编码"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            metrics = json.load(f)
        return {
            "ner_f1": metrics.get("ner_f1", 0.0),
            "re_f1": metrics.get("re_f1", 0.0),
            "duplicate_rate": metrics.get("duplicate_rate", "pending"),
            "unresolved_rate": metrics.get("unresolved_rate", "pending"),
            "evidence_coverage": metrics.get("evidence_coverage", "pending"),
        }
    return {"ner_f1": 0.0, "re_f1": 0.0, "duplicate_rate": "pending",
            "unresolved_rate": "pending", "evidence_coverage": "pending"}


def load_gate_result() -> str:
    """R02: 从闸门验证结果加载，而非硬编码"""
    gate_ledger = Path("11-GATE-LEDGER-v0.2.1.json")
    if gate_ledger.exists():
        with open(gate_ledger) as f:
            ledger = json.load(f)
        all_pass = all(
            info['status'] == 'PASS'
            for gate, info in ledger.get('gates', {}).items()
            if gate.startswith('G') and int(gate[1:]) <= 6
        )
        return "PASS" if all_pass else "FAIL"
    return "UNKNOWN"  # R02: 无闸门数据时报告UNKNOWN而非假PASS


def validate_evidence_binding(graph: dict) -> tuple:
    """R04: 验证证据绑定完整性，返回(是否通过, 失败列表)"""
    failures = []
    entities = graph.get("entities", [])
    
    for entity in entities:
        provenance = entity.get("provenance", {})
        if not provenance.get("source_document_id"):
            failures.append(f"Entity {entity.get('id', 'unknown')} missing source_document_id")
    
    relationships = graph.get("relationships", [])
    for rel in relationships:
        provenance = rel.get("provenance", {})
        if not provenance.get("source_document_id"):
            failures.append(f"Relationship {rel.get('id', 'unknown')} missing source_document_id")
    
    return (len(failures) == 0, failures)


def generate_manifest(
    entity_count: int,
    relation_count: int,
    ontology_version: str,
    gate_result: str,
    projection_status: str = "candidate",
) -> dict:
    """Generate projection manifest."""
    actual_metrics = load_actual_metrics()
    return {
        "package_id": "AKOS-PROJ-SEMANTICA-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_commit": os.environ.get("GIT_COMMIT", "unknown"),
        "ontology_version": ontology_version,
        "ontology_hash": "pending",
        "corpus_hash": "pending",
        "entity_count": entity_count,
        "relation_count": relation_count,
        "quality_metrics": actual_metrics,
        "gate_result": gate_result,
        "projection_status": projection_status,
        "source_of_truth": False,
        "schema_version": "1.0",
        "source_snapshot": "outputs/06_graph.json",
    }


def build_projection_package(graph_path: str = "outputs/06_graph.json") -> str:
    """Build complete AKOS projection package."""
    with open(graph_path) as f:
        g = json.load(f)

    PROJECTION_DIR.mkdir(parents=True, exist_ok=True)

    # Compute hashes
    ontology_hash = compute_hash(open("config/akos_domain_ontology.yaml").read())
    corpus_hash = compute_hash(g)

    # R02: 从闸门结果获取gate_result，不再硬编码
    gate_result = load_gate_result()

    # R04: 验证证据绑定
    evidence_valid, evidence_failures = validate_evidence_binding(g)
    if not evidence_valid and gate_result == "PASS":
        print("⚠️ Evidence binding incomplete, downgrading gate_result to FAIL")
        gate_result = "FAIL"

    # R03: 统一契约 - 使用entities/relationships而非nodes/edges
    entity_count = len(g.get("entities", []))
    relation_count = len(g.get("relationships", []))

    # Manifest
    manifest = generate_manifest(
        entity_count=entity_count,
        relation_count=relation_count,
        ontology_version="1.0",
        gate_result=gate_result,
        projection_status="candidate",
    )
    manifest["ontology_hash"] = ontology_hash
    manifest["corpus_hash"] = corpus_hash

    # Write manifest
    (PROJECTION_DIR / "manifest.yaml").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )

    # R03: Write entities.jsonl from entities (not nodes)
    with open(PROJECTION_DIR / "entities.jsonl", "w") as f:
        for entity in g.get("entities", []):
            entry = {
                "id": entity.get("id", ""),
                "canonical_type": entity.get("label", "UNKNOWN"),
                "text": entity.get("text", ""),
                "source_id": entity.get("source_id", ""),
                "intake_id": entity.get("intake_id", ""),
                "provenance": entity.get("provenance", {}),
                "projection_status": "candidate",
                "source_of_truth": False,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # R03: Write relations.jsonl from relationships (not edges)
    with open(PROJECTION_DIR / "relations.jsonl", "w") as f:
        for rel in g.get("relationships", []):
            entry = {
                "id": hashlib.sha1(json.dumps(rel, sort_keys=True).encode()).hexdigest()[:16],
                "source": rel.get("source", ""),
                "target": rel.get("target", ""),
                "type": rel.get("predicate", "related_to"),
                "confidence": rel.get("confidence", 0),
                "source_id": rel.get("source_id", ""),
                "projection_status": "candidate",
                "source_of_truth": False,
                "evidence_required": rel.get("predicate") in {
                    "funds", "owns", "commits", "purchased_under",
                    "leased_under", "charters_under", "intermediates",
                    "earns", "sells_to", "guarantees", "generates",
                },
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Copy ontology
    import shutil
    shutil.copy("config/akos_domain_ontology.yaml", PROJECTION_DIR / "ontology.yaml")
    shutil.copy("config/ontology_aliases.yaml", PROJECTION_DIR / "ontology_aliases.yaml")

    # Write evidence.jsonl (placeholder)
    with open(PROJECTION_DIR / "evidence.jsonl", "w") as f:
        f.write(json.dumps({"note": "Evidence records pending validation"}, ensure_ascii=False) + "\n")

    # Write review_queue.jsonl
    if os.path.exists("review_queue.json"):
        shutil.copy("review_queue.json", PROJECTION_DIR / "review_queue.jsonl")

    # Write lineage.jsonl
    if os.path.exists("audit_log.jsonl"):
        shutil.copy("audit_log.jsonl", PROJECTION_DIR / "lineage.jsonl")

    # R01: metrics.json使用实际指标
    actual_metrics = load_actual_metrics()
    metrics = {
        "entity_count": entity_count,
        "relation_count": relation_count,
        "ner_f1": actual_metrics["ner_f1"],
        "re_f1": actual_metrics["re_f1"],
        "gate_result": gate_result,
        "projection_status": "candidate",
        "source_of_truth": False,
    }
    (PROJECTION_DIR / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))

    # Write graph_projection.json
    (PROJECTION_DIR / "graph_projection.json").write_text(
        json.dumps(g, ensure_ascii=False)
    )

    print(f"Projection package: {PROJECTION_DIR}/")
    for f in sorted(PROJECTION_DIR.iterdir()):
        print(f"  {f.name} ({f.stat().st_size} bytes)")
    return str(PROJECTION_DIR)


if __name__ == "__main__":
    build_projection_package()

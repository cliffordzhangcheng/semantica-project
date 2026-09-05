"""End-to-end AKOS-adapted Semantica pipeline with domain NER/RE fallback."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
from pipeline_compat import (
    ingest_documents, normalize_documents,
)
from akos_adapter import make_context, inject_metadata, write_audit, submit_for_review
from eval_kg import evaluate_ner, evaluate_re, prepare_gold_entities
from gold_set import GOLD_ENTITIES, GOLD_RELATIONS, GOLD_TEXT
from domain_ner import extract_domain_entities
from domain_re import extract_domain_relations


def main():
    data_dir = Path("data")
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    ctx = make_context(
        source_id="obsidian-vault:ai-depot-ontology",
        tenant_id="akos-internal",
        agent_id="dsh-web",
    )
    print(f"AKOS Context: source={ctx.source_id} session={ctx.work_session_id}")

    write_audit("pipeline_start", "semantica-akos-pipeline", "started", ctx)

    # Stage 1: Ingest
    docs = ingest_documents(data_dir)
    print(f"\n[1/6] Ingested {len(docs)} documents")
    for d in docs:
        inject_metadata(d, ctx)
        print(f"  - {d['metadata']['name']}: {len(d['text'])} chars")

    # Stage 2: Normalize
    docs = normalize_documents(docs)
    for d in docs:
        inject_metadata(d, ctx)
    print(f"\n[2/6] Normalized {len(docs)} docs")

    # Stage 3: Domain NER
    all_entities = []
    for doc in docs:
        entities = extract_domain_entities(doc["text"])
        for i, e in enumerate(entities):
            e["id"] = f"{doc['id']}:e{i}"
            e["doc_id"] = doc["id"]
            inject_metadata(e, ctx)
        all_entities.extend(entities)
    print(f"\n[3/6] Extracted {len(all_entities)} domain entities from {len(docs)} docs")
    label_counts = Counter(e.get("label", "UNKNOWN") for e in all_entities)
    for label, count in label_counts.most_common(15):
        print(f"  {label}: {count}")

    # Stage 4: Domain RE
    all_relations = []
    for doc in docs:
        doc_entities = [e for e in all_entities if e.get("doc_id") == doc["id"]]
        rels = extract_domain_relations(doc["text"], doc_entities)
        for r in rels:
            inject_metadata(r, ctx)
        all_relations.extend(rels)
    print(f"\n[4/6] Extracted {len(all_relations)} domain relations")
    for r in all_relations[:5]:
        src_text = next((e["text"] for e in all_entities if e["id"] == r.get("source")), "?")
        tgt_text = next((e["text"] for e in all_entities if e["id"] == r.get("target")), "?")
        print(f"  {src_text} --[{r.get('type','?')}]--> {tgt_text}")

    # Stage 5: Build graph
    graph = {
        "nodes": all_entities,
        "edges": all_relations,
        "metadata": {
            "source_id": ctx.source_id,
            "intake_id": ctx.intake_id,
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "work_session_id": ctx.work_session_id,
            "entity_count": len(all_entities),
            "relation_count": len(all_relations),
        },
    }
    inject_metadata(graph, ctx)
    print(f"\n[5/6] Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

    # Stage 6: Export
    for fmt in ["json", "graphml"]:
        out_path = out_dir / f"06_graph.{fmt}"
        if fmt == "json":
            out_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2, default=str))
        else:
            _export_graphml(graph, out_path)
        print(f"  Exported {fmt}: {out_path} ({out_path.stat().st_size} bytes)")

    # Gold Set evaluation
    print(f"\n{'='*60}")
    print("GOLD SET EVALUATION")
    print(f"{'='*60}")

    entities = prepare_gold_entities(GOLD_TEXT)
    ner_result = evaluate_ner(entities, GOLD_ENTITIES)

    id_to_text = {e["id"]: e["text"] for e in entities}
    merge_map = {e["text"]: e["merged_into"] for e in entities if "merged_into" in e}
    rels = extract_domain_relations(GOLD_TEXT, entities)
    re_result = evaluate_re(rels, GOLD_RELATIONS, id_to_text, merge_map)

    print(f"NER: P={ner_result['precision']:.4f} R={ner_result['recall']:.4f} F1={ner_result['f1']:.4f}")
    print(f"  Missed: {ner_result['missed']}")
    print(f"  FP: {ner_result['false_positives']}")
    print(f"RE:  P={re_result['precision']:.4f} R={re_result['recall']:.4f} F1={re_result['f1']:.4f}")
    print(f"  Missed: {re_result['missed']}")
    print(f"  FP: {re_result['false_positives']}")

    # Contract compliance
    print(f"\n{'='*60}")
    print("AKOS CONTRACT COMPLIANCE")
    print(f"{'='*60}")
    checks = {
        "source_id injected": all("source_id" in e for e in all_entities),
        "intake_id injected": all("intake_id" in e for e in all_entities),
        "tenant_id injected": all("tenant_id" in e for e in all_entities),
        "provenance present": all("provenance" in e for e in all_entities),
        "audit log exists": Path("audit_log.jsonl").exists(),
        "review queue exists": Path("review_queue.json").exists(),
    }
    for check, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'} {check}")

    all_pass = all(checks.values()) and ner_result["f1"] >= 0.70 and re_result["f1"] >= 0.50
    print(f"\n  OVERALL GATE: {'PASS' if all_pass else 'FAIL'}")
    if not all_pass:
        reasons = []
        if ner_result["f1"] < 0.70:
            reasons.append(f"NER F1={ner_result['f1']:.4f} < 0.70")
        if re_result["f1"] < 0.50:
            reasons.append(f"RE F1={re_result['f1']:.4f} < 0.50")
        for check, passed in checks.items():
            if not passed:
                reasons.append(f"Missing: {check}")
        print(f"  Failure reasons: {'; '.join(reasons)}")

    ticket = submit_for_review(
        {"type": "pipeline_run", "resource": "semantica-akos-pipeline",
         "description": f"NER F1={ner_result['f1']:.4f}, RE F1={re_result['f1']:.4f}",
         "action": "evaluate_kg_quality"},
        ctx, risk_level="medium",
    )
    print(f"\n  Review ticket: {ticket}")

    write_audit("pipeline_end", "semantica-akos-pipeline", "completed" if all_pass else "failed", ctx,
                {"ner_f1": ner_result["f1"], "re_f1": re_result["f1"]})

    results = {
        "ner": ner_result, "re": re_result,
        "contract_checks": checks, "gate_pass": all_pass,
        "entity_count": len(all_entities), "relation_count": len(all_relations),
        "doc_count": len(docs),
    }
    (out_dir / "eval_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    print(f"\nResults saved to outputs/eval_results.json")
    return 0 if all_pass else 1


def _export_graphml(graph: dict, path: Path):
    """Export graph as GraphML XML."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
    lines.append('  <graph id="G" edgedefault="directed">')
    for node in graph.get("nodes", []):
        nid = node.get("id", node.get("text", "unknown"))
        label = node.get("label", node.get("text", ""))
        lines.append(f'    <node id="{nid}">')
        lines.append(f'      <data key="label">{label}</data>')
        lines.append(f'    </node>')
    for i, edge in enumerate(graph.get("edges", [])):
        lines.append(f'    <edge id="e{i}" source="{edge.get("source","")}" target="{edge.get("target","")}">')
        lines.append(f'      <data key="type">{edge.get("type","related_to")}</data>')
        lines.append(f'    </edge>')
    lines.append('  </graph>')
    lines.append('</graphml>')
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
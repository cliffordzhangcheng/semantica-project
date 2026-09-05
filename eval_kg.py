"""Gold Set evaluation for domain NER/RE."""
from __future__ import annotations

import re
import sys
sys.path.insert(0, ".")
from gold_set import GOLD_ENTITIES, GOLD_RELATIONS, GOLD_TEXT


def evaluate_ner(extracted: list, gold: list) -> dict:
    extracted_set = {(e["text"], e.get("label", "UNKNOWN")) for e in extracted}
    gold_set = {(g["text"], g["label"]) for g in gold}
    tp = len(extracted_set & gold_set)
    fp = len(extracted_set - gold_set)
    fn = len(gold_set - extracted_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "extracted": sorted(extracted_set),
        "missed": sorted(gold_set - extracted_set),
        "false_positives": sorted(extracted_set - gold_set),
    }


def _resolve_relation_text(rel: dict, id_to_text: dict, merge_map: dict) -> tuple:
    """Resolve relation source/target from IDs to text, applying merge_map."""
    src = rel.get("source", "")
    tgt = rel.get("target", "")
    if src in id_to_text:
        src = id_to_text[src]
    if tgt in id_to_text:
        tgt = id_to_text[tgt]
    if merge_map:
        src = merge_map.get(src, src)
        tgt = merge_map.get(tgt, tgt)
    return (src, tgt, rel.get("type", "related_to"))


def evaluate_re(extracted: list, gold: list, id_to_text: dict = None, merge_map: dict = None) -> dict:
    id_to_text = id_to_text or {}
    merge_map = merge_map or {}
    extracted_set = {_resolve_relation_text(r, id_to_text, merge_map) for r in extracted}
    gold_set = {(g["source"], g["target"], g["type"]) for g in gold}
    tp = len(extracted_set & gold_set)
    fp = len(extracted_set - gold_set)
    fn = len(gold_set - extracted_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "extracted": sorted(extracted_set),
        "missed": sorted(gold_set - extracted_set),
        "false_positives": sorted(extracted_set - gold_set),
    }


def prepare_gold_entities(text: str) -> list:
    """Extract domain entities from gold text, merge parentheticals, assign IDs."""
    from domain_ner import extract_domain_entities
    entities = extract_domain_entities(text)

    # Merge parenthetical expansions
    paren_map = {}
    for m in re.finditer(r'(.+?)\(([^)]+)\)', text):
        paren_map[m.group(2)] = m.group(1)

    for e in entities:
        if e["text"] in paren_map:
            e["merged_into"] = paren_map[e["text"]]

    # Assign IDs: same merged_into → same ID
    id_counter = 0
    merge_id_map = {}
    for e in entities:
        key = e.get("merged_into", e["text"])
        if key not in merge_id_map:
            merge_id_map[key] = f"e{id_counter}"
            id_counter += 1
        e["id"] = merge_id_map[key]

    return entities


if __name__ == "__main__":
    from domain_re import extract_domain_relations

    print("=" * 60)
    print("Gold Set Evaluation — AI-Depot Domain")
    print("=" * 60)

    entities = prepare_gold_entities(GOLD_TEXT)
    ner_result = evaluate_ner(entities, GOLD_ENTITIES)

    id_to_text = {e["id"]: e["text"] for e in entities}
    merge_map = {e["text"]: e["merged_into"] for e in entities if "merged_into" in e}
    rels = extract_domain_relations(GOLD_TEXT, entities)
    re_result = evaluate_re(rels, GOLD_RELATIONS, id_to_text, merge_map)

    print(f"\nNER: P={ner_result['precision']:.4f} R={ner_result['recall']:.4f} F1={ner_result['f1']:.4f}")
    print(f"  Missed: {ner_result['missed']}")
    print(f"  FP: {ner_result['false_positives']}")
    print(f"RE:  P={re_result['precision']:.4f} R={re_result['recall']:.4f} F1={re_result['f1']:.4f}")
    print(f"  Missed: {re_result['missed']}")
    print(f"  FP: {re_result['false_positives']}")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  NER F1: {ner_result['f1']:.4f}  (threshold: >= 0.70)  {'PASS' if ner_result['f1'] >= 0.70 else 'FAIL'}")
    print(f"  RE  F1: {re_result['f1']:.4f}  (threshold: >= 0.50)  {'PASS' if re_result['f1'] >= 0.50 else 'FAIL'}")
    print(f"{'='*60}")
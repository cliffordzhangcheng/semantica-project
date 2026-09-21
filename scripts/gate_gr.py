#!/usr/bin/env python3
"""
Golden Relation Validation Gate (GR)
Validates that exactly 5 Golden Relations are present and valid
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"

def load_graph():
    path = OUTPUT_DIR / "06_graph.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def load_entity_registry():
    path = SCHEMAS_DIR / "entity_registry.yaml"
    if not path.exists():
        return {}
    import yaml
    with open(path) as f:
        return yaml.safe_load(f).get("entities", {})

def validate_golden_relations(graph, registry):
    """Validate Golden Relations per SPEC v0.4"""
    results = {
        "golden_relation_count": 0,
        "canonical_subject_count": 0,
        "valid_object_count": 0,
        "exact_or_supported_grounding": 0,
        "invalid_predicates": 0,
        "dangling_entities": 0,
        "dangling_evidence": 0,
        "semantic_pollution": 0,
        "issues": []
    }
    
    if not graph:
        results["issues"].append("Graph not found")
        return results
    
    relations = graph.get("relations", [])
    evidence = graph.get("evidence", [])
    entities = graph.get("entities", {})
    
    # Count golden relations
    golden = [r for r in relations if r.get("relation_id", "").startswith("GR-")]
    results["golden_relation_count"] = len(golden)
    
    # Get canonical entity IDs
    canonical_ids = set(registry.keys())
    
    # Validate each golden relation
    for gr in golden:
        relation_id = gr.get("relation_id", "")
        subject_id = gr.get("subject", {}).get("entity_id", "")
        predicate = gr.get("predicate", "")
        obj = gr.get("object", {})
        obj_id = obj.get("entity_id") if isinstance(obj, dict) else None
        grounding = gr.get("grounding_status", "")
        evidence_ref = gr.get("evidence_ref", [])
        
        # Check canonical subject
        if subject_id in canonical_ids:
            results["canonical_subject_count"] += 1
        else:
            results["issues"].append(f"{relation_id}: subject '{subject_id}' not in canonical registry")
        
        # Check valid object
        if obj_id is None or obj_id in canonical_ids:
            results["valid_object_count"] += 1
        else:
            results["issues"].append(f"{relation_id}: object '{obj_id}' not in canonical registry")
        
        # Check grounding status
        if grounding in ["EXACT", "SUPPORTED"]:
            results["exact_or_supported_grounding"] += 1
        else:
            results["issues"].append(f"{relation_id}: invalid grounding '{grounding}'")
        
        # Check predicates (no semantic pollution)
        invalid_chars = ["❓", "⚠️", "✅", "/"]
        has_pollution = any(c in predicate for c in invalid_chars)
        if has_pollution:
            results["semantic_pollution"] += 1
            results["issues"].append(f"{relation_id}: predicate contains pollution chars")
        
        # Check evidence binding
        if evidence_ref:
            # Verify evidence exists
            evidence_ids = [e.get("evidence_id") for e in evidence]
            if all(e in evidence_ids for e in evidence_ref):
                pass  # OK
            else:
                results["dangling_evidence"] += 1
                results["issues"].append(f"{relation_id}: references missing evidence")
        else:
            results["dangling_evidence"] += 1
            results["issues"].append(f"{relation_id}: no evidence_ref")
    
    # Check for unknown/dangling entities (referenced in relations but not in registry)
    all_referenced_ids = set()
    for gr in golden:
        subj_id = gr.get("subject", {}).get("entity_id", "")
        obj = gr.get("object", {})
        obj_id = obj.get("entity_id") if isinstance(obj, dict) else None
        if subj_id:
            all_referenced_ids.add(subj_id)
        if obj_id:
            all_referenced_ids.add(obj_id)
    
    # Dangling = referenced but not in canonical registry
    for eid in all_referenced_ids:
        if eid not in canonical_ids:
            results["dangling_entities"] += 1
            results["issues"].append(f"Dangling entity: '{eid}'")
    
    # Check predicate registry
    valid_predicates = set()
    pred_path = SCHEMAS_DIR / "predicate_registry.yaml"
    if pred_path.exists():
        import yaml
        with open(pred_path) as f:
            pred_registry = yaml.safe_load(f)
            valid_predicates = set(pred_registry.get("predicates", {}).keys())
    
    for gr in golden:
        pred = gr.get("predicate", "")
        if pred and pred not in valid_predicates:
            results["invalid_predicates"] += 1
            results["issues"].append(f"{relation_id}: predicate '{pred}' not in registry")
    
    return results

def run_gate():
    print("=" * 60)
    print("GATE GR: Golden Relation Integrity")
    print("=" * 60)
    
    graph = load_graph()
    registry = load_entity_registry()
    
    if not graph:
        print("❌ Graph not found")
        return False, {"error": "Graph not found"}
    
    results = validate_golden_relations(graph, registry)
    
    print(f"\nResults:")
    print(f"  Golden Relations: {results['golden_relation_count']}/5")
    print(f"  Canonical Subjects: {results['canonical_subject_count']}/5")
    print(f"  Valid Objects: {results['valid_object_count']}/5")
    print(f"  EXACT/SUPPORTED Grounding: {results['exact_or_supported_grounding']}/5")
    print(f"  Invalid Predicates: {results['invalid_predicates']}")
    print(f"  Dangling Entities: {results['dangling_entities']}")
    print(f"  Dangling Evidence: {results['dangling_evidence']}")
    print(f"  Semantic Pollution: {results['semantic_pollution']}")
    
    if results["issues"]:
        print(f"\nIssues:")
        for issue in results["issues"]:
            print(f"  ❌ {issue}")
    
    # Check PASS criteria
    pass_criteria = [
        (results["golden_relation_count"] == 5, "golden_relation_count == 5"),
        (results["canonical_subject_count"] == 5, "canonical_subject_count == 5"),
        (results["valid_object_count"] == 5, "valid_object_count == 5"),
        (results["exact_or_supported_grounding"] == 5, "exact_or_supported_grounding == 5"),
        (results["invalid_predicates"] == 0, "invalid_predicates == 0"),
        (results["dangling_entities"] == 0, "dangling_entities == 0"),
        (results["dangling_evidence"] == 0, "dangling_evidence == 0"),
        (results["semantic_pollution"] == 0, "semantic_pollution == 0"),
    ]
    
    all_pass = all(pc[0] for pc in pass_criteria)
    
    if all_pass:
        print("\n✅ GR PASS: 5/5 Golden Relations validated")
    else:
        print("\n❌ GR FAIL")
        for passed, desc in pass_criteria:
            status = "✓" if passed else "❌"
            print(f"  {status} {desc}")
    
    return all_pass, results


if __name__ == "__main__":
    success, results = run_gate()
    sys.exit(0 if success else 1)

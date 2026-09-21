#!/usr/bin/env python3
"""
Golden Claim Validation Gate (GC)
Validates that exactly 5 Golden Claims are present and valid
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

def load_graph():
    path = OUTPUT_DIR / "06_graph.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def validate_golden_claims(graph):
    """Validate Golden Claims per SPEC v0.4"""
    results = {
        "golden_claim_count": 0,
        "all_canonical_entities": 0,
        "all_controlled_predicates": 0,
        "all_exact_supported_evidence": 0,
        "all_claim_statuses_valid": 0,
        "issues": []
    }
    
    if not graph:
        results["issues"].append("Graph not found")
        return results
    
    claims = graph.get("claims", [])
    
    # Count golden claims
    golden = [c for c in claims if c.get("claim_id", "").startswith("GC-")]
    results["golden_claim_count"] = len(golden)
    
    # Validate each golden claim
    for gc in golden:
        claim_id = gc.get("claim_id", "")
        subject = gc.get("subject", {})
        predicate = gc.get("predicate", "")
        obj = gc.get("object", {})
        grounding = gc.get("grounding_status", "")
        claim_status = gc.get("claim_status", "")
        evidence_ref = gc.get("evidence_ref", [])
        
        # Check canonical subject
        subj_id = subject.get("entity_id", "")
        if subj_id.startswith("org_") or subj_id.startswith("concept_") or subj_id.startswith("resource_") or subj_id.startswith("loc_") or subj_id.startswith("person_") or subj_id.startswith("aggregator_"):
            results["all_canonical_entities"] += 1
        else:
            results["issues"].append(f"{claim_id}: subject '{subj_id}' not canonical")
        
        # Check controlled predicate (no semantic pollution)
        invalid_chars = ["❓", "⚠️", "✅", "/"]
        if not any(c in predicate for c in invalid_chars):
            results["all_controlled_predicates"] += 1
        else:
            results["issues"].append(f"{claim_id}: predicate contains pollution")
        
        # Check grounding status
        if grounding in ["EXACT", "SUPPORTED"]:
            results["all_exact_supported_evidence"] += 1
        else:
            results["issues"].append(f"{claim_id}: invalid grounding '{grounding}'")
        
        # Check claim status
        if claim_status == "OBSERVED":
            results["all_claim_statuses_valid"] += 1
        else:
            results["issues"].append(f"{claim_id}: invalid status '{claim_status}'")
    
    return results

def run_gate():
    print("=" * 60)
    print("GATE GC: Golden Claim Integrity")
    print("=" * 60)
    
    graph = load_graph()
    
    if not graph:
        print("❌ Graph not found")
        return False, {"error": "Graph not found"}
    
    results = validate_golden_claims(graph)
    
    print(f"\nResults:")
    print(f"  Golden Claims: {results['golden_claim_count']}/5")
    print(f"  All Canonical Entities: {results['all_canonical_entities']}/5")
    print(f"  All Controlled Predicates: {results['all_controlled_predicates']}/5")
    print(f"  All EXACT/SUPPORTED: {results['all_exact_supported_evidence']}/5")
    print(f"  All Claim Statuses Valid: {results['all_claim_statuses_valid']}/5")
    
    if results["issues"]:
        print(f"\nIssues:")
        for issue in results["issues"]:
            print(f"  ❌ {issue}")
    
    # Check PASS criteria
    pass_criteria = [
        (results["golden_claim_count"] == 5, "golden_claim_count == 5"),
        (results["all_canonical_entities"] == 5, "all_canonical_entities == 5"),
        (results["all_controlled_predicates"] == 5, "all_controlled_predicates == 5"),
        (results["all_exact_supported_evidence"] == 5, "all_exact_supported_evidence == 5"),
        (results["all_claim_statuses_valid"] == 5, "all_claim_statuses_valid == 5"),
    ]
    
    all_pass = all(pc[0] for pc in pass_criteria)
    
    if all_pass:
        print("\n✅ GC PASS: 5/5 Golden Claims validated")
    else:
        print("\n❌ GC FAIL")
        for passed, desc in pass_criteria:
            status = "✓" if passed else "❌"
            print(f"  {status} {desc}")
    
    return all_pass, results


if __name__ == "__main__":
    success, results = run_gate()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
GSYNC Gate - Cross-artifact Snapshot Consistency
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

def run_gate():
    print("=" * 60)
    print("GATE GSYNC: Cross-artifact Snapshot Consistency")
    print("=" * 60)
    
    # Load all artifacts
    artifacts = {}
    for name in ["06_graph.json", "manifest.json", "determinism_report.json"]:
        path = OUTPUT_DIR / name
        if path.exists():
            with open(path) as f:
                artifacts[name] = json.load(f)
    
    results = {
        "snapshot_consistent": True,
        "issues": []
    }
    
    # Check snapshot IDs match
    if "06_graph.json" in artifacts and "manifest.json" in artifacts:
        graph_snapshot = artifacts["06_graph.json"].get("semantic_snapshot_id")
        manifest_snapshot = artifacts["manifest.json"].get("semantic_snapshot_id")
        
        if graph_snapshot and manifest_snapshot:
            if graph_snapshot != manifest_snapshot:
                results["snapshot_consistent"] = False
                results["issues"].append(f"Snapshot mismatch: graph={graph_snapshot}, manifest={manifest_snapshot}")
        else:
            results["snapshot_consistent"] = False
            results["issues"].append("Missing snapshot IDs")
    
    # Check run IDs match
    if "06_graph.json" in artifacts and "manifest.json" in artifacts:
        graph_run = artifacts["06_graph.json"].get("run_id")
        manifest_run = artifacts["manifest.json"].get("run_id")
        
        if graph_run and manifest_run:
            if graph_run != manifest_run:
                results["snapshot_consistent"] = False
                results["issues"].append(f"Run ID mismatch: graph={graph_run}, manifest={manifest_run}")
    
    print(f"\nResults:")
    print(f"  Snapshot Consistent: {results['snapshot_consistent']}")
    
    if results["issues"]:
        print(f"\nIssues:")
        for issue in results["issues"]:
            print(f"  ❌ {issue}")
    
    all_pass = results["snapshot_consistent"]
    
    if all_pass:
        print("\n✅ GSYNC PASS: All artifacts consistent")
    else:
        print("\n❌ GSYNC FAIL")
    
    return all_pass, results


if __name__ == "__main__":
    success, results = run_gate()
    sys.exit(0 if success else 1)

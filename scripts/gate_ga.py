#!/usr/bin/env python3
"""
Artifact Integrity Gate (GA)
Detects offload markers, temp paths, and critical truncation
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Patterns to detect
OFFLOAD_PATTERNS = [
    "[CONTEXT OFFLOADED]",
    "offload",
    "/var/minis/offloads/"
]

TEMP_PATTERNS = [
    "/tmp/",
    "/var/tmp/",
    "file_write_"
]

CRITICAL_TRUNCATION_KEYWORDS = [
    "critical report truncation",
    "INVALID JSON",
    "truncated"
]

def scan_artifacts():
    """Scan all outputs for violations"""
    results = {
        "offload_markers": 0,
        "temp_paths": 0,
        "critical_truncations": 0,
        "runtime_report_mismatches": 0,
        "issues": []
    }
    
    # Scan JSON files
    for f in OUTPUT_DIR.glob("*.json"):
        content = f.read_text()
        
        # Check offload markers
        for pattern in OFFLOAD_PATTERNS:
            if pattern in content:
                results["offload_markers"] += 1
                results["issues"].append(f"{f.name}: contains '{pattern}'")
        
        # Check temp paths
        for pattern in TEMP_PATTERNS:
            if pattern in content:
                results["temp_paths"] += 1
                results["issues"].append(f"{f.name}: contains '{pattern}'")
        
        # Check critical truncation
        for pattern in CRITICAL_TRUNCATION_KEYWORDS:
            if pattern.lower() in content.lower():
                results["critical_truncations"] += 1
                results["issues"].append(f"{f.name}: contains '{pattern}'")
    
    # Scan JSONL files
    for f in OUTPUT_DIR.glob("*.jsonl"):
        content = f.read_text()
        
        for pattern in OFFLOAD_PATTERNS + TEMP_PATTERNS + CRITICAL_TRUNCATION_KEYWORDS:
            if pattern in content:
                if pattern in OFFLOAD_PATTERNS:
                    results["offload_markers"] += 1
                elif pattern in TEMP_PATTERNS:
                    results["temp_paths"] += 1
                else:
                    results["critical_truncations"] += 1
                results["issues"].append(f"{f.name}: contains '{pattern}'")
    
    # Check manifest consistency
    manifest_path = OUTPUT_DIR / "manifest.json"
    graph_path = OUTPUT_DIR / "06_graph.json"
    
    if manifest_path.exists() and graph_path.exists():
        manifest = json.loads(manifest_path.read_text())
        graph = json.loads(graph_path.read_text())
        
        # Check that reported counts match actual
        if manifest.get("entities_hash"):
            pass  # Can't easily verify hash without rehashing
        
        # Check snapshot ID consistency
        if "semantic_snapshot_id" in manifest:
            if "semantic_snapshot_id" in graph:
                if manifest["semantic_snapshot_id"] == graph["semantic_snapshot_id"]:
                    pass  # OK
                else:
                    results["runtime_report_mismatches"] += 1
            else:
                results["runtime_report_mismatches"] += 1
    
    return results

def run_gate():
    print("=" * 60)
    print("GATE GA: Artifact Integrity")
    print("=" * 60)
    
    results = scan_artifacts()
    
    print(f"\nResults:")
    print(f"  Offload Markers: {results['offload_markers']}")
    print(f"  Temp Paths: {results['temp_paths']}")
    print(f"  Critical Truncations: {results['critical_truncations']}")
    print(f"  Runtime/Report Mismatches: {results['runtime_report_mismatches']}")
    
    if results["issues"]:
        print(f"\nIssues:")
        for issue in results["issues"][:10]:  # Limit output
            print(f"  ❌ {issue}")
    
    # Check PASS criteria
    all_clear = (
        results["offload_markers"] == 0 and
        results["temp_paths"] == 0 and
        results["critical_truncations"] == 0 and
        results["runtime_report_mismatches"] == 0
    )
    
    if all_clear:
        print("\n✅ GA PASS: No artifact integrity issues")
    else:
        print("\n❌ GA FAIL")
    
    return all_clear, results


if __name__ == "__main__":
    success, results = run_gate()
    sys.exit(0 if success else 1)

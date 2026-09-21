#!/usr/bin/env python3
"""
Determinism Gate (GDET)
Validates that double-run produces identical hashes
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

def load_determinism_report():
    path = OUTPUT_DIR / "determinism_report.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def run_gate():
    print("=" * 60)
    print("GATE GDET: Determinism")
    print("=" * 60)
    
    report = load_determinism_report()
    
    if not report:
        print("❌ Determinism report not found")
        return False, {"error": "No determinism_report.json"}
    
    print(f"\nResults:")
    print(f"  Status: {report.get('status', 'UNKNOWN')}")
    print(f"  Runs: {report.get('runs', 0)}")
    
    comparison = report.get("comparison", {})
    for key, matched in comparison.items():
        status = "✓" if matched else "❌"
        print(f"  {status} {key}: {'match' if matched else 'MISMATCH'}")
    
    all_pass = report.get("all_hash_consistent", False)
    
    if all_pass:
        print("\n✅ GDET PASS: Double-run hashes match")
    else:
        print("\n❌ GDET FAIL")
    
    return all_pass, report


if __name__ == "__main__":
    success, results = run_gate()
    sys.exit(0 if success else 1)

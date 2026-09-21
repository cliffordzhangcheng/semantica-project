#!/usr/bin/env python3
"""
Determinism Validator for v0.4
Runs pipeline twice and verifies all hashes match
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

def hash_file(path):
    """Compute hash of file content"""
    content = path.read_text().encode('utf-8')
    return hashlib.sha256(content).hexdigest()[:16]

def hash_object(obj):
    """Compute hash of object (excluding timestamps and run_ids)"""
    # Remove non-deterministic fields
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if k not in ['run_id', 'timestamp', 'created_at', 'semantic_snapshot_id']}
        elif isinstance(o, list):
            return [clean(i) for i in o]
        return o
    return hashlib.sha256(json.dumps(clean(obj), sort_keys=True).encode()).hexdigest()[:16]

def extract_hashes(graph):
    """Extract deterministic hashes from graph"""
    return {
        "entity_registry": hash_object(graph.get("entities", {})),
        "golden_relations": hash_object(graph.get("relations", [])),
        "golden_claims": hash_object(graph.get("claims", [])),
        "graph": hash_object(graph)
    }

def run_pipeline():
    """Run the golden relations builder"""
    import subprocess
    result = subprocess.run(
        ["python3", str(PROJECT_ROOT / "scripts" / "build_golden_relations.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("=" * 60)
    print("Semantica Determinism Validation v0.4")
    print("=" * 60)
    
    results = []
    
    for run_num in [1, 2]:
        print(f"\n[Run {run_num}]")
        print("-" * 40)
        
        # Clean outputs
        if OUTPUT_DIR.exists():
            import shutil
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(parents=True)
        
        # Run pipeline
        success, stdout, stderr = run_pipeline()
        
        if not success:
            print(f"  ❌ Pipeline failed")
            print(f"  stderr: {stderr[:200]}")
            return False
        
        # Load graph
        graph_path = OUTPUT_DIR / "06_graph.json"
        if not graph_path.exists():
            print(f"  ❌ Graph not found")
            return False
        
        with open(graph_path) as f:
            graph = json.load(f)
        
        # Extract hashes
        hashes = extract_hashes(graph)
        
        # Write hashes
        run_hashes = {
            "run": run_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **hashes
        }
        
        with open(OUTPUT_DIR / f"run_{run_num}_hashes.json", "w") as f:
            json.dump(run_hashes, f, indent=2)
        
        print(f"  ✓ Entities: {len(graph['entities'])}")
        print(f"  ✓ Relations: {len(graph['relations'])}")
        print(f"  ✓ Claims: {len(graph['claims'])}")
        print(f"  ✓ Entity hash: {hashes['entity_registry']}")
        print(f"  ✓ Relations hash: {hashes['golden_relations']}")
        print(f"  ✓ Claims hash: {hashes['golden_claims']}")
        
        results.append({
            "run": run_num,
            "hashes": hashes
        })
    
    # Compare
    print("\n" + "=" * 60)
    print("Hash Comparison")
    print("=" * 60)
    
    r1, r2 = results[0], results[1]
    
    matches = {
        "entity_registry": r1["hashes"]["entity_registry"] == r2["hashes"]["entity_registry"],
        "golden_relations": r1["hashes"]["golden_relations"] == r2["hashes"]["golden_relations"],
        "golden_claims": r1["hashes"]["golden_claims"] == r2["hashes"]["golden_claims"],
        "graph": r1["hashes"]["graph"] == r2["hashes"]["graph"]
    }
    
    all_pass = all(matches.values())
    
    for key, passed in matches.items():
        status = "✓" if passed else "❌"
        print(f"  {status} {key}: {r1['hashes'][key]} == {r2['hashes'][key]}")
    
    # Write determinism report
    report = {
        "status": "PASS" if all_pass else "FAIL",
        "runs": 2,
        "comparison": matches,
        "all_hash_consistent": all_pass
    }
    
    with open(OUTPUT_DIR / "determinism_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'✅ DETERMINISM VALIDATED' if all_pass else '❌ DETERMINISM FAILED'}")
    return all_pass

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

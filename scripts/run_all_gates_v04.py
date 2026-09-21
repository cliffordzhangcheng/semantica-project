#!/usr/bin/env python3
"""Run all v0.4 gates and generate ledger"""
import json
from pathlib import Path
from datetime import datetime, timezone

OUTPUT_DIR = Path("outputs")
REPORTS_DIR = OUTPUT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Import and run gates
from gate_gr import run_gate as gr_run
from gate_gc import run_gate as gc_run
from gate_ga import run_gate as ga_run
from gate_gdet import run_gate as gdet_run
from gate_gsync import run_gate as gsync_run

results = {}

# Run each gate
success, data = gr_run()
results["GR"] = {"status": "PASS" if success else "FAIL", "details": str(data)}

success, data = gc_run()
results["GC"] = {"status": "PASS" if success else "FAIL", "details": str(data)}

success, data = ga_run()
results["GA"] = {"status": "PASS" if success else "FAIL", "details": str(data)}

success, data = gdet_run()
results["GDET"] = {"status": "PASS" if success else "FAIL", "details": str(data)}

success, data = gsync_run()
results["GSYNC"] = {"status": "PASS" if success else "FAIL", "details": str(data)}

# Load existing G0-G6 results if available
ledger_path = REPORTS_DIR / "gate_ledger.json"
if ledger_path.exists():
    old_ledger = json.loads(ledger_path.read_text())
    for k, v in old_ledger.get("gates", {}).items():
        if k not in results and k.startswith("G"):
            results[k] = v

# Create ledger
ledger = {
    "run_timestamp": datetime.now(timezone.utc).isoformat(),
    "gates": results,
    "overall": "PASS" if all(v["status"] == "PASS" for v in results.values()) else "FAIL"
}

# Write ledger
(ledger_path).write_text(json.dumps(ledger, indent=2))
print(f"Ledger written: {ledger_path}")
print(f"Overall: {ledger['overall']}")
for g, v in results.items():
    print(f"  {g}: {v['status']}")

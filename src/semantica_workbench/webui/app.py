#!/usr/bin/env python3
"""WebUI application for Semantica"""
from pathlib import Path
import json


def create_app(run_dir: Path):
    """Create app bound to a specific run (no Flask dependency)"""
    # Validate run exists
    manifest_path = run_dir / "run_manifest.json"
    ledger_path = run_dir / "gate_ledger.json"
    
    if not manifest_path.exists():
        raise ValueError(f"Run manifest not found: {manifest_path}")
    if not ledger_path.exists():
        raise ValueError(f"Gate ledger not found: {ledger_path}")
    
    # Load run data
    manifest = json.loads(manifest_path.read_text())
    ledger = json.loads(ledger_path.read_text())
    
    # Load graph
    graph_path = run_dir / "canonical_graph.json"
    graph = {}
    if graph_path.exists():
        graph = json.loads(graph_path.read_text())
    
    run_id = manifest.get("run_id", "unknown")
    overall_status = ledger.get("overall", "NOT_EVALUATED")
    gates = ledger.get("gates", {})
    
    return {
        "run_id": run_id,
        "overall_status": overall_status,
        "gates": gates,
        "entities": graph.get("entities", []),
        "relationships": graph.get("relationships", [])
    }

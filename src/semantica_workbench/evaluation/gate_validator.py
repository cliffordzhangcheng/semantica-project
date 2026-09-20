"""Fail-closed validation gates for generated pipeline artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_SUCCESS = 0
EXIT_SCHEMA_ERROR = 4

class GateResult:
    def __init__(self, gate_id: str, status: str, reason: str = "", binding: dict | None = None):
        self.gate_id = gate_id
        self.status = status
        self.reason = reason
        self.binding = binding or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {"gate": self.gate_id, "status": self.status, "reason": self.reason, "binding": self.binding, "timestamp": self.timestamp}

class GateEngine:
    REQUIRED_GATES = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    def _compute_hash(self, path: Path) -> str:
        """Compute SHA256 hash of a file."""
        if not path.exists():
            return "MISSING"
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]

    def _compute_corpus_hash(self) -> str:
        """Compute hash of all raw corpus files."""
        raw_dir = self.project_root / "data" / "raw"
        if not raw_dir.exists():
            return "MISSING"
        files = sorted(raw_dir.iterdir())
        if not files:
            return "EMPTY"
        content = b"".join(f.read_bytes() for f in files)
        return hashlib.sha256(content).hexdigest()[:16]

    def validate_all(self, run_id: str, graph_hash: str, corpus_hash: str) -> dict:
        results = {}
        for gate in self.REQUIRED_GATES:
            validator = getattr(self, f"_validate_{gate.lower()}", self._default_fail)
            results[gate] = validator(run_id, graph_hash, corpus_hash)
        return {
            "run_id": run_id,
            "graph_hash": graph_hash,
            "corpus_hash": corpus_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gates": {key: value.to_dict() for key, value in results.items()},
            "overall": "PASS" if all(value.status == "PASS" for value in results.values()) else "FAIL",
        }

    def _default_fail(self, run_id, *_):
        return GateResult("UNKNOWN", "FAIL", "Gate not implemented", {"run_id": run_id})

    def _exists(self, relative: str) -> bool:
        return (self.project_root / relative).exists()

    def _validate_g0(self, run_id, graph_hash, corpus_hash):
        """G0: Corpus directory exists and is not empty."""
        raw_dir = self.project_root / "data" / "raw"
        ok = raw_dir.exists() and any(raw_dir.iterdir())
        return GateResult("G0", "PASS" if ok else "FAIL", "" if ok else "Corpus directory missing or empty", {"run_id": run_id})

    def _validate_g1(self, run_id, graph_hash, corpus_hash):
        """G1: Schema file exists."""
        ok = self._exists("schemas/canonical_graph.json")
        return GateResult("G1", "PASS" if ok else "FAIL", "" if ok else "Schema file missing", {"run_id": run_id})

    def _validate_g2(self, run_id, graph_hash, corpus_hash):
        """G2: Graph artifact exists with real hash (no archive fallback)."""
        graph_file = self.project_root / "outputs" / "06_graph.json"
        ok = graph_file.exists() and graph_hash != "MISSING"
        return GateResult("G2", "PASS" if ok else "FAIL", "" if ok else "Ontology/graph artifact missing or hash mismatch", {"run_id": run_id, "graph_hash": graph_hash})

    def _validate_g3(self, run_id, graph_hash, corpus_hash):
        """G3: Evidence file exists (real, not absence-as-PASS)."""
        evidence_file = self.project_root / "outputs" / "reports" / "evidence.jsonl"
        ok = evidence_file.exists() and evidence_file.stat().st_size > 0
        return GateResult("G3", "PASS" if ok else "FAIL", "" if ok else "Evidence file missing or empty", {"run_id": run_id})

    def _validate_g4(self, run_id, graph_hash, corpus_hash):
        """G4: Claims file exists (real, not absence-as-PASS)."""
        claims_file = self.project_root / "outputs" / "reports" / "claims.jsonl"
        ok = claims_file.exists() and claims_file.stat().st_size > 0
        return GateResult("G4", "PASS" if ok else "FAIL", "" if ok else "Claims file missing or empty", {"run_id": run_id})

    def _validate_g5(self, run_id, graph_hash, corpus_hash):
        """G5: All tests pass."""
        result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=self.project_root, capture_output=True)
        return GateResult("G5", "PASS" if result.returncode == 0 else "FAIL", "" if result.returncode == 0 else "Tests failed", {"run_id": run_id})

    def _validate_g6(self, run_id, graph_hash, corpus_hash):
        """G6: No booking status override (fail-open prevention)."""
        booking = self.project_root / "outputs" / "reports" / "booking_status.json"
        ok = not booking.exists() or json.loads(booking.read_text()).get("status") != "BOOKED"
        return GateResult("G6", "PASS" if ok else "FAIL", "Booking status override detected (should not exist)" if booking.exists() else "", {"run_id": run_id})

def run_gates(project_root: Path | str | None = None) -> int:
    root = Path(project_root or Path(__file__).resolve().parents[3]).resolve()
    run_id = "auto-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Compute real hashes
    graph_file = root / "outputs" / "06_graph.json"
    graph_hash = "MISSING" if not graph_file.exists() else hashlib.sha256(graph_file.read_bytes()).hexdigest()[:16]
    
    raw_dir = root / "data" / "raw"
    corpus_hash = "MISSING"
    if raw_dir.exists() and any(raw_dir.iterdir()):
        files = sorted(raw_dir.iterdir())
        content = b"".join(f.read_bytes() for f in files)
        corpus_hash = hashlib.sha256(content).hexdigest()[:16]
    
    result = GateEngine(root).validate_all(run_id, graph_hash, corpus_hash)
    report_dir = root / "outputs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    ledger = report_dir / "gate_ledger.json"
    ledger.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Gate validation complete: {result['overall']}")
    print(f"Ledger written to: {ledger}")
    return EXIT_SUCCESS if result["overall"] == "PASS" else EXIT_SCHEMA_ERROR

if __name__ == "__main__":
    raise SystemExit(run_gates())
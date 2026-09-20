"""Fail-closed validation gates for generated pipeline artifacts."""

from __future__ import annotations

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

    def _validate_g0(self, run_id, *_):
        ok = self._exists("data/raw") and any((self.project_root / "data/raw").iterdir())
        return GateResult("G0", "PASS" if ok else "FAIL", "" if ok else "Corpus directory missing or empty", {"run_id": run_id})

    def _validate_g1(self, run_id, *_):
        ok = self._exists("schemas/canonical_graph.json")
        return GateResult("G1", "PASS" if ok else "FAIL", "" if ok else "Schema file missing", {"run_id": run_id})

    def _validate_g2(self, run_id, *_):
        ok = self._exists("outputs/06_graph.json") or bool(list((self.project_root / "research/archive").glob("*/06_graph.json")))
        return GateResult("G2", "PASS" if ok else "FAIL", "" if ok else "Ontology/graph artifact missing", {"run_id": run_id})

    def _validate_artifact(self, gate, relative, run_id, reason):
        ok = self._exists(relative)
        return GateResult(gate, "PASS" if ok else "FAIL", "" if ok else reason, {"run_id": run_id})

    def _validate_g3(self, run_id, *_):
        return self._validate_artifact("G3", "outputs/reports/evidence.jsonl", run_id, "Evidence file missing")

    def _validate_g4(self, run_id, *_):
        return self._validate_artifact("G4", "outputs/reports/claims.jsonl", run_id, "Claims file missing")

    def _validate_g5(self, run_id, *_):
        result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=self.project_root, capture_output=True)
        return GateResult("G5", "PASS" if result.returncode == 0 else "FAIL", "" if result.returncode == 0 else "Tests failed", {"run_id": run_id})

    def _validate_g6(self, run_id, *_):
        booking = self.project_root / "outputs/reports/booking_status.json"
        booked = booking.exists() and json.loads(booking.read_text()).get("status") == "BOOKED"
        return GateResult("G6", "FAIL" if booked else "PASS", "Booking status present (should not exist)" if booked else "", {"run_id": run_id})


def run_gates(project_root: Path | str | None = None) -> int:
    root = Path(project_root or Path(__file__).resolve().parents[3]).resolve()
    run_id = "auto-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    result = GateEngine(root).validate_all(run_id, "generated", "generated")
    report_dir = root / "outputs/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    ledger = report_dir / "gate_ledger.json"
    ledger.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Gate validation complete: {result['overall']}")
    print(f"Ledger written to: {ledger}")
    return EXIT_SUCCESS if result["overall"] == "PASS" else EXIT_SCHEMA_ERROR


if __name__ == "__main__":
    raise SystemExit(run_gates())

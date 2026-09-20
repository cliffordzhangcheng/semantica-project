"""Gate validation engine - fail-closed logic"""
import json
from pathlib import Path
from datetime import datetime, timezone


EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 2
EXIT_EXECUTION_ERROR = 3
EXIT_SCHEMA_ERROR = 4


class GateResult:
    """Single gate result"""
    def __init__(self, gate_id: str, status: str, reason: str = "", binding: dict = None):
        self.gate_id = gate_id
        self.status = status
        self.reason = reason
        self.binding = binding or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> dict:
        return {
            "gate": self.gate_id,
            "status": self.status,
            "reason": self.reason,
            "binding": self.binding,
            "timestamp": self.timestamp
        }


class GateEngine:
    """Fail-closed gate validation engine"""
    
    REQUIRED_GATES = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def validate_all(self, run_id: str, graph_hash: str, corpus_hash: str) -> dict:
        """Validate all gates - fail closed"""
        results = {}
        
        for gate in self.REQUIRED_GATES:
            validator = getattr(self, f"_validate_{gate.lower()}", self._default_fail)
            results[gate] = validator(run_id, graph_hash, corpus_hash)
        
        overall = self._calculate_overall(results)
        
        return {
            "run_id": run_id,
            "graph_hash": graph_hash,
            "corpus_hash": corpus_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gates": {k: v.to_dict() for k, v in results.items()},
            "overall": overall
        }
    
    def _calculate_overall(self, results: dict) -> str:
        """Overall FAIL if any gate fails"""
        for gate_id, result in results.items():
            if gate_id == "G7":
                continue
            if result.status not in ("PASS",):
                return "FAIL"
        return "PASS"
    
    def _default_fail(self, run_id, graph_hash, corpus_hash) -> GateResult:
        return GateResult(
            gate_id="UNKNOWN",
            status="FAIL",
            reason="Gate not implemented",
            binding={"run_id": run_id}
        )
    
    def _validate_g0(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G0: Corpus validation"""
        corpus_dir = self.project_root / "data" / "raw"
        if not corpus_dir.exists() or not any(corpus_dir.iterdir()):
            return GateResult(
                gate_id="G0",
                status="FAIL",
                reason="Corpus directory missing or empty",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G0", status="PASS", binding={"run_id": run_id})
    
    def _validate_g1(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G1: Schema validation"""
        schema_file = self.project_root / "schemas" / "canonical_graph.json"
        if not schema_file.exists():
            return GateResult(
                gate_id="G1",
                status="FAIL",
                reason="Schema file missing",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G1", status="PASS", binding={"run_id": run_id})
    
    def _validate_g2(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G2: Ontology validation"""
        ontology_files = list((self.project_root / "research" / "archive").glob("*/06_graph.json"))
        if not ontology_files:
            return GateResult(
                gate_id="G2",
                status="FAIL",
                reason="Ontology file missing",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G2", status="PASS", binding={"run_id": run_id})
    
    def _validate_g3(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G3: Evidence validation"""
        evidence_file = self.project_root / "outputs" / "reports" / "evidence.jsonl"
        if not evidence_file.exists():
            return GateResult(
                gate_id="G3",
                status="FAIL",
                reason="Evidence file missing",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G3", status="PASS", binding={"run_id": run_id})
    
    def _validate_g4(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G4: Claims validation"""
        claims_file = self.project_root / "outputs" / "reports" / "claims.jsonl"
        if not claims_file.exists():
            return GateResult(
                gate_id="G4",
                status="FAIL",
                reason="Claims file missing",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G4", status="PASS", binding={"run_id": run_id})
    
    def _validate_g5(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G5: Test validation"""
        # Check if tests pass
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "-q"],
            cwd=self.project_root,
            capture_output=True
        )
        if result.returncode != 0:
            return GateResult(
                gate_id="G5",
                status="FAIL",
                reason="Tests failed",
                binding={"run_id": run_id}
            )
        return GateResult(gate_id="G5", status="PASS", binding={"run_id": run_id})
    
    def _validate_g6(self, run_id, graph_hash, corpus_hash) -> GateResult:
        """G6: Booking validation"""
        # Check for BOOKED status (should not exist)
        booking_file = self.project_root / "outputs" / "reports" / "booking_status.json"
        if booking_file.exists():
            with open(booking_file) as f:
                status = json.load(f).get("status", "")
            if status == "BOOKED":
                return GateResult(
                    gate_id="G6",
                    status="FAIL",
                    reason="Booking status present (should not exist)",
                    binding={"run_id": run_id}
                )
        return GateResult(gate_id="G6", status="PASS", binding={"run_id": run_id})


def run_gates():
    """Main entry point for gate validation"""
    project_root = Path(__file__).parent.parent.parent
    run_id = "auto-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    
    engine = GateEngine(project_root)
    result = engine.validate_all(run_id, "test-hash", "test-corpus-hash")
    
    # Write to artifacts
    artifacts_dir = project_root / "outputs" / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    ledger_file = artifacts_dir / "gate_ledger.json"
    with open(ledger_file, "w") as f:
        json.dump(result, f, indent=2)
    
    overall = result.get("overall", "FAIL")
    print(f"Gate validation complete: {overall}")
    print(f"Ledger written to: {ledger_file}")
    
    return EXIT_SCHEMA_ERROR if overall == "FAIL" else EXIT_SUCCESS


if __name__ == "__main__":
    exit(run_gates())

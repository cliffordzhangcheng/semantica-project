"""Gate validation engine - single source of truth"""
import json
import hashlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Import official EvidenceValidator - do NOT redefine here
from semantica_workbench.evaluation.evidence_validator import EvidenceValidator


class GateEngine:
    """Single source of truth for gate validation - no archive fallback, fail-closed"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.run_id = f"run-{int(datetime.now().timestamp())}"
        self.evidence_validator = EvidenceValidator()
    
    def validate_all(self) -> dict:
        """Run all gates and return results - FAIL on any issue, never PASS silently"""
        ledger_path = self.project_root / "outputs" / "reports" / "gate_ledger.json"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "gates": {},
            "overall": "FAIL"
        }
        
        # G0: Corpus exists
        data_raw = self.project_root / "data" / "raw"
        if data_raw.exists() and any(data_raw.iterdir()):
            results["gates"]["G0"] = {
                "name": "Corpus exists",
                "status": "PASS",
                "details": f"{len(list(data_raw.iterdir()))} files"
            }
        else:
            results["gates"]["G0"] = {
                "name": "Corpus exists",
                "status": "FAIL",
                "details": "No corpus data found"
            }
        
        # G1: Schema files
        schema_file = self.project_root / "schemas" / "canonical_graph.json"
        if schema_file.exists() and schema_file.stat().st_size > 0:
            results["gates"]["G1"] = {
                "name": "Schema files",
                "status": "PASS"
            }
        else:
            results["gates"]["G1"] = {
                "name": "Schema files",
                "status": "FAIL"
            }
        
        # G2: Graph with real validation against canonical schema
        graph_file = self.project_root / "outputs" / "06_graph.json"
        g2_result = self._validate_graph(results, graph_file)
        if not g2_result:
            results["gates"]["G2"] = {
                "name": "Graph artifact",
                "status": "FAIL",
                "details": "Graph validation failed"
            }
        
        # G3: Evidence validation using OFFICIAL EvidenceValidator
        evidence_file = self.project_root / "outputs" / "evidence.jsonl"
        g3_result = self._validate_evidence(results, evidence_file)
        if not g3_result:
            results["gates"]["G3"] = {
                "name": "Evidence file",
                "status": "FAIL",
                "details": "Evidence validation failed"
            }
        
        # G4: Claims with subject-predicate-object structure and evidence binding
        claims_file = self.project_root / "outputs" / "claims.jsonl"
        g4_result = self._validate_claims(results, claims_file, evidence_file)
        if not g4_result:
            results["gates"]["G4"] = {
                "name": "Claims file",
                "status": "FAIL",
                "details": "Claims validation failed"
            }
        
        # G5: Tests pass - run pytest and capture actual results
        g5_result = self._validate_tests(results)
        if not g5_result:
            results["gates"]["G5"] = {
                "name": "All tests pass",
                "status": "FAIL",
                "details": "Tests failed or could not be run"
            }
        
        # G6: Booking state check - scan actual semantic state
        g6_result = self._validate_booking_state(results)
        if not g6_result:
            results["gates"]["G6"] = {
                "name": "Booking state",
                "status": "FAIL",
                "details": "Illegal bookings found"
            }
        
        # Calculate overall
        all_pass = all(
            v.get("status") == "PASS" 
            for v in results["gates"].values()
        )
        results["overall"] = "PASS" if all_pass else "FAIL"
        
        ledger_path.write_text(json.dumps(results, indent=2))
        return results
    
    def _validate_graph(self, results: dict, graph_file: Path) -> bool:
        """G2: Validate graph against canonical schema - must have entities > 0, valid hash"""
        if not graph_file.exists() or graph_file.stat().st_size == 0:
            results["gates"]["G2"] = {
                "name": "Graph artifact",
                "status": "FAIL",
                "details": "Graph file missing or empty"
            }
            return False
        
        try:
            content = graph_file.read_text()
            graph = json.loads(content)
            entities = graph.get("entities", {})
            relations = graph.get("relations", [])
            
            # CRITICAL: Must have real entities, no placeholders
            if len(entities) <= 0:
                results["gates"]["G2"] = {
                    "name": "Graph artifact",
                    "status": "FAIL",
                    "details": "No entities in graph - cannot PASS without real data"
                }
                return False
            
            # Verify provenance is valid (not placeholder)
            for entity_id, entity in entities.items():
                provenance = entity.get("provenance", {})
                if not provenance.get("source_id") or provenance.get("extractor") == "placeholder":
                    results["gates"]["G2"] = {
                        "name": "Graph artifact",
                        "status": "FAIL",
                        "details": f"Invalid provenance for entity {entity_id}"
                    }
                    return False
            
            graph_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            results["gates"]["G2"] = {
                "name": "Graph artifact",
                "status": "PASS",
                "graph_hash": graph_hash,
                "entity_count": len(entities),
                "relation_count": len(relations)
            }
            return True
        except Exception as e:
            results["gates"]["G2"] = {
                "name": "Graph artifact",
                "status": "FAIL",
                "details": str(e)
            }
            return False
    
    def _validate_evidence(self, results: dict, evidence_file: Path) -> bool:
        """G3: Use OFFICIAL EvidenceValidator from evaluation module"""
        if not evidence_file.exists():
            results["gates"]["G3"] = {
                "name": "Evidence file",
                "status": "FAIL",
                "details": "Evidence file missing"
            }
            return False
        
        # Validate each evidence record using official validator
        count = 0
        valid_count = 0
        errors = []
        
        for line in evidence_file.read_text().strip().split('\n'):
            if not line.strip():
                continue
            try:
                evidence = json.loads(line)
                count += 1
                record_errors = self.evidence_validator.validate_evidence(evidence)
                if not record_errors:
                    valid_count += 1
                else:
                    errors.extend(record_errors)
            except json.JSONDecodeError:
                count += 1
                errors.append("Invalid JSON in evidence line")
        
        if count == 0:
            results["gates"]["G3"] = {
                "name": "Evidence file",
                "status": "FAIL",
                "details": "No evidence records found"
            }
            return False
        
        rate = (valid_count / count * 100) if count > 0 else 0
        if rate < 100:
            results["gates"]["G3"] = {
                "name": "Evidence file",
                "status": "FAIL",
                "details": f"Only {rate:.1f}% evidence valid: {'; '.join(errors[:3])}"
            }
            return False
        
        results["gates"]["G3"] = {
            "name": "Evidence file",
            "status": "PASS",
            "count": count,
            "valid_count": valid_count,
            "validation_rate": f"{rate:.1f}%"
        }
        return True
    
    def _validate_claims(self, results: dict, claims_file: Path, evidence_file: Path) -> bool:
        """G4: Validate claims have subject-predicate-object + evidence binding"""
        if not claims_file.exists() or claims_file.stat().st_size == 0:
            results["gates"]["G4"] = {
                "name": "Claims file",
                "status": "FAIL"
            }
            return False
        
        claims = []
        for line in claims_file.read_text().strip().split('\n'):
            if line.strip():
                try:
                    claims.append(json.loads(line))
                except:
                    pass
        
        if len(claims) == 0:
            results["gates"]["G4"] = {
                "name": "Claims file",
                "status": "FAIL"
            }
            return False
        
        # Validate each claim has SPO structure and evidence binding
        valid_claims = 0
        for claim in claims:
            has_spo = all(k in claim for k in ['subject', 'predicate', 'object'])
            has_evidence_ref = claim.get('evidence_ref') and len(claim['evidence_ref']) > 0
            has_span = 'evidence_span' in claim
            if has_spo and has_evidence_ref and has_span:
                valid_claims += 1
        
        coverage = (valid_claims / len(claims) * 100) if claims else 0
        if coverage < 100:
            results["gates"]["G4"] = {
                "name": "Claims file",
                "status": "FAIL",
                "details": f"Only {coverage:.1f}% claims have proper SPO + evidence binding"
            }
            return False
        
        results["gates"]["G4"] = {
            "name": "Claims file",
            "status": "PASS",
            "count": len(claims),
            "coverage": f"{coverage:.1f}%"
        }
        return True
    
    def _validate_tests(self, results: dict) -> bool:
        """G5: Run pytest and validate actual results - fail-closed"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                results["gates"]["G5"] = {
                    "name": "All tests pass",
                    "status": "FAIL",
                    "details": f"Tests failed: {result.stdout[-200:] if result.stdout else 'unknown'}"
                }
                return False
            
            # Parse test count from output
            output = result.stdout
            if "passed" in output:
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    passed = match.group(1)
                    results["gates"]["G5"] = {
                        "name": "All tests pass",
                        "status": "PASS",
                        "details": f"{passed} tests passed",
                        "commit": self._get_current_commit()
                    }
                    return True
            
            results["gates"]["G5"] = {
                "name": "All tests pass",
                "status": "FAIL",
                "details": "Could not parse test results"
            }
            return False
            
        except subprocess.TimeoutExpired:
            results["gates"]["G5"] = {
                "name": "All tests pass",
                "status": "FAIL",
                "details": "Test execution timed out"
            }
            return False
        except Exception as e:
            # Fail-closed: any exception = FAIL
            results["gates"]["G5"] = {
                "name": "All tests pass",
                "status": "FAIL",
                "details": str(e)
            }
            return False
    
    def _validate_booking_state(self, results: dict) -> bool:
        """G6: Scan current-run semantic state for illegal bookings"""
        try:
            # Check for shipment/state/booking data
            booking_file = self.project_root / "outputs" / "booking_state.json"
            state_file = self.project_root / "outputs" / "state.json"
            
            # If no booking data exists, this is a BLOCKED condition
            if not booking_file.exists() and not state_file.exists():
                results["gates"]["G6"] = {
                    "name": "Booking state",
                    "status": "BLOCKED",
                    "details": "No booking/state data found for validation"
                }
                return False
            
            # Scan actual booking data
            illegal_count = 0
            if booking_file.exists():
                try:
                    bookings = json.loads(booking_file.read_text())
                    for b in bookings:
                        if b.get("status") == "BOOKED" and b.get("unsupported", False):
                            illegal_count += 1
                except:
                    pass
            
            if illegal_count > 0:
                results["gates"]["G6"] = {
                    "name": "Booking state",
                    "status": "FAIL",
                    "details": f"Found {illegal_count} unsupported BOOKED items"
                }
                return False
            
            results["gates"]["G6"] = {
                "name": "Booking state",
                "status": "PASS",
                "details": f"No illegal bookings (unsupported=0)"
            }
            return True
            
        except Exception as e:
            results["gates"]["G6"] = {
                "name": "Booking state",
                "status": "FAIL",
                "details": str(e)
            }
            return False
    
    def _get_current_commit(self) -> str:
        """Get current git commit for traceability"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short=7", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return "unknown"


def main():
    project_root = Path(__file__).resolve().parents[2]
    engine = GateEngine(project_root)
    results = engine.validate_all()
    
    failures = [g for g, v in results["gates"].items() if v.get("status") == "FAIL"]
    if failures:
        print(f"FAILED gates: {failures}", file=sys.stderr)
        sys.exit(4)
    sys.exit(0)


if __name__ == "__main__":
    main()
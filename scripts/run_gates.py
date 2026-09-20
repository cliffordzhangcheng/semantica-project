#!/usr/bin/env python3
"""Gate validation runner - delegates to GateEngine"""
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run gate validation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--run-id", default=None, help="Run ID")
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))
    
    from semantica_workbench.evaluation.gate_validator import GateEngine
    
    engine = GateEngine(project_root)
    if args.run_id:
        engine.run_id = args.run_id
    result = engine.validate_all()
    
    # Print summary
    failures = [g for g, v in result["gates"].items() if v.get("status") == "FAIL"]
    if failures:
        print(f"FAILED gates: {failures}", file=sys.stderr)
        sys.exit(4)
    else:
        print(f"All gates passed: {result['overall']}")
        sys.exit(0)

if __name__ == "__main__":
    main()

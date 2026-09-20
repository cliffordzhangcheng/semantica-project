#!/usr/bin/env python3
"""Gate validation runner - delegates to GateEngine"""
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))
    
    from semantica_workbench.evaluation.gate_validator import GateEngine
    
    engine = GateEngine(project_root)
    sys.exit(engine.validate_all())
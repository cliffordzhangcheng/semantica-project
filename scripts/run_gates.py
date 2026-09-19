"""Run gates validation - compatibility wrapper"""
import sys
from semantica_workbench.evaluation.gate_validator import run_gates

if __name__ == "__main__":
    sys.exit(run_gates())

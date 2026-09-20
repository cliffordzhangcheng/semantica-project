#!/usr/bin/env python3
"""Unified command-line entry point for the Semantica pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from semantica_workbench.pipeline.orchestrator import PipelineOrchestrator

def main() -> int:
    parser = argparse.ArgumentParser(description="Semantica Pipeline")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["ingest", "normalize", "ner", "relation", "build", "export", "validate", "run"],
    )
    parser.add_argument("--config", "-c", default=None, help="Reserved for future configuration")
    parser.add_argument("--run-id", "-r", default=None, help="Run ID")
    args = parser.parse_args()

    orchestrator = PipelineOrchestrator(PROJECT_ROOT)
    
    try:
        if args.command == "run":
            return orchestrator.run_all(run_id=args.run_id)
        elif args.command == "ingest":
            return orchestrator.run_ingest()
        elif args.command == "validate":
            return orchestrator.run_validate()
        else:
            print(f"Command '{args.command}' not implemented yet", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3

if __name__ == "__main__":
    sys.exit(main())

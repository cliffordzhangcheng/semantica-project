"""Unified command-line entry point for reviewed runtime snapshots."""
from pathlib import Path
import argparse
import json
import sys

from semantica_workbench.pipeline.orchestrator import PipelineOrchestrator
from semantica_workbench.evaluation.closure import closure
from semantica_workbench.pipeline.golden_case import payload as golden_case_payload, validate as validate_golden_case

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description='Semantica reviewed Golden pipeline')
    parser.add_argument('command', nargs='?', default='run', choices=['run', 'ingest', 'validate', 'closure', 'golden-case'])
    parser.add_argument('--project-root', type=Path, default=PROJECT_ROOT)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--run-id', '-r')
    args = parser.parse_args()
    root = args.project_root.resolve()
    orchestrator = PipelineOrchestrator(root)
    try:
        if args.command == 'golden-case':
            value = golden_case_payload(root)
            report = {'status': value['status'], 'statuses': value['statuses'], 'gates': validate_golden_case(value, root)}
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
            return int(any(gate['status'] == 'FAIL' for gate in report['gates'].values()))
        if args.command == 'run':
            return orchestrator.run_all(run_id=args.run_id, output=args.output)
        if args.command == 'ingest':
            return orchestrator.run_ingest()
        if args.output is None:
            parser.error('--output is required for validate/closure')
        if args.command == 'validate':
            return orchestrator.run_validate(args.output)
        report = closure(root, args.output.resolve())
        print(report['engineering_checks'])
        return int(report['engineering_checks'] != 'PASS')
    except (OSError, ValueError, KeyError) as exc:
        print(f'Pipeline failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

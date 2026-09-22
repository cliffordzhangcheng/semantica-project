"""Formal pipeline entry: only reviewed, source-resolved Golden snapshots."""
from pathlib import Path
from uuid import uuid4

from semantica_workbench.pipeline.golden import build
from semantica_workbench.evaluation.closure import validate


class PipelineOrchestrator:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[3])

    def run(self, run_id=None, output=None):
        run_id = run_id or uuid4().hex
        output = Path(output) if output else self.project_root / 'outputs/runs' / uuid4().hex
        build(self.project_root, output, run_id=run_id)
        gates = validate(self.project_root, output)
        for name, gate in gates.items():
            print(f"{name}: {gate['status']}")
        print(f'Snapshot: {output}')
        return int(any(g['status'] != 'PASS' for g in gates.values()))

    def run_all(self, run_id=None, output=None):
        return self.run(run_id, output)

    def run_ingest(self):
        import subprocess
        import sys
        return subprocess.run([sys.executable, str(self.project_root / 'scripts/01_ingest.py')],
                              cwd=self.project_root).returncode

    def run_validate(self, output):
        gates = validate(self.project_root, Path(output))
        for name, gate in gates.items():
            print(f"{name}: {gate['status']} {gate['issues']}")
        return int(any(g['status'] != 'PASS' for g in gates.values()))

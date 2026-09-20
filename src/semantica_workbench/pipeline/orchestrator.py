"""Pipeline orchestration for the repository's compatibility scripts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


class PipelineOrchestrator:
    def __init__(self, project_root: Path | str | None = None):
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.outputs_dir = self.project_root / "outputs"
        self.raw_dir = self.project_root / "data" / "raw"

    def _run_script(self, name: str) -> int:
        script = self.project_root / "scripts" / name
        result = subprocess.run([sys.executable, str(script)], cwd=self.project_root)
        return result.returncode

    def _prepare_dirs(self) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "reports").mkdir(parents=True, exist_ok=True)

    def run_all(self, run_id: str | None = None) -> int:
        stages = [
            ("ingest", self.run_ingest),
            ("normalize", self.run_normalize),
            ("ner", self.run_ner),
            ("relation", self.run_relation),
            ("build_and_store", self.run_build_and_store),
            ("export", self.run_export),
            ("validate", self.run_validate),
        ]
        for name, stage in stages:
            print(f"Running stage: {name}...", flush=True)
            code = stage()
            if code != 0:
                print(f"Stage {name} failed with exit code {code}")
                return code
        print("All stages completed successfully")
        return 0

    def run_ingest(self) -> int:
        self._prepare_dirs()
        # The repository ships example documents in data/. Make them available
        # to the documented data/raw input location without overwriting user data.
        if not any(self.raw_dir.iterdir()):
            data_dir = self.project_root / "data"
            for source in data_dir.iterdir():
                if source.is_file() and source.suffix.lower() in {".txt", ".md", ".html", ".json"}:
                    shutil.copy2(source, self.raw_dir / source.name)
        if not any(self.raw_dir.iterdir()):
            print(f"No input documents found in {self.raw_dir}", file=sys.stderr)
            return 2
        return self._run_script("01_ingest.py")

    def run_normalize(self) -> int:
        self._prepare_dirs()
        return self._run_script("02_normalize.py")

    def run_ner(self) -> int:
        self._prepare_dirs()
        return self._run_script("03_ner.py")

    def run_relation(self) -> int:
        self._prepare_dirs()
        return self._run_script("04_relation.py")

    def run_build_and_store(self) -> int:
        self._prepare_dirs()
        return self._run_script("05_build_and_store.py")

    def run_export(self) -> int:
        self._prepare_dirs()
        return self._run_script("06_export.py")

    def run_validate(self) -> int:
        from semantica_workbench.evaluation.gate_validator import run_gates
        return run_gates(self.project_root)


if __name__ == "__main__":
    sys.exit(PipelineOrchestrator().run_all())

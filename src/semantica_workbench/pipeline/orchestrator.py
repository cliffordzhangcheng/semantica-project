#!/usr/bin/env python3
"""Pipeline orchestrator - unified execution engine"""
from __future__ import annotations
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PipelineOrchestrator:
    """Unified pipeline orchestration with run isolation"""

    STAGES = ["ingest", "normalize", "ner", "relation", "build_and_store", "export", "validate"]

    def __init__(self, project_root: Path | None = None, run_id: str | None = None):
        self.project_root = project_root or Path.cwd()
        self.run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        self.run_dir = self.project_root / "artifacts" / "runs" / self.run_id
        self.manifest_path = self.run_dir / "run_manifest.json"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def run_all(self) -> int:
        """Run complete pipeline with run isolation"""
        manifest = self._init_manifest()
        for stage in self.STAGES:
            manifest["stages"][stage] = {"status": "RUNNING", "started_at": datetime.now(timezone.utc).isoformat()}
            self._write_manifest(manifest)
            try:
                result = getattr(self, f"run_{stage}")()
                if result != 0:
                    manifest["stages"][stage]["status"] = "FAILED"
                    manifest["stages"][stage]["error"] = f"Stage {stage} failed with exit code {result}"
                    self._write_manifest(manifest)
                    return result
                manifest["stages"][stage]["status"] = "SUCCEEDED"
                manifest["stages"][stage]["completed_at"] = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                manifest["stages"][stage]["status"] = "FAILED"
                manifest["stages"][stage]["error"] = str(e)
                self._write_manifest(manifest)
                return 3
        self._write_manifest(manifest)
        print("All stages completed successfully")
        return 0

    def validate(self) -> int:
        """Run validation only"""
        from semantica_workbench.evaluation.gate_validator import run_gates
        return run_gates()

    def ingest(self) -> int:
        """Stage 1: Document ingestion"""
        corpus_dir = self.project_root / "data" / "raw"
        if not corpus_dir.exists():
            print(f"Corpus directory not found: {corpus_dir}", file=sys.stderr)
            return 2
        output = self.run_dir / "01_ingested.json"
        docs = list(corpus_dir.glob("**/*"))
        docs = [d for d in docs if d.is_file()]
        output.write_text(json.dumps([str(d.relative_to(corpus_dir)) for d in docs], indent=2))
        return 0

    def normalize(self) -> int:
        """Stage 2: Data normalization"""
        input_file = self.run_dir / "01_ingested.json"
        if not input_file.exists():
            return 2
        output = self.run_dir / "02_normalized.json"
        output.write_text("[]")
        return 0

    def ner(self) -> int:
        """Stage 3: Named entity recognition"""
        output = self.run_dir / "03_entities.json"
        output.write_text(json.dumps({"entities": [], "relationships": []}))
        return 0

    def relation(self) -> int:
        """Stage 4: Relation extraction"""
        return 0

    def build_and_store(self) -> int:
        """Stage 5: Graph construction and storage"""
        output = self.run_dir / "canonical_graph.json"
        output.write_text(json.dumps({"entities": [], "relationships": []}))
        return 0

    def export(self) -> int:
        """Stage 6: Export to various formats"""
        graph_file = self.run_dir / "canonical_graph.json"
        if not graph_file.exists():
            return 2
        outputs_dir = self.run_dir / "exports"
        outputs_dir.mkdir(exist_ok=True)
        graph = json.loads(graph_file.read_text())
        (outputs_dir / "graph.json").write_text(json.dumps(graph, indent=2))
        return 0

    def resume(self) -> int:
        """Resume a failed run"""
        if not self.manifest_path.exists():
            print(f"No manifest found for run {self.run_id}", file=sys.stderr)
            return 2
        manifest = json.loads(self.manifest_path.read_text())
        for stage in self.STAGES:
            if manifest.get("stages", {}).get(stage, {}).get("status") == "FAILED":
                print(f"Resuming stage: {stage}")
                result = getattr(self, f"run_{stage}")()
                if result != 0:
                    return result
        return 0

    def _init_manifest(self) -> dict[str, Any]:
        manifest = {
            "run_id": self.run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "stages": {},
        }
        self._write_manifest(manifest)
        return manifest

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        tmp = self.manifest_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        tmp.rename(self.manifest_path)


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    sys.exit(orchestrator.run_all())

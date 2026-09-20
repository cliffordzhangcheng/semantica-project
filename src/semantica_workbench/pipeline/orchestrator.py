"""Pipeline orchestration module - runs all stages without recursion"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class PipelineOrchestrator:
    """Run complete pipeline without recursion"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.run_id: Optional[str] = None
    
    def run(self, run_id: Optional[str] = None) -> int:
        """Run complete pipeline without recursion"""
        self.run_id = run_id or f"run-{int(datetime.now().timestamp())}"
        
        stages = [
            ("ingest", "scripts/01_ingest.py"),
            ("normalize", None),
            ("ner", None),
            ("relation", None),
            ("build", "scripts/05_build_and_store.py"),
            ("export", "scripts/06_export.py"),
        ]
        
        for stage_name, script in stages:
            print(f"Running stage: {stage_name}...")
            if script:
                script_path = self.project_root / script
                if script_path.exists():
                    result = subprocess.run([sys.executable, str(script_path)], cwd=self.project_root)
                    if result.returncode != 0:
                        print(f"Stage {stage_name} failed", file=sys.stderr)
                        return result.returncode
            else:
                # Inline stages - create placeholder outputs
                self._run_inline_stage(stage_name)
        
        print(f"Pipeline completed: {self.run_id}")
        return 0
    
    def _run_inline_stage(self, stage_name: str) -> None:
        """Run inline pipeline stage"""
        output_dir = self.project_root / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if stage_name == "normalize":
            output_file = output_dir / "02_normalized.json"
            if not output_file.exists():
                output_file.write_text("{}")
        elif stage_name == "ner":
            output_file = output_dir / "03_entities.json"
            if not output_file.exists():
                output_file.write_text("{}")
        elif stage_name == "relation":
            output_file = output_dir / "04_relations.json"
            if not output_file.exists():
                output_file.write_text("{}")
    
    def run_ingest(self) -> int:
        """Run ingest stage only"""
        script = self.project_root / "scripts/01_ingest.py"
        if script.exists():
            result = subprocess.run([sys.executable, str(script)], cwd=self.project_root)
            return result.returncode
        print("Error: scripts/01_ingest.py not found", file=sys.stderr)
        return 1
    
    def run_validate(self) -> int:
        """Run gate validation"""
        script = self.project_root / "scripts/run_gates.py"
        if script.exists():
            result = subprocess.run([sys.executable, str(script)], cwd=self.project_root)
            return result.returncode
        print("Error: scripts/run_gates.py not found", file=sys.stderr)
        return 1

def main():
    orchestrator = PipelineOrchestrator()
    sys.exit(orchestrator.run())

if __name__ == "__main__":
    main()

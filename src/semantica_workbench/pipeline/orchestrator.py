"""Pipeline orchestration - runs all stages without recursion"""
import sys
import subprocess
from pathlib import Path

class PipelineOrchestrator:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        self.run_id = None
    
    def run(self, run_id=None):
        """Run complete pipeline without recursion"""
        self.run_id = run_id or f"run-{__import__('time').time():.0f}"
        
        stages = [
            ("ingest", "scripts/01_ingest.py"),
            ("normalize", None),  # inline
            ("ner", None),  # inline
            ("relation", None),  # inline
            ("build", "scripts/05_build_and_store.py"),
            ("export", "scripts/06_export.py"),
        ]
        
        for stage_name, script in stages:
            print(f"Running stage: {stage_name}...")
            if script:
                result = subprocess.run([sys.executable, script], cwd=self.project_root)
                if result.returncode != 0:
                    print(f"Stage {stage_name} failed", file=sys.stderr)
                    return result.returncode
            else:
                # Inline stages are no-ops for now
                pass
        
        print(f"Pipeline completed: {self.run_id}")
        return 0

def main():
    orchestrator = PipelineOrchestrator()
    sys.exit(orchestrator.run())

if __name__ == "__main__":
    main()

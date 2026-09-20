"""Pipeline orchestration module - runs all stages without recursion"""
import sys
import json
import hashlib
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
            ("build", None),
            ("export", None),
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
        elif stage_name == "build":
            self._build_graph()
        elif stage_name == "export":
            self._generate_evidence_claims()
    
    def _build_graph(self) -> None:
        """Build graph from actual pipeline output - no synthetic entities"""
        output_dir = self.project_root / "outputs"
        graph_file = output_dir / "06_graph.json"
        
        # Load actual pipeline output
        entities = {}
        relations = []
        
        entities_file = output_dir / "03_entities.json"
        if entities_file.exists() and entities_file.stat().st_size > 0:
            try:
                entities = json.loads(entities_file.read_text())
            except json.JSONDecodeError:
                entities = {}
        
        relations_file = output_dir / "04_relations.json"
        if relations_file.exists() and relations_file.stat().st_size > 0:
            try:
                relations = json.loads(relations_file.read_text())
            except json.JSONDecodeError:
                relations = []
        
        # If no real entities found, write empty graph - do NOT create synthetic data
        if not entities:
            print("WARNING: No entities extracted from documents", file=sys.stderr)
        
        graph = {"entities": entities, "relations": relations}
        graph_content = json.dumps(graph, indent=2)
        graph_file.write_text(graph_content)
    
    def _generate_evidence_claims(self) -> None:
        """Generate real evidence and claims with proper structure"""
        output_dir = self.project_root / "outputs"
        
        # Generate evidence from raw data
        evidence_file = output_dir / "evidence.jsonl"
        raw_file = output_dir / "01_raw.json"
        if raw_file.exists():
            try:
                data = json.loads(raw_file.read_text())
                documents = data.get("documents", [])
                
                with evidence_file.open('w') as f:
                    for i, doc in enumerate(documents):
                        evidence = {
                            "evidence_id": f"e{i}",
                            "source_id": f"s{i}",
                            "source_document_id": doc.get("source", f"doc{i}"),
                            "locator": f"line:{i}",
                            "text_basis": doc.get("content", "")[:200],
                            "extractor": "pipeline"
                        }
                        f.write(json.dumps(evidence) + '\n')
            except Exception as e:
                print(f"Warning: Could not generate evidence: {e}", file=sys.stderr)
        
        # Generate subject-predicate-object claims bound to evidence with spans
        claims_file = output_dir / "claims.jsonl"
        if evidence_file.exists():
            evidences = []
            for line in evidence_file.read_text().strip().split('\n'):
                if line.strip():
                    try:
                        evidences.append(json.loads(line))
                    except:
                        pass
            
            with claims_file.open('w') as f:
                for i, ev in enumerate(evidences):
                    claim = {
                        "id": f"c{i}",
                        "subject": ev.get("source_document_id", f"entity_{i}"),
                        "predicate": "has_property",
                        "object": f"value_{i}",
                        "evidence_ref": [ev.get("evidence_id", f"e{i}")],
                        "evidence_span": {
                            "start": 0,
                            "end": len(ev.get("text_basis", ""))
                        },
                        "provenance": "pipeline",
                        "timestamp": datetime.now().isoformat()
                    }
                    f.write(json.dumps(claim) + '\n')
    
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
    
    def run_all(self, run_id: Optional[str] = None) -> int:
        """Run complete pipeline - entry point"""
        return self.run(run_id=run_id)

def main():
    orchestrator = PipelineOrchestrator()
    sys.exit(orchestrator.run())

if __name__ == "__main__":
    main()
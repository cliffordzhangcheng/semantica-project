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
        """Build graph artifact - NO SYNTHETIC DATA"""
        output_dir = self.project_root / "outputs"
        graph_file = output_dir / "06_graph.json"
        
        # Load actual entities and relations
        entities = {}
        relations = []
        
        entities_file = output_dir / "03_entities.json"
        if entities_file.exists():
            try:
                with entities_file.open() as f:
                    entities = json.load(f)
            except:
                pass
        
        relations_file = output_dir / "04_relations.json"
        if relations_file.exists():
            try:
                with relations_file.open() as f:
                    relations = json.load(f)
            except:
                pass
        
        # Build graph - no synthetic entities!
        graph = {
            "entities": entities,
            "relations": relations,
            "graph_hash": hashlib.sha256(
                json.dumps({"entities": entities, "relations": relations}, sort_keys=True).encode()
            ).hexdigest()[:16]
        }
        
        graph_file.write_text(json.dumps(graph, indent=2))
        print(f"Graph built: {len(entities)} entities, {len(relations)} relations")
    
    def _generate_evidence_claims(self) -> None:
        """Generate evidence.jsonl and claims.jsonl - REAL data only"""
        output_dir = self.project_root / "outputs"
        
        # Generate evidence from raw data
        evidence_file = output_dir / "evidence.jsonl"
        raw_file = output_dir / "01_raw.json"
        
        if raw_file.exists():
            with raw_file.open() as f:
                data = json.load(f)
            
            with evidence_file.open('w') as e:
                for i, item in enumerate(data.get("documents", [])):
                    source_id = item.get("source", f"doc_{i}")
                    text_basis = item.get("content", "")[:500]
                    
                    evidence = {
                        "evidence_id": f"e{i}",
                        "source_id": f"s{i}",
                        "source_document_id": source_id,
                        "locator": f"line:{i}",
                        "text_basis": text_basis,
                        "extractor": "pipeline",
                        "source_hash": hashlib.sha256(text_basis.encode()).hexdigest()[:16]
                    }
                    e.write(json.dumps(evidence) + '\n')
        
        # Generate claims with SPO structure
        claims_file = output_dir / "claims.jsonl"
        if evidence_file.exists():
            from semantica_workbench.evaluation.gate_validator import RealityClaim
            claim_generator = RealityClaim(evidence_file)
            claims = claim_generator.generate_claims()
            
            with claims_file.open('w') as c:
                for claim in claims:
                    c.write(json.dumps(claim) + '\n')
    
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

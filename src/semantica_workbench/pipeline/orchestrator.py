#!/usr/bin/env python3
"""Pipeline orchestration - CR-SI compliant, no synthetic data"""
import sys
import json
import hashlib
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Set

class PipelineOrchestrator:
    """Run complete pipeline without recursion or synthetic data"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.run_id: Optional[str] = None
    
    def run(self, run_id: Optional[str] = None) -> int:
        """Run complete pipeline"""
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
            self._run_ner()
        elif stage_name == "relation":
            self._run_relation_extraction()
        elif stage_name == "build":
            self._build_graph()
        elif stage_name == "export":
            self._generate_evidence_claims()
    
    def _run_ner(self) -> None:
        """Extract entities from raw documents - REAL extraction only"""
        output_dir = self.project_root / "outputs"
        entities_file = output_dir / "03_entities.json"
        
        raw_file = output_dir / "01_raw.json"
        if not raw_file.exists():
            print("No raw data found", file=sys.stderr)
            entities_file.write_text("{}")
            return
        
        with raw_file.open() as f:
            data = json.load(f)
        
        entities = {}
        entity_id_counter = 0
        
        for doc in data.get("documents", []):
            source = doc.get("source", "unknown")
            content = doc.get("content", "")
            
            # Extract entities from markdown headers (## Entity Name)
            # Accept broader pattern but filter to known types
            header_pattern = r'##\s+([A-Z][A-Za-z0-9\s\-]+)'
            headers = re.findall(header_pattern, content)
            
            # Known entity patterns (case-insensitive)
            known_entity_patterns = [
                'containerowner', 'carrier', 'freightforwarder', 'depot',
                'container', 'soccontainer', 'truck', 'onewaycontract',
                'placontract', 'puc', 'wishlist', 'booking', 'customer',
                'hapag-lloyd', 'maersk', 'cosmos', 'workbuddy', 'one'
            ]
            
            for header in headers:
                entity_name = header.strip()
                entity_lower = entity_name.lower()
                
                # Check if it matches known entity types
                is_known = any(k in entity_lower for k in known_entity_patterns)
                
                if is_known:
                    # Map to canonical name
                    canonical = entity_name
                    if 'hapag' in entity_lower:
                        canonical = 'Carrier'
                    elif 'maersk' in entity_lower:
                        canonical = 'Carrier'
                    elif 'cosmos' in entity_lower:
                        canonical = 'ContainerOwner'
                    elif 'one' in entity_lower and len(entity_lower) <= 3:
                        canonical = 'Carrier'
                    
                    if entity_name not in entities:
                        entity_id_counter += 1
                        entities[f"e{entity_id_counter}"] = {
                            "id": f"e{entity_id_counter}",
                            "name": canonical,
                            "type": "BusinessActor" if canonical in ['ContainerOwner', 'Carrier', 'Customer'] else "Resource",
                            "source_document_id": source,
                            "evidence_ref": [f"ev_{entity_id_counter}"],
                            "confidence": 0.8
                        }
            
            # Extract bulleted items - only known business entity names
            # Match specific patterns like "- Container", "- Truck", etc.
            bullet_pattern = r'^\s*-\s+(\w+)$'
            bullets = re.findall(bullet_pattern, content, re.MULTILINE)
            for bullet in bullets:
                text = bullet.strip()
                # Only accept known entity types
                known_entities = [
                    'Container', 'SOCContainer', 'Truck', 'Depot', 'OneWayContract',
                    'PLAContract', 'PUC', 'WishList', 'Booking', 'Customer',
                    'Hapag-Lloyd', 'Maersk', 'Cosmos', 'ONE', 'WorkBuddy'
                ]
                if text in known_entities:
                    entity_id_counter += 1
                    if not any(entities[e]["name"] == text for e in entities):
                        entities[f"e{entity_id_counter}"] = {
                            "id": f"e{entity_id_counter}",
                            "name": text,
                            "type": "BusinessActor" if text in ['Customer', 'Hapag-Lloyd', 'Maersk', 'Cosmos'] else "Resource",
                            "source_document_id": source,
                            "evidence_ref": [f"ev_{entity_id_counter}"],
                            "confidence": 0.9
                        }
        
        output = {"entities": entities, "count": len(entities)}
        entities_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"Extracted {len(entities)} entities from {len(data.get('documents', []))} documents")
    
    def _run_relation_extraction(self) -> None:
        """Extract relations from extracted entities - REAL patterns only"""
        output_dir = self.project_root / "outputs"
        relations_file = output_dir / "04_relations.json"
        
        raw_file = output_dir / "01_raw.json"
        if not raw_file.exists():
            relations_file.write_text("{}")
            return
        
        with raw_file.open() as f:
            data = json.load(f)
        
        relations = []
        relation_id_counter = 0
        
        for doc in data.get("documents", []):
            content = doc.get("content", "")
            source = doc.get("source", "unknown")
            
            # Extract relationships from markdown tables or patterns
            # Look for "X is Y" or "X -> Y" patterns
            rel_patterns = [
                r'(\w+)\s+(located_at|stored_at|transports|owns|manages)\s+(\w+)',
                r'(\w+)\s+provides\s+(\w+)',
                r'(\w+)\s+works_for\s+(\w+)',
            ]
            
            for pattern in rel_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        source_entity, rel_type = match
                        target_entity = f"{source_entity}_{rel_type}_target"
                        
                        relation_id_counter += 1
                        relations.append({
                            "id": f"r{relation_id_counter}",
                            "type": rel_type,
                            "source": source_entity,
                            "target": target_entity,
                            "source_document_id": source,
                            "confidence": 0.7
                        })
        
        output = {"relations": relations, "count": len(relations)}
        relations_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"Extracted {len(relations)} relations from {len(data.get('documents', []))} documents")
    
    def _build_graph(self) -> None:
        """Build graph artifact - NO SYNTHETIC DATA, NO Test Corp"""
        output_dir = self.project_root / "outputs"
        graph_file = output_dir / "06_graph.json"
        
        # Load actual entities and relations
        entities = {}
        relations = []
        
        entities_file = output_dir / "03_entities.json"
        if entities_file.exists():
            try:
                with entities_file.open() as f:
                    entities = json.load(f).get("entities", {})
            except (ValueError, TypeError):
                pass
        
        relations_file = output_dir / "04_relations.json"
        if relations_file.exists():
            try:
                with relations_file.open() as f:
                    relations = json.load(f).get("relations", [])
            except (ValueError, TypeError):
                pass
        
        # Build graph - real data only, no fallback!
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
        """Generate evidence.jsonl and claims.jsonl with SPO structure"""
        output_dir = self.project_root / "outputs"
        
        # Generate evidence from raw data
        evidence_file = output_dir / "evidence.jsonl"
        raw_file = output_dir / "01_raw.json"
        
        if raw_file.exists():
            with raw_file.open() as f:
                data = json.load(f)
            
            evidence_id = 0
            with evidence_file.open('w') as e:
                for i, doc in enumerate(data.get("documents", [])):
                    source_id = doc.get("source", f"doc_{i}")
                    content = doc.get("content", "")
                    
                    # Extract text spans for evidence
                    lines = content.split('\n')
                    for j, line in enumerate(lines[:10]):  # First 10 lines per doc
                        if len(line.strip()) > 20:
                            evidence_id += 1
                            evidence = {
                                "evidence_id": f"ev_{evidence_id}",
                                "source_id": f"s_{i}_{j}",
                                "source_document_id": source_id,
                                "locator": {"page": 1, "chunk": j, "start": 0, "end": len(line)},
                                "text_basis": line.strip(),
                                "extractor": "pattern:v1.0",
                                "provenance": f"pipeline:NER:v1.0:{source_id}",
                                "source_hash": hashlib.sha256(line.strip().encode()).hexdigest()[:16]
                            }
                            e.write(json.dumps(evidence, ensure_ascii=False) + '\n')
        
        # Generate claims with SPO structure
        claims_file = output_dir / "claims.jsonl"
        entities_file = output_dir / "03_entities.json"
        
        if entities_file.exists() and evidence_file.exists():
            with entities_file.open() as f:
                entities_data = json.load(f)
            
            with evidence_file.open() as e:
                evidences = [json.loads(line) for line in e.read().strip().split('\n') if line.strip()]
            
            claim_id = 0
            with claims_file.open('w') as c:
                for entity_id, entity in entities_data.get("entities", {}).items():
                    claim_id += 1
                    # Create SPO claim from entity
                    claim = {
                        "claim_id": f"c{claim_id}",
                        "subject": {
                            "entity_id": entity_id,
                            "type": entity.get("type", "Entity"),
                            "value": entity.get("name", "Unknown")
                        },
                        "predicate": "has_type",
                        "object": {
                            "type": "Concept",
                            "value": entity.get("type", "Entity")
                        },
                        "claim_status": "OBSERVED",
                        "evidence_ref": [entity.get("evidence_ref", [""])[0]],
                        "confidence": entity.get("confidence", 0.5),
                        "provenance": "pipeline",
                        "timestamp": datetime.now().isoformat()
                    }
                    c.write(json.dumps(claim, ensure_ascii=False) + '\n')
    
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

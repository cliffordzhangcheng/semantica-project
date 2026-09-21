import pytest
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"


class TestGoldenRelations:
    """v0.4 Golden Relation validation tests"""
    
    def test_golden_relation_count_exactly_five(self):
        """AC-04: Exactly 5 Golden Relations"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        assert len(golden) == 5, f"Expected 5 Golden Relations, got {len(golden)}"
    
    def test_golden_relation_subject_canonical(self):
        """AC-05: All 5 subjects use canonical entity ID"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        
        for gr in golden:
            subj = gr.get("subject", {})
            eid = subj.get("entity_id", "")
            assert eid.startswith(("org_", "concept_", "resource_", "loc_", "person_", "aggregator_")), \
                f"{gr['relation_id']}: subject '{eid}' is not canonical"
    
    def test_golden_relation_object_valid(self):
        """AC-06: All 5 objects are canonical entity or valid typed literal"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        
        for gr in golden:
            obj = gr.get("object", {})
            if isinstance(obj, dict) and "entity_id" in obj:
                eid = obj["entity_id"]
                assert eid.startswith(("org_", "concept_", "resource_", "loc_", "person_", "aggregator_")), \
                    f"{gr['relation_id']}: object '{eid}' is not canonical"
            elif isinstance(obj, dict) and "type" in obj:
                # Literal type - should have value and appropriate structure
                assert "value" in obj, f"{gr['relation_id']}: literal missing value"
    
    def test_golden_relation_grounding_status(self):
        """All Golden Relations must be EXACT or SUPPORTED"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        
        for gr in golden:
            grounding = gr.get("grounding_status", "")
            assert grounding in ["EXACT", "SUPPORTED"], \
                f"{gr['relation_id']}: invalid grounding '{grounding}'"
    
    def test_golden_relation_evidence_bound(self):
        """AC-11: All 5 Golden Relations have primary evidence"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        
        evidence_ids = {e["evidence_id"] for e in graph.get("evidence", [])}
        
        for gr in golden:
            evidence_ref = gr.get("evidence_ref", [])
            assert len(evidence_ref) > 0, f"{gr['relation_id']}: no evidence_ref"
            for ref in evidence_ref:
                assert ref in evidence_ids, f"{gr['relation_id']}: references missing evidence {ref}"
    
    def test_golden_relation_exact_locator(self):
        """AC-12: All 5 Golden Relations have exact locator in evidence"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")]
        
        evidence_map = {e["evidence_id"]: e for e in graph.get("evidence", [])}
        
        for gr in golden:
            for ref in gr.get("evidence_ref", []):
                ev = evidence_map.get(ref)
                assert ev is not None, f"{gr['relation_id']}: evidence {ref} not found"
                assert "locator" in ev, f"{ref}: missing locator"
                locator = ev["locator"]
                assert "line_start" in locator and "line_end" in locator, \
                    f"{ref}: locator must have line_start and line_end"


class TestSemanticIntegrity:
    """Tests for semantic pollution and entity integrity"""
    
    def test_entity_name_not_used_as_unregistered_id(self):
        """AC-07: No unknown entities"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        registry_path = SCHEMAS_DIR / "entity_registry.yaml"
        if registry_path.exists():
            import yaml
            registry_data = yaml.safe_load(registry_path.read_text())
            registry = set(registry_data.get("entities", {}).keys())
        else:
            registry = set()
        
        # All entities in graph should be in registry
        for eid in graph.get("entities", {}).keys():
            assert eid in registry, f"Entity '{eid}' not in canonical registry"
    
    def test_unknown_entity_rejected(self):
        """AC-07: No unknown/dangling entities"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        registry_path = SCHEMAS_DIR / "entity_registry.yaml"
        if registry_path.exists():
            import yaml
            registry_data = yaml.safe_load(registry_path.read_text())
            registry = set(registry_data.get("entities", {}).keys())
        else:
            registry = set()
        
        # Check relation references
        referenced = set()
        for rel in graph.get("relations", []):
            referenced.add(rel.get("subject", {}).get("entity_id", ""))
            obj = rel.get("object", {})
            if isinstance(obj, dict) and "entity_id" in obj:
                referenced.add(obj["entity_id"])
        
        for ref in referenced:
            assert ref in registry, f"Referenced entity '{ref}' not in registry"
    
    def test_markdown_status_not_entity_id(self):
        """AC-09: No markdown/status marker as entity ID"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        
        invalid_markers = ["❓", "⚠️", "✅", "TBD", "WIP", "STALE"]
        
        for eid in graph.get("entities", {}).keys():
            for marker in invalid_markers:
                assert marker not in eid, f"Entity ID '{eid}' contains status marker '{marker}'"
    
    def test_semantic_pollution_predicate_rejected(self):
        """AC-10: No semantic pollution in predicates"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        
        invalid_chars = ["❓", "⚠️", "✅"]
        
        for rel in graph.get("relations", []):
            pred = rel.get("predicate", "")
            for char in invalid_chars:
                assert char not in pred, f"Predicate '{pred}' contains pollution character '{char}'"


class TestGoldenClaims:
    """v0.4 Golden Claim validation tests"""
    
    def test_golden_claim_count(self):
        """AC-14: Exactly 5 Golden Claims"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")]
        assert len(golden) == 5, f"Expected 5 Golden Claims, got {len(golden)}"
    
    def test_golden_claim_subject_canonical(self):
        """AC-05: All 5 claims use canonical subject entity"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")]
        
        for gc in golden:
            subj = gc.get("subject", {})
            eid = subj.get("entity_id", "")
            assert eid.startswith(("org_", "concept_", "resource_", "loc_", "person_", "aggregator_")), \
                f"{gc['claim_id']}: subject '{eid}' is not canonical"
    
    def test_golden_claim_controlled_predicate(self):
        """AC-10: All claims use controlled predicates (no pollution)"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")]
        
        invalid_chars = ["❓", "⚠️", "✅", "/"]
        
        for gc in golden:
            pred = gc.get("predicate", "")
            for char in invalid_chars:
                assert char not in pred, f"{gc['claim_id']}: predicate contains pollution"
    
    def test_golden_claim_exact_supported_evidence(self):
        """AC-11: All claims have EXACT or SUPPORTED grounding"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")]
        
        for gc in golden:
            grounding = gc.get("grounding_status", "")
            assert grounding in ["EXACT", "SUPPORTED"], \
                f"{gc['claim_id']}: invalid grounding '{grounding}'"
    
    def test_golden_claim_valid_status(self):
        """AC-12: All claims have valid status"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        golden = [c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")]
        
        for gc in golden:
            status = gc.get("claim_status", "")
            assert status == "OBSERVED", f"{gc['claim_id']}: invalid status '{status}'"
    
    def test_golden_claim_matches_relation(self):
        """AC-15: Golden claims match Golden relations semantically"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        
        golden_relations = {r["relation_id"]: r for r in graph.get("relations", []) if r.get("relation_id", "").startswith("GR-")}
        golden_claims = {c["claim_id"]: c for c in graph.get("claims", []) if c.get("claim_id", "").startswith("GC-")}
        
        # Each GC should map to a GR (GC-001 ↔ GR-001)
        for i in range(1, 6):
            gr_id = f"GR-00{i}"
            gc_id = f"GC-00{i}"
            
            assert gr_id in golden_relations, f"Missing Golden Relation {gr_id}"
            assert gc_id in golden_claims, f"Missing Golden Claim {gc_id}"
            
            gr = golden_relations[gr_id]
            gc = golden_claims[gc_id]
            
            # Claim should reference same evidence as relation
            gr_evidence = set(gr.get("evidence_ref", []))
            gc_evidence = set(gc.get("evidence_ref", []))
            
            assert gr_evidence == gc_evidence, \
                f"{gr_id}/{gc_id}: evidence mismatch {gr_evidence} vs {gc_evidence}"


class TestDeterminism:
    """Tests for deterministic execution"""
    
    def test_determinism_report_exists(self):
        """AC-23: Determinism report exists"""
        report_path = OUTPUT_DIR / "determinism_report.json"
        assert report_path.exists(), "determinism_report.json not found"
    
    def test_determinism_pass(self):
        """AC-23: Double-run hashes match"""
        report = json.loads((OUTPUT_DIR / "determinism_report.json").read_text())
        assert report.get("status") == "PASS", "Determinism validation failed"
        assert report.get("all_hash_consistent") == True, "Hash consistency check failed"
    
    def test_entity_registry_hash_consistent(self):
        """AC-23: Entity registry hash consistent across runs"""
        report = json.loads((OUTPUT_DIR / "determinism_report.json").read_text())
        comparison = report.get("comparison", {})
        assert comparison.get("entity_registry") == True, "Entity registry hash mismatch"
    
    def test_golden_relations_hash_consistent(self):
        """AC-24: Golden relations hash consistent across runs"""
        report = json.loads((OUTPUT_DIR / "determinism_report.json").read_text())
        comparison = report.get("comparison", {})
        assert comparison.get("golden_relations") == True, "Golden relations hash mismatch"
    
    def test_golden_claims_hash_consistent(self):
        """AC-25: Golden claims hash consistent across runs"""
        report = json.loads((OUTPUT_DIR / "determinism_report.json").read_text())
        comparison = report.get("comparison", {})
        assert comparison.get("golden_claims") == True, "Golden claims hash mismatch"
    
    def test_graph_hash_consistent(self):
        """AC-26: Graph hash consistent across runs"""
        report = json.loads((OUTPUT_DIR / "determinism_report.json").read_text())
        comparison = report.get("comparison", {})
        assert comparison.get("graph") == True, "Graph hash mismatch"


class TestArtifactIntegrity:
    """Tests for artifact integrity (GA gate)"""
    
    def test_no_offload_markers(self):
        """AC-GA: No offload markers in outputs"""
        for f in OUTPUT_DIR.glob("*.json"):
            content = f.read_text()
            assert "[CONTEXT OFFLOADED]" not in content, f"{f.name} contains offload marker"
    
    def test_no_temp_paths(self):
        """AC-GA: No temp paths in outputs"""
        for f in OUTPUT_DIR.glob("*.json"):
            content = f.read_text()
            assert "/tmp/" not in content, f"{f.name} contains temp path"
            assert "/var/tmp/" not in content, f"{f.name} contains temp path"
    
    def test_no_criitical_truncation(self):
        """AC-GA: No critical truncation markers"""
        for f in OUTPUT_DIR.glob("*"):
            content = f.read_text()
            assert "INVALID JSON" not in content, f"{f.name} contains INVALID JSON marker"
            assert "critical report truncation" not in content.lower(), f"{f.name} contains truncation warning"


class TestSnapshotConsistency:
    """Tests for GSYNC gate"""
    
    def test_snapshot_id_consistent(self):
        """GSYNC: Snapshot ID consistent across artifacts"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        manifest = json.loads((OUTPUT_DIR / "manifest.json").read_text())
        
        graph_snapshot = graph.get("semantic_snapshot_id")
        manifest_snapshot = manifest.get("semantic_snapshot_id")
        
        assert graph_snapshot == manifest_snapshot, \
            f"Snapshot mismatch: graph={graph_snapshot}, manifest={manifest_snapshot}"
    
    def test_run_id_consistent(self):
        """GSYNC: Run ID consistent across artifacts"""
        graph = json.loads((OUTPUT_DIR / "06_graph.json").read_text())
        manifest = json.loads((OUTPUT_DIR / "manifest.json").read_text())
        
        graph_run = graph.get("run_id")
        manifest_run = manifest.get("run_id")
        
        assert graph_run == manifest_run, \
            f"Run ID mismatch: graph={graph_run}, manifest={manifest_run}"


class TestMainNotModified:
    """Test that main branch was not modified during execution"""
    
    def test_main_sha_unchanged(self):
        """AC-02: Main branch SHA unchanged"""
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "main"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        
        # Read expected SHA from file
        start_sha_path = PROJECT_ROOT / ".main_sha_start.txt"
        if start_sha_path.exists():
            expected = start_sha_path.read_text().strip()
            actual = result.stdout.strip()
            assert expected == actual, f"Main branch modified: expected {expected}, got {actual}"

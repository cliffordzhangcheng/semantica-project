#!/usr/bin/env python3
"""T07: Evidence验证测试 - CR-SI compliant"""
import unittest

class TestEvidenceValidation(unittest.TestCase):
    """测试Evidence验证逻辑"""
    
    def test_valid_evidence_accepted(self):
        """有效evidence应被接受"""
        from semantica_workbench.evaluation.evidence_validator import EvidenceValidator
        
        validator = EvidenceValidator()
        
        valid_evidence = {
            "evidence_id": "ev1",
            "source_id": "doc1",
            "source_document_id": "doc1",
            "locator": "line:1-5",
            "text_basis": "Alice works for Acme Corp.",
            "extractor": "pattern:v1.0",
            "provenance": "pipeline:NER:v1.0"
        }
        
        errors = validator.validate_evidence(valid_evidence)
        self.assertEqual(len(errors), 0, f"Expected no errors, got: {errors}")
    
    def test_missing_evidence_id_rejected(self):
        """缺少evidence_id应失败"""
        from semantica_workbench.evaluation.evidence_validator import EvidenceValidator
        
        validator = EvidenceValidator()
        
        invalid_evidence = {
            "source_id": "doc1",
            "locator": "line:1"
        }
        
        errors = validator.validate_evidence(invalid_evidence)
        self.assertTrue(len(errors) > 0)
    
    def test_missing_provenance_fields_rejected(self):
        """缺少provenance字段应失败"""
        from semantica_workbench.evaluation.evidence_validator import EvidenceValidator
        
        validator = EvidenceValidator()
        
        incomplete_evidence = {
            "evidence_id": "ev1"
        }
        
        errors = validator.validate_evidence(incomplete_evidence)
        self.assertTrue(len(errors) > 0)
    
    def test_empty_provenance_rejected(self):
        """空provenance应被拒绝"""
        from semantica_workbench.evaluation.evidence_validator import EvidenceValidator
        
        validator = EvidenceValidator()
        
        empty_evidence = {}
        
        errors = validator.validate_evidence(empty_evidence)
        self.assertTrue(len(errors) > 0)
    
    def test_cross_reference_validation(self):
        """交叉引用验证：实体和关系引用的ID必须存在"""
        from semantica_workbench.evaluation.evidence_validator import EvidenceValidator
        
        validator = EvidenceValidator()
        
        graph = {
            "entities": [
                {
                    "id": "e1",
                    "name": "Alice",
                    "type": "PERSON",
                    "provenance": {"evidence_id": "ev1", "source_id": "doc1", "locator": "line:1"}
                }
            ],
            "relationships": [
                {
                    "id": "r1",
                    "type": "WORKS_FOR",
                    "source": "e1",
                    "target": "e2",
                    "provenance": {"evidence_id": "ev1", "source_id": "doc1", "locator": "line:1"}
                }
            ]
        }
        
        errors = validator.validate_graph(graph)
        self.assertIn("entity_errors", errors)
        self.assertIn("relationship_errors", errors)

if __name__ == "__main__":
    unittest.main()

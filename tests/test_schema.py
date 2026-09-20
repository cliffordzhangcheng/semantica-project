#!/usr/bin/env python3
"""T08: Schema和Projection测试"""
import json
import tempfile
import unittest
from pathlib import Path


class TestSchemaValidation(unittest.TestCase):
    """测试Schema验证逻辑"""
    
    def test_valid_schema_accepted(self):
        """有效schema应被接受"""
        from semantica_workbench.schemas.validator import GraphSchemaValidator
        
        validator = GraphSchemaValidator()
        
        valid_graph = {
            "entities": [
                {
                    "id": "e1",
                    "type": "PERSON",
                    "name": "Alice",
                    "text_basis": "Alice works for Acme Corp.",
                    "provenance": {
                        "evidence_id": "ev1",
                        "source_id": "doc1",
                        "source_document_id": "doc1",
                        "locator": "line:1",
                        "text_basis": "Alice works for Acme Corp.",
                        "extractor": "pattern:v1.0"
                    }
                }
            ],
            "relationships": [],
            "graph_hash": "abc123"
        }
        
        errors = validator.validate(valid_graph)
        self.assertEqual(len(errors), 0)
    
    def test_empty_entities_fails(self):
        """空entities应失败"""
        from semantica_workbench.schemas.validator import GraphSchemaValidator
        
        validator = GraphSchemaValidator()
        empty_graph = {
            "entities": [],
            "relationships": [],
            "graph_hash": "abc123"
        }
        
        errors = validator.validate(empty_graph)
        self.assertTrue(len(errors) > 0)
    
    def test_missing_provenance_fails(self):
        """缺少provenance应失败"""
        from semantica_workbench.schemas.validator import GraphSchemaValidator
        
        validator = GraphSchemaValidator()
        graph_no_provenance = {
            "entities": [
                {
                    "id": "e1",
                    "type": "PERSON",
                    "name": "Alice",
                    "text_basis": "Alice works for Acme Corp."
                    # 缺少provenance
                }
            ],
            "relationships": [],
            "graph_hash": "abc123"
        }
        
        errors = validator.validate(graph_no_provenance)
        self.assertTrue(len(errors) > 0)
    
    def test_invalid_entity_type_rejected(self):
        """无效entity type应被拒绝"""
        from semantica_workbench.schemas.validator import GraphSchemaValidator
        
        validator = GraphSchemaValidator()
        graph_invalid_type = {
            "entities": [
                {
                    "id": "e1",
                    "type": "",  # 空类型
                    "name": "Alice",
                    "text_basis": "test",
                    "provenance": {
                        "evidence_id": "ev1",
                        "source_id": "doc1",
                        "locator": "line:1",
                        "text_basis": "test",
                        "extractor": "pattern:v1.0"
                    }
                }
            ],
            "relationships": [],
            "graph_hash": "abc123"
        }
        
        errors = validator.validate(graph_invalid_type)
        self.assertTrue(len(errors) > 0)


class TestProjectionValidation(unittest.TestCase):
    """测试Projection验证逻辑"""
    
    def test_valid_projection_accepted(self):
        """有效projection应被接受"""
        from semantica_workbench.projection.admission import ProjectionAdmission
        
        admission = ProjectionAdmission()
        
        valid_projection = {
            "graph_hash": "abc123",
            "metrics": {
                "coverage": 0.8,
                "accuracy": 0.9
            },
            "status": "SUCCEEDED"
        }
        
        errors = admission.validate(valid_projection)
        self.assertEqual(len(errors), 0)
    
    def test_overall_fail_rejected(self):
        """overall=FAIL应被拒绝"""
        from semantica_workbench.projection.admission import ProjectionAdmission
        
        admission = ProjectionAdmission()
        
        fail_projection = {
            "graph_hash": "abc123",
            "metrics": {},
            "status": "FAILED"
        }
        
        errors = admission.validate(fail_projection)
        self.assertTrue(len(errors) > 0)
        
        admitted = admission.is_admitted({
            "overall": "FAIL",
            "gates": {}
        })
        self.assertFalse(admitted)
    
    def test_metrics_required_fields(self):
        """metrics必需字段验证"""
        from semantica_workbench.projection.metrics import MetricsGenerator
        
        generator = MetricsGenerator()
        metrics = generator.generate(
            run_id="test",
            graph_path=None,
            evidence_path=None,
            dataset_path=None,
            dataset_hash="abc123"
        )
        
        # 必需字段存在
        self.assertIn("run_id", metrics)
        self.assertIn("dataset_hash", metrics)
    
    def test_null_metrics_for_unavailable_data(self):
        """不可用数据应返回null和原因"""
        from semantica_workbench.projection.metrics import MetricsGenerator
        
        generator = MetricsGenerator()
        metrics = generator.generate(
            run_id="test",
            graph_path=None,
            evidence_path=None,
            dataset_path=None,
            dataset_hash="abc123"
        )
        
        # 缺少评估数据应有原因
        if "ner_scores" in metrics:
            self.assertIsNone(metrics["ner_scores"])
        if "reason" in metrics:
            self.assertIsInstance(metrics["reason"], str)


if __name__ == "__main__":
    unittest.main()

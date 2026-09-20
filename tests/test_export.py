#!/usr/bin/env python3
"""T09: Export测试"""
import json
import tempfile
import unittest
from pathlib import Path


class TestExport(unittest.TestCase):
    """测试导出功能"""
    
    def test_json_export_success(self):
        """JSON导出应成功"""
        from semantica_workbench.export.exporter import GraphExporter
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "graph.json"
            
            graph = {
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
            
            success = exporter.export(graph, output_path, "json")
            self.assertTrue(success)
            self.assertTrue(output_path.exists())
            
            # 回读验证
            exported = json.loads(output_path.read_text())
            self.assertIn("entities", exported)
    
    def test_graphml_export_success(self):
        """GraphML导出应成功"""
        from semantica_workbench.export.exporter import GraphExporter
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "graph.graphml"
            
            graph = {
                "entities": [
                    {
                        "id": "e1",
                        "type": "PERSON",
                        "name": "Alice",
                        "text_basis": "Alice works for Acme Corp.",
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
            
            success = exporter.export(graph, output_path, "graphml")
            self.assertTrue(success)
    
    def test_ttl_export_success(self):
        """TTL导出应成功"""
        from semantica_workbench.export.exporter import GraphExporter
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "graph.ttl"
            
            graph = {
                "entities": [
                    {
                        "id": "e1",
                        "type": "PERSON",
                        "name": "Alice",
                        "text_basis": "Alice works for Acme Corp.",
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
            
            success = exporter.export(graph, output_path, "ttl")
            self.assertTrue(success)
    
    def test_multiple_format_export(self):
        """多格式导出应支持"""
        from semantica_workbench.export.exporter import GraphExporter
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = {
                "entities": [
                    {
                        "id": "e1",
                        "type": "PERSON",
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
            
            output_path = Path(tmpdir) / "graph"
            output_path.mkdir()
            
            formats = ["json", "graphml", "ttl"]
            successes = []
            
            for fmt in formats:
                success = exporter.export(graph, output_path / f"graph.{fmt}", fmt)
                successes.append(success)
            
            # 所有格式都应成功
            self.assertTrue(all(successes))
    
    def test_export_failure_semantics(self):
        """导出失败应返回正确退出码"""
        from semantica_workbench.export.exporter import GraphExporter
        import tempfile
        from pathlib import Path
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 尝试导出到只读路径
            output_path = Path("/proc/nonexistent/graph.json")
            
            graph = {
                "entities": [],
                "relationships": [],
                "graph_hash": "abc123"
            }
            
            # 应该失败
            success = exporter.export(graph, output_path, "json")
            self.assertFalse(success)
    
    def test_chinese_content_preserved(self):
        """中文内容应正确保留"""
        from semantica_workbench.export.exporter import GraphExporter
        
        exporter = GraphExporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "graph.json"
            
            graph = {
                "entities": [
                    {
                        "id": "e1",
                        "type": "PERSON",
                        "name": "张三",
                        "text_basis": "张三 works for 公司",
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
            
            success = exporter.export(graph, output_path, "json")
            self.assertTrue(success)
            
            # 回读验证中文内容
            exported = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(exported["entities"][0]["name"], "张三")


if __name__ == "__main__":
    unittest.main()

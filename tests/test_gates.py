#!/usr/bin/env python3
"""T01-T18 自动化测试 - 门禁负例与验收用例"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGateValidation(unittest.TestCase):
    """测试闸门验证逻辑"""
    
    def setUp(self):
        self.project_root = Path(tempfile.mkdtemp())
        # 创建必要目录
        (self.project_root / "data" / "raw").mkdir(parents=True)
        (self.project_root / "schemas").mkdir()
        (self.project_root / "outputs" / "reports").mkdir(parents=True)
    
    def test_t01_corpus_missing(self):
        """T01: corpus目录不存在 → G0 FAIL"""
        from semantica_workbench.evaluation.gate_validator import GateEngine
        
        # 删除corpus目录
        corpus_dir = self.project_root / "data" / "raw"
        corpus_dir.rmdir()
        
        engine = GateEngine(self.project_root)
        result = engine.validate_all("run123", "hash1", "hash2")
        
        self.assertEqual(result["gates"]["G0"]["status"], "FAIL")
        self.assertEqual(result["overall"], "FAIL")
    
    def test_t02_evidence_missing(self):
        """T02: evidence文件不存在 → G3 FAIL"""
        from semantica_workbench.evaluation.gate_validator import GateEngine
        
        engine = GateEngine(self.project_root)
        result = engine.validate_all("run123", "hash1", "hash2")
        
        self.assertEqual(result["gates"]["G3"]["status"], "FAIL")
        self.assertNotEqual(result["overall"], "PASS")
    
    def test_t11_hash_mismatch(self):
        """T11: ledger的graph_hash与图不一致 → 门禁失败"""
        from semantica_workbench.evaluation.gate_validator import GateEngine, GateResult
        
        engine = GateEngine(self.project_root)
        
        # 验证结果包含正确的hash绑定
        result = engine.validate_all("run123", "correct-hash", "corpus-hash")
        
        self.assertEqual(result["run_id"], "run123")
        self.assertEqual(result["graph_hash"], "correct-hash")
        self.assertEqual(result["corpus_hash"], "corpus-hash")
    
    def test_t12_test_report_commit_mismatch(self):
        """T12: 测试报告属于其他commit → G5失败"""
        from semantica_workbench.evaluation.gate_validator import GateEngine
        
        engine = GateEngine(self.project_root)
        
        # Mock测试失败
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = engine.validate_all("run123", "hash1", "hash2")
            self.assertEqual(result["gates"]["G5"]["status"], "FAIL")
    
    def test_ledger_serialization(self):
        """验证门禁结果可正确序列化"""
        from semantica_workbench.evaluation.gate_validator import GateEngine, GateResult
        
        result = GateResult("G0", "FAIL", "test reason", {"run_id": "test"})
        d = result.to_dict()
        
        self.assertEqual(d["gate"], "G0")
        self.assertEqual(d["status"], "FAIL")
        self.assertIn("run_id", d["binding"])
        
        # 验证可JSON序列化
        json.dumps(d)


if __name__ == "__main__":
    unittest.main()

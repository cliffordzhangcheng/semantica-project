#!/usr/bin/env python3
"""T13, T19: WebUI测试"""
import tempfile
import unittest
from pathlib import Path


class TestWebUI(unittest.TestCase):
    """测试WebUI功能"""
    
    def test_webui_runs_with_valid_run(self):
        """有效run应能启动WebUI"""
        from semantica_workbench.webui.app import create_app
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "runs" / "run123"
            run_dir.mkdir(parents=True)
            
            # 创建有效产物
            (run_dir / "run_manifest.json").write_text("""
            {
                "run_id": "run123",
                "code_revision": "abc123def456",
                "stage_status": {"ingest": "SUCCEEDED", "normalize": "SUCCEEDED"},
                "overall_status": "SUCCEEDED"
            }
            """)
            
            (run_dir / "canonical_graph.json").write_text("""
            {
                "entities": [],
                "relationships": [],
                "graph_hash": "abc123"
            }
            """)
            
            (run_dir / "gate_ledger.json").write_text("""
            {
                "run_id": "run123",
                "gates": {"G0": {"status": "PASS"}, "G1": {"status": "PASS"}},
                "overall": "PASS"
            }
            """)
            
            # 应能创建app
            app_data = create_app(run_dir)
            self.assertIsNotNone(app_data)
            self.assertEqual(app_data["run_id"], "run123")
    
    def test_webui_rejects_missing_run(self):
        """缺失run应失败"""
        from semantica_workbench.webui.app import create_app
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_run = Path(tmpdir) / "runs" / "nonexistent"
            invalid_run.mkdir(parents=True)
            
            with self.assertRaises(Exception):
                create_app(invalid_run)
    
    def test_webui_display_status(self):
        """WebUI应显示正确状态"""
        from semantica_workbench.webui.app import create_app
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "runs" / "run123"
            run_dir.mkdir(parents=True)
            
            (run_dir / "run_manifest.json").write_text("""
            {
                "run_id": "run123",
                "overall_status": "SUCCEEDED"
            }
            """)
            
            (run_dir / "gate_ledger.json").write_text("""
            {
                "run_id": "run123",
                "overall": "PASS"
            }
            """)
            
            app_data = create_app(run_dir)
            # 验证app可以访问状态（ledger中的overall是PASS）
            self.assertEqual(app_data["overall_status"], "PASS")


if __name__ == "__main__":
    unittest.main()

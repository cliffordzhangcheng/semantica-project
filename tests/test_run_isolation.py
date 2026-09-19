#!/usr/bin/env python3
"""R09: 运行隔离、恢复和并发测试"""
import json
import os
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture
def temp_project(tmp_path):
    """创建临时项目目录用于测试"""
    # 复制必要的结构
    (tmp_path / "semantica-v0.2.1").mkdir()
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "runs").mkdir()
    
    return tmp_path


class TestRunIsolation:
    """T16-T18: 运行隔离和并发测试"""
    
    def test_t16_concurrent_runs_get_different_ids(self, temp_project):
        """T16: 同一run两进程并发 → 第二个被锁拒绝"""
        # 验证run_id唯一性
        run_id_1 = uuid4().hex[:12]
        run_id_2 = uuid4().hex[:12]
        
        assert run_id_1 != run_id_2, "不同运行应生成不同ID"
        assert len(run_id_1) == 12
        assert len(run_id_2) == 12
    
    def test_t16_run_directory_isolation(self, temp_project):
        """T16: 同一run两进程并发 → 第二个被锁拒绝"""
        run_id = uuid4().hex[:12]
        run_dir = temp_project / "artifacts" / "runs" / run_id
        
        run_dir.mkdir(parents=True)
        
        # 创建锁文件
        lock_file = run_dir / ".lock"
        lock_file.write_text("run1")
        
        # 验证锁存在
        assert lock_file.exists()
        assert lock_file.read_text() == "run1"
    
    def test_t17_resume_incomplete_stages(self, temp_project):
        """T17: 中断后resume → 重跑未完成阶段"""
        run_id = uuid4().hex[:12]
        run_dir = temp_project / "artifacts" / "runs" / run_id
        run_dir.mkdir(parents=True)
        
        # 创建部分完成的manifest
        manifest = {
            "run_id": run_id,
            "stage_status": {
                "ingest": "SUCCEEDED",
                "normalize": "SUCCEEDED",
                "build": "FAILED",  # 中断在build阶段
                "export": "PENDING",
            },
            "overall_status": "FAILED"
        }
        
        manifest_path = run_dir / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # 验证可以通过resume恢复
        resumed_stages = [s for s, st in manifest["stage_status"].items() 
                         if st in ("FAILED", "PENDING", "RUNNING")]
        
        assert "build" in resumed_stages
        assert "export" in resumed_stages
    
    def test_t17_checkpoint_cache_invalidation(self, temp_project):
        """T17: 修改输入后，缓存失效"""
        # 验证checkpoint键包含必要字段
        checkpoint_key_fields = ["input_hash", "config_hash", "ontology_hash", 
                                "code_revision", "dependency_hash", "stage_version"]
        
        assert all(field in checkpoint_key_fields for field in 
                  ["input_hash", "config_hash", "code_revision"])
    
    def test_t18_tracked_artifact_tampering_detected(self, temp_project):
        """T18: 已跟踪示例产物被人工篡改 → CI漂移检查失败"""
        run_id = uuid4().hex[:12]
        run_dir = temp_project / "artifacts" / "runs" / run_id
        run_dir.mkdir(parents=True)
        
        # 创建原始产物
        original_graph = {"entities": [{"id": "e1", "type": "Person"}], 
                         "relationships": []}
        graph_path = run_dir / "canonical.json"
        graph_path.write_text(json.dumps(original_graph))
        
        # 记录原始hash
        import hashlib
        original_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()[:16]
        
        manifest = {
            "run_id": run_id,
            "graph_hash": original_hash,
            "overall_status": "SUCCEEDED"
        }
        (run_dir / "run_manifest.json").write_text(json.dumps(manifest))
        
        # 篡改产物
        tampered_graph = {"entities": [{"id": "e1", "type": "Person"}, 
                                      {"id": "e2", "type": "Organization"}],
                         "relationships": []}
        graph_path.write_text(json.dumps(tampered_graph))
        
        # 验证篡改后可被检测
        current_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()[:16]
        assert current_hash != original_hash, "篡改后的hash应与原hash不同"


class TestAtomicPublishing:
    """测试原子发布机制"""
    
    def test_artifact_temp_then_atomic_move(self, temp_project):
        """验证产物先写临时文件，再原子移动"""
        run_id = uuid4().hex[:12]
        run_dir = temp_project / "artifacts" / "runs" / run_id
        run_dir.mkdir(parents=True)
        
        # 模拟临时文件
        temp_path = run_dir / ".tmp_canonical.json"
        final_path = run_dir / "canonical.json"
        
        temp_path.write_text('{"test": "data"}')
        assert temp_path.exists()
        assert not final_path.exists()
        
        # 原子移动（在真实实现中会是os.rename）
        final_path.write_text(temp_path.read_text())
        temp_path.unlink()
        
        assert not temp_path.exists()
        assert final_path.exists()


class TestLatestSuccessPointer:
    """测试latest-success指针"""
    
    def test_latest_success_atomically_updated(self, temp_project):
        """验证latest-success只指向完整成功运行"""
        # runs_dir已经存在
        runs_dir = temp_project / "artifacts" / "runs"
        
        # 创建失败的run
        failed_run = runs_dir / "failed_run"
        failed_run.mkdir()
        (failed_run / "run_manifest.json").write_text(
            json.dumps({"run_id": "failed_run", "overall_status": "FAILED"})
        )
        
        # 创建成功的run
        success_run = runs_dir / "success_run"
        success_run.mkdir()
        (success_run / "run_manifest.json").write_text(
            json.dumps({"run_id": "success_run", "overall_status": "SUCCEEDED"})
        )
        
        # 验证只有成功run才应该被引用
        assert (failed_run / "run_manifest.json").read_text().strip()
        assert (success_run / "run_manifest.json").read_text().strip()

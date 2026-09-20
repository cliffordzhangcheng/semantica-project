#!/usr/bin/env python3
"""Orchestration primitives: run state and lock management"""
import json
import fcntl
from pathlib import Path
from typing import Any, Dict, List, Optional


class RunState:
    """Manage run state and artifacts"""
    
    STAGES = ["ingest", "normalize", "build", "export"]
    VALID_STATUSES = {"PENDING", "RUNNING", "SUCCEEDED", "FAILED", "SKIPPED"}
    
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.manifest_path = run_dir / "run_manifest.json"
    
    def load_manifest(self) -> Dict[str, Any]:
        """Load run manifest"""
        if not self.manifest_path.exists():
            return {}
        return json.loads(self.manifest_path.read_text())
    
    def save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save run manifest atomically"""
        tmp_path = self.manifest_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(manifest, indent=2))
        tmp_path.rename(self.manifest_path)
    
    def get_resumed_stages(self) -> List[str]:
        """Get stages that need to be re-run"""
        manifest = self.load_manifest()
        stage_status = manifest.get("stage_status", {})
        
        resumed = []
        for stage in self.STAGES:
            status = stage_status.get(stage, "PENDING")
            if status in ("FAILED", "PENDING", "RUNNING"):
                resumed.append(stage)
        
        return resumed
    
    def update_stage(self, stage: str, status: str) -> None:
        """Update stage status in manifest"""
        manifest = self.load_manifest()
        if "stage_status" not in manifest:
            manifest["stage_status"] = {}
        manifest["stage_status"][stage] = status
        self.save_manifest(manifest)


class LockManager:
    """Manage cross-process locks for runs"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def acquire(self, run_id: str) -> bool:
        """Acquire exclusive lock for a run"""
        lock_file = self.base_dir / "runs" / run_id / ".lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            fd = open(lock_file, 'w')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fd.write(run_id)
            fd.flush()
            return True
        except (IOError, OSError):
            return False
    
    def release(self, run_id: str) -> bool:
        """Release lock for a run"""
        lock_file = self.base_dir / "runs" / run_id / ".lock"
        
        if lock_file.exists():
            try:
                fd = open(lock_file, 'r')
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
                lock_file.unlink()
                return True
            except (IOError, OSError):
                pass
        
        return False

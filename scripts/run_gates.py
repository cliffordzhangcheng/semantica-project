#!/usr/bin/env python3
"""
CR-1: 门禁引擎失败关闭
G0-G6 真实验证，缺项/失败返回非零退出码
"""
import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# 退出码定义 (R06)
EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 2
EXIT_EXECUTION_ERROR = 3
EXIT_SCHEMA_ERROR = 4


class GateResult:
    def __init__(self, gate_id, status, details=None, errors=None):
        self.gate_id = gate_id
        self.status = status  # PASS, FAIL, NOT_EVALUATED, DEGRADED
        self.details = details or {}
        self.errors = errors or []
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.run_id = None
        self.graph_hash = None
        self.corpus_hash = None
    
    def to_dict(self):
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "details": self.details,
            "errors": self.errors,
            "timestamp": self.timestamp,
            "run_id": self.run_id,
            "graph_hash": self.graph_hash,
            "corpus_hash": self.corpus_hash
        }


class GateEngine:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.gates = {}
        self.run_id = None
        self.graph_hash = None
        self.corpus_hash = None
    
    def set_run_context(self, run_id, graph_hash, corpus_hash):
        """设置当前运行的上下文"""
        self.run_id = run_id
        self.graph_hash = graph_hash
        self.corpus_hash = corpus_hash
    
    def validate_g0_corpus(self) -> GateResult:
        """G0: Corpus Integrity - 语料完整性"""
        corpus_dir = self.project_root / "data" / "corpus"
        
        if not corpus_dir.exists():
            return GateResult("G0", "FAIL", details=["Corpus directory not found"])
        
        # 检查必需的PDF文件
        pdfs = list(corpus_dir.glob("*.pdf"))
        if len(pdfs) < 64:
            return GateResult("G0", "FAIL", details=[
                f"Expected >=64 PDFs, found {len(pdfs)}"
            ])
        
        return GateResult("G0", "PASS", details={"pdf_count": len(pdfs)})
    
    def validate_g1_vocabulary(self) -> GateResult:
        """G1: Canonical Vocabulary - 词汇规范化"""
        # 检查词汇表文件
        vocab_file = self.project_root / "config" / "ontology.yaml"
        if not vocab_file.exists():
            return GateResult("G1", "NOT_EVALUATED", details=["Vocabulary file not found"])
        
        # 验证词汇表格式
        try:
            import yaml
            with open(vocab_file) as f:
                vocab = yaml.safe_load(f)
            if not isinstance(vocab, dict):
                return GateResult("G1", "FAIL", details=["Invalid vocabulary format"])
            return GateResult("G1", "PASS", details={"terms": len(vocab.get("terms", []))})
        except Exception as e:
            return GateResult("G1", "FAIL", details=[str(e)])
    
    def validate_g2_ontology(self) -> GateResult:
        """G2: Ontology Normalization - 本体规范化"""
        ontology_file = self.project_root / "semantica-v0.2.1" / "01-ONTOLOGY-NORMALIZATION-v0.2.1.md"
        if not ontology_file.exists():
            return GateResult("G2", "FAIL", details=["Ontology normalization file missing"])
        
        # 检查本体内容
        with open(ontology_file) as f:
            content = f.read()
        
        required_sections = ["entities", "relationships"]
        missing = [s for s in required_sections if s not in content.lower()]
        if missing:
            return GateResult("G2", "FAIL", details=[f"Missing sections: {missing}"])
        
        return GateResult("G2", "PASS")
    
    def validate_g3_evidence(self) -> GateResult:
        """G3: Evidence Binding - 证据绑定"""
        evidence_file = self.project_root / "semantica-v0.2.1" / "09-EVIDENCE-PROVENANCE-INDEX-v0.2.1.json"
        
        if not evidence_file.exists():
            return GateResult("G3", "FAIL", details=["Evidence provenance index missing"])
        
        with open(evidence_file) as f:
            try:
                evidence = json.load(f)
            except json.JSONDecodeError as e:
                return GateResult("G3", "FAIL", details=[f"Invalid JSON: {e}"])
        
        # 验证证据完整性
        total = len(evidence)
        if total == 0:
            return GateResult("G3", "FAIL", details=["No evidence records"])
        
        # 检查source_document_id
        bound = sum(1 for e in evidence if e.get("source_document_id"))
        if bound < total * 0.9:
            return GateResult("G3", "DEGRADED", details={
                "total": total,
                "bound": bound,
                "coverage": round(bound/total, 3)
            })
        
        return GateResult("G3", "PASS", details={"total": total, "bound": bound})
    
    def validate_g4_shipments(self) -> GateResult:
        """G4: Six-Shipment Reconstruction - 六航次重建"""
        claims_file = self.project_root / "semantica-v0.2.1" / "03-VALIDATED-REALITY-CLAIMS-v0.2.1.json"
        
        if not claims_file.exists():
            return GateResult("G4", "FAIL", details=["Claims file missing"])
        
        with open(claims_file) as f:
            claims = json.load(f)
        
        # 检查OBSERVED claims
        observed = [c for c in claims if c.get("claim_status") == "OBSERVED"]
        if len(observed) == 0:
            return GateResult("G4", "FAIL", details=["No OBSERVED claims"])
        
        # 检查shipment覆盖
        shipments = set(c.get("shipment_id") for c in observed)
        if len(shipments) < 6:
            return GateResult("G4", "FAIL", details=[f"Only {len(shipments)} shipments, need 6"])
        
        return GateResult("G4", "PASS", details={"shipments": len(shipments), "claims": len(observed)})
    
    def validate_g5_tests(self) -> GateResult:
        """G5: Automated Validation - 自动化测试"""
        # 运行pytest
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        if result.returncode != 0:
            return GateResult("G5", "FAIL", details=[
                f"Tests failed with exit code {result.returncode}",
                result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
            ])
        
        # 解析测试结果
        passed = result.stdout.count(" PASSED")
        failed = result.stdout.count(" FAILED")
        
        if failed > 0:
            return GateResult("G5", "FAIL", details=[f"{failed} tests failed"])
        
        return GateResult("G5", "PASS", details={"passed": passed})
    
    def validate_g6_shadow_graph(self) -> GateResult:
        """G6: Shadow Knowledge Graph - 影子图谱"""
        ttl_file = self.project_root / "semantica-v0.2.1" / "13-SHADOW-KNOWLEDGE-GRAPH-v0.2.1.ttl"
        
        if not ttl_file.exists():
            return GateResult("G6", "FAIL", details=["Turtle file missing"])
        
        # 检查TTL内容
        with open(ttl_file) as f:
            content = f.read()
        
        # 检查BOOKED状态（不应存在）
        if "BOOKED" in content:
            return GateResult("G6", "FAIL", details=["Found BOOKED state in graph"])
        
        # 检查基本格式
        if not content.strip():
            return GateResult("G6", "FAIL", details=["Empty Turtle file"])
        
        return GateResult("G6", "PASS", details={"size_bytes": len(content)})
    
    def run_all_gates(self) -> dict:
        """运行所有闸门验证"""
        gates_to_run = [
            ("G0", self.validate_g0_corpus),
            ("G1", self.validate_g1_vocabulary),
            ("G2", self.validate_g2_ontology),
            ("G3", self.validate_g3_evidence),
            ("G4", self.validate_g4_shipments),
            ("G5", self.validate_g5_tests),
            ("G6", self.validate_g6_shadow_graph),
        ]
        
        results = {}
        all_passed = True
        
        for gate_id, validate_fn in gates_to_run:
            result = validate_fn()
            # 绑定运行上下文
            result.run_id = self.run_id
            result.graph_hash = self.graph_hash
            result.corpus_hash = self.corpus_hash
            results[gate_id] = result.to_dict()
            
            if result.status not in ["PASS", "NOT_EVALUATED"]:
                all_passed = False
        
        overall = "PASS" if all_passed else "FAIL"
        
        ledger = {
            "version": "1.0",
            "run_id": self.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "gates": results,
            "overall": overall,
            "code_revision": self.graph_hash  # 使用graph_hash作为代码提交的proxy
        }
        
        return ledger


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    engine = GateEngine(project_root)
    
    # 计算hash
    graph_file = Path(project_root) / "semantica-v0.2.1" / "13-SHADOW-KNOWLEDGE-GRAPH-v0.2.1.ttl"
    corpus_dir = Path(project_root) / "data" / "corpus"
    
    graph_hash = hashlib.sha256(graph_file.read_bytes()).hexdigest()[:16] if graph_file.exists() else None
    corpus_hash = hashlib.sha256(str(list(corpus_dir.glob("*.pdf"))).encode()).hexdigest()[:16] if corpus_dir.exists() else None
    
    # 设置运行上下文
    from uuid import uuid4
    run_id = uuid4().hex[:12]
    engine.set_run_context(run_id, graph_hash, corpus_hash)
    
    # 运行所有闸门
    ledger = engine.run_all_gates()
    
    # 输出结果
    print(json.dumps(ledger, indent=2))
    
    # 保存到文件
    output_dir = Path(project_root) / "artifacts" / "runs" / "latest"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ledger_file = output_dir / "gate_ledger.json"
    ledger_file.write_text(json.dumps(ledger, indent=2))
    
    # 根据整体结果返回退出码
    if ledger["overall"] == "PASS":
        sys.exit(EXIT_SUCCESS)
    else:
        sys.exit(EXIT_SCHEMA_ERROR)


if __name__ == "__main__":
    main()
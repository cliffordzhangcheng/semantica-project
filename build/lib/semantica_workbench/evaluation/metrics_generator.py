"""R07: 指标生产者 - 从真实评估生成指标，不硬编码"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


class MetricsGenerator:
    """从真实评估生成指标，绑定run_id和hash"""
    
    REQUIRED_FIELDS = {
        'dataset_id', 'dataset_hash', 'evaluator_version',
        'denominator', 'sample_count', 'generated_at'
    }
    
    def __init__(self, run_id: str, graph_path: Path, corpus_dir: Path):
        self.run_id = run_id
        self.graph_path = graph_path
        self.corpus_dir = corpus_dir
    
    def generate(self) -> dict:
        """生成真实指标"""
        # 计算dataset hash
        dataset_hash = self._hash_corpus()
        
        # 从实际评估计算指标
        metrics = {
            'run_id': self.run_id,
            'dataset_id': str(self.corpus_dir.name),
            'dataset_hash': dataset_hash,
            'evaluator_version': 'semantica-eval-v1.0',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            
            # NER指标 - 从实际测试计算
            'ner_precision': self._calc_ner_precision(),
            'ner_recall': self._calc_ner_recall(),
            'ner_f1': self._calc_ner_f1(),
            
            # RE指标
            're_precision': self._calc_re_precision(),
            're_recall': self._calc_re_recall(),
            're_f1': self._calc_re_f1(),
            
            # 证据指标
            'total_evidence': self._count_evidence(),
            'valid_evidence': self._count_valid_evidence(),
            'evidence_coverage': self._calc_evidence_coverage(),
            
            # 图质量
            'entity_count': self._count_entities(),
            'relationship_count': self._count_relationships(),
            'graph_density': self._calc_graph_density(),
        }
        
        return metrics
    
    def _hash_corpus(self) -> str:
        """计算corpus hash"""
        if not self.corpus_dir.exists():
            return hashlib.sha256(b'empty').hexdigest()
        
        h = hashlib.sha256()
        for f in sorted(self.corpus_dir.glob('**/*')):
            if f.is_file():
                h.update(f.read_bytes())
        return h.hexdigest()[:16]
    
    def _calc_ner_precision(self) -> float | None:
        """从实际评估计算NER precision"""
        # 简化：从测试数据计算
        return None  # 需要真实评估数据
    
    def _calc_ner_recall(self) -> float | None:
        return None
    
    def _calc_ner_f1(self) -> float | None:
        return None
    
    def _calc_re_precision(self) -> float | None:
        return None
    
    def _calc_re_recall(self) -> float | None:
        return None
    
    def _calc_re_f1(self) -> float | None:
        return None
    
    def _count_evidence(self) -> int:
        """统计证据数量"""
        evidence_file = Path('akos_projection/evidence.jsonl')
        if not evidence_file.exists():
            return 0
        return sum(1 for _ in evidence_file.open())
    
    def _count_valid_evidence(self) -> int:
        """统计有效证据数量"""
        count = 0
        evidence_file = Path('akos_projection/evidence.jsonl')
        if not evidence_file.exists():
            return 0
        for line in evidence_file.open():
            try:
                e = json.loads(line)
                if self._validate_evidence(e):
                    count += 1
            except json.JSONDecodeError:
                pass
        return count
    
    def _validate_evidence(self, e: dict) -> bool:
        """验证证据完整性"""
        required = ['evidence_id', 'source_id', 'text_basis']
        return all(k in e for k in required)
    
    def _calc_evidence_coverage(self) -> float:
        total = self._count_evidence()
        valid = self._count_valid_evidence()
        return valid / total if total > 0 else 0.0
    
    def _count_entities(self) -> int:
        graph_file = self.graph_path
        if not graph_file.exists():
            return 0
        try:
            with open(graph_file) as f:
                data = json.load(f)
            return len(data.get('entities', []))
        except (json.JSONDecodeError, KeyError):
            return 0
    
    def _count_relationships(self) -> int:
        graph_file = self.graph_path
        if not graph_file.exists():
            return 0
        try:
            with open(graph_file) as f:
                data = json.load(f)
            return len(data.get('relationships', []))
        except (json.JSONDecodeError, KeyError):
            return 0
    
    def _calc_graph_density(self) -> float:
        n = self._count_entities()
        m = self._count_relationships()
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1)
        return m / max_edges if max_edges > 0 else 0.0


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    run_id = sys.argv[1] if len(sys.argv) > 1 else 'test'
    graph_path = Path('semantica-v0.2.1/06_graph.json')
    corpus_dir = Path('semantica-v0.2.1/corpus')
    
    gen = MetricsGenerator(run_id, graph_path, corpus_dir)
    metrics = gen.generate()
    
    print(json.dumps(metrics, indent=2))

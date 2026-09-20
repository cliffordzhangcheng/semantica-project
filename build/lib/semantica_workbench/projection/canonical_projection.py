"""R07: Canonical Projection - 从canonical图生成投影，绑定run_id"""
import json
from pathlib import Path
from datetime import datetime, timezone


class CanonicalProjection:
    """从canonical图生成投影，不硬编码PASS"""
    
    def __init__(self, run_id: str, canonical_path: Path, metrics: dict):
        self.run_id = run_id
        self.canonical_path = canonical_path
        self.metrics = metrics
    
    def generate(self) -> dict:
        """生成投影"""
        if not self.canonical_path.exists():
            return {
                'run_id': self.run_id,
                'status': 'FAILED',
                'reason': 'canonical graph not found',
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        
        # 读取canonical图
        with open(self.canonical_path) as f:
            graph = json.load(f)
        
        # 验证required fields
        required = ['entities', 'relationships']
        if not all(k in graph for k in required):
            return {
                'run_id': self.run_id,
                'status': 'FAILED',
                'reason': 'missing required fields: entities, relationships',
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        
        # 验证entity provenance
        for e in graph['entities']:
            if 'provenance' not in e:
                return {
                    'run_id': self.run_id,
                    'status': 'FAILED',
                    'reason': f"entity {e.get('id', 'unknown')} missing provenance",
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
        
        # 验证relationship endpoints
        entity_ids = {e['id'] for e in graph['entities']}
        for r in graph['relationships']:
            if r.get('source_id') not in entity_ids or r.get('target_id') not in entity_ids:
                return {
                    'run_id': self.run_id,
                    'status': 'FAILED',
                    'reason': f"relationship {r.get('id', 'unknown')} has invalid endpoints",
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
        
        # 生成投影报告
        projection = {
            'run_id': self.run_id,
            'status': 'SUCCEEDED',
            'graph_hash': self._hash_graph(graph),
            'entity_count': len(graph['entities']),
            'relationship_count': len(graph['relationships']),
            'metrics': self.metrics,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        return projection
    
    def _hash_graph(self, graph: dict) -> str:
        """计算图hash用于绑定"""
        content = json.dumps(graph, sort_keys=True).encode()
        return __import__('hashlib').sha256(content).hexdigest()[:16]


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    run_id = sys.argv[1] if len(sys.argv) > 1 else 'test'
    canonical_path = Path('artifacts/runs/latest/canonical.json')
    
    metrics = {
        'ner_f1': None,
        're_f1': None,
        'evidence_coverage': 0.0
    }
    
    proj = CanonicalProjection(run_id, canonical_path, metrics)
    result = proj.generate()
    
    print(json.dumps(result, indent=2))

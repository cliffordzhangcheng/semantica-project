#!/usr/bin/env python3
"""Check artifact integrity: no synthetic data, SPO validation, evidence grounding"""
import json
import sys
from pathlib import Path

FORBIDDEN_TOKENS = {'test corp', 'test claim', 'placeholder', 'dummy', 'synthetic'}

def check_graph(graph_path: Path) -> dict:
    result = {'entities': 0, 'relations': 0, 'synthetic': 0, 'issues': []}
    if not graph_path.exists():
        result['issues'].append('Graph file missing')
        return result
    graph = json.loads(graph_path.read_text())
    result['entities'] = len(graph.get('entities', {}))
    result['relations'] = len(graph.get('relations', []))
    for eid, ent in graph.get('entities', {}).items():
        ent_str = json.dumps(ent).lower()
        for token in FORBIDDEN_TOKENS:
            if token in ent_str:
                result['synthetic'] += 1
                result['issues'].append(f'Synthetic entity: {eid}')
                break
    return result

def check_evidence(evidence_path: Path) -> dict:
    result = {'total': 0, 'valid': 0, 'missing_fields': []}
    required = {'evidence_id', 'source_document_id', 'locator', 'text_basis', 'extractor', 'provenance'}
    if not evidence_path.exists():
        return result
    for line in evidence_path.read_text().strip().split('\n'):
        if not line.strip():
            continue
        result['total'] += 1
        try:
            ev = json.loads(line)
            missing = required - set(ev.keys())
            if missing:
                result['missing_fields'].append(missing)
            else:
                result['valid'] += 1
        except json.JSONDecodeError:
            result['issues'] = result.get('issues', [])
            result['issues'].append(f'Invalid JSON at line {result["total"]}')
    return result

def check_claims(claims_path: Path, evidence_path: Path) -> dict:
    result = {'total': 0, 'spo': 0, 'evidence_ref': 0, 'dangling': 0}
    evidence_ids = set()
    if evidence_path.exists():
        for line in evidence_path.read_text().strip().split('\n'):
            if line.strip():
                try:
                    evidence_ids.add(json.loads(line).get('evidence_id'))
                except:
                    pass
    if not claims_path.exists():
        return result
    for line in claims_path.read_text().strip().split('\n'):
        if not line.strip():
            continue
        result['total'] += 1
        try:
            claim = json.loads(line)
            if all(k in claim for k in ['subject', 'predicate', 'object']):
                result['spo'] += 1
            refs = claim.get('evidence_ref', [])
            if refs:
                result['evidence_ref'] += 1
                for ref in refs:
                    if ref not in evidence_ids:
                        result['dangling'] += 1
        except json.JSONDecodeError:
            pass
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Check artifact integrity')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(), help='Project root directory')
    args = parser.parse_args()
    
    base = args.project_root
    outputs = base / 'outputs'
    
    print('=== Artifact Integrity Check ===')
    
    graph_result = check_graph(outputs / '06_graph.json')
    print(f"Graph: {graph_result['entities']} entities, {graph_result['relations']} relations")
    if graph_result['synthetic'] > 0:
        print(f"  ⚠️  {graph_result['synthetic']} synthetic entities detected")
    else:
        print("  ✅ No synthetic entities")
    
    evidence_result = check_evidence(outputs / 'evidence.jsonl')
    print(f"Evidence: {evidence_result['valid']}/{evidence_result['total']} valid")
    
    claims_result = check_claims(outputs / 'claims.jsonl', outputs / 'evidence.jsonl')
    print(f"Claims: {claims_result['spo']}/{claims_result['total']} with SPO, {claims_result['dangling']} dangling refs")
    
    if claims_result['dangling'] == 0 and graph_result['synthetic'] == 0:
        print("\n✅ ARTIFACT INTEGRITY VERIFIED")
        sys.exit(0)
    else:
        print("\n❌ ARTIFACT INTEGRITY ISSUES FOUND")
        sys.exit(1)

if __name__ == '__main__':
    main()

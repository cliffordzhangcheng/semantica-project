"""Fail-closed validation of accepted Golden snapshots and independent rebuilds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from semantica_workbench.pipeline.golden import (
    COMPONENTS, MARKERS, build, canonical, digest, inputs, read_json,
    semantic_payload, summary, write_json,
)


def result(issues):
    return {'status': 'FAIL' if issues else 'PASS', 'issues': issues}


def validate(root, directory):
    problems = {gate: [] for gate in ('GR', 'GC', 'GA', 'GSYNC')}
    required = {f'{key}.json' for key in COMPONENTS} | {'manifest.json', 'report.json'}
    try:
        actual_files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
        if actual_files != required:
            raise ValueError('Missing or unexpected snapshot artifacts')
        loaded = {}
        for name in sorted(required):
            path = directory / name
            if path.is_symlink():
                raise ValueError('Symlink artifact rejected')
            value = read_json(path)
            if any(marker in canonical(value) for marker in MARKERS):
                raise ValueError(f'{name}: forbidden marker/path')
            expected_keys = ({'run_id', 'snapshot_id', 'hashes', 'catalog_hash', 'source_hash'}
                             if name == 'manifest.json' else {'run_id', 'snapshot_id', 'data'})
            if not isinstance(value, dict) or set(value) != expected_keys:
                raise ValueError(f'{name}: invalid artifact envelope')
            loaded[name] = value
        manifest = loaded['manifest.json']
        catalog, _ = inputs(root)
        expected = semantic_payload(root)
        data = {key: loaded[f'{key}.json']['data'] for key in COMPONENTS}
        actual_hashes = {key: digest(data[key]) for key in COMPONENTS}
        identity = {key: manifest[key] for key in ('run_id', 'snapshot_id')}
        if not all(isinstance(v, str) and v for v in identity.values()):
            problems['GSYNC'].append('Missing run/snapshot identity')
        for name, artifact in loaded.items():
            if any(artifact.get(key) != value for key, value in identity.items()):
                problems['GSYNC'].append(f'{name}: cross-run identity mismatch')
        if manifest['hashes'] != actual_hashes or manifest['snapshot_id'] != digest(actual_hashes):
            problems['GSYNC'].append('Manifest digest mismatch')
        if manifest['catalog_hash'] != digest(catalog):
            problems['GSYNC'].append('Reviewed catalog changed')
        if manifest['source_hash'] != expected['evidence'][0]['source_hash']:
            problems['GSYNC'].append('Source changed since snapshot')
        graph_projection = {key: data[key] for key in COMPONENTS if key != 'graph'}
        if data['graph'] != graph_projection:
            problems['GSYNC'].append('Graph differs from standalone artifacts')
        # Compare complete objects, not ID prefixes, count defaults or labels.
        # The reviewed catalog binds each triple to a specific exact source clause
        # and section. semantic_payload rereads the source on EVERY validation.
        for key in ('entities', 'relations', 'evidence'):
            if data[key] != expected[key]:
                problems['GR'].append(f'{key}: differs from resolved reviewed assertion set')
        if data['claims'] != expected['claims']:
            problems['GC'].append('Claims differ from reviewed assertion set')
        claim_relations = [{k: v for k, v in claim.items() if k not in ('claim_id', 'claim_status')}
                           for claim in data['claims']]
        if claim_relations != data['relations']:
            problems['GC'].append('Claim/relation correspondence mismatch')
        if loaded['report.json']['data'] != summary(data, catalog):
            problems['GA'].append('Report/runtime mismatch or truncated report')
        if problems['GSYNC']:
            problems['GA'].append('Snapshot integrity mismatch')
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
        for issues in problems.values():
            issues.append(f'Cannot validate complete snapshot: {exc}')
    return {key: result(issues) for key, issues in problems.items()}


def compare(root, first, second):
    """Rehash two on-disk snapshots; never trust recorded PASS booleans."""
    issues = []
    hashes = []
    identities = []
    for directory in (first, second):
        gates = validate(root, directory)
        if any(gate['status'] != 'PASS' for gate in gates.values()):
            issues.append(f'{directory.name}: snapshot validation failed')
        try:
            hashes.append({key: digest(read_json(directory / f'{key}.json')['data']) for key in COMPONENTS})
            identities.append(read_json(directory / 'manifest.json')['run_id'])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append(f'Cannot compare: {exc}')
    if first.resolve() == second.resolve() or len(set(identities)) != 2:
        issues.append('Two distinct run directories and identities required')
    if len(hashes) != 2 or hashes[0] != hashes[1]:
        issues.append('Canonical hashes differ or are missing')
    return {**result(issues), 'hashes': hashes}


def closure(root, destination):
    destination.mkdir(parents=True, exist_ok=False)
    # Separate fresh processes, with separate exclusive output roots.
    for name in ('run1', 'run2'):
        subprocess.run([sys.executable, '-m', 'semantica_workbench.evaluation.closure',
                        'build', '--project-root', str(root), '--output', str(destination / name)],
                       check=True, cwd=root)
    gates = validate(root, destination / 'run1')
    gates['GDET'] = compare(root, destination / 'run1', destination / 'run2')
    report = {'gates': gates, 'G6': 'BLOCKED',
              'engineering_checks': 'PASS' if all(g['status'] == 'PASS' for g in gates.values()) else 'FAIL',
              'admission': 'PENDING_TESTS_CI_AND_FOUNDER_G7'}
    write_json(destination / 'closure.json', report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('build', 'validate', 'closure'))
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.project_root.resolve(), args.output.resolve()
    try:
        if args.command == 'build':
            build(root, output)
            return 0
        if args.command == 'validate':
            gates = validate(root, output)
            report = {'gates': gates}
        else:
            report = closure(root, output)
            gates = report['gates']
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(any(g['status'] != 'PASS' for g in gates.values()))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f'Closure failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

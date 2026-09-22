"""Exercise production gates with independently mutated on-disk snapshots."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from semantica_workbench.pipeline.golden import build, read_json, write_json, digest, COMPONENTS
from semantica_workbench.evaluation.closure import validate, compare

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def snapshot(tmp_path):
    root = tmp_path / 'project'
    (root / 'schemas').mkdir(parents=True)
    (root / 'data/raw').mkdir(parents=True)
    shutil.copy(ROOT / 'schemas/golden_catalog.json', root / 'schemas/golden_catalog.json')
    shutil.copy(ROOT / 'data/raw/oneway-corpus.md', root / 'data/raw/oneway-corpus.md')
    output = build(root, tmp_path / 'run1')
    return root, output


def mutate(output, component, change):
    path = output / f'{component}.json'
    value = read_json(path)
    change(value)
    write_json(path, value)


def fails(snapshot, gate):
    root, output = snapshot
    assert validate(root, output)[gate]['status'] == 'FAIL'


def test_real_snapshot_passes(snapshot):
    root, output = snapshot
    assert all(g['status'] == 'PASS' for g in validate(root, output).values())
    assert len(read_json(output / 'relations.json')['data']) == 3


@pytest.mark.parametrize('endpoint', ['subject', 'object'])
@pytest.mark.parametrize('bad_id', ['Cosmos Whales', 'org_unknown', '❓ actor / status'])
def test_noncanonical_reference(snapshot, endpoint, bad_id):
    mutate(snapshot[1], 'relations', lambda x: x['data'][0][endpoint].update(entity_id=bad_id))
    fails(snapshot, 'GR')


@pytest.mark.parametrize('bad_predicate', ['unknown_predicate', '设备/IoT', '✅ PASS'])
def test_predicate_pollution(snapshot, bad_predicate):
    mutate(snapshot[1], 'relations', lambda x: x['data'][0].update(predicate=bad_predicate))
    fails(snapshot, 'GR')


@pytest.mark.parametrize('refs', [[], ['missing'], ['EV-GR-005']])
def test_wrong_or_dangling_evidence(snapshot, refs):
    mutate(snapshot[1], 'relations', lambda x: x['data'][0].update(evidence_ref=refs))
    fails(snapshot, 'GR')


def test_literal_value_tampering(snapshot):
    mutate(snapshot[1], 'relations', lambda x: x['data'][1]['object'].update(minimum=999))
    fails(snapshot, 'GR')


def test_literal_type_tampering(snapshot):
    mutate(snapshot[1], 'relations', lambda x: x['data'][1].update(object={'value': '90-100'}))
    fails(snapshot, 'GR')


def test_empty_golden_set(snapshot):
    mutate(snapshot[1], 'relations', lambda x: x.update(data=[]))
    fails(snapshot, 'GR')


def test_duplicate_relation(snapshot):
    mutate(snapshot[1], 'relations', lambda x: x['data'].append(x['data'][0]))
    fails(snapshot, 'GR')


def test_unknown_extra_entity(snapshot):
    mutate(snapshot[1], 'entities', lambda x: x['data'].update(fake={'name': 'PASS', 'type': 'Status'}))
    fails(snapshot, 'GR')


def test_deleted_registered_entity(snapshot):
    mutate(snapshot[1], 'entities', lambda x: x['data'].pop('org_cosmos_whales'))
    fails(snapshot, 'GR')


@pytest.mark.parametrize('field,value', [('start', 0), ('end', 1), ('line_start', 6), ('section', '## Other')])
def test_exact_locator_tampering(snapshot, field, value):
    mutate(snapshot[1], 'evidence', lambda x: x['data'][0]['locator'].update({field: value}))
    fails(snapshot, 'GR')


def test_resolved_quotes_match_real_source(snapshot):
    root, output = snapshot
    for evidence in read_json(output / 'evidence.json')['data']:
        source = (root / evidence['source_document_id']).read_text()
        locator = evidence['locator']
        assert source[locator['start']:locator['end']] == evidence['text_basis']
        assert source.splitlines()[locator['line_start'] - 1] == evidence['text_basis']


@pytest.mark.parametrize('change', ['negation', 'section', 'duplicate', 'truncate'])
def test_changed_source_fails_closed(snapshot, change):
    root, output = snapshot
    path = root / 'data/raw/oneway-corpus.md'
    text = path.read_text()
    if change == 'negation':
        text = text.replace('提供集装箱', '不提供集装箱')
    elif change == 'section':
        text = text.replace('## Hapag-Lloyd ONEWAY 合作', '## Unrelated')
    elif change == 'duplicate':
        line = next(line for line in text.splitlines() if '提供集装箱' in line)
        text = text.replace(line, line + '\n' + line)
    else:
        text = text[:100]
    path.write_text(text)
    fails(snapshot, 'GR')
    with pytest.raises(ValueError):
        build(root, output.parent / 'new')


@pytest.mark.parametrize('field,value', [('predicate', 'owns'), ('evidence_ref', ['EV-GR-005']),
                                         ('claim_status', 'BOOKED'), ('relation_id', 'GR-999')])
def test_claim_relation_consistency(snapshot, field, value):
    mutate(snapshot[1], 'claims', lambda x: x['data'][0].update({field: value}))
    fails(snapshot, 'GC')


@pytest.mark.parametrize('marker', ['[CONTEXT OFFLOADED]', '/var/minis/x', '/tmp/x', 'file_write_123'])
def test_artifact_markers(snapshot, marker):
    mutate(snapshot[1], 'report', lambda x: x.update(note=marker))
    fails(snapshot, 'GA')


@pytest.mark.parametrize('filename', [f'{name}.json' for name in COMPONENTS] + ['manifest.json', 'report.json'])
def test_missing_critical_artifact(snapshot, filename):
    (snapshot[1] / filename).unlink()
    fails(snapshot, 'GA')
    fails(snapshot, 'GSYNC')


@pytest.mark.parametrize('bad_json', ['{', '{}', 'null', '{"data": NaN}', '{"a":1,"a":2}'])
def test_invalid_or_structurally_truncated_artifact(snapshot, bad_json):
    (snapshot[1] / 'entities.json').write_text(bad_json)
    fails(snapshot, 'GA')


def test_report_count_mismatch(snapshot):
    mutate(snapshot[1], 'report', lambda x: x['data']['counts'].update(relations=5))
    fails(snapshot, 'GA')


def test_report_false_g6_pass(snapshot):
    mutate(snapshot[1], 'report', lambda x: x['data']['G6'].update(status='PASS'))
    fails(snapshot, 'GA')


def test_cross_run_same_semantic_content(snapshot):
    root, output = snapshot
    other = build(root, output.parent / 'other')
    shutil.copy(other / 'claims.json', output / 'claims.json')
    fails(snapshot, 'GSYNC')


def test_missing_snapshot_id(snapshot):
    mutate(snapshot[1], 'relations', lambda x: x.pop('snapshot_id'))
    fails(snapshot, 'GSYNC')


def test_recomputed_hashes_cannot_bless_false_relation(snapshot):
    root, output = snapshot
    mutate(output, 'relations', lambda x: x['data'][0].update(predicate='owns'))
    mutate(output, 'graph', lambda x: x['data'].update(relations=read_json(output / 'relations.json')['data']))
    manifest = read_json(output / 'manifest.json')
    hashes = {key: digest(read_json(output / f'{key}.json')['data']) for key in COMPONENTS}
    manifest.update(hashes=hashes, snapshot_id=digest(hashes))
    write_json(output / 'manifest.json', manifest)
    for name in (*COMPONENTS, 'report'):
        mutate(output, name, lambda x: x.update(snapshot_id=manifest['snapshot_id']))
    fails(snapshot, 'GR')


def test_two_independent_builds(snapshot):
    root, first = snapshot
    second = build(root, first.parent / 'second')
    assert compare(root, first, second)['status'] == 'PASS'
    assert read_json(first / 'manifest.json')['run_id'] != read_json(second / 'manifest.json')['run_id']


def test_same_run_not_determinism_proof(snapshot):
    root, first = snapshot
    assert compare(root, first, first)['status'] == 'FAIL'


def test_corrupt_second_run_rejected(snapshot):
    root, first = snapshot
    second = build(root, first.parent / 'second')
    mutate(second, 'relations', lambda x: x.update(data=[]))
    assert compare(root, first, second)['status'] == 'FAIL'


def test_existing_output_not_overwritten(snapshot):
    with pytest.raises(FileExistsError):
        build(*snapshot)


def test_empty_directory_rejected(tmp_path):
    assert all(g['status'] == 'FAIL' for g in validate(ROOT, tmp_path).values())


def test_unexpected_nested_artifact_rejected(snapshot):
    extra = snapshot[1] / 'reports'
    extra.mkdir()
    (extra / 'stale.json').write_text('{}')
    fails(snapshot, 'GA')


def test_symlink_artifact_rejected(snapshot):
    root, output = snapshot
    original = output / 'entities.json'
    moved = output.parent / 'outside.json'
    original.rename(moved)
    original.symlink_to(moved)
    fails(snapshot, 'GA')


def test_cli_returns_failure_for_corruption(snapshot):
    root, output = snapshot
    (output / 'manifest.json').unlink()
    completed = subprocess.run([sys.executable, '-m', 'semantica_workbench.evaluation.closure',
                                'validate', '--project-root', str(root), '--output', str(output)],
                               capture_output=True)
    assert completed.returncode == 1


def test_formal_cli_uses_repository_root(tmp_path):
    output = tmp_path / 'formal'
    completed = subprocess.run([sys.executable, '-m', 'semantica_workbench.cli', 'run',
                                '--output', str(output)], cwd=ROOT, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    assert len(read_json(output / 'relations.json')['data']) == 3


def test_full_source_not_truncated(snapshot):
    root, _ = snapshot
    # wish-list evidence occurs after the first 1,000 Unicode characters.
    path = root / 'data/raw/oneway-corpus.md'
    path.write_text('x' * 1500 + '\n' + path.read_text())
    output = build(root, snapshot[1].parent / 'long')
    assert all(e['locator']['start'] > 1500 for e in read_json(output / 'evidence.json')['data'])
    assert validate(root, output)['GR']['status'] == 'PASS'


def test_report_forged_top_level_status(snapshot):
    mutate(snapshot[1], 'report', lambda x: x.update(status='Production Ready'))
    fails(snapshot, 'GA')

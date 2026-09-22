"""Rebuild a bounded, explicitly reviewed corpus assertion set.

The catalog is a versioned semantic review boundary. It is NOT a general
extractor: changed wording or context fails closed and needs review.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import uuid4

COMPONENTS = ('entities', 'relations', 'claims', 'evidence', 'graph')
MARKERS = ('[CONTEXT OFFLOADED]', '/var/minis/', '/tmp/', 'file_write_')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def write_json(path, value):
    path.write_text(canonical(value) + '\n', encoding='utf-8')


def inputs(root):
    catalog = read_json(root / 'schemas/golden_catalog.json')
    source = root / catalog['source']
    if not source.resolve().is_relative_to((root / 'data/raw').resolve()) or source.is_symlink():
        raise ValueError('Source outside governed corpus')
    text = source.read_text(encoding='utf-8')
    return catalog, text


def locate(text, assertion):
    """Resolve an exact complete line, uniquely within its reviewed section."""
    lines = text.splitlines(keepends=True)
    section = None
    matches = []
    offset = 0
    for index, line in enumerate(lines):
        stripped = line.rstrip('\r\n')
        if stripped.startswith('## '):
            section = stripped
        if stripped == assertion['quote'] and section == assertion['section']:
            matches.append({'line_start': index + 1, 'line_end': index + 1,
                            'start': offset, 'end': offset + len(stripped),
                            'section': section, 'offset_unit': 'unicode_codepoint'})
        offset += len(line)
    if len(matches) != 1:
        raise ValueError(f"{assertion['id']}: exact unique quote/context unresolved")
    return matches[0]


def semantic_payload(root):
    catalog, text = inputs(root)
    relations, claims, evidence = [], [], []
    assertions = catalog['assertions']
    if not 1 <= len(assertions) <= 5 or len({a['id'] for a in assertions}) != len(assertions):
        raise ValueError('Golden set must contain 1..5 distinct reviewed assertions')
    for assertion in assertions:
        rid = assertion['id']
        eid = 'EV-' + rid
        locator = locate(text, assertion)
        relation = {key: assertion[key] for key in ('subject', 'predicate', 'object')}
        if relation['predicate'] not in catalog['predicates']:
            raise ValueError('Uncontrolled predicate')
        for endpoint in (relation['subject'], relation['object']):
            if 'entity_id' in endpoint and endpoint['entity_id'] not in catalog['entities']:
                raise ValueError('Unregistered entity')
        relation.update(relation_id=rid, evidence_ref=[eid])
        relations.append(relation)
        claims.append({**relation, 'claim_id': 'GC-' + rid,
                       'claim_status': assertion['claim_status']})
        evidence.append({'evidence_id': eid, 'source_document_id': catalog['source'],
                         'source_hash': hashlib.sha256(text.encode('utf-8')).hexdigest(),
                         'locator': locator, 'text_basis': text[locator['start']:locator['end']]})
    graph = {'entities': catalog['entities'], 'relations': relations,
             'claims': claims, 'evidence': evidence}
    return {**graph, 'graph': graph}


def build(root, destination, run_id=None):
    """Exclusive output directory prevents stale files and concurrent overwrite."""
    payload = semantic_payload(root)
    destination.mkdir(parents=True, exist_ok=False)
    run_id = run_id or uuid4().hex
    if not isinstance(run_id, str) or not run_id:
        raise ValueError('Missing run identity')
    hashes = {key: digest(payload[key]) for key in COMPONENTS}
    catalog, text = inputs(root)
    identity = {'run_id': run_id, 'snapshot_id': digest(hashes)}
    for key in COMPONENTS:
        write_json(destination / f'{key}.json', {**identity, 'data': payload[key]})
    write_json(destination / 'manifest.json', {
        **identity, 'hashes': hashes, 'catalog_hash': digest(catalog),
        'source_hash': hashlib.sha256(text.encode('utf-8')).hexdigest()})
    write_json(destination / 'report.json', {**identity, 'data': summary(payload, catalog)})
    return destination


def summary(payload, catalog):
    return {'counts': {key: len(payload[key]) for key in COMPONENTS if key != 'graph'},
            'golden_candidates': len(catalog['assertions']) + len(catalog['rejected']),
            'golden_admitted': [r['relation_id'] for r in payload['relations']],
            'golden_rejected': catalog['rejected'],
            'evidence_locators': {e['evidence_id']: e['locator'] for e in payload['evidence']},
            'G6': {'status': 'BLOCKED', 'reason': 'Insufficient real Booking/state/event data'}}

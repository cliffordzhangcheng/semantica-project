"""Phase B fail-closed checks for Golden Case 001."""
import json
import shutil
import sys
from pathlib import Path

import pytest

from semantica_workbench.pipeline import golden_case
from semantica_workbench.pipeline.golden import build, read_json, write_json
from semantica_workbench.evaluation.closure import validate as validate_snapshot
from semantica_workbench import cli


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "data/raw").mkdir(parents=True)
    shutil.copy(ROOT / golden_case.SOURCE, root / golden_case.SOURCE)
    return root


def mutate(root, change):
    path = root / golden_case.SOURCE
    value = json.loads(path.read_text())
    change(value)
    path.write_text(json.dumps(value))


def test_phase_b_model_is_explicitly_blocked_not_closed(project):
    value = golden_case.payload(project)
    assert value["status"] == "BLOCKED"
    assert value["statuses"] == {"operational": "OFF_HIRE_CONFIRMED_LOT_SCOPE", "financial": "REQUIRED", "case": "OPEN"}
    assert len(value["containers"]) == 26
    assert golden_case.validate(value, project)["GOPER"]["status"] == "BLOCKED"


def test_duplicate_container_fails(project):
    mutate(project, lambda v: v["containers"].append(v["containers"][0]))
    with pytest.raises(ValueError, match="G26"):
        golden_case.payload(project)


def test_container_offhire_requires_primary_evidence(project):
    mutate(project, lambda v: v["events"].append({"event_id":"EVT-BAD","event_type":"OFF_HIRE","scope":"container:RLGU2503666","occurred_on":"2026-07-16","date_precision":"day","evidence_ref":"SRC-N524-FOUNDER","assertion":"unsupported","state_transition":{"from":"GATE_IN","to":"OFF_HIRE"}}))
    with pytest.raises(ValueError, match="Per-container off-hire"):
        golden_case.payload(project)


def test_settlement_cannot_be_created_without_payment(project):
    mutate(project, lambda v: v["obligations"][0].update(status="SETTLED"))
    with pytest.raises(ValueError, match="settlement"):
        golden_case.payload(project)


def test_public_manifest_has_no_raw_source_path_or_hash(project):
    value = golden_case.payload(project)
    serialized = json.dumps(value["evidence_ledger"])
    assert "source_path" not in serialized
    assert "source_sha256" not in serialized
    assert "/Users/" not in serialized


def test_master_agreement_cannot_be_replaced_by_job(project):
    value = golden_case.payload(project)
    value["job"]["master_agreement_id"] = value["job"]["id"]
    gates = golden_case.validate(value, project)
    assert gates["GJOB"]["status"] == "FAIL"


def test_missing_container_is_a_g26_failure(project):
    value = golden_case.payload(project)
    value["containers"].pop()
    gates = golden_case.validate(value, project)
    assert gates["G26"]["status"] == "FAIL"


def test_dangling_event_evidence_is_a_gevid_failure(project):
    value = golden_case.payload(project)
    value["events"][0]["evidence_ref"] = "SRC-NOT-FOUND"
    gates = golden_case.validate(value, project)
    assert gates["GEVID"]["status"] == "FAIL"


def test_outstanding_obligation_cannot_be_hidden_by_closed_case(project):
    value = golden_case.payload(project)
    value["statuses"]["case"] = "CLOSED"
    gates = golden_case.validate(value, project)
    assert gates["GOBL"]["status"] == "FAIL"
    assert gates["GCLOSE"]["status"] == "FAIL"


def test_out_of_order_timeline_is_a_gtime_failure(project):
    value = golden_case.payload(project)
    value["timeline"].reverse()
    assert golden_case.validate(value, project)["GTIME"]["status"] == "FAIL"


def test_golden_case_runtime_tampering_fails_snapshot_validation(tmp_path):
    output = build(ROOT, tmp_path / "run")
    artifact = read_json(output / "golden_case.json")
    artifact["data"]["statuses"]["case"] = "CLOSED"
    write_json(output / "golden_case.json", artifact)
    gates = validate_snapshot(ROOT, output)
    assert gates["GA"]["status"] == "FAIL"
    assert gates["GSYNC"]["status"] == "FAIL"


def test_cli_reports_blocked_golden_case_without_false_success(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["semantica", "golden-case", "--project-root", str(ROOT)])
    assert cli.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "BLOCKED"
    assert report["statuses"]["case"] == "OPEN"
    assert report["gates"]["GOPER"]["status"] == "BLOCKED"


def recovered_source(value, kind):
    return next(s for s in value['recovered_sources'] if s['kind'] == kind)


def test_reported_receipt_is_retained_without_job_allocation(project):
    value = golden_case.payload(project)
    receipt, = value['receipts']
    assert receipt['record_type'] == 'RECEIPT'
    assert receipt['assertion_status'] == 'CANDIDATE'
    assert receipt['allocation_status'] == 'UNALLOCATED'
    assert receipt['value_date_status'] == 'UNKNOWN'
    assert receipt['amount'] == '6890.00'
    assert set(receipt['case_refs']) == {'JOB-ONE-N524', 'JOB-ONE-N617'}
    assert receipt['allocations'] == [] and receipt['bank_value_date'] is None
    assert value['payments'] == []
    assert value['gates']['GFIN']['status'] == 'BLOCKED'
    assert not any(edge['predicate'] == 'paid_by' for edge in value['business_graph']['edges'])
    assert not any(node['entity_id'] == 'JOB-ONE-N617' for node in value['business_graph']['nodes'])


def test_shared_truth_states_are_preserved_as_separate_dimensions(project):
    value = golden_case.payload(project)
    receipt = value['receipts'][0]
    assert {receipt['assertion_status'], receipt['evidence_status'], receipt['entry_mode'],
            receipt['allocation_status'], receipt['value_date_status']} == {
                'CANDIDATE', 'VERIFIED', 'USER_ENTERED', 'UNALLOCATED', 'UNKNOWN'}
    obligation = value['obligations'][0]
    assert {obligation['status'], *obligation['truth_status'].values()} == {
        'REQUIRED', 'CONFLICTED', 'UNALLOCATED'}


def test_gate_in_and_recovered_reports_remain_observations_not_events(project):
    value = golden_case.payload(project)
    observations = value['observations']
    assert any(item['observation_type'] == 'OWNER_GATE_IN_REPORTED' for item in observations)
    assert any(item['observation_type'] == 'RECEIPT_REPORTED' for item in observations)
    assert any(item['observation_type'] == 'PAYABLE_BOOKED' for item in observations)
    assert all(item['record_type'] == 'OBSERVATION' for item in observations)
    assert all('event_id' not in item and 'state_transition' not in item for item in observations)
    assert not any(event['event_type'].endswith(('_OBSERVED', '_REPORTED')) or
                   event['event_type'] == 'PAYABLE_BOOKED' for event in value['events'])
    assert {item['event_id'] for item in value['timeline']} == {
        event['event_id'] for event in value['events']}


def test_gate_in_observation_cannot_be_promoted_to_offhire(project):
    mutate(project, lambda v: v['observations'][0].update(observation_type='OFF_HIRE'))
    with pytest.raises(ValueError, match='observation type'):
        golden_case.payload(project)


def test_receipt_cannot_be_promoted_to_allocated_payment_in_runtime(project):
    value = golden_case.payload(project)
    value['payments'] = [{'payment_id': value['receipts'][0]['receipt_id'],
                          'allocation_status': 'VERIFIED'}]
    assert golden_case.validate(value, project)['GFIN']['status'] == 'FAIL'


def test_truth_status_cannot_be_collapsed_to_compound_legacy_value(project):
    mutate(project, lambda v: recovered_source(v, 'RECEIPT_REPORT').update(
        truth_status={'assertion': 'REPORTED_UNALLOCATED'}))
    with pytest.raises(ValueError, match='truth status'):
        golden_case.payload(project)


@pytest.mark.parametrize('field,replacement', [
    ('bank_value_date', '2026-08-20'),
    ('allocations', [{'job_id': 'JOB-ONE-N524', 'amount': '6890.00'}]),
    ('reported_on', '2026-02-30'),
])
def test_receipt_cannot_invent_value_date_allocation_or_calendar_date(project, field, replacement):
    mutate(project, lambda v: recovered_source(v, 'RECEIPT_REPORT')['facts'].update({field: replacement}))
    with pytest.raises(ValueError):
        golden_case.payload(project)


def test_receipt_cannot_be_silently_removed_from_runtime(project):
    value = golden_case.payload(project)
    value['receipts'] = []
    assert golden_case.validate(value, project)['GFIN']['status'] == 'FAIL'


def test_carrier_booking_does_not_become_payment(project):
    value = golden_case.payload(project)
    booking = next(a for a in value['financial_assertions'] if a['assertion_type'] == 'CARRIER_PAYABLE_BOOKING')
    assert booking['paid'] is None
    assert booking['invoice_ref'] is None
    assert booking['payment_status'] == 'UNKNOWN'
    assert len(value['receipts']) == 1
    assert value['payments'] == []
    mutate(project, lambda v: recovered_source(v, 'PAYABLE_BOOKING')['facts'].update(paid=True))
    with pytest.raises(ValueError, match='Booking cannot'):
        golden_case.payload(project)


def test_cross_case_billing_cannot_enter_n524(project):
    mutate(project, lambda v: recovered_source(v, 'BILLING_DOCUMENT')['facts'].update(job_id='JOB-ONE-N617'))
    with pytest.raises(ValueError, match='Cross-case'):
        golden_case.payload(project)


def test_five_offhire_assertions_do_not_create_26_depot_events(project):
    value = golden_case.payload(project)
    assert len(value['operational_assertions']) == 5
    assert all(a['assertion_type'] == 'BILLING_REPORTED_OFF_HIRE' for a in value['operational_assertions'])
    assert all(a['record_type'] == 'OBSERVATION' for a in value['operational_assertions'])
    assert all(a['support_strength'] == 'DIRECT_BILLING_DOCUMENT' for a in value['operational_assertions'])
    assert not any(e['event_type'] == 'OFF_HIRE' for e in value['events'])
    value['operational_assertions'][0]['container'] = 'RLGU2503666'
    assert golden_case.validate(value, project)['GOPER']['status'] == 'FAIL'


def test_weekly_series_covers_all_containers_without_creating_events(project):
    value = golden_case.payload(project)
    series, = value['weekly_evidence']
    assert series['record_type'] == 'OBSERVATION_SERIES'
    assert series['attachment_count'] == 25
    assert series['observation_count'] == 435
    assert (series['week_start'], series['week_end']) == (7, 29)
    assert set(series['covered_containers']) == set(value['containers'])
    assert series['evidence_status'] == 'VERIFIED'
    assert not any(event['evidence_ref'] == 'SRC-N524-WEEKLY-RECOVERED-20260926'
                   for event in value['events'])


def test_per_container_states_keep_unresolved_units_explicit(project):
    value = golden_case.payload(project)
    states = value['container_states']
    assert len(states) == 26
    assert sum(item['state_status'] == 'CANDIDATE' for item in states) == 5
    assert sum(item['state_status'] == 'UNKNOWN' for item in states) == 21
    assert all(item['weekly_coverage_status'] == 'VERIFIED' for item in states)
    assert all(item['reconciliation_status'] == 'REQUIRED' for item in states)
    assert all((item['off_hire_date'] is not None) == (item['state_status'] == 'CANDIDATE')
               for item in states)
    assert all((item['off_hire_evidence_ref'] is not None) ==
               (item['state_status'] == 'CANDIDATE') for item in states)


def test_weekly_series_count_or_container_omission_fails(project):
    mutate(project, lambda v: recovered_source(v, 'WEEKLY_OBSERVATION_SERIES')['facts'].update(
        observation_count=434))
    with pytest.raises(ValueError, match='coverage'):
        golden_case.payload(project)
    mutate(project, lambda v: recovered_source(v, 'WEEKLY_OBSERVATION_SERIES')['facts'].update(
        observation_count=435,
        covered_containers=recovered_source(v, 'WEEKLY_OBSERVATION_SERIES')['facts']['covered_containers'][:-1]))
    with pytest.raises(ValueError, match='container coverage'):
        golden_case.payload(project)


def test_wrong_offhire_locator_or_strength_fails(project):
    value = golden_case.payload(project)
    value['operational_assertions'][0]['locator'] = 'Commercial Invoice!C999:H999'
    value['operational_assertions'][0]['support_strength'] = 'DEPOT_CONFIRMED'
    assert golden_case.validate(value, project)['GOPER']['status'] == 'FAIL'


def test_source_hash_and_locator_required_at_admission(project):
    mutate(project, lambda v: v['recovered_sources'][0]['bindings'][0].update(locator=''))
    with pytest.raises(ValueError, match='hash or locator'):
        golden_case.payload(project)


def test_billing_versions_remain_alternatives_not_additional_obligations(project):
    value = golden_case.payload(project)
    assert len(value['obligations']) == 3
    assert len(value['billing_documents']) == 2
    assert {i['code'] for i in value['reconciliation_issues']} >= {
        'DOCUMENT_VERSION_CONFLICT', 'NUMERIC_AND_WRITTEN_TOTAL_DIFFER', 'RECEIPT_ALLOCATION_UNRESOLVED'}
    assert all(o['status'] == 'REQUIRED' for o in value['obligations'])
    assert all(o['truth_status'] == {'verification': 'CONFLICTED',
               'allocation': 'UNALLOCATED', 'reconciliation': 'REQUIRED'}
               for o in value['obligations'])
    balance = next(a for a in value['financial_assertions'] if a['assertion_type'] == 'CREDITOR_BALANCE_CLAIM')
    assert balance['as_of'] == '2026-08-20'
    assert balance['current_balance_status'] == 'UNKNOWN'
    comparison = next(a for a in value['financial_assertions'] if a['assertion_type'] == 'BILLING_TOTAL_COMPARISON')
    assert comparison['billing_total'] == '921.62'
    assert comparison['numeric_totals_match'] is True
    assert comparison['assertion_status'] == 'VERIFIED'
    assert comparison['settlement_status'] == 'UNKNOWN'


def test_erased_case_cannot_pass_as_absent_manifest(project):
    gates = golden_case.validate(golden_case.blocked_payload(), project)
    assert gates['GEVID']['status'] == 'FAIL'


def test_billing_comparison_is_calculated_not_a_fixed_pass(project):
    mutate(project, lambda v: recovered_source(v, 'BILLING_DOCUMENT')['facts'].update(amount='700.00'))
    value = golden_case.payload(project)
    comparison = next(a for a in value['financial_assertions'] if a['assertion_type'] == 'BILLING_TOTAL_COMPARISON')
    assert comparison['numeric_totals_match'] is False
    assert 'BILLING_BALANCE_MISMATCH' in {i['code'] for i in value['reconciliation_issues']}
    assert value['statuses']['case'] == 'OPEN'


def test_recovered_components_have_rebuild_hashes_even_while_blocked(tmp_path):
    from semantica_workbench.evaluation.closure import compare
    first = build(ROOT, tmp_path / 'first')
    second = build(ROOT, tmp_path / 'second')
    result = compare(ROOT, first, second)
    assert result['status'] == 'PASS'
    hashes = result['golden_case_hashes']
    assert hashes[0] == hashes[1]
    assert {'receipts', 'payments', 'observations', 'weekly_evidence',
            'container_states', 'operational_assertions', 'billing_documents',
            'evidence_ledger'} <= set(hashes[0])
    summary = read_json(first / 'report.json')['data']['golden_case_001']
    assert summary['golden_case_hashes'] == hashes[0]
    assert summary['gates']['GFIN']['status'] == 'BLOCKED'


def test_redacted_source_mutation_invalidates_prior_snapshot(project, tmp_path):
    (project / 'schemas').mkdir()
    shutil.copy(ROOT / 'schemas/golden_catalog.json', project / 'schemas/golden_catalog.json')
    for name in ('oneway-corpus.md', 'reality-pilot-001-evidence.json'):
        shutil.copy(ROOT / 'data/raw' / name, project / 'data/raw' / name)
    output = build(project, tmp_path / 'snapshot')
    mutate(project, lambda v: v['recovered_sources'][0]['bindings'][0].update(sha256='a' * 64))
    assert validate_snapshot(project, output)['GSYNC']['status'] == 'FAIL'

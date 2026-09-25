"""Phase B fail-closed checks for Golden Case 001."""
import json
import shutil
from pathlib import Path

import pytest

from semantica_workbench.pipeline import golden_case
from semantica_workbench.pipeline.golden import build, read_json, write_json
from semantica_workbench.evaluation.closure import validate as validate_snapshot


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
    assert value["statuses"] == {"operational": "OFF_HIRE_CONFIRMED_LOT_SCOPE", "financial": "OUTSTANDING", "case": "OPEN"}
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

"""Reality Pilot 001 adversarial checks against the business artifact boundary."""
import shutil
from pathlib import Path

import pytest

from semantica_workbench.evaluation.closure import compare, validate
from semantica_workbench.pipeline.golden import COMPONENTS, build, read_json, write_json, digest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def pilot(tmp_path):
    root = tmp_path / "project"
    (root / "schemas").mkdir(parents=True)
    (root / "data/raw").mkdir(parents=True)
    for filename in ("golden_catalog.json",):
        shutil.copy(ROOT / "schemas" / filename, root / "schemas" / filename)
    for filename in ("oneway-corpus.md", "reality-pilot-001-evidence.json"):
        shutil.copy(ROOT / "data/raw" / filename, root / "data/raw" / filename)
    return root, build(root, tmp_path / "run")


def edit_business(output, change):
    value = read_json(output / "business.json")
    change(value["data"])
    write_json(output / "business.json", value)


def fails(pilot, gate):
    assert validate(*pilot)[gate]["status"] == "FAIL"


def test_pilot_passes_with_explicit_business_gates(pilot):
    gates = validate(*pilot)
    assert all(gates[gate]["status"] == "PASS" for gate in ("GEVENT", "GSTATE", "GTIME", "G6"))


def test_event_without_evidence_fails(pilot):
    edit_business(pilot[1], lambda value: value["events"][0].update(evidence_ref="SRC-MISSING"))
    fails(pilot, "GEVENT")


def test_state_transition_without_event_fails(pilot):
    edit_business(pilot[1], lambda value: value["state_transitions"][0].update(event_id="EVT-MISSING"))
    fails(pilot, "GSTATE")


def test_invented_timestamp_fails(pilot):
    edit_business(pilot[1], lambda value: value["events"][0].update(occurred_on="2026-01-29T00:00:00Z"))
    fails(pilot, "GTIME")


def test_out_of_order_event_fails(pilot):
    edit_business(pilot[1], lambda value: value["timeline"].reverse())
    fails(pilot, "GTIME")


def test_case_identity_mismatch_fails(pilot):
    edit_business(pilot[1], lambda value: value["case"].update(contract_reference="ONE-N617"))
    fails(pilot, "G6")


def test_wrong_evidence_locator_fails(pilot):
    edit_business(pilot[1], lambda value: value["events"][1].update(locator="XIA-A!A999:N999"))
    fails(pilot, "GEVENT")


def test_case_specific_fact_promoted_to_generic_fact_fails(pilot):
    value = read_json(pilot[1] / "relations.json")
    value["data"].append({"relation_id": "GR-CASE", "subject": {"entity_id": "CASE-ONE-N524"},
                          "predicate": "has_lot", "object": {"entity_id": "LOT-ONE-N524-26"},
                          "evidence_ref": ["SRC-PI-20260409"]})
    write_json(pilot[1] / "relations.json", value)
    fails(pilot, "GR")


def test_missing_timeline_artifact_fails(pilot):
    edit_business(pilot[1], lambda value: value.update(timeline=[]))
    fails(pilot, "GTIME")


def test_cross_run_business_artifact_mismatch_fails(pilot):
    root, first = pilot
    second = build(root, first.parent / "second")
    shutil.copy(second / "business.json", first / "business.json")
    assert validate(root, first)["GSYNC"]["status"] == "FAIL"


def test_independent_rebuild_covers_business_canonical_hashes(pilot):
    root, first = pilot
    second = build(root, first.parent / "second")
    result = compare(root, first, second)
    assert result["status"] == "PASS"
    assert result["business_hashes"][0] == result["business_hashes"][1]
    assert set(result["business_hashes"][0]) == {"case_entities", "events", "state_transitions", "timeline", "business_graph"}


def test_source_mutation_fails(pilot):
    root, output = pilot
    path = root / "data/raw/reality-pilot-001-evidence.json"
    path.write_text(path.read_text() + "\n")
    assert validate(root, output)["GSYNC"]["status"] == "FAIL"

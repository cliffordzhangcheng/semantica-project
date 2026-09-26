import json
from pathlib import Path

from semantica_workbench.export.one_n524_contract import build_bundle, canonical_bytes, export_bundle


ROOT = Path(__file__).resolve().parents[1]


def test_contract_is_complete_and_fail_closed():
    contract, matrix, manifest = build_bundle(ROOT)
    assert contract["source_truth_head"] == matrix["source_truth_head"] == manifest["source_truth_head"] == \
        "f83e17555a485a8aec5d8d55e26bc26eb2d3f886"
    assert manifest["supersedes_manifest_sha256"] == \
        "8a0ca702c74690cafad41c952c9c97328ae93fe37ab142aa26fec81a1745e8ec"
    assert len(contract["containers"]) == matrix["coverage"]["containers"] == 26
    assert matrix["coverage"] == {
        "containers": 26,
        "owner_depot_gate_in_observations": 20,
        "carrier_notified_off_hire_observations": 18,
        "billing_reported_off_hire_observations": 5,
        "weekly_series_container_coverage": 26,
        "individual_candidate_dates": 26,
        "business_reconciled_individual_dates": 0,
    }
    assert contract["payments"] == []
    assert contract["allocations"][0]["status"] == "UNALLOCATED"
    assert contract["settlements"][0]["status"] == "UNKNOWN"
    assert contract["closure_gate"]["status"] == "BLOCKED"
    assert manifest["blocking_conditions"] == ["GOPER_BLOCKED", "GTIME_BLOCKED", "GFIN_BLOCKED"]


def test_observations_and_date_semantics_are_not_promoted():
    contract, matrix, _ = build_bundle(ROOT)
    assert all("event_id" not in item for item in contract["observations"])
    assert {item["event_type"] for item in contract["events"]}.isdisjoint({
        "OWNER_DEPOT_GATE_IN_REPORTED", "CARRIER_OFF_HIRE_DATE_NOTIFIED", "BILLING_REPORTED_OFF_HIRE"
    })
    assert any(row["depot_gate_in_date"] != row["carrier_notified_off_hire_date"]
               for row in matrix["rows"] if row["depot_gate_in_date"] and row["carrier_notified_off_hire_date"])


def test_bundle_is_deterministic_redacted_and_matches_committed_files(tmp_path):
    first = export_bundle(ROOT, tmp_path / "first")
    second = export_bundle(ROOT, tmp_path / "second")
    assert first == second
    target = ROOT / "contracts/one-n524/v0.4.1"
    for name in first:
        assert (target / name).read_bytes() == (tmp_path / "first" / name).read_bytes()
    text = "".join(path.read_text() for path in target.glob("*.json"))
    assert "/Users/" not in text
    assert "private_ledger_ref" not in text
    assert "source_sha256" not in text
    json.loads(canonical_bytes(build_bundle(ROOT)[0]))

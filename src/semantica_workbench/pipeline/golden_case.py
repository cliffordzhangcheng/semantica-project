"""Fail-closed canonical runtime for Golden Case 001 (ONE-N524).

The public manifest is deliberately redacted.  Its source aliases bind to exact
hashes and locators in the private evidence ledger; it never contains an
original file path, message body, contact detail, signature, or payment data.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .golden import digest, read_json


SOURCE = Path("data/raw/golden-case-001-redacted-evidence.json")
GATES = ("GMASTER", "GJOB", "G26", "GOPER", "GFIN", "GOBL", "GEVID", "GTIME", "GCLOSE")
CONTAINER = re.compile(r"^[A-Z]{4}\d{7}$")


def source_hash(root: Path) -> str | None:
    path = root / SOURCE
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def blocked_payload() -> dict:
    return {
        "status": "BLOCKED", "reason": "Golden Case 001 redacted evidence manifest is absent",
        "master_agreement": None, "job": None, "equipment_lot": None,
        "containers": [], "events": [], "state_transitions": [], "obligations": [],
        "payments": [], "evidence_ledger": [], "timeline": [],
        "statuses": {"operational": "UNKNOWN", "financial": "UNKNOWN", "case": "OPEN"},
        "gates": {gate: {"status": "BLOCKED", "issues": []} for gate in GATES},
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def payload(root: Path) -> dict:
    path = root / SOURCE
    if not path.exists():
        return blocked_payload()
    data = read_json(path)
    expected = {"master_agreement", "job", "equipment_lot", "containers", "sources", "events", "obligations"}
    _require(set(data) == expected, "Golden Case manifest has an unexpected shape")
    master, job, lot = data["master_agreement"], data["job"], data["equipment_lot"]
    _require(set(master) == {"id", "rule_ids", "evidence_ref", "execution_status"}, "Invalid master agreement")
    _require(master["execution_status"] == "OWNER_SIGNED_COUNTERSIGNATURE_NOT_VISIBLE", "Invalid execution status")
    _require(set(job) == {"id", "master_agreement_id", "booking_reference", "evidence_ref"}, "Invalid job")
    _require(job["id"] == "JOB-ONE-N524" and job["master_agreement_id"] == master["id"], "Unstable job identity")
    _require(set(lot) == {"id", "job_id", "quantity", "equipment_type", "evidence_ref"}, "Invalid lot")
    _require(lot["job_id"] == job["id"] and lot["quantity"] == 26 and lot["equipment_type"] == "20HC", "Invalid lot identity")
    containers = data["containers"]
    _require(len(containers) == 26 and len(set(containers)) == 26 and all(CONTAINER.fullmatch(value) for value in containers), "G26 container identity failure")
    sources = data["sources"]
    required_source = {"evidence_id", "source_alias", "source_type", "source_date", "supports", "support_strength", "sensitivity", "redaction_status", "private_ledger_ref", "notes"}
    _require(len(sources) >= 7 and len({s.get("evidence_id") for s in sources}) == len(sources), "Invalid evidence ledger")
    _require(all(set(source) == required_source and source["redaction_status"] == "REDACTED" and source["private_ledger_ref"].startswith("N524-") for source in sources), "Unsafe or incomplete evidence ledger")
    source_ids = {source["evidence_id"] for source in sources}
    events = data["events"]
    required_event = {"event_id", "event_type", "scope", "occurred_on", "date_precision", "evidence_ref", "assertion", "state_transition"}
    _require(len(events) >= 4 and len({event.get("event_id") for event in events}) == len(events), "Insufficient events")
    for event in events:
        _require(set(event) == required_event and event["evidence_ref"] in source_ids, "Event without evidence")
        _require(event["date_precision"] == "day" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", event["occurred_on"]) is not None, "Invented timestamp")
        _require(set(event["state_transition"]) == {"from", "to"}, "Malformed state transition")
        _require(not (event["event_type"] == "OFF_HIRE" and event["scope"].startswith("container:")), "Per-container off-hire is not source-bound")
    obligations = data["obligations"]
    required_obligation = {"obligation_id", "type", "status", "evidence_ref", "notes"}
    _require(len(obligations) >= 3 and all(set(item) == required_obligation and item["evidence_ref"] in source_ids for item in obligations), "Invalid obligation")
    _require(all(item["status"] == "OUTSTANDING_UNALLOCATED" for item in obligations), "Unsupported settlement")
    transitions = [{"transition_id": f"ST-{event['event_id']}", "event_id": event["event_id"], "scope": event["scope"], **event["state_transition"], "occurred_on": event["occurred_on"], "evidence_ref": event["evidence_ref"]} for event in events]
    timeline = [{"event_id": event["event_id"], "occurred_on": event["occurred_on"], "date_precision": "day"} for event in sorted(events, key=lambda e: (e["occurred_on"], e["event_id"]))]
    nodes = ([{"entity_id": master["id"], "type": "MasterAgreement"}, {"entity_id": job["id"], "type": "OneWayLeaseJob"}, {"entity_id": lot["id"], "type": "EquipmentLot", "quantity": 26, "equipment_type": "20HC"}]
             + [{"entity_id": f"CONTAINER-{container}", "type": "Container", "container_number": container, "operational_state": "UNRECONCILED"} for container in containers])
    edges = [{"subject": job["id"], "predicate": "governed_by", "object": master["id"], "evidence_ref": master["evidence_ref"]}, {"subject": job["id"], "predicate": "has_equipment_lot", "object": lot["id"], "evidence_ref": lot["evidence_ref"]}]
    return {"status": "BLOCKED", "master_agreement": master, "job": job, "equipment_lot": lot, "containers": containers, "events": events, "state_transitions": transitions, "obligations": obligations, "payments": [], "evidence_ledger": sources, "timeline": timeline, "business_graph": {"nodes": nodes, "edges": edges}, "statuses": {"operational": "OFF_HIRE_CONFIRMED_LOT_SCOPE", "financial": "OUTSTANDING", "case": "OPEN"}, "gates": {"GMASTER": {"status": "PASS", "issues": []}, "GJOB": {"status": "PASS", "issues": []}, "G26": {"status": "PASS", "issues": []}, "GOPER": {"status": "BLOCKED", "issues": ["Per-container off-hire confirmation is not yet bound"]}, "GFIN": {"status": "PASS", "issues": []}, "GOBL": {"status": "PASS", "issues": []}, "GEVID": {"status": "PASS", "issues": []}, "GTIME": {"status": "BLOCKED", "issues": ["Cross-source operational timestamps require reconciliation"]}, "GCLOSE": {"status": "PASS", "issues": ["Case correctly remains OPEN"]}}}


def validate(value: dict, root: Path) -> dict:
    expected = payload(root)
    if value != expected:
        return {gate: {"status": "FAIL", "issues": ["Golden Case artifact differs from governed manifest"]} for gate in GATES}
    return expected["gates"]


def canonical_hashes(value: dict) -> dict:
    return {key: digest(value[key]) for key in ("master_agreement", "job", "equipment_lot", "containers", "events", "state_transitions", "obligations", "timeline", "business_graph", "statuses")}

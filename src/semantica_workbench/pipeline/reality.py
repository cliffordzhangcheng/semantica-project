"""Fail-closed Reality Pilot 001 business artifacts.

This module contains no extractor.  Each event is an explicit, source-bound
assertion reviewed from the private business documents named in the governed
evidence manifest.  The private originals stay outside the repository; their
SHA-256 values and precise locators make later re-checking possible.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .golden import digest, read_json


SOURCE = Path("data/raw/reality-pilot-001-evidence.json")
REQUIRED_EVENT = {
    "event_id", "event_type", "scope", "occurred_on", "date_precision",
    "evidence_ref", "locator", "assertion", "state_transition",
}


def source_path(root: Path) -> Path:
    return root / SOURCE


def source_hash(root: Path) -> str | None:
    path = source_path(root)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def blocked_payload() -> dict:
    """Keep the inherited Golden runtime usable in repositories without pilot data."""
    return {
        "status": "BLOCKED",
        "reason": "Reality Pilot 001 governed evidence is absent",
        "case": None,
        "case_entities": [],
        "events": [],
        "state_transitions": [],
        "timeline": [],
        "business_graph": {"nodes": [], "edges": []},
        "source_documents": [],
        "gates": {key: {"status": "BLOCKED"} for key in ("GEVENT", "GSTATE", "GTIME", "G6")},
    }


def payload(root: Path) -> dict:
    path = source_path(root)
    if not path.exists():
        return blocked_payload()
    data = read_json(path)
    if set(data) != {"case", "sources", "events"}:
        raise ValueError("Reality evidence manifest has an unexpected shape")
    case = data["case"]
    required_case = {"case_id", "contract_reference", "booking_reference", "purchase_order", "origin_depot", "destination_port", "redelivery_depot", "equipment"}
    if set(case) != required_case or case["equipment"] != {"quantity": 26, "type": "20HC"}:
        raise ValueError("Reality case identity is incomplete")
    sources = data["sources"]
    source_ids = {source.get("id") for source in sources}
    if len(sources) < 4 or len(source_ids) != len(sources):
        raise ValueError("Reality sources are incomplete or duplicated")
    if any(set(source) != {"id", "source_path", "source_sha256", "locator", "facts"}
           or len(source["source_sha256"]) != 64 for source in sources):
        raise ValueError("Reality source provenance is invalid")
    events = data["events"]
    if len(events) < 3 or len({event.get("event_id") for event in events}) != len(events):
        raise ValueError("Reality events are incomplete or duplicated")
    for event in events:
        if set(event) != REQUIRED_EVENT:
            raise ValueError("Reality event has an unexpected field")
        if event["evidence_ref"] not in source_ids or event["date_precision"] != "day":
            raise ValueError("Reality event has invalid evidence or time precision")
        if len(event["occurred_on"]) != 10 or "T" in event["occurred_on"]:
            raise ValueError("Invented event timestamp rejected")
        if set(event["state_transition"]) != {"from", "to"}:
            raise ValueError("Reality transition is malformed")
    events = sorted(events, key=lambda event: (event["occurred_on"], event["event_id"]))
    transitions = [{"transition_id": f"ST-{event['event_id']}", "event_id": event["event_id"],
                    "scope": event["scope"], **event["state_transition"],
                    "occurred_on": event["occurred_on"], "evidence_ref": event["evidence_ref"]}
                   for event in events]
    case_entities = [
        {"entity_id": case["case_id"], "type": "OneWayLeaseCase", "contract_reference": case["contract_reference"], "booking_reference": case["booking_reference"]},
        {"entity_id": "LOT-ONE-N524-26", "type": "ContainerLot", **case["equipment"]},
        {"entity_id": "DEPOT-CNSGHMJ1", "type": "Depot", "code": case["origin_depot"]},
        {"entity_id": "PORT-PLGDNDCT", "type": "PortOrDepot", "code": case["destination_port"]},
        {"entity_id": "DEPOT-TUCHOM-TRADECON", "type": "RedeliveryDepot", "name": case["redelivery_depot"]},
    ]
    graph = {
        "nodes": case_entities + [{"entity_id": event["event_id"], "type": "BusinessEvent"} for event in events],
        "edges": [
            {"subject": case["case_id"], "predicate": "has_lot", "object": "LOT-ONE-N524-26", "evidence_ref": "SRC-PI-20260409"},
            {"subject": "LOT-ONE-N524-26", "predicate": "originated_at", "object": "DEPOT-CNSGHMJ1", "evidence_ref": "SRC-PI-20260409"},
            {"subject": "LOT-ONE-N524-26", "predicate": "redelivery_authorized_at", "object": "DEPOT-TUCHOM-TRADECON", "evidence_ref": "SRC-ERI-26"},
        ] + [{"subject": case["case_id"], "predicate": "has_event", "object": event["event_id"], "evidence_ref": event["evidence_ref"]} for event in events],
    }
    return {
        "status": "PASS_CANDIDATE",
        "case": case,
        "case_entities": case_entities,
        "events": events,
        "state_transitions": transitions,
        "timeline": [{"event_id": event["event_id"], "occurred_on": event["occurred_on"], "date_precision": "day"} for event in events],
        "business_graph": graph,
        "source_documents": sources,
        "gates": {key: {"status": "PASS"} for key in ("GEVENT", "GSTATE", "GTIME", "G6")},
        "limitations": ["No payment confirmation: no SETTLED or CLOSED state.", "The weekly-report snapshot covers 17 of 26 containers; no claim that all 26 were off-hired."],
    }


def validate(value: dict, root: Path) -> dict:
    expected = payload(root)
    problems = {key: [] for key in ("GEVENT", "GSTATE", "GTIME", "G6")}
    if value != expected:
        for issues in problems.values():
            issues.append("Business artifact differs from the reviewed evidence manifest")
        return {key: {"status": "FAIL", "issues": issues} for key, issues in problems.items()}
    if value["status"] == "BLOCKED":
        return {key: {"status": "BLOCKED", "issues": []} for key in problems}
    event_ids = {event["event_id"] for event in value["events"]}
    evidence_ids = {source["id"] for source in value["source_documents"]}
    if len(value["events"]) < 3 or any(event["evidence_ref"] not in evidence_ids for event in value["events"]):
        problems["GEVENT"].append("Missing source-grounded business event")
    if any("T" in event["occurred_on"] for event in value["events"]):
        problems["GTIME"].append("Invented timestamp")
    source_backed = [transition for transition in value["state_transitions"] if transition["from"] != "NOT_RECORDED"]
    if len(source_backed) < 2 or any(transition["event_id"] not in event_ids for transition in value["state_transitions"]):
        problems["GSTATE"].append("Transition without source event")
    for transition in source_backed:
        prior = [event for event in value["events"] if event["scope"] == transition["scope"]
                 and event["occurred_on"] <= transition["occurred_on"]
                 and event["state_transition"]["to"] == transition["from"]]
        if not prior:
            problems["GSTATE"].append("Transition has no earlier source-backed state")
    if value["timeline"] != sorted(value["timeline"], key=lambda item: (item["occurred_on"], item["event_id"])):
        problems["GTIME"].append("Timeline is not deterministic")
    if not value["case"]["contract_reference"] or not value["case"]["booking_reference"]:
        problems["G6"].append("Unstable case identity")
    if any(problems[key] for key in ("GEVENT", "GSTATE", "GTIME")):
        problems["G6"].append("A prerequisite business gate failed")
    return {key: {"status": "FAIL" if issues else "PASS", "issues": issues} for key, issues in problems.items()}


def canonical_hashes(value: dict) -> dict:
    return {key: digest(value[key]) for key in ("case_entities", "events", "state_transitions", "timeline", "business_graph")}

"""Fail-closed canonical runtime for Golden Case 001 (ONE-N524).

The public manifest is deliberately redacted.  Its source aliases bind to exact
hashes and locators in the private evidence ledger; it never contains an
original file path, message body, contact detail, signature, or bank account details. Recovered monetary assertions are redacted
semantic facts, not confidential originals.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .golden import digest, read_json
from .golden_case_recovery import TRUTH_STATES, project as project_recovery


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
        "containers": [], "observations": [], "events": [], "state_transitions": [],
        "obligations": [], "receipts": [], "payments": [], "evidence_ledger": [], "timeline": [],
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
    expected = {"master_agreement", "job", "equipment_lot", "containers", "sources",
                "observations", "events", "obligations", "recovered_sources"}
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
    recovered = project_recovery(data["recovered_sources"], job["id"], containers)
    sources = sources + data["recovered_sources"]
    source_ids = {source["evidence_id"] for source in sources}
    _require(len(source_ids) == len(sources), "Duplicate source identity")
    for owner in (master, job, lot):
        _require(owner["evidence_ref"] in source_ids, "Entity without evidence")
    observations = data["observations"] + recovered["observations"]
    _require(len({item.get("observation_id") for item in observations}) == len(observations),
             "Duplicate observation identity")
    allowed_observations = {"OWNER_GATE_IN_REPORTED", "RECEIPT_REPORTED",
                            "OWNER_DEPOT_GATE_IN_REPORTED",
                            "CARRIER_OFF_HIRE_DATE_NOTIFIED",
                            "BILLING_REPORTED_OFF_HIRE", "PAYABLE_BOOKED"}
    for observation in observations:
        _require(observation.get("record_type") == "OBSERVATION" and
                 observation.get("evidence_ref") in source_ids,
                 "Observation without evidence")
        _require(observation.get("observation_type") in allowed_observations,
                 "Unsupported observation type")
        _require("event_id" not in observation and "state_transition" not in observation,
                 "Observation promoted to event")
        _require(observation.get("assertion_status") in TRUTH_STATES and
                 observation.get("evidence_status") in TRUTH_STATES,
                 "Observation truth status missing")
        if observation["observation_type"] == "OWNER_GATE_IN_REPORTED":
            _require(observation.get("evidence_ref") == "SRC-N524-GATEIN" and
                     observation.get("scope") == "lot:LOT-ONE-N524-26",
                     "Gate-in observation promoted or changed scope")
        if observation["observation_type"] in {
                "OWNER_DEPOT_GATE_IN_REPORTED", "CARRIER_OFF_HIRE_DATE_NOTIFIED"}:
            _require(str(observation.get("scope", "")).startswith("container:") and
                     observation["scope"].split(":", 1)[1] in containers,
                     "Per-container operational observation has invalid scope")
    events = data["events"]
    required_event = {"event_id", "event_type", "scope", "occurred_on", "date_precision", "evidence_ref", "assertion", "state_transition"}
    _require(len(events) >= 3 and len({event.get("event_id") for event in events}) == len(events), "Insufficient events")
    for event in events:
        _require(set(event) == required_event and event["evidence_ref"] in source_ids, "Event without evidence")
        _require(event["date_precision"] == "day" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", event["occurred_on"]) is not None, "Invented timestamp")
        _require(set(event["state_transition"]) == {"from", "to"}, "Malformed state transition")
        _require(not event["event_type"].endswith(("_OBSERVED", "_REPORTED")) and
                 event["event_type"] != "PAYABLE_BOOKED", "Observation promoted to event")
        _require(not (event["event_type"] == "OFF_HIRE" and event["scope"].startswith("container:")), "Per-container off-hire is not source-bound")
    obligations = data["obligations"]
    required_obligation = {"obligation_id", "type", "status", "truth_status", "evidence_ref", "notes"}
    _require(len(obligations) >= 3 and all(set(item) == required_obligation and item["evidence_ref"] in source_ids for item in obligations), "Invalid obligation")
    required_truth = {"verification": "CONFLICTED", "allocation": "UNALLOCATED",
                      "reconciliation": "REQUIRED"}
    _require(all(item["status"] == "REQUIRED" and item["truth_status"] == required_truth
                 for item in obligations), "Unsupported settlement")
    transitions = [{"transition_id": f"ST-{event['event_id']}", "event_id": event["event_id"], "scope": event["scope"], **event["state_transition"], "occurred_on": event["occurred_on"], "evidence_ref": event["evidence_ref"]} for event in events]
    timeline = [{"event_id": event["event_id"], "occurred_on": event["occurred_on"], "date_precision": "day"} for event in sorted(events, key=lambda e: (e["occurred_on"], e["event_id"]))]
    container_states = recovered["container_states"]
    _require(len(container_states) == 26 and
             {item["container"] for item in container_states} == set(containers),
             "Per-container state coverage failure")
    _require(all(item["operational_state"] == "OFF_HIRE_CONFIRMED_LOT_SCOPE" and
                 item["operational_state_scope"] == "LOT" and
                 item["individual_off_hire_date_status"] == "CANDIDATE" and
                 item["off_hire_date"] is not None and
                 item["off_hire_evidence_refs"]
                 for item in container_states),
             "Lot completion and individual date evidence were conflated")
    _require(all(item["weekly_coverage_status"] == "VERIFIED" and
                 item["reconciliation_status"] == "REQUIRED" for item in container_states),
             "Per-container weekly coverage or reconciliation status changed")
    state_by_container = {item["container"]: item for item in container_states}
    nodes = ([{"entity_id": master["id"], "type": "MasterAgreement"}, {"entity_id": job["id"], "type": "OneWayLeaseJob"}, {"entity_id": lot["id"], "type": "EquipmentLot", "quantity": 26, "equipment_type": "20HC"}]
             + [{"entity_id": f"CONTAINER-{container}", "type": "Container",
                 "container_number": container,
                 "operational_state": state_by_container[container]["operational_state"],
                 "operational_state_scope": state_by_container[container]["operational_state_scope"],
                 "individual_off_hire_date_status": state_by_container[container]["individual_off_hire_date_status"],
                 "reconciliation_status": state_by_container[container]["reconciliation_status"]}
                for container in containers])
    edges = [{"subject": job["id"], "predicate": "governed_by", "object": master["id"], "evidence_ref": master["evidence_ref"]}, {"subject": job["id"], "predicate": "has_equipment_lot", "object": lot["id"], "evidence_ref": lot["evidence_ref"]}]
    for container in containers:
        edges.append({"subject": lot["id"], "predicate": "contains", "object": f"CONTAINER-{container}", "evidence_ref": lot["evidence_ref"]})
    for item in obligations:
        nodes.append({"entity_id": item["obligation_id"], "type": "FinancialObligation", "status": item["status"]})
        edges.append({"subject": job["id"], "predicate": "has_obligation", "object": item["obligation_id"], "evidence_ref": item["evidence_ref"]})
    for receipt in recovered["receipts"]:
        nodes.append({"entity_id": receipt["receipt_id"], "type": "Receipt",
                      "assertion_status": receipt["assertion_status"],
                      "allocation_status": receipt["allocation_status"],
                      "case_refs": receipt["case_refs"]})
        edges.append({"subject": job["id"], "predicate": "has_receipt_observation",
                      "object": receipt["receipt_id"], "evidence_ref": receipt["evidence_ref"]})
    for document in recovered["billing_documents"]:
        nodes.append({"entity_id": document["document_id"], "type": "ProformaInvoice", "charge_type": document["charge_type"]})
        edges.append({"subject": job["id"], "predicate": "has_billing_document", "object": document["document_id"], "evidence_ref": document["evidence_ref"]})
    return {
        "status": "BLOCKED", "master_agreement": master, "job": job,
        "equipment_lot": lot, "containers": containers, "observations": observations,
        "events": events,
        "state_transitions": transitions, "obligations": obligations,
        "receipts": recovered["receipts"], "payments": recovered["payments"],
        "evidence_ledger": sources,
        "billing_documents": recovered["billing_documents"],
        "weekly_evidence": recovered["weekly_evidence"],
        "container_states": container_states,
        "operational_assertions": recovered["operational_assertions"],
        "financial_assertions": recovered["financial_assertions"],
        "reconciliation_issues": recovered["reconciliation_issues"],
        "timeline": timeline, "business_graph": {"nodes": nodes, "edges": edges},
        "statuses": {"operational": "OFF_HIRE_CONFIRMED_LOT_SCOPE",
                     "financial": "REQUIRED", "case": "OPEN"},
        "gates": {gate: {"status": "BLOCKED" if gate in ("GOPER", "GTIME", "GFIN") else "PASS",
                         "issues": _pending_issues(gate)} for gate in GATES},
    }


def _pending_issues(gate):
    return {
        "GOPER": ["All 26 containers have source-bound candidate dates; lot completion remains distinct from individual date reconciliation"],
        "GTIME": ["Depot gate-in and carrier-notified off-hire dates are retained as distinct semantics where they differ"],
        "GFIN": ["Reported receipt allocation and billing conflicts remain unresolved"],
        "GCLOSE": ["Case correctly remains OPEN"],
    }.get(gate, [])



def validate(value: dict, root: Path) -> dict:
    """Validate the rendered runtime independently of stored gate labels."""
    issues = {gate: [] for gate in GATES}
    expected = payload(root)
    if value.get("status") == "BLOCKED" and value.get("master_agreement") is None:
        if expected.get("master_agreement") is not None:
            return {gate: {"status": "FAIL", "issues": ["Existing Golden Case artifact was erased"]} for gate in GATES}
        return {gate: {"status": "BLOCKED", "issues": []} for gate in GATES}
    master, job, lot = value.get("master_agreement"), value.get("job"), value.get("equipment_lot")
    if not master or not master.get("rule_ids") or master.get("execution_status") != "OWNER_SIGNED_COUNTERSIGNATURE_NOT_VISIBLE":
        issues["GMASTER"].append("Master Agreement lineage is invalid")
    if not job or job.get("id") != "JOB-ONE-N524" or not master or job.get("master_agreement_id") != master.get("id"):
        issues["GJOB"].append("Job is not bound to the Master Agreement")
    containers = value.get("containers", [])
    if len(containers) != 26 or len(set(containers)) != 26 or any(not isinstance(item, str) or not CONTAINER.fullmatch(item) for item in containers):
        issues["G26"].append("Container identities are incomplete or collide")
    if not lot or lot.get("job_id") != (job or {}).get("id") or lot.get("quantity") != len(containers) or lot.get("equipment_type") != "20HC":
        issues["G26"].append("Equipment lot is not consistent with job/container identities")
    evidence = {item.get("evidence_id"): item for item in value.get("evidence_ledger", [])}
    if not evidence or any(item.get("redaction_status") != "REDACTED" or not str(item.get("private_ledger_ref", "")).startswith("N524-") for item in evidence.values()):
        issues["GEVID"].append("Evidence lineage is unsafe or incomplete")
    events = value.get("events", [])
    transitions = {item.get("event_id"): item for item in value.get("state_transitions", [])}
    for event in events:
        if event.get("evidence_ref") not in evidence:
            issues["GEVID"].append("Event has dangling evidence")
        if event.get("event_type") == "OFF_HIRE" and str(event.get("scope", "")).startswith("container:"):
            issues["GOPER"].append("Container off-hire lacks primary evidence")
        transition = transitions.get(event.get("event_id"))
        if not transition or transition.get("scope") != event.get("scope") or transition.get("evidence_ref") != event.get("evidence_ref"):
            issues["GOPER"].append("Event/state transition lineage is broken")
        if event.get("date_precision") != "day" or not isinstance(event.get("occurred_on"), str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", event["occurred_on"]) is None:
            issues["GTIME"].append("Event has an invented or imprecise timestamp")
        if str(event.get("event_type", "")).endswith(("_OBSERVED", "_REPORTED")) or event.get("event_type") == "PAYABLE_BOOKED":
            issues["GOPER"].append("Observation was promoted to an event")
    timeline = value.get("timeline", [])
    expected_timeline = [{"event_id": event["event_id"], "occurred_on": event["occurred_on"], "date_precision": "day"} for event in sorted(events, key=lambda event: (event["occurred_on"], event["event_id"]))]
    if timeline != expected_timeline:
        issues["GTIME"].append("Timeline does not deterministically rebuild from events")
    if value.get("observations") != expected.get("observations"):
        issues["GOPER"].append("Observations differ from source assertions")
    if value.get("weekly_evidence") != expected.get("weekly_evidence"):
        issues["GEVID"].append("Weekly report-series coverage differs from recovered evidence")
    if value.get("container_states") != expected.get("container_states"):
        issues["GOPER"].append("Per-container unresolved states differ from source assertions")
    for field in ("receipts", "payments", "billing_documents", "financial_assertions", "reconciliation_issues"):
        if value.get(field) != expected.get(field):
            issues["GFIN"].append(f"Recovered {field} differ from source assertions")
    if value.get("payments"):
        issues["GFIN"].append("Receipt was promoted to an allocated payment")
    if value.get("operational_assertions") != expected.get("operational_assertions"):
        issues["GOPER"].append("Off-hire assertion scope or source lineage changed")
    obligations = value.get("obligations", [])
    required_truth = {"verification": "CONFLICTED", "allocation": "UNALLOCATED",
                      "reconciliation": "REQUIRED"}
    if not obligations or any(item.get("evidence_ref") not in evidence or
                              item.get("status") != "REQUIRED" or
                              item.get("truth_status") != required_truth for item in obligations):
        issues["GFIN"].append("Financial obligation is unsupported or falsely settled")
    if value.get("statuses", {}).get("financial") != "REQUIRED" or value.get("statuses", {}).get("case") != "OPEN":
        issues["GOBL"].append("Outstanding obligation is hidden by case status")
        issues["GCLOSE"].append("Case closure is unsupported")
    # Written owner/carrier evidence now covers all individual dates, while
    # depot gate-in and carrier-effective off-hire semantics remain distinct.
    # BLOCKED remains correct until business reconciliation admits final events.
    operational = value.get("statuses", {}).get("operational")
    if operational != "OFF_HIRE_CONFIRMED_LOT_SCOPE":
        issues["GOPER"].append("Operational status is not scoped to available evidence")
    if value != expected:
        issues["GEVID"].append("Runtime differs from the governed evidence manifest")
    result = {}
    for gate, messages in issues.items():
        if messages:
            result[gate] = {"status": "FAIL", "issues": messages}
        else:
            result[gate] = {"status": "BLOCKED" if gate in ("GOPER", "GTIME", "GFIN") else "PASS",
                            "issues": _pending_issues(gate)}
    return result


def canonical_hashes(value: dict) -> dict:
    if value.get("master_agreement") is None:
        return {}
    return {key: digest(value[key]) for key in (
        "master_agreement", "job", "equipment_lot", "containers", "observations", "events", "state_transitions",
        "obligations", "receipts", "payments", "billing_documents", "weekly_evidence",
        "container_states", "operational_assertions", "financial_assertions",
        "reconciliation_issues", "evidence_ledger", "timeline", "business_graph", "statuses")}

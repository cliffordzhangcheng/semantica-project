"""Deterministic, redacted ONE-N524 contract for the candidate Workbench spine."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from semantica_workbench.pipeline import golden_case


SCHEMA_VERSION = "one-n524-bounded-operational-contract-v0.4.1"
SOURCE_TRUTH_HEAD = "f83e17555a485a8aec5d8d55e26bc26eb2d3f886"
SHARED_SPINE_MANIFEST_SHA256 = "808cfda4b9f4fc1558cc5564e8a2334708e81dcdd0c999252609e82cb69ee6d2"
LINEAGE = "TASK-20260924-AKOS-CODEX8-CONVERGENCE-OWNER-RECONCILIATION-v0.1"
CONTRACT_FILE = "one-n524-bounded-operational-contract-v0.4.1.json"
MATRIX_FILE = "one-n524-evidence-matrix-v0.4.1.json"
MANIFEST_FILE = "IMMUTABLE-ONE-N524-CONTRACT-MANIFEST-20260926-v0.4.1.json"
SUPERSEDES_MANIFEST_SHA256 = "8a0ca702c74690cafad41c952c9c97328ae93fe37ab142aa26fec81a1745e8ec"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_bundle(root: Path) -> tuple[dict, dict, dict]:
    runtime = golden_case.payload(root)
    _require(runtime["job"]["id"] == "JOB-ONE-N524", "unstable ONE-N524 identity")
    _require(len(runtime["containers"]) == len(runtime["container_states"]) == 26,
             "ONE-N524 must contain exactly 26 container dispositions")
    _require(runtime["payments"] == [], "receipt or payable booking was promoted to Payment")
    _require(runtime["statuses"] == {
        "operational": "OFF_HIRE_CONFIRMED_LOT_SCOPE", "financial": "REQUIRED", "case": "OPEN"
    }, "ONE-N524 fail-closed status changed")
    _require(all(item["individual_off_hire_date_status"] == "CANDIDATE" and
                 item["reconciliation_status"] == "REQUIRED"
                 for item in runtime["container_states"]), "individual dates were promoted")

    evidence = [{
        "object_type": "EvidenceAssertion",
        "evidence_id": item["evidence_id"],
        "source_alias": item.get("source_alias", item["evidence_id"]),
        "source_type": item.get("source_type", item.get("kind", "REDACTED_SOURCE")),
        "source_date": item.get("source_date"),
        "support_strength": item["support_strength"],
        "redaction_status": item["redaction_status"],
    } for item in runtime["evidence_ledger"]]

    containers = [{
        "object_type": "Container",
        "container_id": f"CONTAINER-{item['container']}",
        "container_number": item["container"],
        "job_id": runtime["job"]["id"],
        "equipment_type": runtime["equipment_lot"]["equipment_type"],
        "lot_completion_state": item["operational_state"],
        "lot_completion_scope": item["operational_state_scope"],
        "individual_date_status": item["individual_off_hire_date_status"],
        "selected_candidate_date": item["off_hire_date"],
        "selected_candidate_date_basis": item["off_hire_date_basis"],
        "depot_gate_in_date": item["depot_gate_in_date"],
        "carrier_notified_off_hire_date": item["carrier_notified_off_hire_date"],
        "billing_reported_off_hire_date": item["billing_reported_off_hire_date"],
        "date_semantics_status": item["date_semantics_status"],
        "evidence_refs": item["off_hire_evidence_refs"],
        "weekly_coverage_status": item["weekly_coverage_status"],
        "reconciliation_status": item["reconciliation_status"],
    } for item in runtime["container_states"]]

    documents = [{"object_type": "Document", **deepcopy(item)}
                 for item in runtime["billing_documents"]]
    document_versions = []
    for issue in runtime["reconciliation_issues"]:
        if issue["code"] == "DOCUMENT_VERSION_CONFLICT":
            for index, amount in enumerate(issue["alternative_amounts"], 1):
                document_versions.append({
                    "object_type": "DocumentVersion",
                    "document_ref": issue["document_ref"],
                    "version_id": f"{issue['document_ref']}-V{index}",
                    "amount": amount,
                    "currency": "USD",
                    "truth_status": "CONFLICTED",
                    "evidence_ref": issue["evidence_ref"],
                })

    payment_claims = []
    for index, item in enumerate(runtime["financial_assertions"], 1):
        payment_claims.append({
            "object_type": "PaymentClaim",
            "payment_claim_id": f"PAYMENT-CLAIM-ONE-N524-{index:02d}",
            **deepcopy(item),
        })
    allocations = [{
        "object_type": "Allocation",
        "allocation_id": f"ALLOCATION-{item['receipt_id']}",
        "receipt_id": item["receipt_id"],
        "job_id": None,
        "amount": None,
        "status": "UNALLOCATED",
    } for item in runtime["receipts"]]

    exceptions = [{
        "object_type": "Exception",
        "exception_id": f"EXCEPTION-ONE-N524-{index:02d}",
        **deepcopy(item),
    } for index, item in enumerate(runtime["reconciliation_issues"], 1)]
    next_actions = [
        {
            "object_type": "NextAction", "action_id": "ACTION-N524-OPER-DATE-RECONCILIATION",
            "owner": "CODEX5", "current": "26 source-bound candidate dates; 20 owner gate-in and 18 carrier notices",
            "target": "business-reviewed disposition for each individual date semantic",
            "next": "consume the immutable matrix and preserve all three date dimensions",
            "trigger": "CODEX8 adapter import", "blocker": "GOPER and GTIME remain BLOCKED",
        },
        {
            "object_type": "NextAction", "action_id": "ACTION-N524-FIN-RECONCILIATION",
            "owner": "Founder/business reviewer", "current": "receipt is UNALLOCATED and payment is UNKNOWN",
            "target": "case-specific receipt allocation and reconciled document versions",
            "next": "review receipt allocation, debit-note versions and PI conflicts",
            "trigger": "business evidence or explicit disposition", "blocker": "GFIN remains BLOCKED",
        },
        {
            "object_type": "NextAction", "action_id": "ACTION-N524-CODEX8-CONSUME",
            "owner": "CODEX8", "current": "v0.4 contract frozen against the v0.3.1 shared spine",
            "target": "read-only Workbench rendering from this contract",
            "next": "verify manifest hashes, then import without semantic promotion",
            "trigger": "manifest and contract hash match", "blocker": "reject on hash or invariant mismatch",
        },
    ]

    closure_prerequisites = {
        "all_26_container_dispositions_present": len(containers) == 26,
        "all_individual_dates_business_reconciled": all(i["reconciliation_status"] == "VERIFIED" for i in containers),
        "document_conflicts_dispositioned": not exceptions,
        "charge_ledger_reconciled": runtime["gates"]["GFIN"]["status"] == "PASS",
        "receipt_allocated": bool(runtime["receipts"]) and all(i["allocation_status"] != "UNALLOCATED" for i in runtime["receipts"]),
        "payment_verified": bool(runtime["payments"]),
        "settlement_verified": False,
        "zero_blocking_exceptions": not exceptions,
        "explicit_closure_approval": False,
    }
    contract = {
        "schema_version": SCHEMA_VERSION,
        "contract_id": "ONE-N524-BOUNDED-OPERATIONAL-CONTRACT-v0.4.1",
        "lineage": LINEAGE,
        "authority": "DERIVED_READ_ONLY_CANDIDATE",
        "source_truth_head": SOURCE_TRUTH_HEAD,
        "shared_spine_manifest_sha256": SHARED_SPINE_MANIFEST_SHA256,
        "boundaries": {"production_change": False, "canonical_change": False,
                       "new_database": False, "second_spine": False, "raw_evidence_included": False},
        "invariants": [
            "Observation != Event", "Gate-In != Off-Hire",
            "Receipt != Payment != Allocation != Settlement", "Payable Booked != Paid",
            "UNKNOWN and UNALLOCATED fail closed",
        ],
        "agreements": [{"object_type": "Agreement", **deepcopy(runtime["master_agreement"])}],
        "agreement_versions": [{
            "object_type": "AgreementVersion", "agreement_id": runtime["master_agreement"]["id"],
            "version_id": "MASTER-AGREEMENT-2023-OWNER-SIGNED-PHOTOCOPY",
            "execution_status": runtime["master_agreement"]["execution_status"],
            "evidence_ref": runtime["master_agreement"]["evidence_ref"],
        }],
        "jobs": [{"object_type": "Job", "case_status": runtime["statuses"]["case"], **deepcopy(runtime["job"])}],
        "equipment_lots": [{"object_type": "EquipmentLot", **deepcopy(runtime["equipment_lot"])}],
        "containers": containers,
        "observations": [{"object_type": "Observation", **deepcopy(item)}
                         for item in runtime["observations"]],
        "events": [{"object_type": "Event", **deepcopy(item)}
                   for item in runtime["events"]],
        "documents": documents,
        "document_versions": document_versions,
        "charges": [{"object_type": "Charge", "charge_id": f"CHARGE-{item['document_id']}",
                     "document_id": item["document_id"], "charge_type": item["charge_type"],
                     "amount": item["numeric_total"], "currency": item["currency"],
                     "reconciliation_status": item["reconciliation_status"]} for item in runtime["billing_documents"]],
        "conflicts": exceptions,
        "payment_claims": payment_claims,
        "receipts": deepcopy(runtime["receipts"]),
        "payments": [],
        "allocations": allocations,
        "settlements": [{"object_type": "Settlement", "settlement_id": "SETTLEMENT-ONE-N524",
                         "status": "UNKNOWN", "payment_refs": [], "allocation_refs": []}],
        "evidence_assertions": evidence,
        "exceptions": exceptions,
        "next_actions": next_actions,
        "closure_gate": {"object_type": "ClosureGate", "gate_id": "CLOSURE-GATE-ONE-N524",
                         "status": "BLOCKED", "prerequisites": closure_prerequisites,
                         "blocking_gate_ids": ["GOPER", "GTIME", "GFIN"]},
        "source_gates": deepcopy(runtime["gates"]),
    }

    matrix = {
        "schema_version": "one-n524-evidence-matrix-v0.4.1",
        "case_id": runtime["job"]["id"],
        "source_truth_head": SOURCE_TRUTH_HEAD,
        "coverage": {
            "containers": 26,
            "owner_depot_gate_in_observations": sum(i.get("observation_type") == "OWNER_DEPOT_GATE_IN_REPORTED" for i in runtime["observations"]),
            "carrier_notified_off_hire_observations": sum(i.get("observation_type") == "CARRIER_OFF_HIRE_DATE_NOTIFIED" for i in runtime["observations"]),
            "billing_reported_off_hire_observations": sum(i.get("observation_type") == "BILLING_REPORTED_OFF_HIRE" for i in runtime["observations"]),
            "weekly_series_container_coverage": len(runtime["weekly_evidence"][0]["covered_containers"]),
            "individual_candidate_dates": sum(bool(i["selected_candidate_date"]) for i in containers),
            "business_reconciled_individual_dates": sum(i["reconciliation_status"] == "VERIFIED" for i in containers),
        },
        "rows": containers,
    }
    manifest = {
        "manifest_version": "one-n524-contract-manifest-v0.4.1",
        "lineage": LINEAGE,
        "status": "FROZEN_FOR_CODEX8_READ_ONLY_CONSUMPTION",
        "supersedes_manifest_sha256": SUPERSEDES_MANIFEST_SHA256,
        "source_truth_head": SOURCE_TRUTH_HEAD,
        "shared_spine_manifest_sha256": SHARED_SPINE_MANIFEST_SHA256,
        "files": {
            CONTRACT_FILE: digest(contract),
            MATRIX_FILE: digest(matrix),
        },
        "machine_action": "CODEX8_VERIFY_HASHES_THEN_IMPORT_READ_ONLY_WITHOUT_SEMANTIC_PROMOTION",
        "blocking_conditions": ["GOPER_BLOCKED", "GTIME_BLOCKED", "GFIN_BLOCKED"],
        "production_change": False,
        "canonical_change": False,
    }
    validate_bundle(contract, matrix, manifest)
    return contract, matrix, manifest


def validate_bundle(contract: dict, matrix: dict, manifest: dict) -> None:
    _require(contract["authority"] == "DERIVED_READ_ONLY_CANDIDATE", "contract claimed canonical authority")
    _require(len(contract["containers"]) == len(matrix["rows"]) == 26, "matrix coverage changed")
    _require(contract["payments"] == [] and contract["settlements"][0]["status"] == "UNKNOWN",
             "financial truth was promoted")
    _require(all(item["object_type"] != "Event" for item in contract["observations"]),
             "observation promoted to event")
    _require(contract["closure_gate"]["status"] == "BLOCKED", "case was closed")
    _require(manifest["files"][CONTRACT_FILE] == digest(contract),
             "contract hash mismatch")
    _require(manifest["files"][MATRIX_FILE] == digest(matrix),
             "matrix hash mismatch")
    serialized = canonical_bytes((contract, matrix, manifest)).decode()
    _require("/Users/" not in serialized and "private_ledger_ref" not in serialized and
             "source_sha256" not in serialized, "private evidence leaked")


def export_bundle(root: Path, destination: Path) -> dict[str, str]:
    contract, matrix, manifest = build_bundle(root)
    destination.mkdir(parents=True, exist_ok=True)
    values = {
        CONTRACT_FILE: contract,
        MATRIX_FILE: matrix,
        MANIFEST_FILE: manifest,
    }
    for name, value in values.items():
        (destination / name).write_bytes(canonical_bytes(value))
    return {name: hashlib.sha256((destination / name).read_bytes()).hexdigest() for name in values}

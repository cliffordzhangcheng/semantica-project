"""Review Queue Upgrade — P1-4

Status: pending → approved / rejected / needs_revision / superseded
High-risk objects auto-force review: ownership, funding, contract,
payment, legal/compliance, decision, production gate, identity merge/split.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, ".")
from akos_adapter import write_audit, make_context

QUEUE_PATH = Path("review_queue.json")
AUDIT_PATH = Path("audit_log.jsonl")

HIGH_RISK_TYPES = {
    "ownership", "funding", "contract", "payment",
    "legal_compliance", "decision", "production_gate", "identity_merge", "identity_split"
}

HIGH_RISK_CLASSES = {
    "CapitalProvider", "ProjectSPV", "ContainerOwner", "Carrier",
    "ContainerAgent", "Lessee", "Manufacturer", "Operator", "Founder",
    "CapitalCommitment", "PurchaseContract", "LeaseContract", "OneWayContract",
    "PLAContract", "InvoicePayment", "DecisionCard", "PUCMargin",
    "OffHireCondition", "DefaultChain", "MinimumVolume",
}

HIGH_RISK_RELATIONS = {
    "funds", "owns", "commits", "purchased_under", "leased_under",
    "charters_under", "intermediates", "earns", "sells_to",
    "guarantees", "generates", "governs", "subject_to",
}


def create_ticket(
    item_type: str,
    proposed_change: dict,
    risk_level: str,
    reason: str,
    evidence: list = None,
    source: str = "",
    confidence: float = 0.5,
    schema_impact: str = "",
) -> dict:
    """Create a review ticket."""
    ticket = {
        "ticket_id": f"REV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.urandom(3).hex().upper()}",
        "item_type": item_type,
        "risk_level": risk_level,
        "confidence": confidence,
        "reason_for_review": reason,
        "proposed_change": proposed_change,
        "evidence": evidence or [],
        "source": source,
        "schema_impact": schema_impact,
        "status": "pending",
        "reviewer": None,
        "decision": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return ticket


def is_high_risk(item_type: str, item_class: str = "", relation_type: str = "") -> bool:
    """Determine if an item requires mandatory review."""
    if item_type in HIGH_RISK_TYPES:
        return True
    if item_class in HIGH_RISK_CLASSES:
        return True
    if relation_type in HIGH_RISK_RELATIONS:
        return True
    return False


def load_queue() -> list:
    """Load existing review queue."""
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text())
    return []


def save_queue(queue: list):
    """Save review queue."""
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


def add_item(
    item_type: str,
    proposed_change: dict,
    risk_level: str = "medium",
    reason: str = "",
    evidence: list = None,
    source: str = "",
    confidence: float = 0.5,
    schema_impact: str = "",
    item_class: str = "",
    relation_type: str = "",
) -> str:
    """Add item to review queue. Returns ticket_id."""
    queue = load_queue()

    # Auto-force review for high-risk items
    if is_high_risk(item_type, item_class, relation_type):
        risk_level = "high"
        reason = reason or f"Auto-forced review: {item_type} is high-risk"

    ticket = create_ticket(
        item_type=item_type,
        proposed_change=proposed_change,
        risk_level=risk_level,
        reason=reason,
        evidence=evidence,
        source=source,
        confidence=confidence,
        schema_impact=schema_impact,
    )
    queue.append(ticket)
    save_queue(queue)

    # Audit
    ctx = make_context("review-queue", "akos-governance")
    write_audit(
        "review_submit",
        ticket["ticket_id"],
        "pending",
        ctx,
        {"risk_level": risk_level, "item_type": item_type},
    )
    return ticket["ticket_id"]


def approve(ticket_id: str, reviewer: str, notes: str = "") -> bool:
    """Approve a review ticket."""
    queue = load_queue()
    for t in queue:
        if t["ticket_id"] == ticket_id:
            t["status"] = "approved"
            t["reviewer"] = reviewer
            t["decision"] = "approved"
            t["review_notes"] = notes
            t["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue)
            ctx = make_source_context(reviewer)
            write_audit("review_approve", ticket_id, "approved", ctx, {"notes": notes})
            return True
    return False


def reject(ticket_id: str, reviewer: str, reason: str = "") -> bool:
    """Reject a review ticket."""
    queue = load_queue()
    for t in queue:
        if t["ticket_id"] == ticket_id:
            t["status"] = "rejected"
            t["reviewer"] = reviewer
            t["decision"] = "rejected"
            t["review_notes"] = reason
            t["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue)
            ctx = make_source_context(reviewer)
            write_audit("review_reject", ticket_id, "rejected", ctx, {"reason": reason})
            return True
    return False


def needs_revision(ticket_id: str, reviewer: str, notes: str = "") -> bool:
    """Mark ticket as needs revision."""
    queue = load_queue()
    for t in queue:
        if t["ticket_id"] == ticket_id:
            t["status"] = "needs_revision"
            t["reviewer"] = reviewer
            t["decision"] = "needs_revision"
            t["review_notes"] = notes
            t["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue)
            ctx = make_source_context(reviewer)
            write_audit("review_revise", ticket_id, "needs_revision", ctx, {"notes": notes})
            return True
    return False


def supersede(ticket_id: str, superseded_by: str) -> bool:
    """Mark ticket as superseded by another ticket."""
    queue = load_queue()
    for t in queue:
        if t["ticket_id"] == ticket_id:
            t["status"] = "superseded"
            t["superseded_by"] = superseded_by
            t["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue)
            ctx = make_source_context("review-queue")
            write_audit("review_supersede", ticket_id, "superseded", ctx, {"by": superseded_by})
            return True
    return False


def get_stats() -> dict:
    """Get review queue statistics."""
    queue = load_queue()
    stats = {"total": len(queue), "pending": 0, "approved": 0, "rejected": 0,
             "needs_revision": 0, "superseded": 0, "high_risk": 0}
    for t in queue:
        s = t.get("status", "pending")
        stats[s] = stats.get(s, 0) + 1
        if t.get("risk_level") == "high":
            stats["high_risk"] += 1
    return stats


def make_source_context(source: str) -> "AKOSContext":
    return make_context(source, "akos-governance")


if __name__ == "__main__":
    # Auto-populate from graph: high-risk entities need review
    import json as _json
    with open("outputs/06_graph.json") as f:
        g = _json.load(f)

    for n in g.get("nodes", []):
        label = n.get("label", "")
        if label in HIGH_RISK_CLASSES:
            add_item(
                item_type="entity",
                proposed_change={"action": "canonicalize", "entity": n.get("text", ""), "type": label},
                risk_level="high",
                reason=f"Auto-review: {label} is high-risk class",
                source=n.get("source_id", ""),
                confidence=n.get("confidence", 0.5),
                item_class=label,
            )

    for e in g.get("edges", []):
        rel = e.get("type", "")
        if rel in HIGH_RISK_RELATIONS:
            add_item(
                item_type="relation",
                proposed_change={"action": "validate", "relation": rel, "source": e.get("source", ""), "target": e.get("target", "")},
                risk_level="high",
                reason=f"Auto-review: {rel} is high-risk relation",
                source=e.get("source_id", ""),
                confidence=e.get("confidence", 0.5),
                relation_type=rel,
            )

    stats = get_stats()
    print(f"Review Queue: {stats['total']} tickets ({stats['high_risk']} high-risk)")
    print(f"  Status: {stats}")
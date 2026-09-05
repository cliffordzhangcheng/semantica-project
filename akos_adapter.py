"""AKOS Contract Adapter for Semantica — P0 compliance layer.

Implements the 5 P0 gaps from REPORT-20260822:
  1. source_id / intake_id injection
  2. provenance / lineage tracking
  3. tenant isolation
  4. review queue / Founder gate
  5. audit receipt
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

AUDIT_LOG_PATH = Path(os.environ.get("AKOS_AUDIT_LOG", "/var/minis/workspace/semantica-project-clean/audit_log.jsonl"))
REVIEW_QUEUE_PATH = Path(os.environ.get("AKOS_REVIEW_QUEUE", "/var/minis/workspace/semantica-project-clean/review_queue.json"))


@dataclass
class AKOSContext:
    source_id: str
    intake_id: str
    tenant_id: str
    agent_id: str
    work_session_id: str
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    provenance: Dict[str, Any] = field(default_factory=dict)


def make_context(source_id: str, tenant_id: str = "akos-default", agent_id: str = "dsh-web") -> AKOSContext:
    return AKOSContext(
        source_id=source_id,
        intake_id=f"intake-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        agent_id=agent_id,
        work_session_id=f"ws-{uuid.uuid4().hex[:8]}",
        provenance={"created_by": agent_id, "source": source_id},
    )


def inject_metadata(record: Dict[str, Any], ctx: AKOSContext) -> Dict[str, Any]:
    """Inject AKOS contract fields into any Semantica output record."""
    record["source_id"] = ctx.source_id
    record["intake_id"] = ctx.intake_id
    record["tenant_id"] = ctx.tenant_id
    record["agent_id"] = ctx.agent_id
    record["work_session_id"] = ctx.work_session_id
    record["timestamp"] = ctx.timestamp
    record["provenance"] = {
        **ctx.provenance,
        "source_id": ctx.source_id,
        "intake_id": ctx.intake_id,
    }
    return record


def write_audit(action: str, resource: str, verdict: str, ctx: AKOSContext, details: Optional[Dict] = None) -> None:
    """Append an immutable audit receipt."""
    entry = {
        "action": action,
        "resource": resource,
        "verdict": verdict,
        "agent_id": ctx.agent_id,
        "work_session_id": ctx.work_session_id,
        "timestamp": ctx.timestamp,
        "source_id": ctx.source_id,
        "intake_id": ctx.intake_id,
        "details": details or {},
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def submit_for_review(record: Dict[str, Any], ctx: AKOSContext, risk_level: str = "medium") -> str:
    """Submit a proposed action to the review queue. Returns ticket_id."""
    ticket_id = f"REV-{uuid.uuid4().hex[:10].upper()}"
    entry = {
        "ticket_id": ticket_id,
        "risk_level": risk_level,
        "agent_id": ctx.agent_id,
        "work_session_id": ctx.work_session_id,
        "record_summary": {k: record.get(k) for k in ("type", "resource", "action", "description") if k in record},
        "status": "pending",
        "submitted_at": ctx.timestamp,
        "requires_founder_approval": risk_level in ("high", "critical"),
    }
    REVIEW_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if REVIEW_QUEUE_PATH.exists():
        existing = json.loads(REVIEW_QUEUE_PATH.read_text())
    existing.append(entry)
    REVIEW_QUEUE_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    write_audit("submit_for_review", ticket_id, "pending", ctx, {"risk_level": risk_level})
    return ticket_id


def check_tenant_access(tenant_id: str, resource_tenant: str, action: str) -> bool:
    """Tenant isolation check. Returns True if access is granted."""
    if tenant_id != resource_tenant:
        write_audit("tenant_deny", f"{resource_tenant}/{action}", "denied",
                    make_context(resource_tenant, tenant_id, "akos-governance"),
                    {"reason": "tenant_mismatch"})
        return False
    return True
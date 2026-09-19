# PR-0 Baseline Check Report

**Date**: 2026-09-19  
**Author**: OpenMinis  
**Task**: Execute SPR-0 per HANDOFF document

---

## 1. Baseline Verification

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| HEAD commit | 35d2a231b992ca1e23c185ace098ded1640f91b6 | 35d2a231b992ca1e23c185ace098ded1640f91b6 | ✅ |
| Tree | 526a992c... | 526a992c... | ✅ |
| Files | 107 | 107 | ✅ |
| CI workflows | None | None | ✅ |

---

## 2. Findings Reproduced (F02-F09)

### F02: Contract Inconsistency
- `pipeline_compat.py` uses entities/relationships API
- `akos_projection.py` reads nodes/edges format
- **Risk**: Silent desync between pipeline output and projection input

### F03: Projection Hardcoded PASS
- `ner_f1=0.9091` and `re_f1=0.8` hardcoded in akos_projection.py
- `gate_result="PASS"` hardcoded
- Empty input still reports PASS
- **Risk**: Gate result disconnected from actual validation

### F04: Export Failure Not Propagated
- `scripts/06_export.py` catches all exceptions and returns None
- All failures treated as success
- **Risk**: Silent data loss

### F07: UI Hardcoded PASS
- `webui/index.html` shows "Gate: PASS" regardless of actual state
- **Risk**: Misleading status display

### F09: Missing Research Artifacts
- README claims deliverables 02, 05, 06, 08, 09 exist
- Only 4 research notes present
- **Risk**: Documentation-inventory mismatch

---

## 3. Environment

| Component | Version |
|-----------|---------|
| Python | 3.12.14 |
| OS | Linux aarch64 (Android/Alpine via PRoot) |
| git | 2.54.0 |

---

## 4. Deliverables

- `baseline.md` → `/var/minis/workspace/semantica-project-clean/`
- `PR-0-BASELINE-CHECK.md` → this report

---

## 5. Next Steps

Per SPEC §8 batching sequence:

| Batch | Content |
|-------|---------|
| **PR-1** | R01/R02 - Runtime result propagation + Quality gate separation |
| PR-2 | R03/R04 - Contract unification + Evidence validation |
| PR-3 | R05/R06/R07 - Modularization, dependency pinning, CI |
| PR-4 | R08/R09 - Runtime isolation, recovery, UI binding |
| PR-5 | Research asset governance |

Waiting for Founder instruction to proceed with PR-1.

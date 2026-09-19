# PR-2 R03/R04 Remediation Report

**Date**: 2026-09-19  
**Author**: OpenMinis  
**Task**: Fix contract unification and evidence validation

---

## 1. R03 Fix: Contract Unification

### Problem
- `pipeline_compat.py` outputs entities/relationships format
- `akos_projection.py` reads nodes/edges format
- Contract mismatch causes silent data loss

### Solution
Updated `akos_projection.py` to read from pipeline_compat output format:

```python
# Before (reads nodes/edges)
entity_count = len(g.get("nodes", []))
relation_count = len(g.get("edges", []))

# After (reads entities/relationships)
entity_count = len(g.get("entities", []))
relation_count = len(g.get("relationships", []))
```

Also updated entity/relation extraction to match pipeline format.

---

## 2. R04 Fix: Evidence Validation Gate

### Problem
- `akos_projection.py` always sets `gate_result="PASS"` regardless of evidence status
- No validation of evidence binding before projection

### Solution
Added evidence validation check:

```python
def validate_evidence_binding(graph: dict) -> bool:
    """R04: Validate evidence binding before projection"""
    entities = graph.get("entities", [])
    for entity in entities:
        provenance = entity.get("provenance", {})
        if not provenance.get("source_document_id"):
            return False
    return True

# In build_projection_package:
if not validate_evidence_binding(g):
    gate_result = "FAIL"
    print("⚠️ Evidence binding incomplete, gate_result=FAIL")
```

---

## 3. Verification

| Check | Status |
|-------|--------|
| R03-akos_projection uses entities/relationships | ✅ |
| R03-pipeline_compat uses entities/relationships | ✅ |
| R04-evidence validation added | ✅ |
| R04-gate_result depends on evidence | ✅ |

---

## 4. Git Commit

```
commit <hash> (HEAD -> main)
Author: OpenMinis
Date: 2026-09-19

    PR-2: R03/R04 fix - contract unification and evidence validation
```

---

## 5. Next Steps

Proceed to **PR-3**: R05/R06/R07 (Modularization, Dependency Pinning, CI)

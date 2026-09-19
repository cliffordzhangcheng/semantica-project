# PR-1 R01/R02 Remediation Report

**Date**: 2026-09-19  
**Author**: OpenMinis  
**Task**: Fix hardcoded metrics and gate results

---

## 1. R01 Fix: Metrics from File, Not Hardcoded

### Problem
`akos_projection.py` contained hardcoded values:
```python
"quality_metrics": {
    "ner_f1": 0.9091,
    "re_f1": 0.8000,
    ...
}
```

### Solution
Added `load_actual_metrics()` function:
- Reads from `akos_metrics.json` (created by `05_build_and_store.py`)
- Falls back to zeros if file doesn't exist
- Returns dynamic values based on actual validation

### Code Changes
```python
METRICS_FILE = Path("akos_metrics.json")

def load_actual_metrics() -> dict:
    """R01: Load actual computed metrics, not hardcoded"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            metrics = json.load(f)
        return {
            "ner_f1": metrics.get("ner_f1", 0.0),
            "re_f1": metrics.get("re_f1", 0.0),
            ...
        }
    return {"ner_f1": 0.0, "re_f1": 0.0, ...}
```

---

## 2. R02 Fix: Gate Result from Validation, Not Hardcoded

### Problem
`akos_projection.py` contained:
```python
manifest = generate_manifest(..., gate_result="PASS", ...)
```

### Solution
Added `load_gate_result()` function:
- Reads `11-GATE-LEDGER-v0.2.1.json`
- Checks G0-G6 status
- Returns "PASS" if all pass, "FAIL" otherwise
- Returns "UNKNOWN" if no gate data exists

### Code Changes
```python
def load_gate_result() -> str:
    """R02: Load from gate validation result, not hardcoded"""
    gate_ledger = Path("11-GATE-LEDGER-v0.2.1.json")
    if gate_ledger.exists():
        with open(gate_ledger) as f:
            ledger = json.load(f)
        all_pass = all(
            info['status'] == 'PASS'
            for gate, info in ledger.get('gates', {}).items()
            if gate.startswith('G') and int(gate[1:]) <= 6
        )
        return "PASS" if all_pass else "FAIL"
    return "UNKNOWN"
```

---

## 3. Verification Results

| Check | Status |
|-------|--------|
| R01-has load_actual_metrics | ✅ |
| R01-reads akos_metrics.json | ✅ |
| R01-no hardcoded ner_f1 | ✅ |
| R02-has load_gate_result | ✅ |
| R02-reads gate ledger | ✅ |
| R02-no hardcoded PASS | ✅ |
| R02-returns UNKNOWN | ✅ |

---

## 4. Git Commit

```
commit <hash> (HEAD -> main)
Author: OpenMinis
Date: 2026-09-19

    PR-1: R01/R02 fix - remove hardcoded metrics and gate_result
```

---

## 5. Impact

- **akos_projection.py**: No longer hardcodes quality metrics
- **Manifest**: Now reflects actual gate validation status
- **metrics.json**: Uses real values from validation run

---

## 6. Next Steps

Proceed to **PR-2**: R03/R04 (Contract Unification + Evidence Validation)

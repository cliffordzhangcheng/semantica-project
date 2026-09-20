# Semantica Project

**Reality Ontology Engine** - A knowledge graph framework for reality ontology construction and validation.

## Repository Status

This repository is under active remediation. See the [remediation report](SEMANTICA-REMEDIATION-SUMMARY-v1.3.md) for details.

## Current Branch

- **Remediation Branch**: `openminis/semantica-corrective-remediation-v1.3`
- **Status**: 51 tests passing locally

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Run CLI help
python -m semantica_workbench.cli --help

# Run pipeline
python -m semantica_workbench.cli run --run-id <id>
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run gate validation
python -m pytest tests/test_gates.py -v
```

## Project Structure

```
semantica-project/
├── src/semantica_workbench/
│   ├── adapters/          # Legacy format adapters
│   ├── evaluation/        # Gate validation & metrics
│   ├── export/            # Multi-format export (JSON/GraphML/TTL)
│   ├── orchestration/     # Run state & lock management
│   ├── pipeline/          # Pipeline orchestrator
│   ├── projection/        # Canonical projection & metrics
│   ├── schemas/           # JSON schema validators
│   └── webui/             # Web UI (lightweight, no Flask)
├── scripts/               # Shell script compatibility layer
├── tests/                 # Test suite (51 tests)
│   ├── test_gates.py      # T01-T18 gate validation tests
│   ├── test_schema.py     # Schema validation tests
│   ├── test_evidence.py   # Evidence validation tests
│   ├── test_export.py     # Export tests
│   └── test_webui.py      # WebUI tests
└── .github/workflows/
    └── validation.yml     # CI workflow
```

## Validation Gates (G0-G6)

| Gate | Description | Status |
|------|-------------|--------|
| G0 | Corpus integrity | ✅ |
| G1 | Vocabulary completeness | ✅ |
| G2 | Evidence validity | ✅ |
| G3 | Projection admission | ✅ |
| G4 | Hash consistency | ✅ |
| G5 | Test coverage | ✅ |
| G6 | Artifact integrity | ✅ |

## Test Coverage

```
51 passed, 3 warnings
```

### Gate Tests (T01-T18)
- T01: Empty corpus validation
- T02: Sparse vocabulary detection
- T03: Empty ledger validation
- T04: Partial ledger validation
- T05: Projection admission
- T06: Legacy adapter conversion
- T07: Evidence validation
- T08: Schema validation
- T09: Export failure handling
- T10: Metrics producer
- T11: Hash consistency
- T12: Report commit consistency
- T13: WebUI status display
- T14: Export readback with special characters
- T15: Asset integrity check
- T16: Concurrent run locking
- T17: Run resume
- T18: Artifact corruption detection

## Remediation History

### v1.3 (2026-09-20) - Final State
✅ All P0-P1 remediation items complete
✅ 51 tests passing
✅ Real implementations (no placeholder text)
✅ Gate engine strict failure mode
✅ Canonical schema consistency
✅ Multi-format export with failure handling

### Key Fixes
1. Removed all `[CONTEXT OFFLOADED]` placeholder text
2. Restored real implementations for orchestrator, legacy_adapter, evidence_validator
3. Fixed shell script syntax
4. Implemented complete test suite (T01-T18)
5. Fixed schema validator (metadata made optional)
6. Added proper error handling for exports
7. Implemented LockManager for run isolation
8. Created WebUI without Flask dependency
9. Updated .gitignore to exclude build artifacts

## GitHub Actions

The CI workflow runs on push to any branch. Due to API permission limitations, detailed logs require repository admin access.

**Local verification**:
```bash
git clone https://github.com/cliffordzhangcheng/semantica-project.git
cd semantica-project
git checkout openminis/semantica-corrective-remediation-v1.3
python -m pytest tests/ -v
```

## References

- [Remediation Specification v1.3](SPEC-20260920-SEMANTICA-OPENMINIS-CORRECTIVE-REMEDIATION-v1.3.md)
- [Remediation Summary](SEMANTICA-REMEDIATION-SUMMARY-v1.3.md)

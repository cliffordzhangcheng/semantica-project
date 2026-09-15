# AKOS Semantica Ingestion Package

**Version:** v0.1  
**Created:** 2026-09-15  
**Status:** `INGESTION_READY` (conditional)

## Overview

This package contains structured assets for AKOS to ingest logistics ontology data from email corpora.

## Files

| File | Description |
|------|-------------|
| `corpus_register.json` | Source inventory with provenance metadata |
| `entities.jsonl` | 67 entity candidates with confidence and ambiguity notes |
| `relations.jsonl` | 157 relation candidates with evidence refs |
| `provenance_map.yaml` | AKOS-compatible provenance schema v1.0 |
| `pattern_catalog.json` | 8 reusable interaction patterns assessed |
| `gap_matrix.json` | 7 capability gaps with adoption recommendations |

## Corpus Summary

- **Total emails:** 80 (COSW-001: 50, CNTR-001: 30)
- **Total entities:** 67 (6 ShippingLines, 12 Ports, 7 ContainerTypes, 10 Persons, 8 Organizations, 24 BusinessTerms)
- **Total relations:** 157 (85 direct extractions + 72 inferred)
- **Provenance coverage:** 100%

## Acceptance Criteria Status

| Criteria | Status | Notes |
|----------|--------|-------|
| >= 20 evidence-grounded entity candidates | ✅ PASS | 67 entities |
| >= 30 relation candidates | ✅ PASS | 157 relations |
| 100% relation candidates contain provenance refs | ✅ PASS | All have evidence |
| Ambiguity and UNKNOWN explicitly represented | ✅ PASS | Field present in entities |
| At least 5 reusable interaction patterns | ✅ PASS | 8 patterns assessed |

## AKOS Integration Path

1. **Immediate:** Import `entities.jsonl` and `relations.jsonl` into AKOS ontology
2. **Short-term:** Implement `provenance_map.yaml` schema for audit trail
3. **Medium-term:** Port P001-P004, P006 interaction patterns to AKOS portal
4. **Long-term:** Build automated email ingestion pipeline

## Quality Rules Applied

- ✅ Provenance first - every entity/relation traces to source email
- ✅ UNKNOWN explicit - ambiguity field populated where relevant
- ✅ No invented relationships - all from corpus or explicitly marked as inferred
- ✅ Candidate != canonical - promotion_recommendation set to 'candidate'
- ✅ Visualization quality does not substitute for semantic correctness

## Next Actions

- [ ] Review entity candidates with domain experts
- [ ] Promote high-confidence entities to AKOS canonical list
- [ ] Implement provenance schema in AKOS compliance module
- [ ] Integrate email ingestion pipeline

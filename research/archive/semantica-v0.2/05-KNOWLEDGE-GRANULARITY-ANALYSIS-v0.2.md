# Knowledge Granularity Analysis v0.2

**Date:** 2026-09-17 14:49:34
**Baseline:** semantica-report-20260917-yiboke.md

## Entity Granularity Assessment

| Entity Category | v0.1 Count | v0.2 Count | Change | Granularity |
|----------------|------------|------------|--------|-------------|
| Shipper (canonical) | 2 | 1 | -1 | HIGH |
| Consignee (canonical) | 2 | 1 | -1 | HIGH |
| Forwarder (canonical) | 1 | 1 | 0 | HIGH |
| Route-specific | 6 | 6 | 0 | HIGH |
| Amount (individual) | 43 | 6 | -37 | MEDIUM |
| Weight (individual) | 77 | 6 | -71 | MEDIUM |

## Missing Granularity

### Required but Missing
1. **Carrier Name**: Missing from all 6 shipments
2. **Flight Numbers**: Not available in corpus
3. **Actual Weight**: Only quoted/estimated weights
4. **Actual Value**: No invoice amounts extracted
5. **Booking Reference**: Not captured
6. **MAWB Number**: Not captured
7. **HAWB Number**: Not captured
8. **Commodity Code**: HS codes not extracted
9. **Cargo Dimensions**: Length/width/height missing
10. **Package Count**: Not granularly captured

### Optional but Recommended
1. **Currency Codes**: ISO 4217 standard
2. **Time Zones**: For timeline accuracy
3. **Warehouse Codes**: For storage tracking
4. **Agent Contact Details**: Phone/email
5. **Customs Broker**: If applicable

## Fill Plan

| Gap | Fill Method | Priority | Effort |
|-----|-------------|----------|--------|
| Carrier Name | Email text search | HIGH | Low |
| Flight Numbers | Extract from emails | HIGH | Low |
| Actual Weight | PDF OCR search | HIGH | Medium |
| Booking Reference | Subject line parsing | MEDIUM | Low |
| MAWB Number | MAWB document scan | MEDIUM | Medium |

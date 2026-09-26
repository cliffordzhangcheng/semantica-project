# Golden Case 001 — Local Evidence Recovery Correction

Canonical task: GitHub Issue #7 / PR #8
Reviewed: 2026-09-26
Scope: corrected archive coverage and subsequent admission of scoped assertions.

## Finding

The authorized local exports do contain receipt correspondence, billing
documents and later operational evidence. The previous scan omitted a second
archive and searched raw encoded mail. The previous blanket absence claims
and request for replacement uploads are withdrawn.

## Reproducible private inventory

The private `N524-rescan-20260926` ledger contains `index.json`,
`supplement.json`, and `reconciliation.json`, plus decoded derivatives.
Exact source paths, original SHA-256 values, MIME part indices, worksheet rows,
support strength and limitations remain private. The rescan and supplementary
scripts are stored beside the private ledgers, outside the public repository.

| Measure | Result |
|---|---|
| Exported EML file copies | 1,159 across two authorized roots |
| Byte-distinct messages decoded | 712 |
| Directly matching messages | 121 |
| Loose XLSX/XLSM/PDF files inspected | 45; 25 matched |
| Direct matched message dates | 2026-01-12 through 2026-09-02 |
| Distinct relevant weekly attachment hashes | 25, W07–W29 |
| Relevant weekly rows / container identities | 435 / 26 |
| Additional formats | Four XLS read; TXT/DOCX read; ZIP members inventoried |
| Remaining extraction limits | Images/image-only PDFs not exhaustively OCRed; binary DOC unsupported |

Counts describe inventory, not independent facts or admissible events. Quoted
email history is not another independent confirmation. Repeated weekly rows
are observations; removal from a later weekly report is not an off-hire event.
Zero parser exceptions do not establish complete visual-content extraction.

## Recovered evidence and admission boundary

| Private alias | Finding | Boundary |
|---|---|---|
| `SRC-N524-RECEIPT-REPORTED-20260820` | Customer statement reporting bank receipt in a combined N524/N617 payment thread | Receipt assertion is present. Job allocation and bank value date remain unresolved; the full receipt cannot be assigned to N524. |
| `SRC-N524-SPLIT-PI-20260820` | Separate repair and per-diem PIs reconcile numerically to the balance requested in the receipt email and the revised debit note | Billed/requested balance at that source date, not an independently verified current balance or proof of settlement. |
| `SRC-N524-BILLING-OFFHIRE-DATES` | Five identified containers have explicit off-hire dates in billing remarks; quoted customer correspondence corroborates the last four units' return date | Billing/customer assertion, not depot EIR. Does not supply 26 independent off-hire timestamps. |
| `SRC-N524-DN-VERSION-CONFLICT` | Same debit-note reference has differing totals in two local versions | Preserve both hashes and revision context; do not double count or choose by basename. |
| `SRC-N524-PAYABLE-BOOKED-20260902` | Carrier reply and screenshot show payable booking and due-date information | Booking is not payment. Preserve the prose/image year discrepancy. |

## Reconciliation still required

- The combined reported receipt differs from the sum of the two job PIs. An
  assumed bank fee is not evidence of allocation.
- A per-diem PI has inconsistent numeric and written totals; charging-period
  descriptions and earlier debit-note versions also differ.
- Operational snapshots, billing assertions and lot-level completion must be
  reconciled at their respective scopes, retaining source-specific dates.
- The Phase B runtime now retains recovered receipt, billing and operational
  assertions. Its financial state is `RECONCILIATION_REQUIRED`; no current
  receivable or settlement is inferred from the historical statements.

The initial correction updated reports; the subsequent Phase B implementation
admits these scoped assertions. Neither stage claims a Golden Case pass,
merges PR #8, or modifies production. Raw confidential
sources and monetary reconciliation details remain in the private ledger.
Reconciliation remains in progress. One optional Founder clarification asks
whether the combined receipt settles the two base PIs and whether the difference
is a bank fee. Pending a reply, allocation remains unknown. No new upload
is requested, and unrelated implementation work can continue.

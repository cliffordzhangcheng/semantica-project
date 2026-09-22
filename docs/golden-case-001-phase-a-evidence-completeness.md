# Golden Case 001 — Phase A evidence completeness

Canonical task: GitHub Issue #7  
Case: ONE-N524 / ONE524SGH  
Status: evidence recovery in progress; this report records the completed first
full inventory pass and its gaps.

## Scope and scan method

The authorised local One-Way archive was scanned recursively without a result
limit. The scan covered 535 EML files and all 36 files in the ONE-N524 case
folder. It searched the job aliases, booking and purchase-order aliases,
redelivery reference, invoice/debit-note aliases, and the complete 26-container
set extracted from the case spreadsheets. No unreadable file was encountered in
this pass. Email results were not limited to a first page or sampled subset.

The private evidence ledger holds exact source paths, hashes, message IDs and
sensitive locators. This public report deliberately uses aliases only.

## Coverage ledger

| Evidence family | Alias | Coverage | Result |
|---|---|---|---|
| Framework agreement | `SRC-MASTER-TEMPLATE-2022` | 4-page confidential template located and hashed | Not an executed/signed agreement: placeholders remain. It cannot establish job-specific or executed master-agreement facts. |
| Job formation / release | `SRC-N524-PICKUP-NOTICE` | Direct job-alias email located | Present; attachment exists and is held only in the private ledger. |
| Lot and container identity | `SRC-N524-PI-20260409` | 26/26 unit rows | Present. The PI and tracing sheet independently enumerate the same 26 canonical numbers. |
| Operational tracing | `SRC-N524-CONTAINER-TRACING` | 26/26 rows | Present; event/date fields require per-row extraction before admission. |
| Owner gate-in snapshot | `SRC-N524-OWNER-GATEIN` | 26/26 rows | Present; gate-in is not off-hire. |
| Redelivery authorisation | `SRC-N524-ERI` | Lot-level reference | Present. |
| Off-hire correspondence | `SRC-N524-OFFHIRE-MAILS` | 8 direct archive messages; 13 distinct unit references | Partial: messages are evidence of correspondence and identified-unit status, not a complete 26-unit off-hire proof. |
| Debit notes / obligations | `SRC-N524-DN-202605`, `SRC-N524-DN-202608` | 3 and 4 named-unit rows respectively | Present for identified charges; does not prove payment or settlement. |
| Damage / repair | `SRC-N524-DAMAGE-3666`, `SRC-N524-DAMAGE-3671` | Estimates plus image package | Present, subject to later charge-to-obligation linkage. |
| Payments / allocation | `SRC-N524-PAYMENT` | No case-specific payment allocation found in this pass | Gap. No payment, `SETTLED`, or `CLOSED` fact may be asserted. |

## Completeness results

- **Container identity:** 26/26 accounted for in three independent case files.
- **Email pagination:** complete recursive scan of 535 local messages; no
  search-limit-based absence assertion was made.
- **Attachment coverage:** attachments are recorded in the private ledger; raw
  attachments and confidential originals are not stored in Git.
- **Date coverage:** direct N524 evidence spans job/pick-up correspondence in
  January 2026 through the latest debit-note materials in August 2026.
- **Master Agreement:** the located file is a confidential unsigned template,
  not the signed agreement required by `GMASTER`.

## Blocking gaps for Phase B admission

1. The signed/effective Master Agreement, or an authorised executed equivalent,
   with a safe private alias and page/clause lineage.
2. Source-grounded per-container off-hire/return evidence for the units not
   supported by a primary event record.
3. Case-specific payment or allocation evidence before any financial settlement
   state can be modeled.
4. A reconciled mapping from damage estimates and debit-note lines to the
   affected obligation(s), where the charge is to be admitted.

No schema, runtime, or UI facts have been changed by Phase A. In particular,
`GATE_IN` has not been promoted to `OFF_HIRE`, and operational completion is
not treated as financial settlement.

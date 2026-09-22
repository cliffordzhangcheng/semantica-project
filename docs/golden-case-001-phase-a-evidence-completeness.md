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
| Framework agreement | `SRC-MASTER-PHOTOCOPY-2022` | Founder confirms the confidential photocopy is signed and stamped | The first located filename contains `Template`; its visual signing page does not display the marks. It is therefore not yet bound to the Founder-confirmed photocopy hash. This is a source-identity reconciliation item, not a conclusion that the agreement is unsigned. |
| Job formation / release | `SRC-N524-PICKUP-NOTICE` | Direct job-alias email located | Present; attachment exists and is held only in the private ledger. |
| Lot and container identity | `SRC-N524-PI-20260409` | 26/26 unit rows | Present. The PI and tracing sheet independently enumerate the same 26 canonical numbers. |
| Operational tracing | `SRC-N524-CONTAINER-TRACING` | 26/26 rows | Present; event/date fields require per-row extraction before admission. |
| Owner gate-in snapshot | `SRC-N524-OWNER-GATEIN` | 26/26 rows | Present; gate-in is not off-hire. |
| Redelivery authorisation | `SRC-N524-ERI` | Lot-level reference | Present. |
| Owner weekly movement reports | `SRC-N524-WEEKLY-REPORTS` | 15 spreadsheet attachments across W07–W18; every report attachment was unpacked and searched | Present. The reports provide owner movement/status updates over the lifecycle. One non-readable spreadsheet attachment is recorded in the private ledger. |
| Off-hire correspondence | `SRC-N524-OFFHIRE-MAILS` | 8 direct archive messages; 13 distinct unit references | Present as written owner/customer confirmation context. Together with weekly owner reports and any Maersk tracking result, it is the accepted evidence channel; a paper EIR is not required by this case model. |
| Debit notes / obligations | `SRC-N524-DN-202605`, `SRC-N524-DN-202608` | 3 and 4 named-unit rows respectively | Present for identified charges; does not prove payment or settlement. |
| Damage / repair | `SRC-N524-DAMAGE-3666`, `SRC-N524-DAMAGE-3671` | Estimates plus image package | Present, subject to later charge-to-obligation linkage. |
| Payments / allocation | `SRC-N524-PAYMENT` | No case-specific payment allocation found in this pass | Gap. No payment, `SETTLED`, or `CLOSED` fact may be asserted. |

## Completeness results

- **Container identity:** 26/26 accounted for in three independent case files.
- **Email pagination:** complete recursive scan of 535 local messages; no
  search-limit-based absence assertion was made.
- **Weekly-report attachment scan:** all spreadsheet attachments in the same
  archive were unpacked and searched against all 26 identifiers. Fifteen
  reports matched, spanning W07 through W18.
- **Attachment coverage:** attachments are recorded in the private ledger; raw
  attachments and confidential originals are not stored in Git.
- **Date coverage:** direct N524 evidence spans job/pick-up correspondence in
  January 2026 through the latest debit-note materials in August 2026.
- **Master Agreement:** Founder confirms the governing photocopy is signed and
  stamped. The exact locally named file/hash still needs reconciliation before
  `GMASTER` can bind the agreement to its source alias.

## Blocking gaps for Phase B admission

1. Reconcile the signed/stamped photocopy identified by Founder with a private
   source alias, hash and page/clause lineage.
2. Extract each weekly report's per-container status chronology, and supplement
   it with the authorised Maersk tracking results where weekly records leave a
   lifecycle ambiguity.
3. Case-specific payment or allocation evidence before any financial settlement
   state can be modeled.
4. A reconciled mapping from damage estimates and debit-note lines to the
   affected obligation(s), where the charge is to be admitted.

No schema, runtime, or UI facts have been changed by Phase A. In particular,
`GATE_IN` has not been promoted to `OFF_HIRE`, and operational completion is
not treated as financial settlement.

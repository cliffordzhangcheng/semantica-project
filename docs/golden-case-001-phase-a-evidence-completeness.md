# Golden Case 001 — Phase A evidence completeness

Canonical task: GitHub Issue #7  
Case: ONE-N524 / ONE524SGH  
Status: local evidence recovered; source reconciliation remains in progress.
Corrected 2026-09-26 after expanding the archive and decoding MIME content.

## Scope and scan method

The earlier 535-message inventory covered only one archive subtree and searched
raw email bytes. It omitted the separate exported email archive and could miss
encoded bodies and attachments. Its description as a full evidence pass and
its payment/off-hire absence conclusions are withdrawn.

The corrected recursive inventory covers both authorized archive roots: 1,159
EML file copies, 712 byte-distinct messages, and 45 loose spreadsheets/PDFs.
All messages were MIME-decoded, including plain-text and HTML bodies; all
XLSX/XLSM/PDF attachments were attempted. A supplementary pass read the four
legacy XLS attachments, TXT and DOCX content and inventoried ZIP members.
Searches used job, booking, redelivery and billing aliases and all 26 container
numbers without a result cap. There are 121 directly matching messages and 25
matching loose files. These are candidate evidence counts, not event counts.

No parser exceptions were recorded in these passes. This does not mean all
content is readable: images and image-only PDF pages have not been exhaustively
OCRed, and one binary DOC remains unsupported. The 381 unusual-extension
attachments were identified by file signatures as PNG/JPEG/GIF images.
Selected agreement images and the payment-booking screenshot were visually
reviewed. Text-search absence must not imply evidence absence.

The private evidence ledger holds exact source paths, hashes, message IDs and
sensitive locators. This public report deliberately uses aliases only.

## Coverage ledger

| Evidence family | Alias | Coverage | Result |
|---|---|---|---|
| Framework agreement | `SRC-MASTER-AGREEMENT-20230327` | Email chain plus four confidential image pages | Present. The Owner signing block on page 3 is visually confirmed as signed and stamped. The agreement's stated effective date is separately recorded; the parent email's 2023-03-27 transmission date is not treated as a signature date. The supplied photocopy does not visibly show a Maersk counter-signature; the email chain supplies the revised-agreement and transmission context. |
| Job formation / release | `SRC-N524-PICKUP-NOTICE` | Direct job-alias email located | Present; attachment exists and is held only in the private ledger. |
| Lot and container identity | `SRC-N524-PI-20260409` | 26/26 unit rows | Present. The PI and tracing sheet independently enumerate the same 26 canonical numbers. |
| Operational tracing | `SRC-N524-CONTAINER-TRACING` | 26/26 rows | Present; event/date fields require per-row extraction before admission. |
| Owner gate-in snapshot | `SRC-N524-OWNER-GATEIN` | 26 listed rows; 20 dated gate-in entries and 6 blank entries | Present, with six per-container date gaps. Gate-in is not off-hire. |
| Redelivery authorisation | `SRC-N524-ERI` | Lot-level reference | Present. |
| Owner weekly movement reports | `SRC-N524-WEEKLY-REPORTS` | 25 byte-distinct spreadsheet attachments across W07–W29; 435 matching rows across all 26 units | Present. Snapshots preserve sheet/row and parent-message lineage. Disappearance from a later report is not an off-hire event. |
| Off-hire correspondence and billing dates | `SRC-N524-OFFHIRE-MAILS`, `SRC-N524-BILLING-OFFHIRE-DATES` | Billing remarks name five units and their off-hire dates; a quoted customer email corroborates the last four units' return date | Present as billing/customer assertions, not depot EIRs. Written confirmations are an accepted evidence channel; paper EIRs are not required. Per-container runtime admission still requires scoped reconciliation. |
| Debit notes / obligations | `SRC-N524-DN-202605`, `SRC-N524-DN-202608` | Original and revised charge documents, including conflicting versions | Present for identified charges; version reconciliation is required before balances are derived. Does not prove payment or settlement. |
| Damage / repair | `SRC-N524-DAMAGE-3666`, `SRC-N524-DAMAGE-3671` | Estimates plus image package | Present, subject to later charge-to-obligation linkage. |
| Receipt / allocation | `SRC-N524-RECEIPT-REPORTED-20260820` | Customer-reported bank receipt in the combined N524/N617 thread | Present. Record the receipt assertion; do not assign the entire combined receipt to N524 or invent a bank value date. Allocation remains unresolved. |
| Revised billing / payable booking | `SRC-N524-SPLIT-PI-20260820`, `SRC-N524-PAYABLE-BOOKED-20260902` | Split repair/per-diem PIs, debit note and carrier booking reply | Present. A booked payable is not proof of payment. Document versions and conflicting fields require reconciliation. |

## Completeness results

- **Container identity:** 26/26 accounted for in three independent case files.
- **Tracing coverage:** the case tracing sheet contains a dated loading entry
  for 26/26 containers, a dated gate-out entry for 22/26, and a dated gate-in
  entry for 12/26. These are source observations pending reconciliation with
  the weekly-report layer.
- **Earlier cross-source alignment:** all 12 dated tracing gate-in observations have a
  same-type, same-date weekly-report counterpart. The corresponding counts are
  2/22 for gate-out and 1/26 for loading, so those two event types remain
  explicitly unresolved rather than being silently selected from one source.
  These counts describe the old comparison; the expanded weekly set has not
  yet been reconciled into a replacement lifecycle timeline.
- **Email pagination:** both local archive trees fully enumerated; 712
  byte-distinct messages decoded. No first-page or result-limit sampling.
- **Weekly-report attachment scan:** 25 unique matching attachment hashes,
  spanning W07 through W29. Forwarded copies are linked to the same attachment
  rather than counted as additional observations.
- **Per-container normalization:** the matching reports yielded 390 source
  observations in the old pass. The corrected, attachment-deduplicated pass
  contains 435 rows across 26/26 containers; the counts must not be added.
  They are retained as dated source
  snapshots in the private ledger. Repeated or non-monotonic snapshots are not
  silently converted into a single lifecycle sequence; they require event-level
  reconciliation before runtime admission.
- **Owner gate-in coverage:** 20/26 containers have a dated owner gate-in
  entry; the other six remain explicit per-container gaps. These entries are
  retained as gate-in observations only.
- **Attachment coverage:** attachments are recorded in the private ledger; raw
  attachments and confidential originals are not stored in Git.
- **Date coverage:** direct N524 evidence spans job/pick-up correspondence in
  January 12, 2026 through a carrier payment-booking reply on September 2,
  2026. The separately reviewed 2023 Master Agreement retains its own lineage.
- **Master Agreement:** the governing confidential photocopy is now bound in
  the private ledger to its parent email and all four attachment hashes. Its
  Owner signature/stamp are visually confirmed. A private semantic rule registry
  now preserves clause/page lineage; counterparty execution is modeled only to
  the strength shown by the supplied copy and email chain.

## Reconciliation work before runtime admission

1. Reconcile each container's expanded weekly snapshots and the recovered
   off-hire assertions, preserving source strength. A billing assertion must
   not become a depot-confirmed event, nor a five-unit fact a 26-unit fact.
2. Bind the reported receipt separately from job/invoice allocation. The
   combined receipt and the two job PI totals differ; do not silently infer a
   bank fee, settlement, or allocation. A source report date is not a value date.
3. A reconciled mapping from damage estimates and debit-note lines to the
   affected obligation(s), where the charge is to be admitted.
4. Resolve same-reference debit-note versions, numerical versus written totals,
   charging-period descriptions, and the carrier reply's year discrepancy.
   Keep historical and revised documents distinct; do not double count them.

These are agent reconciliation tasks using already supplied local materials.
The previous request for the Founder to resupply evidence is withdrawn pending
this work. See `golden-case-001-local-evidence-recovery.md`. The current runtime
has not yet admitted these recovered facts; its earlier empty payment list is
not a finding that the archive contains no receipt evidence.

No schema, runtime, or UI facts have been changed by Phase A. In particular,
`GATE_IN` has not been promoted to `OFF_HIRE`, and operational completion is
not treated as financial settlement.

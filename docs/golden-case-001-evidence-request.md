# Golden Case 001 — Evidence Request

## Purpose

This request completes the remaining Phase A evidence gaps for job `ONE-N524`.
It does **not** request paper EIRs. For this case, a written Owner confirmation
(email or WeChat), a Maersk tracking result, or a later Owner weekly report is a
valid operational evidence channel when it identifies the container and the
relevant event.

## Evidence already bound

- Stable job and equipment-lot identity: 26 containers, independently listed
  by case materials.
- Job formation/pick-up notice, tracing sheet, Owner gate-in snapshot, and 15
  Owner weekly reports.
- Owner-signed framework-agreement copy, held in the private ledger only.
- PI/invoice/debit-note and selected damage materials.

## Required to admit per-container off-hire events

The current source set supports lot-level Founder confirmation that all 26
containers were off-hired by 2026-07-16. It does not yet bind a primary,
per-container written confirmation for that result. Supply **one** of the
following complete evidence sets for all 26 containers:

1. Maersk tracking history or export for each container; or
2. Owner email/WeChat confirmation that names the containers and their
   off-hire/return dates; or
3. Later Owner weekly reports that identify the return/off-hire event and date
   for each container.

The material must preserve these fields:

| Field | Required |
|---|---|
| Container number | Yes |
| Event meaning (`EMPTY_RETURN`, Owner gate-in, off-hire, or equivalent) | Yes |
| Event date/time as supplied | Yes |
| Location/depot when supplied | Yes |
| Source date and source identity | Yes |
| Owner/Carrier confirmation context | Yes |

Addresses, phone numbers, account data, signatures, full message chains, and
unrelated container rows may be redacted. Do not redact container number,
event/date, the relevant location, or the source/date needed to establish
lineage.

## Required to reconcile operational timestamps

The tracing sheet and weekly-report snapshots agree exactly for all 12 dated
gate-in observations. Gate-out and loading dates need an authoritative history
or source explanation before they are represented as one reconciled event
timeline. A Maersk history export covering the 26 containers is the preferred
single source because it can resolve both this discrepancy and final off-hire
status.

## Required before financial settlement may be asserted

The existing PI, invoice, and debit-note materials establish obligations, not
payment allocation. For every payment to be modeled as allocated to `ONE-N524`,
provide a remittance advice, bank confirmation, payment email, or other
case-specific allocation record with:

| Field | Required |
|---|---|
| Payment reference | Yes |
| Value date | Yes |
| Currency and amount | Yes |
| Payer/payee role | Yes |
| Invoice/debit-note reference and allocation | Yes |

Bank account numbers, unrelated transactions, and non-case-specific payment
details may be redacted. If no such allocation exists, the model will retain
the obligation as outstanding and will not assert `SETTLED` or `CLOSED`.

## Optional supporting evidence

- A countersigned framework-agreement copy, if one exists, to strengthen
  counterparty execution lineage.
- Repair settlement, waiver, dispute, or adjustment records for the identified
  damage/debit-note items.
- A later written reconciliation of the six blank Owner gate-in entries.

## Admission rules

No supplied record will be converted into an event merely because it is a
narrative summary. Every admitted event retains its source alias, file/message
hash, exact private locator, support strength, and sensitivity classification
in the private ledger. Raw confidential evidence remains outside Git.

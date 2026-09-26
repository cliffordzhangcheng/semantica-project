# Golden Case 001 — Phase B Runtime Checkpoint

Canonical task: GitHub Issue #7 / PR #8. Updated 2026-09-26.

## Current runtime result

Recovered source assertions are now admitted to the canonical artifact with
source hashes, exact redacted locators, support strength and private-ledger
references. Admission of an assertion does not resolve its business ambiguity.

```text
operational status = OFF_HIRE_CONFIRMED_LOT_SCOPE
financial status   = RECONCILIATION_REQUIRED
case status        = OPEN
runtime status     = BLOCKED
```

The previous blanket `OUTSTANDING` label has been removed. Runtime now retains:

- One creditor-reported receipt in the combined N524/N617 thread, with unknown
  bank value date and no invoice/job allocations. The report date is used only
  for a `RECEIPT_REPORTED` event, not as the date money entered the bank.
- Two proforma invoices for different charge categories. Alternative debit-note
  versions remain reconciliation issues rather than additional obligations.
- A creditor balance claim scoped to its source date, explicitly not a verified
  current receivable, and a separate carrier payable-booking assertion.
- Five per-container billing assertions of off-hire dates. These retain their
  exact worksheet rows and source strength; they do not become depot-confirmed
  events or create dates for the remaining 21 containers.
- Visible allocation, billing-version, numerical/written total, charging-period
  and source-date discrepancies. No financial closure is inferred.

The graph links the job to its lot, containers, obligations and invoices. A
receipt is linked by `mentioned_in_receipt`, never `paid_by`; N617 remains an
external thread reference and is not admitted as a second Golden Case.

## Gate result

| Gate | Result | Meaning |
|---|---|---|
| GMASTER | PASS | Existing Master Agreement hierarchy checks retained. |
| GJOB | PASS | N524 remains bound to the Master Agreement. |
| G26 | PASS | All 26 canonical container identities remain present. |
| GOPER | BLOCKED | Billing assertions are retained; full lifecycle reconciliation is incomplete. |
| GFIN | BLOCKED | Reported receipt allocation and billing differences remain unresolved. |
| GOBL | PASS | All three obligation categories remain visible as requiring reconciliation. |
| GEVID | PASS | Projection agrees with reviewed redacted inputs; confidential-original authentication requires the private admission check. |
| GTIME | BLOCKED | Weekly/tracing lifecycle reconciliation remains incomplete. |
| GCLOSE | PASS | OPEN is retained; this is a closure-integrity check, not a CLOSED assertion. |

## Verification boundary

`golden-case` renders the current artifact. Its exit status detects FAIL;
BLOCKED is not a completed Golden Case. A passing general CI run does not turn
GOPER/GFIN/GTIME into PASS or approve the case for Founder G7.

Canonical hashes now cover payments, billing documents, source assertions,
reconciliation issues and the evidence ledger in addition to entities, events,
transitions, timeline and graph. They are exposed even when business status is
BLOCKED and compared across independent rebuilds.

The private admission check verifies original file/attachment SHA-256 values,
invoice dates and totals, exact container/remarks rows and the receipt statement.
It does not independently establish bank settlement or resolve conflicting
business statements. Raw sources remain outside Git.

Remaining work includes source reconciliation, complete operational modeling,
and the interactive UI required by Issue #7. No merge or production change.

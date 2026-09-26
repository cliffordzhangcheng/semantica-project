# Golden Case 001 — Evidence Request Status

Canonical task: GitHub Issue #7
Updated: 2026-09-26
Status: **WITHDRAWN_PENDING_LOCAL_RECONCILIATION**

The earlier request to resupply off-hire and payment evidence was premature.
The corrected local scan recovered later weekly reports, explicit billing
off-hire dates, a customer-reported receipt in the N524/N617 thread, revised
PIs/debit notes, and a carrier payable-booking reply. See
`golden-case-001-local-evidence-recovery.md` and the corrected completeness
report. No new Founder upload/export is requested. One optional clarification on the
combined receipt and its difference from the two base PIs is pending; the model
retains unknown allocation while work continues.

## Work to complete using existing sources

- Reconcile all 26 container histories across weekly, tracing and written
  confirmations. Preserve billing/customer assertions as such; do not require
  paper EIRs or manufacture off-hire from gate-in or disappearance from a report.
- Trace the combined receipt to job/invoice allocation and retain an unknown
  bank value date where the evidence supplies only the date of the statement.
- Reconcile revised billing versions and conflicting totals/date descriptions;
  do not count a debit note and its replacement PI as separate charges.
- Admit reviewed facts into runtime with hashes and exact private locators.
  Do not equate a booked invoice or planned payment with a completed payment.

## If a genuine residual gap remains

Only after the existing source reconciliation, produce one consolidated request
identifying the unresolved fact, sources already inspected, the minimum field
needed, and why it cannot be established locally. Preserve case/container or
invoice identifiers, the stated event/date, source identity and allocation
scope. Unrelated transactions, contacts, addresses, account numbers and
signatures may remain redacted. Confidential originals remain outside Git.

The lack of a reviewed allocation does not establish that nothing was paid.
No `SETTLED` or `CLOSED` state may be asserted from the combined receipt alone.

# Golden Case 001 — Phase B Runtime Checkpoint

## Current runtime result

`ONE-N524` now rebuilds as a separate canonical runtime artifact. It models the
Master Agreement, the job, the 26-container equipment lot, individual container
identities, source-bound events, financial obligations, and a redacted evidence
ledger.

The runtime result is deliberately:

```text
operational status = OFF_HIRE_CONFIRMED_LOT_SCOPE
financial status   = OUTSTANDING
case status        = OPEN
runtime status     = BLOCKED
```

The lot-level off-hire confirmation does not create 26 individual off-hire
timestamps. No payment allocation is present, so no obligation is `SETTLED` and
the case cannot be `CLOSED`.

## Gate result

| Gate | Result | Meaning |
|---|---|---|
| GMASTER | PASS | Master Agreement hierarchy and rule lineage are bound. |
| GJOB | PASS | `ONE-N524` is bound to the Master Agreement. |
| G26 | PASS | 26 unique canonical container identities are present. |
| GOPER | BLOCKED | Per-container primary off-hire confirmation is not bound. |
| GFIN | PASS | Obligations are source-bound and no unsupported payment exists. |
| GOBL | PASS | Outstanding obligations remain visible. |
| GEVID | PASS | Public evidence metadata is redacted and points to private-ledger references. |
| GTIME | BLOCKED | Weekly-report and tracing timestamps need reconciliation. |
| GCLOSE | PASS | `OPEN` is correctly retained. |

## Verification

Run the current result with:

```sh
PYTHONPATH=src python3 -m semantica_workbench.cli golden-case
```

The command exits non-zero only for a failed gate. `BLOCKED` is a valid result
while evidence is incomplete; it is not converted into a pass candidate.

The runtime artifact is included in two independent clean rebuilds. Its
canonical hash must match across both builds before a later gate review.

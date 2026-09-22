# Reality Pilot 002 — Case selection and evidence audit

Canonical task: GitHub Issue #5  
Baseline: `96628c133a268ea1e2133eeb0889d2ab7b3bbd21`

This audit precedes any schema or runtime change. A case is admitted only when
its identity and every proposed event can be tied to a source original.

| Candidate | Decision | Evidence found | Reason |
|---|---|---|---|
| ONE-N524 | Retain | Pilot 001 governed manifest | Existing bounded reference case; not reinterpreted here. |
| ONE-N617 / ONE617TST | Admit provisionally | Original contract setup, pick-up notice, PI, arrival/redelivery correspondence, and off-hire-date queries | Stable contract and booking identifiers, 30 × 20HC, Qingdao → Brisbane. It has a real operational chain, but no depot-issued EIR or confirmed lot-level off-hire completion. |
| Shanghai → Cape Town | Reject from admission | `our wish list.eml` | The local corpus contains Cape Town only as a corridor availability row. No executable-case identifier, booking/release, movement, or off-hire original was found. |
| ONE-H227 / ONEH227SGH | Not admitted | Pick-up notice, container pre-advice, destination arrival-window and off-hire-detail requests | It is a real historical operational thread, but the available originals do not establish a source-grounded completed off-hire event. It is not used to fill the required second new-case slot. |
| Xiamen → Port Louis; Brisbane/Fremantle discussions | Negative controls only | Opportunity / availability correspondence | No execution evidence. These threads must remain opportunities. |

## Frozen selection result

The reviewed set contains ONE-N524 and one admissible new case (ONE-N617).
Reality Pilot 002 requires two additional admitted real cases. The minimum is
therefore not met. No schema delta is proposed, and no business event, state,
timestamp, or generic ontology fact is created from the incomplete candidates.

## Source observations

ONE-N617 original sources establish: Maersk set up contract `ONE-N617` with
booking `ONE617TST`; a 30 × 20HC pick-up notice was sent for Qingdao with
Brisbane redelivery; the PI lists the same contract/booking and thirty unit
numbers; and the Australian correspondence records off-hire-depot coordination
and a stated off-hire for VSTU5409142. These are sufficient to preserve the
case as evidence-ready, but not to infer settlement or lot completion.

The audit deliberately treats mail send dates as correspondence metadata, not
as substituted operational timestamps.

# Runtime closure v1 — reality audit and disposition

Task: https://github.com/cliffordzhangcheng/semantica-project/issues/1
Base/main at takeover: eb8af3b949142b83303b9f87f8d06d7d7bd99489
Candidate reviewed: bca182eab63f24f541354242e12eeb249f1bc8b5
Owner: Codex, manually relayed by Founder on 2026-09-22.

Clean main invocation after moving committed outputs aside returned exit 0:
6 ingested documents, 4 entities, 0 relations. Claims/evidence are not
semantically joined. Ingestion clips content to 1,000 characters; the default orchestrator
resolves its project root to src/ and silently skips a missing ingestion script.
The CLI supplies the correct root but still admits a zero-relation result. Baseline artifacts/logs are under ignored artifacts/baseline.

## OpenMinis diff disposition

- KEEP (design only): bounded Golden relations, explicit entity registry,
  typed literal objects, distinct GR/GC/GA/GDET/GSYNC gates. No wholesale port.
- REWORK: builder and entity registry. data/corpora does not exist; hardcoded
  evidence locators do not match data/raw. Generic contract/container subjects
  lose the scope of a quotation or completed lot. Publication is attributed
  to a company although the source names its contact.
- REWORK: GR checks IDs/labels, not resolved source support; GC checks ID
  prefixes without registry membership or relation equality. GA ignores
  several missing/invalid artifacts. GSYNC can pass an empty directory and
  omits standalone relations/claims/evidence. Hashes in the builder are JSON
  prefixes, not digests. GDET trusts report booleans; reports repeat them.
- REWORK: tests must invoke real validators against adversarial mutations and
  build their own fixtures, rather than inspect committed generated output.
- DROP: committed outputs, gate result text, status/completion declarations,
  cached bytecode, report templates, CI installation fallback, and removal
  of semantica dependency (existing compatibility tests import it).
- DROP: new off_hire_at alias; the existing registry already has off_hires_at.

## Bounded semantic decision

Admit three source assertions, only as corpus assertions:
1. Cosmos Whales provides_service_to Hapag-Lloyd (explicit service sentence).
2. The Hapag-Lloyd ONEWAY **quotation**, has_free_days 90–100 days. This is
   quoted terms, not an executed contract or Booking state.
3. Mr. Phen Lak publishes the wish list mentioned in that contact sentence.
   No inference that the entire carrier is the publisher.

Reject the generic contract PUC candidate: its USD 150 sentence does not
uniquely identify an executed contract. Reject the generic container off-hire
candidate: a completed 26-container lot is not a universal container fact.
These can be modeled later with reviewed case/contract identities.

The curated assertion catalog is an explicit review boundary, not a general
semantic entailment model. Exact full lines and section context must resolve;
any source change requires renewed review. G6 remains BLOCKED: no sufficient
real Booking/state/event validation is supplied. Founder review/merge remains
separate from machine engineering checks.

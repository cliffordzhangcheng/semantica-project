# Semantica Ontology Project

The runtime closure pipeline rebuilds a bounded set of reviewed logistics
assertions from `data/raw/oneway-corpus.md`. It currently admits three Golden
relations with canonical IDs, exact source spans, scoped claims and SHA-256
snapshot manifests. This is engineering evidence for further business
validation; G6 is BLOCKED and Founder G7 review is required for admission.

## Install and run

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' -c constraints.txt
.venv/bin/python -m semantica_workbench.cli run
.venv/bin/python -m pytest tests/ -v --junitxml=artifacts/tests.xml
.venv/bin/python -m semantica_workbench.cli closure --output artifacts/closure
.venv/bin/python -m semantica_workbench.cli validate --output artifacts/closure/run1
```

`run` creates an exclusive snapshot beneath `outputs/runs/`. `closure` launches
two independent processes into new directories and verifies GR, GC, GA, GDET
and GSYNC. The output directory must not already exist; use a new name on a
subsequent run. Validation rereads source text, verifies the full reviewed
assertions, recalculates digests, compares standalone artifacts to the graph,
and checks report counts/locators against runtime data. Any missing, malformed,
mixed-run, unsupported or unexpected artifact fails closed.

`schemas/golden_catalog.json` is the explicit semantic review boundary. It
binds complete source clauses and section context to reviewed triples; it is
not a general NLP extractor. Changes to the catalog require semantic review.
The input is a curated summary corpus, not independently authenticated raw
business evidence. A quoted term is not an executed contract or booking.

See [takeover audit](docs/runtime-closure-audit.md) for OpenMinis KEEP/REWORK/DROP
and rejected candidates. Historical extraction scripts and G0–G7 reports are
retained for research/compatibility; they are not the runtime admission path.
Generated outputs, bytecode and package metadata are not versioned.

CI runs all existing tests plus adversarial gate regressions, performs the two
clean rebuilds and uploads commit-bound runtime evidence. A green CI result
is an engineering candidate only. No production or AKOS writes are performed.

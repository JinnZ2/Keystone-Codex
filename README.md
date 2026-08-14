# Keystone-Codex

A machine-readable **library of keystone technologies** — the ecological, social,
informational, material, and ethical systems that unlocked entire lineages and
endured across crises.

Designed to be **AI-checkable**: explicit claims, evidence with quality weights,
rule-based proofs, and a falsification loop that runs against its own claims and
records what it finds.

## Why

We want a culture engineered from the **best technologies of all ages** — Terra
Preta and Indus plumbing alongside the lathe and the transistor, councils beside
TCP/IP. The Codex encodes each candidate with machine-verifiable fields and scores
it against transparent thresholds.

The second half of that job is harder and matters more: **checking whether the codex
is telling the truth about itself.** A library of keystones assembled by people who
already believe these are keystones will confirm itself unless something is built to
stop it. That is what `src/falsify.py` is for.

## The loop

```
hypothesize → run → falsified? → edit the claim → register unknowns → rerun
```

State a claim about the corpus in `hypotheses/`, bind it to a test, and run it. When
the data says no, the claim gets edited — not the data. Questions raised on the way
land in `UNKNOWNS.md`. Every run appends to `ledger/runs.jsonl`, which is never
rewritten, so what the project once believed stays legible after it stops believing
it.

```bash
python3 src/falsify.py            # run every hypothesis, update ledger and unknowns
python3 src/falsify.py --only H007 --dry-run
python3 src/falsify.py --strict   # exit 1 if anything is falsified (for CI)
```

**What the first run found.** Seven of eight hypotheses were falsified against the
repository as it stood. A sample:

- **H002** — every one of the 15 `unlocks` targets in the corpus resolved to
  nothing. `build_graph.py` had been drawing edges to invented nodes, and the
  `unlocks_lineage` scoring criterion was counting strings.
- **H006** — under rules v1.0 all five entries passed and four scored a perfect
  1.0. Every criterion read a number the author had typed; none read the evidence
  behind it. The rubric was confirming the selection that put entries in the
  repository, not evaluating them. Rules v1.1 added three evidence-reading criteria;
  v1.0 is retired to `legacy/` and still runnable.
- **H007** — `shadow_search.py` reported golden-ratio spacing among emergence dates
  as possible evidence of "underlying systemic coupling". Against a seeded uniform
  null model the catalogue produces *fewer* phi-triads than random dates in the same
  window (p = 0.97). The claim was replaced rather than softened, and the detector
  is kept as a labelled negative control — a demonstration of how much structure a
  triad search manufactures from a few dozen dates.

The current run is in `falsification_report.md`; the history is in
`ledger/LEDGER.md`.

## Install (no internet required)

```bash
python3 -V                      # 3.8+, no dependencies

python3 src/validate.py         # schema checks
python3 src/falsify.py          # the loop
python3 src/prove.py            # score + prove each keystone
python3 src/build_graph.py      # graph.json + graph.dot
python3 src/render_timeline.py  # timeline.md
python3 src/shadow_search.py    # interactive candidate playground

bash examples/run_all.sh        # all of the above in order
```

## Layout

```
schema/         JSON Schemas — keystone entries, proof traces, hypotheses
rules/          Scoring thresholds (keystone_rules.json) and the lineage vocabulary
data/<domain>/  Encoded keystone entries, one file each
data/*.json     Registries — the shadow catalogue. Never treated as entries.
hypotheses/     Falsifiable claims about the corpus, bound to tests
ledger/         Append-only run history. The durable record.
unknowns/       Open questions, with the run that raised each
anthropology/   Frontier methods and findings, and what they'd revise here
legacy/         Superseded and still runnable. Precedence carries.
src/            Loader, validator, proof engine, falsifier, exporters
examples/       Quick scripts
```

The split between `data/<domain>/` and `data/*.json` is load-bearing: everything
loads through `src/corpus.py`, which treats subdirectory files as entries and
top-level files as registries. Before that existed, each script walked `data/`
independently, and dropping a catalogue file at the top of it crashed the proof
engine.

## Adding a keystone

Create a JSON file at `data/<domain>/<id>.json` following
`schema/keystone.schema.json`, then:

```bash
python3 src/validate.py
python3 src/falsify.py
python3 src/prove.py
```

Things the loop will catch, so it is faster to get them right first:

- **Every `evidence_ref` must resolve** to an evidence `id` in the same file. A typo
  turns an evidenced claim into a bare assertion (H004).
- **Every `unlocks` target must resolve** to another entry id or a term in
  `rules/lineage_terms.json`. Add the term if it is missing (H002).
- **If `longevity_years` doesn't match `era.end - era.start`** within 25%, declare a
  `longevity_basis` saying what the number measures — attested operation,
  persistence after abandonment, or a floor under a contested start date (H003).
- **Your entry appears in `data/shadow_catalogue.json`** with `status: "confirmed"`
  and the same id (H001).

**It is fine for an entry to fail.** `data/social/hxaro.json` fails on purpose:
its antiquity has never been established, so it enters the floor it can defend
rather than a number that would score well. Entering a figure the evidence does not
support is the failure mode this whole apparatus exists to catch.

## Scoring

`rules/keystone_rules.json` (v1.1) weights seven criteria. Four describe the
technology — longevity, replication across regions, downstream lineages,
decentralization. Three describe the record behind it — mean evidence quality,
number of distinct evidence types, and whether every claim is actually backed.
Pass score is 0.70.

Currently 7 of 9 entries pass. The two that don't are worth understanding:

- **the lathe** (0.62) fails longevity at 228 years against a 300-year bar. That is
  arguably the correct answer, and the rubric giving it is the point.
- **hxaro** (0.68) fails longevity and replication — both because of gaps in the
  archaeological record, not because of anything about risk-pooling networks.

Which raises the question the rubric cannot answer about itself: if it
systematically ranks technologies by how well their records survived, it is
measuring preservation and calling it merit. That is **U-H006-2**, and it is open.

## Legacy

`legacy/` holds superseded rule sets and documents. Nothing there is deleted and
everything there still runs:

```bash
python3 src/prove.py --rules legacy/rules/keystone_rules.v1.json --out-suffix .v1
```

A verdict reached under an old rubric is still a verdict that was reached. See
`legacy/README.md`.

## Output artifacts

| File | What it is |
| --- | --- |
| `falsification_report.md` | Latest run: every hypothesis, verdict, detail |
| `ledger/LEDGER.md` | Every run, oldest first, never rewritten |
| `UNKNOWNS.md` | Open, resolved, and dormant questions |
| `proof_report.md` | Keystone verdicts with per-criterion traces |
| `graph.json` / `graph.dot` | Lineage graph; keystone and family nodes distinguished |
| `timeline.md` | Encoded entries ordered by first attestation |

## Design notes

- **Proofs as data.** Structured claims and evidence with quality weights.
- **Transparent thresholds.** `rules/keystone_rules.json`, with the revision note
  saying which run forced the change.
- **Falsification is not failure.** `src/falsify.py` exits 0 when hypotheses fail —
  that is the loop working. Use `--strict` if you want CI to disagree.
- **Dormant ≠ resolved.** A question that stops being raised because the data moved
  under it is still open. `UNKNOWNS.md` keeps the two apart.
- **No external deps.** Pure Python stdlib; optional Graphviz to render `.dot`.
- **Offline-first.** Suitable for rural and off-grid workflows.

## Credits

Initiated by JinnZ2 × ChatGPT. MIT licensed.

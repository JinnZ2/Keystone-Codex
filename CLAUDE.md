# CLAUDE.md — Keystone-Codex

## RULE 1 — Target and rendering are recorded separately

When a hypothesis or a detector is falsified, record two things:

| | |
|---|---|
| **target** | what it was trying to measure |
| **rendering** | the specific method or claim that failed |

**Falsifying a rendering does not close its target.** The target goes to
`UNKNOWNS.md` as open, unless a test reached the target itself.

This is enforced, not requested. A hypothesis carries a `measures` block
(`target`, `rendering`, `target_question`, `target_reached`); when it is
falsified, `src/falsify.py` raises `target_question` as an open unknown unless
`target_reached` is true. A falsified hypothesis carrying no block at all is
noted in the report, so the gap is visible rather than inferred from silence.

**The worked case.** H007 proposed golden-ratio spacing in emergence dates as
evidence of cross-domain systemic coupling. The detector was falsified against
a null model (p = 0.864 at `run-001-baseline`, 0.983 at
`run-005-recent-finds`), the claim was replaced by its own negation, and H007
now reports *supported*. That is true of the **rendering** and says nothing
about the **target**: nothing in this repository has measured cross-domain
coupling, and the instrument that was going to is now a negative control. The
target is open at `U-H007-3`. `U-H007-2` — do two further detectors survive the
same null — is marked rendering-level for the same reason: no result about a
detector closes it.

Applied retroactively to H007 only. H001–H006 and H008 carry no `measures`
block; what each was aiming at, as distinct from what it tests, is not recorded
anywhere and was not inferred here.

## RULE 2 — Role is not category

`domain` says what kind of thing an entry is. `layer_role` says what it does in
an assembly. They are separate fields and neither derives from the other.

`SYSTEMS_ANALOGY.md` assigns **roles**: *"Social / Governance = Motherboard +
Bus. Routes communication, connects components, regulates timing."* Routing and
timing is a function. Two categories sharing one function is not a conflation of
the categories, and the earlier reading of that line as a domain error is
corrected in ledger note `N-001` — appended, with `U-H005-4`'s resolution left
standing, because social and governance **are** distinct domains and that
argument holds.

The crosstab in the first declared system shows the two fields carrying
different statements, read straight off the source's own example lists: `BUS`
covers domains `{ethical, governance}` and `IO` covers `{economic, social}`. The
map from domain to role is not one-to-one in the source itself.

The repository already contains two artifacts that disagree about this and
neither declares that it is answering it. `.fieldlink.json`'s `layer_map`
derives layers from **domain** and files `gift_economy` under `motherboard_bus`
and `ubuntu_philosophy` under `bios_firmware`; `SYSTEMS_ANALOGY.md` names the
potlatch under **I/O** and Ubuntu under **Motherboard + Bus**. `src/health.py`
reads the first and prints a verdict computed on it. Neither file is changed
here and neither is wrong on its own terms.

Which of the two owns an assignment — and whether a role is relational, so that
the same entry carries different roles in different assemblies — is open at
`U-ARCH-1`. The integration report reports such a disagreement and **resolves
neither side**.

## What This Project Is

Keystone-Codex is a machine-readable library of **keystone technologies** — ecological, social, informational, material, and ethical systems that unlocked entire lineages and endure across crises. Entries are JSON documents with explicit claims, evidence references, and rule-based proof scoring to determine "keystone" status.

Design principles: offline-first, zero dependencies, schema-driven, culturally pluralist, fully auditable proofs.

## Tech Stack

- **Language**: Python 3.8+ (stdlib only — no external dependencies)
- **Data format**: JSON with JSON Schema validation (Draft 2020-12)
- **Graph output**: Optional Graphviz (.dot)
- **License**: MIT

## Repository Structure

```
data/                       # Keystone entries organized by domain (8 domains)
  ecological/               # e.g., terra_preta.json
  economic/                 # e.g., rotating_credit.json
  social/                   # e.g., gift_economy.json
  governance/               # e.g., haudenosaunee_council.json
  information/              # e.g., quipu.json
  material/                 # e.g., lathe.json
  ethical/                  # e.g., ubuntu_philosophy.json
  infrastructure/           # e.g., indus_plumbing.json
  shadow_catalogue.json     # REGISTRY — candidates + confirmed index
  candidates.json           # REGISTRY — shortlist queue
  evaluator_claims.json     # REGISTRY — ships EMPTY; read by H-BYPASS
systems/                    # Assemblies: entry ids + declared joints
schema/
  keystone.schema.json      # Main data schema (evidence + layer_role enums live here)
  proof.schema.json         # Schema for proof trace output
  hypothesis.schema.json    # Schema for falsifiable claims
  system.schema.json        # Schema for an assembly
  evaluator_claim.schema.json  # Schema for a recorded semantic bypass
rules/
  keystone_rules.json       # Scoring criteria, weights, thresholds (v1.1)
  lineage_terms.json        # Declared vocabulary that `unlocks` may point at
hypotheses/                 # H001–H008 plus H-ARCH-1..3 and H-BYPASS
ledger/
  runs.jsonl                # APPEND-ONLY run history. Never edited.
  LEDGER.md                 # Rendered from runs.jsonl
unknowns/
  register.json             # Open/resolved/dormant questions
anthropology/
  FRONTIER.md               # Methods and findings that would revise entries here
legacy/                     # Superseded and still runnable — see legacy/README.md
tests/                      # unittest suite
src/
  __main__.py               # Unified CLI entry point
  corpus.py                 # THE loader. Everything reads data/ through this.
  validate.py               # Deep schema validation with cross-reference checks
  prove.py                  # Scoring engine, rule-set driven
  falsify.py                # Falsification engine + test kinds
  build_graph.py            # Graph topology; keystone/lineage/dangling nodes
  render_timeline.py        # Markdown timeline renderer
  query.py                  # Query/filter entries by domain, score, region, era
  analyze.py                # Cross-entry analysis (coverage, gaps, integrity)
  health.py                 # System health dashboard
  systems.py                # Integration report over systems/ — no score, no rank
  fieldlink_export.py       # BioGrid2.0 export
  scaffold.py               # Generate new entry templates
  shadow_search.py          # Interactive candidate playground
examples/
  run_all.sh                # Convenience script to run full pipeline
```

**Loading rule — important.** Files in `data/<domain>/` are entries. Files at the
top of `data/` are registries. Files in `systems/` are assemblies of entries and
live outside `data/` for that reason. Everything loads through `src/corpus.py`;
never write a new `os.walk` over `data/`. There used to be eight of them, each
excluding registry files by name, and `prove.py` crashed on both branches at
merge time because they knew about `candidates.json` but not
`shadow_catalogue.json`.

## Common Commands

```bash
# Unified CLI — all commands available via:
python3 -m src <command>

# Run the full pipeline (validate → score → graph → timeline)
python3 -m src all

# Individual commands
python3 -m src validate          # Validate all entries against schema
python3 -m src score             # Score entries → proof_traces.json, proof_report.md
python3 -m src graph             # Build graph → graph.json, graph.dot
python3 -m src timeline          # Render timeline → timeline.md
python3 -m src falsify           # Run hypotheses → ledger, unknowns
python3 -m src falsify --only H007 --dry-run
python3 -m src falsify --strict  # exit 1 if any hypothesis is falsified

# Tests
python3 -m unittest discover -s tests

# Score under a retired rule set (verdicts stay reproducible)
python3 -m src score --rules legacy/rules/keystone_rules.v1.json --out-suffix .v1

# Query and analysis
python3 -m src query --domain governance
python3 -m src query --keystones-only
python3 -m src query --era-after -1000 --min-score 0.8
python3 -m src analyze           # Domain coverage, dangling unlocks, evidence stats
python3 -m src systems           # Integration report over systems/
python3 -m src systems --json    # The same report as data

# Scaffold a new entry
python3 -m src new <domain> <id>
# e.g.: python3 -m src new economic barter_networks

# Legacy direct invocation still works
python3 src/validate.py
bash examples/run_all.sh
```

There is no build step, no package install, and no virtual environment needed.

## Data Model

Each entry in `data/{domain}/` is a JSON file following `schema/keystone.schema.json`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique snake_case identifier |
| `name` | string | Human-readable name |
| `domain` | enum | One of: ecological, economic, social, governance, information, material, ethical, infrastructure |
| `region` | string | Geographic origin/distribution |
| `era` | object | `{start, end}` in years (negative = BCE) |
| `summary` | string | One-sentence description |
| `metrics.longevity_years` | int | Duration in years |
| `metrics.replication_regions` | int | Independent adoption regions |
| `metrics.decentralization_score` | float 0–1 | Systemic decentralization |
| `metrics.ethical_alignment` | float 0–1 | Optional ethical score |
| `claims` | array | Structured claims with evidence_refs |
| `evidence` | array | Sources with type, URI, quality (0–1) |
| `unlocks` | array | Downstream technology IDs |

## Scoring System

Defined in `rules/keystone_rules.json`:

Rules **v1.1**. Four criteria describe the technology; three describe the record
behind it.

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Longevity | 0.18 | ≥ 300 years |
| Replication | 0.14 | ≥ 2 regions |
| Unlocks lineage | 0.12 | ≥ 2 downstream families |
| Decentralization | 0.10 | ≥ 0.5 score |
| Evidence strength | 0.20 | mean quality ≥ 0.75 |
| Evidence independence | 0.14 | ≥ 3 distinct evidence types |
| Claim coverage | 0.12 | every claim backed by a resolving ref |

**Pass threshold**: 0.70 aggregate.

**No evidence-quality multiplier.** An earlier design scaled the raw score by
mean evidence quality. Both mechanisms address the same flaw and applying both
would penalise evidence twice, so the explicit criteria won: a trace saying
`evidence_independence ✖` tells you what to fix, while a silently scaled score
does not. The trade-off — discrete thresholds are cliff-edged where a
multiplier degrades smoothly — is documented at the top of `src/prove.py`.

`rules/keystone_rules.json` carries a `revision_note` naming the run that forced
each change. v1.0 is retired to `legacy/` and still runnable.

Output includes per-criterion pass/fail, weighted score, evidence quality,
`is_keystone`, `rules_version`, and the full proof trace.

## Falsification Loop

`src/falsify.py` is the part that checks whether the codex is telling the truth
about itself. Each file in `hypotheses/` states a claim, binds it to a test kind
implemented in `falsify.py`, and carries its revision history.

```
hypothesize → run → falsified? → edit the claim → register unknowns → rerun
```

Rules for working in here:

- **A falsified hypothesis is a result, not a broken build.** The engine exits 0.
  CI runs it without `--strict` deliberately.
- **Edit the claim, not the data.** If a test fails because the corpus is wrong,
  fix the corpus. If it fails because the claim was wrong, rewrite the claim and
  append to its `revisions` array saying which run forced it.
- **Never silently retune a threshold to make a test pass.** H006's revision is
  the worked example: it was re-derived around a different statistic, with the
  measurements that justified the change recorded in the revision.
- **`ledger/runs.jsonl` is append-only.** Never edit or reorder it.
- **Dormant ≠ resolved.** A question whose hypothesis stops failing goes
  `dormant`, not `resolved`. Only a written `resolution` resolves it.

## The Architecture Layer

Added **beside** the per-entry rubric, not in place of it. The two measure
different things and neither reads the other's output:

```
entry     one technology against thresholds          src/prove.py      rules v1.1
system    a set of entries plus joints, reported on  src/systems.py    no rules file
```

`SYSTEMS_ANALOGY.md` (2025) is the original frame and its measurand is
**integration**, not per-entry merit. The rubric is sound work aimed at a
different measurand; it stays, unchanged, and this layer does not feed it.

**Eight optional entry fields** carry what an assembly needs to be read:
`layer_role`, `runs_on`, `adapted_to`, `dependency_load`, `field_rebuildable`,
`spread_mechanism`, `attribution_basis`, `separation_claim`. All are optional
and **zero entries declare any of them**; that is the finding H-ARCH-1 reports,
not an oversight to be filled in quietly. `UNSET` is a legal explicit value and
counts as *declared*: an entry saying nobody has read it for its role is a
reading, and it is a different state from a field nobody has touched.

**Four hypotheses.** H-ARCH-1 (role coverage), H-ARCH-2 (runs_on resolves
within a system), H-ARCH-3 (the integration report has resolution — H006's
ceiling-saturation check pointed at the new layer so it can fail too), H-BYPASS
(the evaluator-claim register).

**`data/evaluator_claims.json` ships empty and H-BYPASS returns `no data`.**
Not *supported*: a claim with nothing recorded against it has not been tested,
it has been left alone, and a pass over zero rows would turn the absence of a
search into evidence for the thing nobody searched for. This is the same
distinction the register keeps between *dormant* and *resolved*, one layer down.

**Verdicts are three-valued.** `passed` is `True`, `False` or `None`. `--strict`
exits 1 on `False` only; `None` is counted and reported separately everywhere
and is never folded into either.

## Adding a New Keystone Entry

1. Run `python3 -m src new <domain> <id>` to scaffold a template
2. Fill in name, region, era, summary, metrics, claims, evidence, unlocks
3. Include ≥ 2 claims with evidence references
4. Evidence should cite primary/authoritative sources (prefer DOI/ISBN)
5. Run `python3 -m src validate` to check schema compliance
6. Run `python3 -m src score` and review `proof_report.md`
7. Run `python3 -m src analyze` to check for dangling unlocks

## Validation

`validate.py` checks:
- All required top-level fields present
- `domain` is a valid enum value
- `era` has integer `start` and `end`
- `metrics` has all required fields with correct types and ranges
- `claims` have `id`, `statement`, and `evidence_refs`
- `evidence` has `id`, `type`, `source`; type must be a valid enum
- Cross-references: every `evidence_refs` in claims points to an existing evidence ID

## Evidence Types

Valid values for `evidence.type` (enforced by schema):
`archaeological_record`, `peer_reviewed_study`, `ethnographic_record`, `primary_text`, `engineering_record`, `replication_record`, `radiocarbon_date`, `standards_spec`, `field_measurement`, `oral_tradition_encoded`

**Single source of truth**: the enum in `schema/keystone.schema.json`.
`validate.py` derives `VALID_EVIDENCE_TYPES` from it and H008 checks every
declared type is actually used. Do not restate the list anywhere else — it
previously lived in three places and had already drifted.

## Code Conventions

- **No external dependencies** — only Python stdlib (`json`, `os`, `sys`, `datetime`, `collections`)
- **File handles**: Always use `with` statements
- **JSON indentation**: 2 spaces
- **IDs**: snake_case (e.g., `terra_preta`)
- **Python naming**: snake_case for functions/variables
- **Docstrings**: Present on all functions

## Outputs

All generated files are gitignored (see `.gitignore`):

| File | Format | Description |
|------|--------|-------------|
| `proof_traces.json` | JSON | Machine-readable proof data with evidence quality |
| `proof_report.md` | Markdown | Human-readable verdicts |
| `graph.json` | JSON | Nodes (real + placeholder) and edges |
| `graph.dot` | Graphviz DOT | Visual graph with dashed placeholder nodes |
| `timeline.md` | Markdown | Date-sorted keystone list |
| `falsification_report.md` | Markdown | Latest run: every hypothesis and verdict |

**Not gitignored**, deliberately: `ledger/runs.jsonl`, `ledger/LEDGER.md`,
`unknowns/register.json`, `UNKNOWNS.md`, `legacy/reports/*`. The line is whether
a file can be rebuilt from the current corpus. A proof report can. A ledger
cannot — it records what was believed before the corpus changed, which is the
only reason it is worth keeping.

## Integration

The `.fieldlink.json` file connects this repo to the [BioGrid2.0 Atlas](https://github.com/JinnZ2/BioGrid2.0) for glyph, protocol, and sensor manifests.

## CI/CD

`.github/workflows/ci.yml` runs on push and PR to `main`, across Python 3.8,
3.10, and 3.12: validate → falsify → score → graph → timeline → analyze →
`unittest discover -s tests`.

The falsify step runs without `--strict`, so a falsified hypothesis reports but
does not fail the build. That is deliberate.

## Key Design Decisions

- **Proofs as data**: Claims and evidence are structured, not narrative; quality weighting is explicit
- **Evidence quality matters**: Scoring factors in source reliability, not just metrics
- **Transparent thresholds**: All scoring rules live in `keystone_rules.json` and are fully auditable
- **Offline-first**: No external API calls; suitable for rural/off-grid workflows
- **Cross-cultural equity**: No prestige bias; non-Western sources are weighted equally
- **Mosaic perspective**: No single culture had all keystones — the reference atlas (`legacy/references.md`) makes this explicit
- **Self-falsification**: The codex tests its own claims and records the failures. `ledger/LEDGER.md` is the honest history; `UNKNOWNS.md` is what is still open
- **Retire, don't delete**: Superseded rule sets stay runnable. v1.0 is the control that demonstrates v1.1 is an improvement rather than merely a change
- **Entries may fail on purpose**: `data/social/hxaro.json` enters the longevity floor it can defend and takes the failing score. Never inflate a metric to clear a bar
- **Graph integrity**: Placeholder nodes make dangling unlock references visible rather than silently broken
- **Additive, never replacing**: The architecture layer sits beside the per-entry rubric rather than correcting it. Two instruments aimed at two measurands, neither reading the other
- **A new layer must be able to fail**: H-ARCH-3 is H006's saturation check pointed at the integration report. A layer added without a test that can refuse it will confirm whatever it is handed
- **No score on a part, in the systems layer**: no combined score, no ranking of members, no ordering of systems by satisfaction. A number attached to a part turns an integration measure back into a supremacy measure. `tests/test_systems.py` asserts the absence rather than trusting it
- **Absent is not zero**: a `runs_on` fraction is `None` when nothing was declared. Zero-of-zero and zero-of-eleven are different results and a float cannot hold both
- **Report the disagreement, resolve neither side**: where an entry and a system declare different roles for the same member, the conflict is reported and neither wins. Picking one would settle `U-ARCH-1` by fiat

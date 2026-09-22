# CLAUDE.md — Keystone-Codex

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
schema/
  keystone.schema.json      # Main data schema (evidence type enum lives here)
  proof.schema.json         # Schema for proof trace output
  hypothesis.schema.json    # Schema for falsifiable claims
rules/
  keystone_rules.json       # Scoring criteria, weights, thresholds (v1.1)
  lineage_terms.json        # Declared vocabulary that `unlocks` may point at
hypotheses/                 # H001–H008: falsifiable claims bound to test kinds
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
  fieldlink_export.py       # BioGrid2.0 export
  scaffold.py               # Generate new entry templates
  shadow_search.py          # Interactive candidate playground
examples/
  run_all.sh                # Convenience script to run full pipeline
```

**Loading rule — important.** Files in `data/<domain>/` are entries. Files at the
top of `data/` are registries. Everything loads through `src/corpus.py`; never
write a new `os.walk` over `data/`. There used to be eight of them, each
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

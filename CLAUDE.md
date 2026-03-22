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
schema/
  keystone.schema.json      # Main data schema (with evidence type enum)
  proof.schema.json         # Schema for proof trace output
rules/
  keystone_rules.json       # Scoring criteria, weights, thresholds
src/
  __main__.py               # Unified CLI entry point
  validate.py               # Deep schema validation with cross-reference checks
  prove.py                  # Scoring engine with evidence quality weighting
  build_graph.py            # Graph topology with placeholder node detection
  render_timeline.py        # Markdown timeline renderer
  query.py                  # Query/filter entries by domain, score, region, era
  analyze.py                # Cross-entry analysis (coverage, gaps, integrity)
  scaffold.py               # Generate new entry templates
examples/
  run_all.sh                # Convenience script to run full pipeline
```

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

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Longevity | 0.35 | ≥ 300 years |
| Replication | 0.25 | ≥ 2 regions |
| Unlocks lineage | 0.25 | ≥ 1 downstream tech |
| Decentralization | 0.15 | ≥ 0.5 score |

**Pass threshold**: 0.65 aggregate.

**Evidence quality modifier**: The raw criteria score is scaled by evidence quality (range 0.7–1.0). High-quality evidence preserves the score; poor evidence can reduce it by up to 30%. This means entries with weak sourcing need stronger metrics to pass.

Output includes per-criterion pass/fail, weighted score, evidence quality, `is_keystone` flag, and full proof trace.

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
`archaeological_record`, `peer_reviewed_study`, `primary_text`, `engineering_record`, `replication_record`, `radiocarbon_date`, `standards_spec`, `field_measurement`, `oral_tradition_encoded`

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

## Integration

The `.fieldlink.json` file connects this repo to the [BioGrid2.0 Atlas](https://github.com/JinnZ2/BioGrid2.0) for glyph, protocol, and sensor manifests.

## CI/CD

No CI pipelines are configured. Validation is manual via `python3 -m src validate`.

## Key Design Decisions

- **Proofs as data**: Claims and evidence are structured, not narrative; quality weighting is explicit
- **Evidence quality matters**: Scoring factors in source reliability, not just metrics
- **Transparent thresholds**: All scoring rules live in `keystone_rules.json` and are fully auditable
- **Offline-first**: No external API calls; suitable for rural/off-grid workflows
- **Cross-cultural equity**: No prestige bias; non-Western sources are weighted equally
- **Mosaic perspective**: No single culture had all keystones — the reference atlas (`references.md`) makes this explicit
- **Graph integrity**: Placeholder nodes make dangling unlock references visible rather than silently broken

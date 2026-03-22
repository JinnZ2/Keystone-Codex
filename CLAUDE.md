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
data/                       # Keystone entries organized by domain
  ecological/               # e.g., terra_preta.json
  governance/               # e.g., haudenosaunee_council.json
  information/              # e.g., quipu.json
  infrastructure/           # e.g., indus_plumbing.json
  material/                 # e.g., lathe.json
schema/
  keystone.schema.json      # Main data schema for entries
  proof.schema.json         # Schema for proof trace output
rules/
  keystone_rules.json       # Scoring criteria, weights, thresholds
src/
  validate.py               # Schema validation for all entries
  prove.py                  # Scoring engine & proof trace generation
  build_graph.py            # Graph topology (nodes/edges, .dot output)
  render_timeline.py        # Markdown timeline renderer
examples/
  run_all.sh                # Convenience script to run full pipeline
```

## Common Commands

```bash
# Validate all data entries against the schema
python3 src/validate.py

# Score entries and generate proof reports
python3 src/prove.py
# → proof_traces.json, proof_report.md

# Generate graph topology
python3 src/build_graph.py
# → graph.json, graph.dot

# Generate timeline
python3 src/render_timeline.py
# → timeline.md

# Run the full pipeline
bash examples/run_all.sh
```

There is no build step, no package install, and no virtual environment needed.

## Data Model

Each entry in `data/{domain}/` is a JSON file following `schema/keystone.schema.json`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique kebab-case identifier |
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

**Pass threshold**: 0.65 aggregate. Output includes per-criterion pass/fail, weighted score, `is_keystone` flag, and full proof trace.

## Adding a New Keystone Entry

1. Create `data/{domain}/{id}.json` following `schema/keystone.schema.json`
2. Include ≥ 2 claims with evidence references
3. Evidence should cite primary/authoritative sources (prefer DOI/ISBN)
4. Run `python3 src/validate.py` to check schema compliance
5. Run `python3 src/prove.py` and review `proof_report.md`

## Evidence Types

Valid values for `evidence.type` (documented in `CITATIONS.md`):
`archaeological_record`, `peer_reviewed_study`, `primary_text`, `engineering_record`, `replication_record`, `radiocarbon_date`, `standards_spec`, `field_measurement`, `oral_tradition_encoded`

## Code Conventions

- **No external dependencies** — only Python stdlib (`json`, `os`, `datetime`, `math`)
- **JSON indentation**: 2 spaces
- **IDs**: kebab_case (e.g., `terra_preta`)
- **Python naming**: snake_case for functions/variables
- **Error handling**: Lightweight; relies on schema validation rather than defensive coding
- **Docstrings**: Present on all functions

## Outputs

| File | Format | Description |
|------|--------|-------------|
| `proof_traces.json` | JSON | Machine-readable proof data |
| `proof_report.md` | Markdown | Human-readable verdicts |
| `graph.json` | JSON | Nodes and edges for visualization |
| `graph.dot` | Graphviz DOT | Diagram rendering input |
| `timeline.md` | Markdown | Date-sorted keystone list |

## Integration

The `.fieldlink.json` file connects this repo to the [BioGrid2.0 Atlas](https://github.com/JinnZ2/BioGrid2.0) for glyph, protocol, and sensor manifests.

## CI/CD

No CI pipelines are configured. Validation is manual via `python3 src/validate.py`.

## Key Design Decisions

- **Proofs as data**: Claims and evidence are structured, not narrative; quality weighting is explicit
- **Transparent thresholds**: All scoring rules live in `keystone_rules.json` and are fully auditable
- **Offline-first**: No external API calls; suitable for rural/off-grid workflows
- **Cross-cultural equity**: No prestige bias; non-Western sources are weighted equally
- **Mosaic perspective**: No single culture had all keystones — the reference atlas (`references.md`) makes this explicit

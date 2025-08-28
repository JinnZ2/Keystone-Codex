# Keystone‑Codex

A machine‑readable **library of keystone technologies** — the ecological, social, informational, material, and ethical systems that unlocked entire lineages and endure across crises.  
Designed to be **AI‑checkable** with explicit claims, evidence, and rule‑based proofs.

## Why
We want a culture engineered from the **best technologies of all ages** — Terra Preta and Indus plumbing sit alongside the lathe and the transistor, councils beside TCP/IP.  
The Codex encodes each candidate with machine‑verifiable fields and runs **proof checks** (longevity, replication, lineage unlock, decentralization, etc.).

## Install (no internet required)
```bash
python3 -V  # 3.8+
python3 src/prove.py          # score + prove each keystone
python3 src/build_graph.py    # output graph.json + graph.dot
python3 src/render_timeline.py# timeline.md
python3 src/validate.py       # light schema checks
```

## Folder layout
```
schema/          # JSON Schemas (lightweight validation targets)
rules/           # Rule thresholds for keystone proofs
data/            # Machine‑readable entries
src/             # Validators, proof engine, exporters
examples/        # Quick scripts
CITATIONS.md     # How to cite and add sources
```

## Add a keystone
Create a new JSON file under an appropriate domain subfolder in `data/` using the schema.
Then run:
```bash
python3 src/validate.py
python3 src/prove.py
```

If it passes thresholds, it will be marked `"is_keystone": true` with a proof trace.

## Output artifacts
- `proof_report.md` — human‑readable verdicts + traces
- `graph.json` — nodes/edges for downstream visualizers
- `graph.dot` — Graphviz dot file for diagrams
- `timeline.md` — date‑sorted list with metrics

## Design notes
- **Proofs as data**: Each item carries structured claims and evidence with quality weights.
- **Transparent thresholds**: See `rules/keystone_rules.json`.
- **No external deps**: pure Python stdlib; optional Graphviz if you choose to render `.dot`.
- **Offline‑first**: Suitable for rural/off‑grid workflows.

## Credits
Initiated by JinnZ2 × ChatGPT. MIT licensed.
```

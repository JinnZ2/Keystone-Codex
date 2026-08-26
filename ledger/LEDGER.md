# Hypothesis Ledger

Every falsification run, oldest first. Nothing here is edited after the fact — a claim that was falsified stays falsified in the record, and its revision appears as a later run. This is the file to read if you want to know what this project already tried and what the data did to it.

Generated from `ledger/runs.jsonl` by `src/falsify.py`.

## run-001-baseline

1 supported · 7 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H001` | **falsified** | 2 id mismatch(es) between catalogue and entries |
| `H002` | **falsified** | 15/15 unlock targets dangle (0 lineage terms declared) |
| `H003` | **falsified** | 3 entries state a longevity their era does not support |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.733 |
| `H005` | **falsified** | 3/8 domains below 1 encoded entries: economic, social, ethical |
| `H006` | **falsified** | 5/5 entries pass — the rubric is not rejecting anything |
| `H007` | **falsified** | phi-triads (2065) are not rarer than chance (null mean 2229.2, p=0.864) |
| `H008` | **falsified** | 3 declared evidence type(s) unused, 0 used but undeclared |

## run-002-post-repair

8 supported · 0 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H001` | supported | all 9 confirmed catalogue ids resolve to encoded entries |
| `H002` | supported | all 27 unlock targets resolve |
| `H003` | supported | all 9 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.770 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 7/9 pass, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (7147) indistinguishable from chance (null mean 8079.1, p=0.970) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

## run-003-full-pipeline

8 supported · 0 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H001` | supported | all 9 confirmed catalogue ids resolve to encoded entries |
| `H002` | supported | all 27 unlock targets resolve |
| `H003` | supported | all 9 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.770 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 7/9 pass, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (7147) indistinguishable from chance (null mean 8079.1, p=0.970) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

## run-004-merge-main

16 supported · 0 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H001` | supported | all 9 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H001` | supported | all 9 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H002` | supported | all 85 unlock targets resolve, no id collisions |
| `H002` | supported | all 85 unlock targets resolve, no id collisions |
| `H003` | supported | all 40 entries coherent within 25% (3 by declared basis) |
| `H003` | supported | all 40 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.804 |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.804 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 37/40 pass, 32% at ceiling, spread 0.380 — rubric discriminates |
| `H006` | supported | 37/40 pass, 32% at ceiling, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (7147) indistinguishable from chance (null mean 8079.1, p=0.970) — negative control holds |
| `H007` | supported | phi-triads (7147) indistinguishable from chance (null mean 8079.1, p=0.970) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |
| `H008` | supported | all 10 declared evidence types exercised |

## run-005-recent-finds

8 supported · 0 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H001` | supported | all 11 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H002` | supported | all 90 unlock targets resolve, no id collisions |
| `H003` | supported | all 42 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.805 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 39/42 pass, 31% at ceiling, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (9141) indistinguishable from chance (null mean 10415.0, p=0.983) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

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

## run-006-architecture-layer

9 supported · 3 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H-ARCH-1` | **falsified** | 42/42 entries declare no layer_role (100%) — the architecture layer exists and is empty |
| `H-ARCH-2` | supported | every runs_on target in 1 evaluable system(s) resolves to a present member |
| `H-ARCH-3` | **falsified** | 1 evaluable system(s), below the 2 needed for saturation to mean anything — with one reading the spread is zero by construction; 1/1 systems report full satisfaction — the report cannot tell an integrated system from an unchecked one; spread 0.000 — the report barely separates the systems it reads |
| `H-BYPASS` | _no data_ | data/evaluator_claims.json exists and holds 0 records — no data |
| `H001` | supported | all 11 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H002` | supported | all 90 unlock targets resolve, no id collisions |
| `H003` | supported | all 42 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.805 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 39/42 pass, 31% at ceiling, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (9141) indistinguishable from chance (null mean 10415.0, p=0.983) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

## run-006b-architecture-layer

9 supported · 3 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H-ARCH-1` | **falsified** | 42/42 entries declare no layer_role (100%) — the architecture layer exists and is empty |
| `H-ARCH-2` | supported | every runs_on target in 1 evaluable system(s) resolves to a present member |
| `H-ARCH-3` | **falsified** | 1 evaluable system(s), below the 2 needed for saturation to mean anything — with one reading the spread is zero by construction; 1/1 systems report full satisfaction — the report cannot tell an integrated system from an unchecked one; spread 0.000 — the report barely separates the systems it reads |
| `H-BYPASS` | _no data_ | data/evaluator_claims.json exists and holds 0 records — no data |
| `H001` | supported | all 11 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H002` | supported | all 90 unlock targets resolve, no id collisions |
| `H003` | supported | all 42 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.805 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 39/42 pass, 31% at ceiling, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (9141) indistinguishable from chance (null mean 10415.0, p=0.983) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

## run-20260922T165824Z

9 supported · 3 falsified

| Hypothesis | Verdict | Summary |
| --- | --- | --- |
| `H-ARCH-1` | **falsified** | 42/42 entries declare no layer_role (100%) — the architecture layer exists and is empty |
| `H-ARCH-2` | supported | every runs_on target in 1 evaluable system(s) resolves to a present member |
| `H-ARCH-3` | **falsified** | 1 evaluable system(s), below the 2 needed for saturation to mean anything — with one reading the spread is zero by construction; 1/1 systems report full satisfaction — the report cannot tell an integrated system from an unchecked one; spread 0.000 — the report barely separates the systems it reads |
| `H-BYPASS` | _no data_ | data/evaluator_claims.json exists and holds 0 records — no data |
| `H001` | supported | all 11 confirmed catalogue ids resolve to encoded entries; 24 entries indexed nowhere |
| `H002` | supported | all 90 unlock targets resolve, no id collisions |
| `H003` | supported | all 42 entries coherent within 25% (3 by declared basis) |
| `H004` | supported | every claim backed by ≥1 resolving ref; mean quality 0.805 |
| `H005` | supported | all 8 domains have ≥1 encoded entries |
| `H006` | supported | 39/42 pass, 31% at ceiling, spread 0.380 — rubric discriminates |
| `H007` | supported | phi-triads (9141) indistinguishable from chance (null mean 10415.0, p=0.983) — negative control holds |
| `H008` | supported | all 10 declared evidence types exercised |

## Notes

Corrections and clarifications appended to the ledger without rewriting the run they correct. A note never edits an earlier record; the earlier record and the note both stand, and a reader sees what was believed and what was said about it afterwards.

### N-001 — Role is not category: what SYSTEMS_ANALOGY.md assigned

_appended 2026-09-22 · concerns `U-H005-4`_

U-H005-4 is resolved and stays resolved. Social and governance are distinct DOMAINS, the argument for it holds, and hxaro and great_law_of_peace demonstrate the distinction. Nothing in that resolution is withdrawn here.

What this note adds is that the reading of SYSTEMS_ANALOGY.md carried in that resolution and in README.md -- that the document had "run the two together under one heading" -- describes a domain error the document was not making. Its architecture map assigns ROLES: "Social / Governance = Motherboard + Bus. Routes communication, connects components, regulates timing." Routing and timing is a function, not a category, and two categories sharing one function is not a conflation of the categories. A bus and a power supply are different roles; a governance council and a reciprocity network can both be doing routing.

Domain and role are now separate fields. schema/keystone.schema.json carries layer_role beside domain, and the crosstab in the first declared system shows them carrying different statements: reading the roles straight off SYSTEMS_ANALOGY.md's own example lists, BUS covers the domains {ethical, governance} and IO covers {economic, social}, so the map from domain to role is not one-to-one in the source itself. Ubuntu is filed in this corpus under 'ethical' and named by the source under Motherboard + Bus; the potlatch is filed under 'social' and named under the I/O system. Both are transcriptions, not readings.

The open question that replaces the correction is U-ARCH-1: which of the two a given assignment belongs to, when a source names a role and a corpus files a category, and what decides it. The integration report reports such a disagreement and resolves neither side.

### N-002 — Correction to N-001: where the misreading is carried

_appended 2026-09-22 · concerns `N-001`_

N-001 states that the reading it corrects is carried "in that resolution and in README.md". The README half is wrong. Searched 2026-09-22: README.md carries no sentence about social and governance being run together, and the phrase appears only in U-H005-4's resolution text in unknowns/register.json, which UNKNOWNS.md renders. N-001's substance is unaffected; only its pointer was wrong.

This is appended rather than fixed in place because twelve run records were written after N-001 and editing a line with runs after it is the history rewrite the append-only rule exists to prevent. The check that caught it is the same one: a note may be corrected in place only while it is still the last record, and it was not.

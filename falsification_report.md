# Falsification Report
_Run `run-003-full-pipeline` · 8 supported · 0 falsified_

A falsified hypothesis is a result, not a bug. The loop is: state the claim, run it, and when the data says no, edit the claim rather than the data. Open questions land in `UNKNOWNS.md`; the run history is in `ledger/LEDGER.md`.

## H001 — ✅ supported

**Claim.** A keystone has exactly one identity: the id in data/shadow_catalogue.json and the id of its encoded entry are the same string.

**Prediction.** Every catalogue row with status 'confirmed' resolves to an encoded entry with the same id, and every encoded entry appears in the catalogue.

**Test.** `id_consistency` — all 9 confirmed catalogue ids resolve to encoded entries

## H002 — ✅ supported

**Claim.** The `unlocks` field states a lineage claim that can be checked: every target names something the repository defines.

**Prediction.** Every unlock target resolves either to another encoded keystone id or to a term declared in rules/lineage_terms.json.

**Test.** `unlock_resolution` — all 27 unlock targets resolve

## H003 — ✅ supported

**Claim.** metrics.longevity_years is derivable from the entry's own era, within a quarter.

**Prediction.** For every entry, |longevity_years - (era.end - era.start)| / span <= 0.25, unless the entry declares a longevity_basis explaining what narrower thing it measures.

**Test.** `era_longevity_coherence` — all 9 entries coherent within 25% (3 by declared basis)

<details><summary>detail</summary>

- great_law_of_peace: 500yr vs 825yr span — declared basis: Conservative floor, not era span. The founding date is genuinely contested — estimates range from the 12th century to c. 1450, and the 1142 eclipse-based date is disputed. 500 years measures from the latest credible founding estimate to the present, so the figure understates rather than overstates. Under the earliest estimates the true figure exceeds 800 years. See U-H003-1.
- indus_plumbing: 600yr vs 900yr span — declared basis: Attested operational span, not era span. The era brackets the Mature Harappan period through to the end of urban occupation (c. 2600–1700 BCE); the drainage systems are evidenced as maintained infrastructure for roughly the first 600 years, after which the archaeological signal is of decline and disuse rather than operation. Maintained and merely extant are different states and this entry reports the first.
- terra_preta: 500yr vs 2500yr span — declared basis: Persistence after abandonment, not duration of practice. The era covers the period during which the soils were being made (c. 1000 BCE to 1500 CE); the keystone property being measured is that fertility survives roughly 500 years without further input, which is what modern field trials on abandoned sites demonstrate. Duration of practice and duration of effect are different numbers and this entry reports the second.

</details>

## H004 — ✅ supported

**Claim.** No claim in the codex floats: each is tied to at least one evidence item that actually exists in its entry, and the corpus averages adequate source quality.

**Prediction.** Every claim has >= 1 evidence_ref resolving to an evidence id in the same entry, and mean evidence quality across the corpus is >= 0.7.

**Test.** `evidence_floor` — every claim backed by ≥1 resolving ref; mean quality 0.770

## H005 — ✅ supported

**Claim.** The encoded corpus covers the domains the schema declares — the codex is not quietly a catalogue of one or two kinds of technology.

**Prediction.** Every domain in the schema enum has at least one fully encoded entry.

**Test.** `domain_coverage` — all 8 domains have ≥1 encoded entries

<details><summary>detail</summary>

- ecological: 1 encoded
- economic: 1 encoded
- social: 1 encoded
- governance: 1 encoded
- information: 1 encoded
- material: 1 encoded
- ethical: 1 encoded
- infrastructure: 2 encoded

</details>

## H006 — ✅ supported

**Claim.** The keystone rule set discriminates: run over the corpus it separates entries rather than admitting all of them.

**Prediction.** No more than 90% of encoded entries score as keystones, and the spread between the highest and lowest score is at least 0.2.

**Test.** `rubric_discrimination` — 7/9 pass, spread 0.380 — rubric discriminates

<details><summary>detail</summary>

- budj_bim: 1.0 (pass)
- great_law_of_peace: 1.0 (pass)
- quipu: 1.0 (pass)
- terra_preta: 1.0 (pass)
- indus_plumbing: 0.86 (pass)
- kula_ring: 0.86 (pass)
- nunuku_covenant: 0.86 (pass)
- hxaro: 0.68 (fail)
- lathe: 0.62 (fail)
- pass_fraction=0.78 (max 0.9), score_spread=0.380 (min 0.2)

</details>

## H007 — ✅ supported

**Claim.** Golden-ratio spacing among technology emergence dates in this catalogue is indistinguishable from chance, and the phi detector in src/shadow_search.py is retained as a negative control rather than as a finding.

**Prediction.** The number of phi-spaced triads among catalogue start dates does not exceed the number found in the same count of dates drawn uniformly from the same window, at p < 0.05 over 300 seeded trials.

**Test.** `phi_significance` — phi-triads (7147) indistinguishable from chance (null mean 8079.1, p=0.970) — negative control holds

<details><summary>detail</summary>

- n=81 dates spanning -50000..2001
- observed phi-triads (within 10%): 7147
- null model mean: 8079.1 over 300 seeded trials
- null range: 6809..8839
- p = 0.9701 (alpha 0.05)

</details>

**Revision history.**
- `run-001-baseline` — Falsified against a seeded uniform null model: observed 2065 phi-triads vs null mean 2229.2, p = 0.864. The direction of the test was inverted along with the claim, so a future corpus that genuinely does show phi structure will falsify the replacement in turn.

## H008 — ✅ supported

**Claim.** The evidence taxonomy in CITATIONS.md describes how the codex actually works — every declared type is used, and no entry uses a type the taxonomy does not declare.

**Prediction.** Each of the nine declared evidence types appears at least once in the encoded corpus, and every type used is declared.

**Test.** `taxonomy_exercised` — all 10 declared evidence types exercised

<details><summary>detail</summary>

- declared: 10, used: 10

</details>

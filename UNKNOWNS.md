# Unknowns Register

Questions this project does not have answers to. Most were opened by a hypothesis that failed; some were pinned by hand because they matter and no test reaches them yet.

**Open** — live, and worth someone's time. **Resolved** — answered, with the answer written down. **Dormant** — the test that raised it stopped asking, and nobody ever answered it. Dormant is not resolved, and the two are kept apart on purpose: a question that goes quiet because the data changed under it is still open, it just lost its alarm.

_Reconciled at `run-005-recent-finds` · 9 open · 11 resolved · 0 dormant_

## Open

### U-C-1 — What makes two occurrences of a technology independent replications rather than one tradition?
- Raised by **curated** · first seen `run-002-post-repair` · **pinned**
- Trigger: budj_bim scores replication_regions=2 by counting Brewarrina; kula_ring scores 1 by refusing to count Melanesian ceremonial exchange rings. The two cases are close to parallel and the entries apply different standards to them.

### U-C-2 — Which era values in this codex would current archaeological methods revise, if anyone checked?
- Raised by **curated** · first seen `run-002-post-repair` · **pinned**
- Trigger: Airborne LIDAR, sedimentary and ancient DNA, dental calculus proteomics, and Bayesian radiocarbon modelling have overturned settlement-scale and chronology claims across the field since roughly 2018. No era value in data/ has been rechecked against any of them.

### U-H001-2 — Which registry indexes the encoded corpus — data/shadow_catalogue.json, data/candidates.json, or both? They currently overlap in zero rows.
- Raised by **H001** · first seen `run-004-merge-main` · **pinned**
- Trigger: Merging main produced two candidate registries whose rows overlap in zero ids, while 24 of 40 encoded entries appear in neither.

### U-H003-2 — How old is hxaro?
- Raised by **H003** · first seen `run-002-post-repair` · **pinned**
- Trigger: data/social/hxaro.json enters 125 years as a deliberate floor and takes a failing score rather than assert a number the evidence does not support.

### U-H003-3 — When was the Kayanerenkó:wa founded?
- Raised by **H003** · first seen `run-002-post-repair` · **pinned**
- Trigger: great_law_of_peace declares a longevity_basis of 500 years as a floor because the founding date is contested.

### U-H006-2 — Does the rubric discriminate correctly, or merely discriminate?
- Raised by **H006** · first seen `run-002-post-repair` · **pinned**
- Trigger: v1.1 rejects hxaro (0.68) and the lathe (0.62), and both rejections are about the surviving record rather than about the technology.

### U-H006-3 — Is claim_coverage a floor the corpus genuinely clears, or dead weight?
- Raised by **H006** · first seen `run-004-merge-main` · **pinned**
- Trigger: claim_coverage fails for 0 of 40 entries — it contributes a constant 0.12 to every score and ranks nothing.

### U-H006-4 — Are the inert criteria (claim_coverage) floors the corpus genuinely clears, or dead weight nobody has tested?
- Raised by **H006** · first seen `run-004-merge-main`
- Trigger: 1 criterion/criteria fire for no entry in the corpus

### U-H007-2 — Do the cross-domain resonance and shadow-lineage detectors survive the same null model the phi detector failed?
- Raised by **H007** · first seen `run-002-post-repair` · **pinned**
- Trigger: only one of the four pattern detectors in src/shadow_search.py has ever been tested against chance.

## Resolved

### U-H001-1 — Is the catalogue id or the entry id the canonical name for a keystone, and what enforces the link?
- Raised by **H001** · first seen `run-001-baseline`
- Trigger: confirmed-status catalogue rows and encoded entries drifted apart
- **Resolution** (`run-002-post-repair`): The encoded entry is canonical; the catalogue indexes it. The Great Law of Peace was filed as `haudenosaunee_council` in the catalogue and `great_law_of_peace` in the entry — the entry id won and the catalogue was corrected. H001 now checks the link in both directions, so the two cannot drift again without a run failing.

### U-H002-1 — Are `unlocks` pointers to other keystones, or names of downstream technology families? The field is being used for both.
- Raised by **H002** · first seen `run-001-baseline`
- Trigger: no unlock target resolved to anything the repo defines
- **Resolution** (`run-002-post-repair`): Both, and now explicitly. A target is either another entry id (a direct descent claim) or a term declared in rules/lineage_terms.json (a family claim). The vocabulary file was created with 27 terms covering every target in the corpus, and build_graph.py renders the two kinds as different node shapes rather than silently inventing nodes for free text.

### U-H003-1 — Does longevity_years mean attested continuous use, survival of the artefact, or revivability? Each gives a different number for the same technology.
- Raised by **H003** · first seen `run-001-baseline`
- Trigger: stated longevity and era span disagreed with no declared basis
- **Resolution** (`run-002-post-repair`): It is not one thing, and entries now have to say which one they mean. Three bases are in use: persistence after abandonment (terra_preta — the era covers 2500 years of practice while the metric reports ~500 years of retained fertility), attested operational span (indus_plumbing — 600 of 900 era years evidenced as maintained rather than merely extant), and conservative floor under a contested start date (great_law_of_peace, kula_ring, nunuku_covenant, hxaro). Any entry drifting more than 25% from its era span must declare a longevity_basis or fail H003.

### U-H005-1 — What keystone belongs in the 'economic' domain, and why has nothing been encoded there yet — absence of candidates, or absence of attention?
- Raised by **H005** · first seen `run-001-baseline`
- Trigger: domain 'economic' had 0 encoded entries
- **Resolution** (`run-002-post-repair`): Absence of attention. The catalogue already listed seven economic candidates that nobody had written up. kula_ring is now encoded.

### U-H005-2 — What keystone belongs in the 'social' domain, and why has nothing been encoded there yet — absence of candidates, or absence of attention?
- Raised by **H005** · first seen `run-001-baseline`
- Trigger: domain 'social' had 0 encoded entries
- **Resolution** (`run-002-post-repair`): The domain had never been used because no source document in this repo distinguished it from governance. hxaro is now encoded there, which also settles U-H005-4.

### U-H005-3 — What keystone belongs in the 'ethical' domain, and why has nothing been encoded there yet — absence of candidates, or absence of attention?
- Raised by **H005** · first seen `run-001-baseline`
- Trigger: domain 'ethical' had 0 encoded entries
- **Resolution** (`run-002-post-repair`): Absence of attention. nunuku_covenant is now encoded, with its failure mode stated as a claim rather than omitted.

### U-H005-4 — Are 'social' and 'governance' distinct domains, or one domain listed twice in the schema enum?
- Raised by **H005** · first seen `run-001-baseline`
- Trigger: governance was populated while social had never been used
- **Resolution** (`run-002-post-repair`): Distinct, and the distinction is now demonstrated rather than asserted. Governance is binding collective decision-making with authority behind it (great_law_of_peace). Social is relational infrastructure with no authority at all — obligation networks, risk pooling, cohort structure (hxaro). Every prose document in this repo, references.md and SYSTEMS_ANALOGY.md included, had run the two together under one heading, which is why the enum slot sat empty.

### U-H006-1 — Is the corpus genuinely uniform in quality, or is the rubric too easy? A rubric only tested on entries chosen because they are keystones cannot tell you.
- Raised by **H006** · first seen `run-001-baseline`
- Trigger: 100% of entries passed under rules v1.0
- **Resolution** (`run-002-post-repair`): The rubric was too easy. Under v1.0 all five entries passed and four scored a perfect 1.0, because every criterion read a number the author had typed and none read the evidence behind it. v1.1 keeps those four at reduced weight and adds evidence_strength, evidence_independence, and claim_coverage. Seven of nine now pass with a spread of 0.38. Whether it discriminates *correctly* is a different question — see U-H006-2.

### U-H007-1 — Does any temporal-spacing regularity survive a null model, or is every such pattern an artefact of the number of dates and the width of the window?
- Raised by **H007** · first seen `run-001-baseline`
- Trigger: the phi detector's output was indistinguishable from random dates
- **Resolution** (`run-002-post-repair`): For phi specifically: no. p = 0.970 against a seeded uniform null over 300 trials; the catalogue produces fewer phi-triads than random dates in the same window. The claim was replaced rather than weakened and the detector is retained as a negative control. The general question is not closed — it is now U-H007-2.

### U-H008-1 — Under what conditions does the codex accept oral tradition as evidence, and at what quality weight? The type is declared but has never been used.
- Raised by **H008** · first seen `run-001-baseline`
- Trigger: an evidence type the project claims to admit had zero uses
- **Resolution** (`run-002-post-repair`): Accepted on transmission control, not on medium. CITATIONS.md now states the criterion, and five entries use the type at qualities from 0.7 to 0.85. A law recited under ceremonial verification by trained holders (great_law_of_peace, 0.8) weighs more than a general community account (hxaro, 0.7). Budj Bim is the calibration case: Gunditjmara tradition asserted the eel traps' antiquity, and the radiocarbon dates arrived later and confirmed it.

### U-H008-2 — Is the unused half of the evidence taxonomy aspirational or dead vocabulary?
- Raised by **H008** · first seen `run-001-baseline`
- Trigger: 3 of 9 declared evidence types were unused
- **Resolution** (`run-002-post-repair`): It was dead vocabulary; it is now exercised. All nine original types appear in the corpus, and ethnographic_record was added to the taxonomy because the anthropological entries needed a category that peer_reviewed_study was being stretched to cover.

## Dormant

_None._

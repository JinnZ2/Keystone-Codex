# Unknowns Register

Questions this project does not have answers to. Most were opened by a hypothesis that failed; some were pinned by hand because they matter and no test reaches them yet.

**Open** — live, and worth someone's time. **Resolved** — answered, with the answer written down. **Dormant** — the test that raised it stopped asking, and nobody ever answered it. Dormant is not resolved, and the two are kept apart on purpose: a question that goes quiet because the data changed under it is still open, it just lost its alarm. **Frame-level** — not a gap in a value but a question about the frame the values are read in; these do not resolve by filling a field, so they are listed apart rather than mixed into the work queue.

Some entries are marked *target-level* or *rendering-level*. A rendering is a specific method or claim; a target is what it was aimed at. Falsifying a rendering closes the rendering. See CLAUDE.md RULE 1.

_Reconciled at `run-006b-architecture-layer` · 13 open · 11 resolved · 0 dormant · 9 frame-level_

## Frame-level

_Questions about the frame rather than about a value in it: where the entry boundary was cut, what a metric is being read as, what the rubric has no row for. These are kept out of the Open list because they do not resolve by filling a field. Each declares the frame it was raised from._

### F1 — Where was the boundary cut that makes this one entry, and on what grounds?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Every entry is a node drawn around a piece of a continuous system, and the cut is a claim that nothing is being reported about. Terra preta is soil, waste handling, settlement pattern and fire practice; the codex carries one entry. schema/keystone.schema.json now has a separation_claim field and 0 entries declare it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F2 — Do longevity_years and replication_regions measure fit, or do they measure how long something was carried and how far it was pushed?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: The rubric weights longevity at 0.18 and replication at 0.14 and neither distinguishes a technology adopted because it worked in the receiving conditions from one that arrived with a population or was installed by a party with power over the receiving population. schema now has a spread_mechanism field (FIT / CARRIED / IMPOSED / UNKNOWN) and 0 entries declare it. Until it is declared, a high replication count and a high score are the same number read twice.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F3 — Where the holders of a technology were destroyed, the record thins for a reason. In which direction does that bias run, and by how much?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Distinct from U-H006-2, which asks whether the rubric discriminates correctly on the surviving record. This asks about the record itself, and the difference is that the sign is known in advance: conquest and displacement remove holders, transmission and documentation both, so the deficit is not noise distributed evenly. The evidence_strength and evidence_independence criteria together carry 0.34 of the rubric and both read the surviving record with no term for this.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F4 — Does this entry's attribution to this region and era rest on a text naming the technology, or on dating of physical remains?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: evidence.type records what backs an individual claim. Nothing records what backs the entry's own identity, and the two are different questions: a corpus that admits textual attribution on the same footing as material dating will over-represent the technologies of literate societies without any single entry being wrong. schema now has an attribution_basis field (MATERIAL / TEXTUAL / ORAL / CONTESTED) and 0 entries declare it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F5 — What does this technology require in order to operate, and is its endurance being read without that?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Endurance scored with no dependency footprint is endurance measured on one side of the ledger. A technology that lasted 500 years while consuming little and one that lasted 500 years on continuous input score the same under longevity_years. schema now has a dependency_load field and 0 entries declare it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F6 — What conditions was this technology selected against — what is its operating envelope?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Nothing in the codex records the constraints an entry passed through, so nothing distinguishes a technology that held under stress from one that was never stressed. This is the field that would let 'endured across crises' in the project's own first sentence be checked rather than asserted. schema now has an adapted_to field and 0 entries declare it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F7 — What does the rubric have no row for?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Seven criteria: longevity, replication, unlocks, decentralization, evidence strength, evidence independence, claim coverage. None reads how the technology failed, what it cost to deliver, or what it consumed while running. A dimension with no row cannot score low; it scores nothing, and an entry weak on it is indistinguishable from an entry strong on it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F8 — Is decentralization a property of these technologies, or a selection preference of this codex filed as a property?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: decentralization_score is weighted 0.10 with a threshold of 0.5, so a centralized technology loses points for being centralized. Nothing in the repository establishes that decentralization is a keystone property rather than a value held by the people assembling the corpus. The criterion reads a number the author typed, which is the same defect H006 found in the retired v1.0 rubric and repaired for the four metric criteria by adding evidence-reading criteria beside them, not by fixing the four.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

### F9 — Can this loop raise a question about a row it never opened?
- Raised by **external-review** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Every hypothesis in hypotheses/ tests a field that exists. The falsification loop reads the corpus through the schema, so a dimension the schema has no field for produces no failure anywhere and leaves no trace of its absence. That makes F1 through F8 unreachable from inside: each of them names something the loop was structurally unable to notice. This is the frame-level question that governs the other eight, and no test in this repository reaches it.
- Reviewer frame: external review 2026-09-22, read against SYSTEMS_ANALOGY.md and the coupling-default frame

## Open

### U-ARCH-1 — When a source assigns a ROLE and a corpus files a CATEGORY, which one is the entry's, and what decides it?
- Raised by **architecture-layer** · first seen `run-006-architecture-layer` · **pinned**
- Trigger: Opened by ledger note N-001. domain and layer_role are now separate fields and they disagree in the first declared system: ubuntu_philosophy is filed 'ethical' and named by SYSTEMS_ANALOGY.md under Motherboard + Bus; gift_economy is filed 'social' and named under the I/O system. The integration report reports the disagreement and resolves neither side, because a role may be relational -- a property of the assembly an entry sits in rather than of the entry -- in which case the same entry carries different roles in different systems and neither field is wrong. Nothing in the repository establishes whether that is so. Two artifacts already in the repository disagree about it and neither declares that it is answering it. `.fieldlink.json`'s layer_map assigns layers by DOMAIN (motherboard_bus <- {social, governance}, bios_firmware <- {ethical}) and lists gift_economy under motherboard_bus and ubuntu_philosophy under bios_firmware. SYSTEMS_ANALOGY.md names the potlatch under the I/O system and Ubuntu under Motherboard + Bus. Those are the same two entries the first declared system flags, reached from the opposite direction: the fieldlink map derives role from domain, the source assigns role directly, and where they differ src/health.py prints a verdict ('weakest layer: bios_firmware') computed on the derived assignment. Neither file is changed by the architecture layer and neither is wrong on its own terms; what is missing is a statement of which assignment is the entry's.

### U-C-1 — What makes two occurrences of a technology independent replications rather than one tradition?
- Raised by **curated** · first seen `run-002-post-repair` · **pinned**
- Trigger: budj_bim scores replication_regions=2 by counting Brewarrina; kula_ring scores 1 by refusing to count Melanesian ceremonial exchange rings. The two cases are close to parallel and the entries apply different standards to them.

### U-C-2 — Which era values in this codex would current archaeological methods revise, if anyone checked?
- Raised by **curated** · first seen `run-002-post-repair` · **pinned**
- Trigger: Airborne LIDAR, sedimentary and ancient DNA, dental calculus proteomics, and Bayesian radiocarbon modelling have overturned settlement-scale and chronology claims across the field since roughly 2018. No era value in data/ has been rechecked against any of them.

### U-H-ARCH-1-1 — Can this corpus be read as an architecture, and what would have to be declared before that question has an answer?
- Raised by **H-ARCH-1** · first seen `run-006-architecture-layer`
- Trigger: the rendering was falsified (42/42 entries declare no layer_role (100%) — the architecture layer exists and is empty); the target it was aimed at -- whether this corpus can be read as an architecture rather than as a list -- is not closed by that

### U-H-ARCH-3-1 — Does the integration report discriminate between assemblies, or does it only describe the one set that has been declared so far?
- Raised by **H-ARCH-3** · first seen `run-006-architecture-layer`
- Trigger: the rendering was falsified (1 evaluable system(s), below the 2 needed for saturation to mean anything — with one reading the spread is zero by construction; 1/1 systems report full satisfaction — the report cannot tell an integrated system from an unchecked one; spread 0.000 — the report barely separates the systems it reads); the target it was aimed at -- whether the integration report discriminates between assemblies -- is not closed by that

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
- Raised by **H007** · first seen `run-002-post-repair` · **pinned** · rendering-level
- Trigger: only one of the four pattern detectors in src/shadow_search.py has ever been tested against chance.
- Rendering of: H007

### U-H007-3 — Does cross-domain systemic coupling exist among these technologies, and what would measure it?
- Raised by **H007** · first seen `run-006-architecture-layer` · **pinned** · target-level
- Trigger: CLAUDE.md RULE 1 applied retroactively. The phi detector was the rendering and it was falsified (p = 0.864 at run-001-baseline, 0.983 at run-005-recent-finds). H007 now reports supported because the claim was replaced by its own negation, which is a true statement about the detector and no statement about the target. Nothing in this repository has measured cross-domain coupling. U-H007-2 asks whether two further detectors survive the same null; that is also rendering-level and also does not reach this.
- Target of: H007

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

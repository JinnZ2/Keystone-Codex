# Anthropology Frontier

What has changed in the field recently, and what it does to this codex.

This is a working document, not a literature review. Each section names a method or
a finding, then says which entry, metric, or hypothesis it puts pressure on. A
method that cannot change anything here does not belong on this page.

The reason to keep it: the codex encodes dates, spans, and replication counts as if
they were settled. Most are not. Several of the numbers in `data/` are one dataset
away from being wrong, and it is better to say which ones.

---

## Methods

### Airborne LIDAR

Laser scanning through forest canopy has repeatedly found settlement at densities
the literature had ruled out. Angkor's urban extent (Evans et al. 2013), the Maya
lowlands (Canuto et al. 2018, ~61,000 structures across Petén), the Casarabe sites
in the Llanos de Mojos (Prümers et al. 2022), and the Upano Valley platform-and-road
complex in Amazonian Ecuador (Rostain et al. 2024).

**Pressure on this codex.** The Upano result is the sharpest warning: a settlement
system with tens of kilometres of engineered roads, in a region the standard account
described as sparsely occupied by mobile groups. `terra_preta` is encoded with
`replication_regions: 3` and a decentralization score of 0.8 — both assume a
dispersed, small-settlement Amazonia. If Amazonian dark earths turn out to be
associated with dense planned settlement, "decentralized" is describing our former
ignorance of the political system rather than the political system.

Added to the catalogue as `upano_valley_urbanism`. Not yet encoded, because the
entry's honest metrics are not yet knowable.

### Ancient DNA, and sedimentary DNA

Population genomics has replaced diffusionist accounts of technology spread with
tested models of movement — sometimes confirming migration where the archaeology
had settled on cultural transmission, sometimes the reverse. Sedimentary aDNA
detects presence from cave floor sediment with no skeletal material at all.

**Pressure on this codex.** `replication_regions` currently means "appeared in N
regions", which quietly assumes independent invention. aDNA can distinguish a
technology that moved with people from one that was reinvented — the exact
distinction **U-C-1** says the codex cannot presently make. This is the most likely
route to actually resolving that unknown rather than restating it.

### Dental calculus: proteomics, starch, DNA

Hardened plaque preserves food proteins, starch granules, and oral microbiome DNA
for millennia. Milk peptides have established dairying in specific individuals long
before the lactase persistence allele spread (Warinner et al. and subsequent work).

**Pressure on this codex.** Direct evidence of what people ate, from the person who
ate it, at a resolution site-level plant remains cannot reach. Bears on any
subsistence-technology entry, and would give `chuno` an evidence base far stronger
than the ethnographic account it would currently be encoded on.

### Bayesian radiocarbon modelling

Chronological modelling that combines dates with stratigraphic priors, tightening
event sequences from centuries to decades and testing whether transitions were
gradual or abrupt.

**Pressure on this codex.** Directly on `era` and on `metrics.longevity_years`,
which H003 now requires be either derivable from the era or explained. Three
entries carry a `longevity_basis` precisely because their dating is soft:
`great_law_of_peace` (**U-H003-3**), `nunuku_covenant`, and `kula_ring`. Bayesian
modelling of the relevant sequences is the concrete way those floors become
estimates.

### Zooarchaeology by mass spectrometry (ZooMS)

Species identification from collagen peptides in bone fragments too small to
identify morphologically — turning excavation waste back into data.

**Pressure on this codex.** `budj_bim` rests on channel dating and oral tradition.
Faunal identification of eel remains in associated deposits would convert "these are
eel traps" from a strong inference into a direct measurement.

### Isotope provenance

Strontium, oxygen, and lead ratios locate where a person or material came from,
mapping mobility and sourcing networks.

**Pressure on this codex.** `kula_ring` scores `replication_regions: 1` and its
oldest evidence item — shell valuable distribution — is weighted 0.6, the lowest in
the corpus. Provenance work on Massim shell valuables would test whether the circuit
is older than its ethnographic attestation, which is what its `longevity_basis`
declines to assert.

### High-resolution paleoclimate proxies

Speleothems, varves, and ice cores now give annual to decadal resolution, making it
possible to test collapse narratives against what the climate actually did rather
than against what a chronicle said it did.

**Pressure on this codex.** The codex scores longevity but has no vocabulary for
*why* something ended. `cahokia` is in the catalogue partly as a collapse case;
`nunuku_covenant` encodes its failure mode as a claim. A `failure_mode` field is the
obvious next schema addition and is deliberately not being added until there are
enough entries to shape it.

---

## Shifts in framing

### The stage model keeps failing

Agriculture → surplus → sedentism → hierarchy → monuments does not describe
Göbekli Tepe and the Taş Tepeler enclosures, Poverty Point, Budj Bim, or the
Northwest Coast. Graeber and Wengrow's *The Dawn of Everything* (2021) pushed this
into general argument — that societies experimented with political form, sometimes
seasonally, rather than climbing a ladder. The book is contested in its particulars
and the underlying counter-examples are not.

**Pressure on this codex.** `data/infrastructure/budj_bim.json` is encoded partly
for this reason, and `SYSTEMS_ANALOGY.md` should be read with it in hand: the
computer-architecture metaphor is useful for arguing that integration beats
supremacy, and it carries a hidden assumption that components are assembled in a
fixed order. The evidence says the order is not fixed.

### Amazonia is engineered, not pristine

Dark earths, geoglyphs, causeways, raised fields, and managed tree assemblages —
the "untouched rainforest" of mid-20th-century ecology is substantially a
post-epidemic landscape, and the trees themselves show domestication signatures.

**Pressure on this codex.** Directly supports `terra_preta`. It also means the
"pristine baseline" framing that regenerative agriculture arguments often reach for
is itself the artefact.

### Traditional ecological knowledge as data

Fire regimes, fishery management, and species behaviour held in community knowledge
are increasingly treated as evidence rather than as context — sometimes producing
results that published science had missed.

**Pressure on this codex.** This is the shift `oral_tradition_encoded` exists to
serve. It went unused for a year until H008 caught it (**U-H008-1**); five entries
use it now. Budj Bim is the case that settles the argument: Gunditjmara tradition
asserted the eel traps' antiquity, and radiocarbon confirmed it.

### Collapse usually means decentralization

Depopulation, political fragmentation, and abandonment of monumental construction
are different events, and the collapse literature increasingly separates them.

**Pressure on this codex.** `longevity_years` conflates all three. `indus_plumbing`
declares a basis distinguishing "maintained" from "extant" for exactly this reason;
it is the only entry that does.

---

## Work list

Ordered by how much a result would change:

1. **Encode `budj_bim`'s sibling.** `brewarrina_fish_traps` is in the catalogue.
   Encoding it is the empirical route into **U-C-1**, since the two systems are the
   codex's clearest test of what independent replication means.
2. **A `failure_mode` field.** `nunuku_covenant` demonstrates that a technology's
   boundary conditions are engineering content. Needs three or four more entries
   before the field can be designed rather than guessed.
3. **Null-model the remaining detectors.** **U-H007-2**. The phi detector failed;
   resonance and shadow lineages have never been tested and have a known
   tokenisation artefact.
4. **An independence criterion for `replication`.** Or drop the criterion. It carries
   0.14 of the score on a judgement the codex cannot currently defend.
5. **Recheck era values against current chronologies.** **U-C-2**. Nothing in `data/`
   has been checked against anything published since it was written.
6. **Encode the governance candidates.** `gadaa` and `xeer` are both live systems
   with substantial literature, and both test whether the rubric's
   `decentralization_score` means anything precise.

## Candidate hypotheses

Not yet added to `hypotheses/`, sketched here so they are not lost:

- **H009 — recency bias.** Median entry era-start should not drift toward the
  present as the corpus grows. Easy to test, and would catch the codex quietly
  becoming a history of the last two millennia.
- **H010 — evidence-type independence.** No entry should have all its evidence
  produced by a single research tradition. `evidence_independence` counts type
  labels, which is a weaker check than it looks.
- **H011 — region concentration.** No macro-region should supply more than a stated
  share of encoded entries. Requires a region taxonomy the repo does not have, and
  writing one is itself a decision worth arguing about in public.

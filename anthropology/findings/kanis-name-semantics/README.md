# Kültepe/Kaniš name semantics — relational corpus design

Deep-research package compiled 30 September 2026. Encoded as
`data/information/kanis_merchant_archives.json`.

The finding that changed the codex is methodological: **build a relational
prosopographic corpus, not a list of translated names.** The unit chain is
name → person → attestation → document → family/network → semantic coding,
with ordinary Old Assyrian vocabulary as a control. Language assignment is
not ethnicity (Goedegebuure 2008). Most pilot names in this pass are not
yet statistically usable.

`pilot_names.json` is the seed table. `sources/` holds the scholar-export CSVs
the pass was built from.

A later pass resolved **Kt 86/k 41** against Veenhof KT 12 no. 3: eleven names,
all hapaxes or near-hapaxes, which Kloekhorst does not recognize as Kanišite
Anatolian. Encoded as `kt86k41.json`. Pikašnurikizi and Taripiazi are now
tablet-anchored without gaining a gloss. The next test is whether other small
tablets show the same hapax-cluster distribution — a genre question, not an
etymology question.

Pressure on this codex is recorded in `anthropology/FRONTIER.md` and as **U-C-4**.
The economic system the tablets record is shadow-catalogued as
`karum_credit_trade` and is not encoded, so the archive is not silently
scored as a bank.

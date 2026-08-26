# CITATIONS

Each entry under `data/<domain>/` carries an `evidence` array. Prefer primary and
authoritative sources. Use stable identifiers (DOI/ISBN/handle) where one exists —
and omit the `uri` field rather than guess at one.

Every `evidence_refs` entry on a claim must name an evidence `id` in the same file.
`src/falsify.py` (H004) checks this; a ref that does not resolve turns an evidenced
claim into a bare assertion without anyone noticing.

## Evidence types

| Type | Use for |
| --- | --- |
| `archaeological_record` | Excavated material, site reports, artefact distributions |
| `radiocarbon_date` | Published dates with laboratory context and calibration |
| `peer_reviewed_study` | Journal articles and scholarly monographs |
| `ethnographic_record` | Systematic fieldwork accounts, named observer and period |
| `oral_tradition_encoded` | Knowledge held and transmitted by a community as its own record |
| `primary_text` | Documents contemporary with the subject, including recensions and testimony |
| `engineering_record` | Drawings, patents, specifications, surviving mechanisms |
| `standards_spec` | Published standards and their revision history |
| `replication_record` | Independent reproduction of the effect outside its origin context |
| `field_measurement` | Direct measurement of a surviving or reconstructed system |

## On oral tradition

`oral_tradition_encoded` was declared in the first version of this file and went
unused for the repository's first year — the codex claimed an openness its data did
not practise. H008 catches that, and the type is now in use across five entries.

It is not a weaker category by default. A law recited under ceremonial verification
by trained holders, or a partnership genealogy attached to a named object, is a
controlled transmission channel with error correction built in. Weight the specific
source on how it is transmitted and verified, not on whether it was ever written
down. Budj Bim is the standing example: Gunditjmara tradition asserted the eel
traps' antiquity long before the radiocarbon dates arrived, and the dates confirmed
the tradition.

Where a community holds the knowledge, attribute it to that community. Do not
launder it through the first outsider who published it.

## Minimal example

```json
{
  "id": "terra_preta",
  "evidence": [
    {
      "id": "e1",
      "type": "peer_reviewed_study",
      "source": "Glaser & Woods (2004) Amazonian Dark Earths",
      "uri": "doi:10.1007/978-3-662-05568-0",
      "quality": 0.9
    }
  ],
  "claims": [
    { "id": "c1", "statement": "...", "evidence_refs": ["e1"] }
  ]
}
```

## Quality weights

`quality` is a judgement about the source, in [0, 1]. It feeds the
`evidence_strength` criterion in `rules/keystone_rules.json`, so inflating it
inflates a verdict. Rough calibration:

- **0.85–1.0** — direct, dated, independently checkable; the claim is what the source is about
- **0.7–0.85** — solid scholarship or well-transmitted community record, some inference to the claim
- **0.5–0.7** — indirect, contested, or the claim is a secondary reading of the source
- **below 0.5** — do not carry the claim on it alone

If an entry cannot reach the evidence floor honestly, let it fail. `data/social/hxaro.json`
is kept failing on purpose for exactly this reason.

# CITATIONS

Each `data/*.json` includes a `evidence` array. Prefer primary/authoritative sources.
Use stable identifiers (DOI/ISBN/handle) when possible.

Evidence types:
- archaeological_record
- peer_reviewed_study
- primary_text
- engineering_record
- replication_record
- radiocarbon_date
- standards_spec
- field_measurement
- oral_tradition_encoded

Minimal example:
```json
{
  "id": "terra_preta",
  "evidence": [
    {
      "id": "e1",
      "type": "peer_reviewed_study",
      "source": "Glaser & Woods (2004) - Amazonian Dark Earths",
      "uri": "doi:10.1007/978-3-662-05568-0",
      "quality": 0.9
    }
  ]
}
```

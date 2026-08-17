#!/usr/bin/env python3
"""
Scaffold a new keystone entry with a valid template.
Usage: python3 -m src new <domain> <id>
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(__file__))

VALID_DOMAINS = [
    "ecological", "economic", "social", "governance",
    "information", "material", "ethical", "infrastructure"
]

TEMPLATE = {
    "id": "",
    "name": "",
    "domain": "",
    "region": "",
    "era": {"start": 0, "end": 0},
    "summary": "",
    "metrics": {
        "longevity_years": 0,
        "replication_regions": 0,
        "decentralization_score": 0.0,
        "ethical_alignment": 0.0
    },
    "claims": [
        {
            "id": "c1",
            "statement": "",
            "evidence_refs": ["e1"]
        },
        {
            "id": "c2",
            "statement": "",
            "evidence_refs": ["e2"]
        }
    ],
    "evidence": [
        {
            "id": "e1",
            "type": "peer_reviewed_study",
            "source": "",
            "uri": "",
            "quality": 0.0
        },
        {
            "id": "e2",
            "type": "archaeological_record",
            "source": "",
            "quality": 0.0
        }
    ],
    "unlocks": [],
    "notes": ""
}

def main():
    args = sys.argv[2:] if len(sys.argv) > 2 else sys.argv[1:]
    if len(args) < 2:
        print("Usage: python3 -m src new <domain> <id>")
        print(f"Domains: {', '.join(VALID_DOMAINS)}")
        sys.exit(1)

    domain = args[0]
    entry_id = args[1]

    if domain not in VALID_DOMAINS:
        print(f"Invalid domain '{domain}'. Choose from: {', '.join(VALID_DOMAINS)}")
        sys.exit(1)

    domain_dir = os.path.join(ROOT, "data", domain)
    os.makedirs(domain_dir, exist_ok=True)

    path = os.path.join(domain_dir, f"{entry_id}.json")
    if os.path.exists(path):
        print(f"Entry already exists: {path}")
        sys.exit(1)

    entry = dict(TEMPLATE)
    entry["id"] = entry_id
    entry["domain"] = domain

    with open(path, "w") as f:
        json.dump(entry, f, indent=2)

    print(f"Created {path}")
    print("Fill in name, region, era, summary, metrics, claims, evidence, and unlocks.")

if __name__ == "__main__":
    main()

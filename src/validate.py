#!/usr/bin/env python3
"""
Lightweight schema checks without external deps.
"""
import os, json, sys

ROOT = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(ROOT, "schema", "keystone.schema.json")) as f:
    SCHEMA = json.load(f)

REQUIRED_TOP = set(SCHEMA["required"])

VALID_DOMAINS = set(SCHEMA["properties"]["domain"]["enum"])

REQUIRED_METRICS = set(SCHEMA["properties"]["metrics"]["required"])

VALID_EVIDENCE_TYPES = {
    "archaeological_record", "peer_reviewed_study", "primary_text",
    "engineering_record", "replication_record", "radiocarbon_date",
    "standards_spec", "field_measurement", "oral_tradition_encoded"
}

def iter_items():
    data_dir = os.path.join(ROOT, "data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(base, f)
                with open(p) as fh:
                    yield p, json.load(fh)

def check_item(p, obj):
    errors = []
    # Top-level required keys
    missing = REQUIRED_TOP - set(obj.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
    # Claims must be a list
    if not isinstance(obj.get("claims", []), list):
        errors.append("claims must be a list")
    # Evidence must be a list
    if not isinstance(obj.get("evidence", []), list):
        errors.append("evidence must be a list")
    # Domain enum check
    domain = obj.get("domain")
    if domain is not None and domain not in VALID_DOMAINS:
        errors.append(f"invalid domain '{domain}', expected one of {sorted(VALID_DOMAINS)}")
    # Era structure
    era = obj.get("era")
    if era is not None:
        if not isinstance(era, dict):
            errors.append("era must be an object")
        else:
            for field in ("start", "end"):
                if field not in era:
                    errors.append(f"era missing '{field}'")
                elif not isinstance(era[field], int):
                    errors.append(f"era.{field} must be an integer")
    # Metrics structure
    metrics = obj.get("metrics")
    if metrics is not None:
        if not isinstance(metrics, dict):
            errors.append("metrics must be an object")
        else:
            missing_m = REQUIRED_METRICS - set(metrics.keys())
            if missing_m:
                errors.append(f"metrics missing required keys: {sorted(missing_m)}")
            if not isinstance(metrics.get("longevity_years", 0), int):
                errors.append("metrics.longevity_years must be an integer")
            if not isinstance(metrics.get("replication_regions", 0), int):
                errors.append("metrics.replication_regions must be an integer")
            dec = metrics.get("decentralization_score", 0)
            if not isinstance(dec, (int, float)):
                errors.append("metrics.decentralization_score must be a number")
            elif not (0 <= dec <= 1):
                errors.append(f"metrics.decentralization_score={dec} out of range [0,1]")
    # Claim structure
    for i, claim in enumerate(obj.get("claims", [])):
        if not isinstance(claim, dict):
            errors.append(f"claims[{i}] must be an object")
            continue
        for field in ("id", "statement", "evidence_refs"):
            if field not in claim:
                errors.append(f"claims[{i}] missing '{field}'")
    # Evidence structure
    evidence_ids = set()
    for i, ev in enumerate(obj.get("evidence", [])):
        if not isinstance(ev, dict):
            errors.append(f"evidence[{i}] must be an object")
            continue
        for field in ("id", "type", "source"):
            if field not in ev:
                errors.append(f"evidence[{i}] missing '{field}'")
        etype = ev.get("type")
        if etype is not None and etype not in VALID_EVIDENCE_TYPES:
            errors.append(f"evidence[{i}] invalid type '{etype}'")
        eid = ev.get("id")
        if eid is not None:
            evidence_ids.add(eid)
    # Cross-reference: claim evidence_refs point to existing evidence IDs
    if evidence_ids:
        for i, claim in enumerate(obj.get("claims", [])):
            if not isinstance(claim, dict):
                continue
            for ref in claim.get("evidence_refs", []):
                if ref not in evidence_ids:
                    errors.append(f"claims[{i}] references unknown evidence '{ref}'")
    if errors:
        for e in errors:
            print(f"[FAIL] {p}: {e}")
        return False
    return True

def main():
    all_ok = True
    count = 0
    for p, obj in iter_items():
        count += 1
        if not check_item(p, obj):
            all_ok = False
        else:
            print(f"[OK]   {p}")
    if count == 0:
        print("[WARN] No data files found")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()

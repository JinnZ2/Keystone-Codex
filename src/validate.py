#!/usr/bin/env python3
"""
Lightweight schema checks without external deps.

Checks entries under data/<domain>/ against schema/keystone.schema.json and
sanity-checks the registries that sit at the top of data/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT
SCHEMA = corpus.load_schema("keystone.schema.json")

REQUIRED_TOP = set(SCHEMA["required"])
VALID_DOMAINS = set(SCHEMA["properties"]["domain"]["enum"])
REQUIRED_METRICS = set(SCHEMA["properties"]["metrics"]["required"])

# Derived from the schema rather than duplicated here. The list used to live in
# this file *and* in the schema *and* in H008's params, so adding
# ethnographic_record meant editing three places and finding out at runtime
# which one you forgot.
VALID_EVIDENCE_TYPES = set(
    SCHEMA["properties"]["evidence"]["items"]["properties"]["type"]["enum"]
)

# Back-compat aliases: earlier code used these names.
DOMAINS = VALID_DOMAINS
METRICS_REQUIRED = REQUIRED_METRICS


def iter_items():
    """(path, entry) pairs for every encoded keystone."""
    return corpus.load_entries_with_paths()


def check_item(p, obj, strict_location=False):
    """
    Validate one entry. Prints failures and returns True if clean.

    strict_location additionally checks that the file sits in
    data/<its own domain>/. It defaults off because callers that validate an
    entry in memory have no meaningful path to check; run() turns it on.
    """
    errors = []

    # Top-level required keys
    missing = REQUIRED_TOP - set(obj.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    # Claims and evidence must be lists
    if not isinstance(obj.get("claims", []), list):
        errors.append("claims must be a list")
    if not isinstance(obj.get("evidence", []), list):
        errors.append("evidence must be a list")
    if not isinstance(obj.get("unlocks", []), list):
        errors.append("unlocks must be a list")

    # Domain enum check
    domain = obj.get("domain")
    if domain is not None and domain not in VALID_DOMAINS:
        errors.append(f"invalid domain '{domain}', expected one of {sorted(VALID_DOMAINS)}")

    # The directory is part of the contract: data/<domain>/<file>.json
    if strict_location and domain is not None and domain in VALID_DOMAINS:
        folder = os.path.basename(os.path.dirname(p))
        if folder != domain:
            errors.append(f"lives in data/{folder}/ but declares domain '{domain}'")

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
            if isinstance(era.get("start"), int) and isinstance(era.get("end"), int):
                if era["end"] < era["start"]:
                    errors.append(f"era ends ({era['end']}) before it starts ({era['start']})")

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

    # Cross-reference: claim evidence_refs point to existing evidence ids
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


def check_catalogue(entries):
    """Structural checks on data/shadow_catalogue.json."""
    problems = []
    seen = set()
    for e in entries:
        eid = e.get("id")
        if eid in seen:
            problems.append(f"duplicate catalogue id '{eid}'")
        seen.add(eid)
        if e.get("status") not in ("confirmed", "shadow"):
            problems.append(f"'{eid}': status must be confirmed|shadow, got {e.get('status')!r}")
        if e.get("domain") not in VALID_DOMAINS:
            problems.append(f"'{eid}': domain '{e.get('domain')}' not in schema enum")
    return problems


def run():
    """Run validation, return True if all OK."""
    all_ok = True
    count = 0

    for path, obj in iter_items():
        count += 1
        rel = os.path.relpath(path, ROOT)
        if check_item(rel, obj, strict_location=True):
            print(f"[OK]   {rel}")
        else:
            all_ok = False

    if count == 0:
        print("[WARN] No data files found")

    catalogue_problems = check_catalogue(corpus.load_catalogue())
    if catalogue_problems:
        all_ok = False
        for p in catalogue_problems:
            print(f"[FAIL] data/shadow_catalogue.json: {p}")
    else:
        print("[OK]   data/shadow_catalogue.json")

    return all_ok


def main():
    sys.exit(0 if run() else 1)


if __name__ == "__main__":
    main()

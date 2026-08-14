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

SCHEMA = corpus.load_schema("keystone.schema.json")
REQUIRED_TOP = set(SCHEMA["required"])
DOMAINS = set(SCHEMA["properties"]["domain"]["enum"])
METRICS_REQUIRED = set(SCHEMA["properties"]["metrics"]["required"])


def check_entry(path, obj):
    problems = []

    missing = REQUIRED_TOP - set(obj.keys())
    if missing:
        problems.append(f"missing top-level keys: {sorted(missing)}")

    domain = obj.get("domain")
    if domain is not None and domain not in DOMAINS:
        problems.append(f"domain '{domain}' not in schema enum")

    # The directory is part of the contract: data/<domain>/<file>.json
    folder = os.path.basename(os.path.dirname(path))
    if domain is not None and folder != domain:
        problems.append(f"lives in data/{folder}/ but declares domain '{domain}'")

    for key in ("claims", "evidence", "unlocks"):
        if key in obj and not isinstance(obj[key], list):
            problems.append(f"{key} must be a list")

    metrics = obj.get("metrics")
    if isinstance(metrics, dict):
        missing_metrics = METRICS_REQUIRED - set(metrics.keys())
        if missing_metrics:
            problems.append(f"metrics missing: {sorted(missing_metrics)}")
    elif "metrics" in obj:
        problems.append("metrics must be an object")

    era = obj.get("era")
    if isinstance(era, dict) and "start" in era and "end" in era:
        if era["end"] < era["start"]:
            problems.append(f"era ends ({era['end']}) before it starts ({era['start']})")

    return problems


def check_catalogue(entries):
    problems = []
    seen = {}
    for e in entries:
        eid = e.get("id")
        if eid in seen:
            problems.append(f"duplicate catalogue id '{eid}'")
        seen[eid] = e
        if e.get("status") not in ("confirmed", "shadow"):
            problems.append(f"'{eid}': status must be confirmed|shadow, got {e.get('status')!r}")
        if e.get("domain") not in DOMAINS:
            problems.append(f"'{eid}': domain '{e.get('domain')}' not in schema enum")
    return problems


def main():
    all_ok = True

    for path, obj in corpus.load_entries_with_paths():
        rel = os.path.relpath(path, corpus.ROOT)
        problems = check_entry(path, obj)
        if problems:
            all_ok = False
            for p in problems:
                print(f"[FAIL] {rel}: {p}")
        else:
            print(f"[OK]   {rel}")

    catalogue_problems = check_catalogue(corpus.load_catalogue())
    if catalogue_problems:
        all_ok = False
        for p in catalogue_problems:
            print(f"[FAIL] data/shadow_catalogue.json: {p}")
    else:
        print("[OK]   data/shadow_catalogue.json")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

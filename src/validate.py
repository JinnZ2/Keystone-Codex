#!/usr/bin/env python3
"""
Lightweight schema checks without external deps.
"""
import os, json, sys

ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMA = json.load(open(os.path.join(ROOT, "schema", "keystone.schema.json")))

REQUIRED_TOP = set(SCHEMA["required"])

def iter_items():
    data_dir = os.path.join(ROOT,"data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(base,f)
                yield p, json.load(open(p))

def check_item(p, obj):
    ok = True
    missing = REQUIRED_TOP - set(obj.keys())
    if missing:
        print(f"[FAIL] {p}: missing top-level keys: {sorted(missing)}")
        ok = False
    # minimal type checks
    if ok and not isinstance(obj.get("claims",[]), list):
        print(f"[FAIL] {p}: claims must be a list")
        ok = False
    if ok and not isinstance(obj.get("evidence",[]), list):
        print(f"[FAIL] {p}: evidence must be a list")
        ok = False
    return ok

def main():
    all_ok = True
    for p, obj in iter_items():
        if not check_item(p, obj):
            all_ok = False
        else:
            print(f"[OK]   {p}")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()

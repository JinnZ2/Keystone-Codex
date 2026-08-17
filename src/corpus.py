#!/usr/bin/env python3
"""
Single shared loader for everything under data/.

Layout convention (enforced here, documented in README):

    data/<domain>/<id>.json   -> a keystone ENTRY, validated against
                                 schema/keystone.schema.json
    data/<name>.json          -> a REGISTRY (catalogues, indexes); never
                                 treated as an entry

Before this module existed each script did its own os.walk over data/ and
picked up every *.json it found. When data/shadow_catalogue.json landed at the
top of data/, prove.py crashed on a missing "metrics" key and validate.py
reported it as a malformed entry. Loading rules live in one place now so a new
registry file can never break the proof pipeline again.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
RULES_DIR = os.path.join(ROOT, "rules")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def entry_paths():
    """Absolute paths of every keystone entry, sorted for deterministic output."""
    paths = []
    for domain in sorted(os.listdir(DATA_DIR)):
        domain_dir = os.path.join(DATA_DIR, domain)
        if not os.path.isdir(domain_dir):
            continue  # top-level file -> registry, not an entry
        for fname in sorted(os.listdir(domain_dir)):
            if fname.endswith(".json"):
                paths.append(os.path.join(domain_dir, fname))
    return paths


def load_entries():
    """Every fully-encoded keystone entry, sorted by id."""
    items = [_read(p) for p in entry_paths()]
    items.sort(key=lambda x: x.get("id", ""))
    return items


def load_entries_with_paths():
    """(path, entry) pairs — for validators that need to name the bad file."""
    return [(p, _read(p)) for p in entry_paths()]


def load_catalogue():
    """The shadow catalogue: confirmed entries plus uncoded candidates."""
    return _read(os.path.join(DATA_DIR, "shadow_catalogue.json"))["entries"]


def load_rules(path=None):
    """
    Load a rule set. Pass an explicit path to score against an archived
    version, e.g. legacy/rules/keystone_rules.v1.json — that is what makes
    superseded verdicts reproducible instead of merely remembered.
    """
    if path is None:
        path = os.path.join(RULES_DIR, "keystone_rules.json")
    elif not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    return _read(path)


def load_lineage_terms():
    """
    Declared downstream lineage families that `unlocks` may point at.
    Absent file means no vocabulary has been declared yet — an empty
    vocabulary, not an error, so the falsifier can report on that state
    rather than crash on it.
    """
    path = os.path.join(RULES_DIR, "lineage_terms.json")
    if not os.path.exists(path):
        return {"version": "0", "terms": []}
    return _read(path)


def load_schema(name):
    return _read(os.path.join(ROOT, "schema", name))


def evidence_types():
    """
    The declared evidence taxonomy, from the schema. Single source of truth —
    src/validate.py and hypothesis H008 both read it from here rather than
    keeping their own copies.
    """
    schema = load_schema("keystone.schema.json")
    return schema["properties"]["evidence"]["items"]["properties"]["type"]["enum"]


def load_candidates():
    """Rows from the candidates registry. Absent file means none, not an error."""
    path = os.path.join(DATA_DIR, "candidates.json")
    if not os.path.exists(path):
        return []
    return _read(path).get("candidates", [])

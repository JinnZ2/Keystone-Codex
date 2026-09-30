#!/usr/bin/env python3
"""
Single shared loader for everything under data/.

Layout convention (enforced here, documented in README):

    data/<domain>/<id>.json   -> a keystone ENTRY, validated against
                                 schema/keystone.schema.json
    data/<name>.json          -> a REGISTRY (catalogues, indexes); never
                                 treated as an entry
    systems/<id>.json         -> a SYSTEM: a set of entry ids plus declared
                                 joints, validated against
                                 schema/system.schema.json. Systems live
                                 outside data/ because a system is an assembly
                                 OF entries, not another entry.

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
SYSTEMS_DIR = os.path.join(ROOT, "systems")


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


def load_systems():
    """
    Every declared system, sorted by id. Absent directory means no systems
    have been declared — an empty architecture layer, not an error, so the
    falsifier reports on that state rather than crashing on it.
    """
    if not os.path.isdir(SYSTEMS_DIR):
        return []
    items = []
    for fname in sorted(os.listdir(SYSTEMS_DIR)):
        if fname.endswith(".json"):
            items.append(_read(os.path.join(SYSTEMS_DIR, fname)))
    items.sort(key=lambda x: x.get("id", ""))
    return items


def layer_roles():
    """
    The declared layer_role vocabulary, from the schema. Single source of
    truth, same arrangement as evidence_types(): src/systems.py and the
    H-ARCH hypotheses read it from here rather than keeping copies.

    UNSET is in the enum and is excluded here, because UNSET is a declaration
    that the role is unread, not a role a system can be missing.
    """
    schema = load_schema("keystone.schema.json")
    enum = schema["properties"]["layer_role"]["enum"]
    return [r for r in enum if r != "UNSET"]


def load_evaluator_claims():
    """
    Rows from the evaluator-claim register. Absent file means the register has
    not been created; an existing file with zero rows means it was created and
    is empty. The two are different states and are returned as such: None for
    absent, a list (possibly empty) for present.
    """
    path = os.path.join(DATA_DIR, "evaluator_claims.json")
    if not os.path.exists(path):
        return None
    return _read(path).get("claims", [])

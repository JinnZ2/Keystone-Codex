#!/usr/bin/env python3
"""
Tests for the shared corpus loader.

The regression these guard against is specific and has already happened twice:
a registry file (shadow_catalogue.json, candidates.json) lands at the top of
data/, every module's own os.walk picks it up as though it were a keystone
entry, and the proof engine dies on a missing "metrics" key.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src import corpus


class TestEntryRegistrySplit(unittest.TestCase):
    def test_entries_come_only_from_domain_subdirectories(self):
        for path in corpus.entry_paths():
            parent = os.path.basename(os.path.dirname(path))
            self.assertNotEqual(
                parent, "data",
                f"{path} sits at the top of data/ and must be treated as a registry")

    def test_registries_are_not_loaded_as_entries(self):
        loaded = {os.path.basename(p) for p in corpus.entry_paths()}
        for registry in ("shadow_catalogue.json", "candidates.json"):
            self.assertNotIn(registry, loaded)

    def test_every_entry_has_the_keys_the_pipeline_assumes(self):
        entries = corpus.load_entries()
        self.assertGreater(len(entries), 0)
        for x in entries:
            # prove.py indexes these directly; a registry slipping through
            # would fail here exactly as it did in production.
            for key in ("id", "name", "domain", "era", "metrics"):
                self.assertIn(key, x, f"{x.get('id', '?')} missing {key}")

    def test_entries_are_sorted_deterministically(self):
        ids = [x["id"] for x in corpus.load_entries()]
        self.assertEqual(ids, sorted(ids))

    def test_paths_and_entries_agree(self):
        self.assertEqual(len(corpus.entry_paths()),
                         len(corpus.load_entries_with_paths()))


class TestRegistries(unittest.TestCase):
    def test_catalogue_rows_have_ids_and_status(self):
        for row in corpus.load_catalogue():
            self.assertIn("id", row)
            self.assertIn(row.get("status"), ("confirmed", "shadow"))

    def test_candidates_absent_is_not_an_error(self):
        self.assertIsInstance(corpus.load_candidates(), list)


class TestRules(unittest.TestCase):
    def test_default_rules_load(self):
        rules = corpus.load_rules()
        self.assertIn("criteria", rules)
        self.assertIn("pass_score", rules)

    def test_archived_rules_still_load(self):
        """Retired rule sets must stay runnable — that is what legacy/ is for."""
        v1 = corpus.load_rules("legacy/rules/keystone_rules.v1.json")
        self.assertEqual(v1["version"], "1.0")

    def test_criteria_weights_are_sane(self):
        rules = corpus.load_rules()
        total = sum(c["weight"] for c in rules["criteria"])
        self.assertAlmostEqual(total, 1.0, places=6)
        self.assertLessEqual(rules["pass_score"], total)

    def test_evidence_types_come_from_the_schema(self):
        types = corpus.evidence_types()
        schema = corpus.load_schema("keystone.schema.json")
        self.assertEqual(
            types,
            schema["properties"]["evidence"]["items"]["properties"]["type"]["enum"])

    def test_lineage_terms_have_unique_ids(self):
        ids = [t["id"] for t in corpus.load_lineage_terms()["terms"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_missing_lineage_file_yields_empty_vocabulary(self):
        """Absence is a state to report on, not a crash."""
        original = corpus.RULES_DIR
        try:
            with tempfile.TemporaryDirectory() as tmp:
                corpus.RULES_DIR = tmp
                self.assertEqual(corpus.load_lineage_terms()["terms"], [])
        finally:
            corpus.RULES_DIR = original


class TestCorpusIntegrity(unittest.TestCase):
    def test_entry_ids_are_unique(self):
        ids = [x["id"] for x in corpus.load_entries()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_entry_filename_matches_nothing_in_particular_but_json_parses(self):
        for path in corpus.entry_paths():
            with open(path, encoding="utf-8") as f:
                json.load(f)


if __name__ == "__main__":
    unittest.main()

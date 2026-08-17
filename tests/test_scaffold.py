#!/usr/bin/env python3
"""Tests for the scaffold module."""
import unittest
import os
import sys
import json
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.scaffold import TEMPLATE, VALID_DOMAINS


class TestTemplate(unittest.TestCase):
    def test_template_has_required_fields(self):
        required = {"id", "name", "domain", "region", "era", "summary",
                     "metrics", "claims", "evidence", "unlocks"}
        self.assertTrue(required.issubset(set(TEMPLATE.keys())))

    def test_template_claims_have_structure(self):
        for claim in TEMPLATE["claims"]:
            self.assertIn("id", claim)
            self.assertIn("statement", claim)
            self.assertIn("evidence_refs", claim)

    def test_template_evidence_has_structure(self):
        for ev in TEMPLATE["evidence"]:
            self.assertIn("id", ev)
            self.assertIn("type", ev)
            self.assertIn("source", ev)

    def test_valid_domains_match_schema(self):
        schema_path = os.path.join(ROOT, "schema", "keystone.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        schema_domains = set(schema["properties"]["domain"]["enum"])
        self.assertEqual(set(VALID_DOMAINS), schema_domains)


if __name__ == "__main__":
    unittest.main()

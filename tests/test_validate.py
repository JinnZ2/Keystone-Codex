#!/usr/bin/env python3
"""Tests for the validation module."""
import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.validate import check_item, REQUIRED_TOP, VALID_DOMAINS, VALID_EVIDENCE_TYPES


def make_valid_entry(**overrides):
    """Return a minimal valid entry, with optional overrides."""
    entry = {
        "id": "test_entry",
        "name": "Test Entry",
        "domain": "ecological",
        "region": "Test Region",
        "era": {"start": -1000, "end": 500},
        "summary": "A test keystone.",
        "metrics": {
            "longevity_years": 500,
            "replication_regions": 3,
            "decentralization_score": 0.8
        },
        "claims": [
            {"id": "c1", "statement": "Test claim", "evidence_refs": ["e1"]}
        ],
        "evidence": [
            {"id": "e1", "type": "peer_reviewed_study", "source": "Test source", "quality": 0.8}
        ],
        "unlocks": ["test_downstream"]
    }
    entry.update(overrides)
    return entry


class TestValidEntry(unittest.TestCase):
    def test_valid_entry_passes(self):
        entry = make_valid_entry()
        self.assertTrue(check_item("test.json", entry))

    def test_all_real_data_files_pass(self):
        """Every JSON file in data/ must pass validation."""
        data_dir = os.path.join(ROOT, "data")
        count = 0
        for base, _, files in os.walk(data_dir):
            for f in files:
                if f.endswith(".json") and f != "candidates.json":
                    p = os.path.join(base, f)
                    import json
                    with open(p) as fh:
                        obj = json.load(fh)
                    self.assertTrue(check_item(p, obj), f"Validation failed for {p}")
                    count += 1
        self.assertGreater(count, 0, "No data files found")


class TestMissingFields(unittest.TestCase):
    def test_missing_top_level_key(self):
        entry = make_valid_entry()
        del entry["name"]
        self.assertFalse(check_item("test.json", entry))

    def test_missing_metrics_field(self):
        entry = make_valid_entry()
        del entry["metrics"]["longevity_years"]
        self.assertFalse(check_item("test.json", entry))

    def test_missing_era_start(self):
        entry = make_valid_entry()
        del entry["era"]["start"]
        self.assertFalse(check_item("test.json", entry))

    def test_missing_claim_statement(self):
        entry = make_valid_entry()
        entry["claims"] = [{"id": "c1", "evidence_refs": ["e1"]}]
        self.assertFalse(check_item("test.json", entry))

    def test_missing_evidence_type(self):
        entry = make_valid_entry()
        entry["evidence"] = [{"id": "e1", "source": "Test"}]
        self.assertFalse(check_item("test.json", entry))


class TestInvalidValues(unittest.TestCase):
    def test_invalid_domain(self):
        entry = make_valid_entry(domain="invalid_domain")
        self.assertFalse(check_item("test.json", entry))

    def test_invalid_evidence_type(self):
        entry = make_valid_entry()
        entry["evidence"] = [{"id": "e1", "type": "blog_post", "source": "Test"}]
        self.assertFalse(check_item("test.json", entry))

    def test_decentralization_out_of_range(self):
        entry = make_valid_entry()
        entry["metrics"]["decentralization_score"] = 1.5
        self.assertFalse(check_item("test.json", entry))

    def test_era_not_integer(self):
        entry = make_valid_entry()
        entry["era"]["start"] = "ancient"
        self.assertFalse(check_item("test.json", entry))

    def test_claims_not_list(self):
        entry = make_valid_entry(claims="not a list")
        self.assertFalse(check_item("test.json", entry))

    def test_evidence_not_list(self):
        entry = make_valid_entry(evidence="not a list")
        self.assertFalse(check_item("test.json", entry))


class TestCrossReferences(unittest.TestCase):
    def test_dangling_evidence_ref(self):
        entry = make_valid_entry()
        entry["claims"] = [{"id": "c1", "statement": "Test", "evidence_refs": ["e99"]}]
        self.assertFalse(check_item("test.json", entry))

    def test_valid_evidence_ref(self):
        entry = make_valid_entry()
        self.assertTrue(check_item("test.json", entry))


class TestValidDomains(unittest.TestCase):
    def test_all_eight_domains_accepted(self):
        for domain in VALID_DOMAINS:
            entry = make_valid_entry(domain=domain)
            self.assertTrue(check_item("test.json", entry), f"Domain '{domain}' rejected")


if __name__ == "__main__":
    unittest.main()

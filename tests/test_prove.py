#!/usr/bin/env python3
"""Tests for the scoring/proof module."""
import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.prove import score_item, evidence_quality, PASS_SCORE, criteria_by_name


def make_entry(longevity=500, regions=3, unlocks=3, dec_score=0.8, evidence_q=None):
    """Build a test entry with configurable metrics."""
    evidence = []
    if evidence_q is not None:
        for i, q in enumerate(evidence_q):
            evidence.append({"id": f"e{i}", "type": "peer_reviewed_study", "source": "Test", "quality": q})
    else:
        evidence = [{"id": "e1", "type": "peer_reviewed_study", "source": "Test", "quality": 0.8}]
    return {
        "id": "test",
        "metrics": {
            "longevity_years": longevity,
            "replication_regions": regions,
            "decentralization_score": dec_score
        },
        "unlocks": ["u"] * unlocks,
        "evidence": evidence
    }


class TestScoringCriteria(unittest.TestCase):
    def test_all_criteria_pass(self):
        entry = make_entry(longevity=500, regions=3, unlocks=2, dec_score=0.8)
        result = score_item(entry)
        self.assertTrue(result["is_keystone"])
        self.assertGreaterEqual(result["score"], PASS_SCORE)
        for t in result["trace"]:
            self.assertTrue(t["passed"], f"Criterion {t['rule']} should pass")

    def test_all_criteria_fail(self):
        entry = make_entry(longevity=10, regions=0, unlocks=0, dec_score=0.1)
        result = score_item(entry)
        self.assertFalse(result["is_keystone"])
        self.assertEqual(result["score"], 0.0)
        for t in result["trace"]:
            self.assertFalse(t["passed"], f"Criterion {t['rule']} should fail")

    def test_longevity_boundary(self):
        threshold = criteria_by_name["longevity"]["threshold"]
        below = score_item(make_entry(longevity=threshold - 1))
        at = score_item(make_entry(longevity=threshold))
        above = score_item(make_entry(longevity=threshold + 1))
        self.assertFalse(below["trace"][0]["passed"])
        self.assertTrue(at["trace"][0]["passed"])
        self.assertTrue(above["trace"][0]["passed"])

    def test_replication_boundary(self):
        threshold = criteria_by_name["replication"]["threshold"]
        below = score_item(make_entry(regions=threshold - 1))
        at = score_item(make_entry(regions=threshold))
        self.assertFalse(below["trace"][1]["passed"])
        self.assertTrue(at["trace"][1]["passed"])

    def test_unlocks_boundary(self):
        threshold = criteria_by_name["unlocks_lineage"]["threshold"]
        below = score_item(make_entry(unlocks=threshold - 1))
        at = score_item(make_entry(unlocks=threshold))
        self.assertFalse(below["trace"][2]["passed"])
        self.assertTrue(at["trace"][2]["passed"])

    def test_decentralization_boundary(self):
        threshold = criteria_by_name["decentralization"]["threshold"]
        below = score_item(make_entry(dec_score=threshold - 0.01))
        at = score_item(make_entry(dec_score=threshold))
        self.assertFalse(below["trace"][3]["passed"])
        self.assertTrue(at["trace"][3]["passed"])


class TestEvidenceQuality(unittest.TestCase):
    def test_quality_average(self):
        entry = make_entry(evidence_q=[0.8, 0.6])
        self.assertAlmostEqual(evidence_quality(entry), 0.7)

    def test_no_quality_returns_zero(self):
        entry = {"evidence": [{"id": "e1", "type": "peer_reviewed_study", "source": "Test"}]}
        self.assertEqual(evidence_quality(entry), 0.0)

    def test_empty_evidence(self):
        entry = {"evidence": []}
        self.assertEqual(evidence_quality(entry), 0.0)

    def test_high_quality_preserves_score(self):
        high_q = make_entry(evidence_q=[1.0, 1.0])
        result = score_item(high_q)
        # quality_factor = 0.7 + 0.3*1.0 = 1.0, so score is unmodified
        raw = sum(t["weight"] for t in result["trace"] if t["passed"])
        self.assertAlmostEqual(result["score"], round(raw * 1.0, 3))

    def test_low_quality_reduces_score(self):
        low_q = make_entry(evidence_q=[0.0, 0.0])
        result = score_item(low_q)
        # quality_factor = 0.7 + 0.3*0.0 = 0.7
        raw = sum(t["weight"] for t in result["trace"] if t["passed"])
        self.assertAlmostEqual(result["score"], round(raw * 0.7, 3))


class TestTraceFormat(unittest.TestCase):
    def test_trace_has_all_criteria(self):
        result = score_item(make_entry())
        self.assertEqual(len(result["trace"]), 4)
        rules = [t["rule"] for t in result["trace"]]
        self.assertTrue(any("longevity" in r for r in rules))
        self.assertTrue(any("replication" in r for r in rules))
        self.assertTrue(any("unlocks" in r for r in rules))
        self.assertTrue(any("decentralization" in r for r in rules))

    def test_trace_rules_match_thresholds(self):
        """Rule strings must reflect actual threshold values from rules JSON."""
        result = score_item(make_entry())
        for t in result["trace"]:
            rule_name = t["rule"].split(">=")[0]
            if rule_name in criteria_by_name:
                expected_threshold = criteria_by_name[rule_name]["threshold"]
                self.assertIn(str(expected_threshold), t["rule"])

    def test_result_has_evidence_quality(self):
        result = score_item(make_entry())
        self.assertIn("evidence_quality", result)


class TestRealDataScoring(unittest.TestCase):
    def test_all_real_entries_score(self):
        """Every data file must score without errors."""
        import json
        data_dir = os.path.join(ROOT, "data")
        count = 0
        for base, _, files in os.walk(data_dir):
            for f in files:
                if f.endswith(".json") and f != "candidates.json":
                    p = os.path.join(base, f)
                    with open(p) as fh:
                        obj = json.load(fh)
                    result = score_item(obj)
                    self.assertIn("id", result)
                    self.assertIn("is_keystone", result)
                    self.assertIn("score", result)
                    self.assertIsInstance(result["score"], float)
                    self.assertGreaterEqual(result["score"], 0.0)
                    self.assertLessEqual(result["score"], 1.0)
                    count += 1
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for the scoring/proof module."""
import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.prove import score_item, evidence_quality, PASS_SCORE, criteria_by_name, rules

# Distinct types so the evidence_independence criterion can be satisfied.
DEFAULT_TYPES = ["peer_reviewed_study", "archaeological_record", "oral_tradition_encoded"]


def make_entry(longevity=500, regions=3, unlocks=3, dec_score=0.8,
               evidence_q=None, types=None, claims=True):
    """
    Build a test entry that clears every criterion by default.

    Rules v1.1 scores the evidence as well as the metrics, so a fixture with a
    single source and no claims no longer represents a passing entry. Callers
    that want a specific criterion to fail should say so explicitly.
    """
    qualities = [0.8, 0.8, 0.8] if evidence_q is None else list(evidence_q)
    types = types or DEFAULT_TYPES
    evidence = [
        {"id": f"e{i}", "type": types[i % len(types)], "source": "Test", "quality": q}
        for i, q in enumerate(qualities)
    ]
    entry = {
        "id": "test",
        "metrics": {
            "longevity_years": longevity,
            "replication_regions": regions,
            "decentralization_score": dec_score
        },
        "unlocks": ["u"] * unlocks,
        "evidence": evidence,
    }
    if claims and evidence:
        entry["claims"] = [
            {"id": "c1", "statement": "Test claim", "evidence_refs": [evidence[0]["id"]]}
        ]
    else:
        entry["claims"] = []
    return entry


class TestScoringCriteria(unittest.TestCase):
    def test_all_criteria_pass(self):
        entry = make_entry(longevity=500, regions=3, unlocks=2, dec_score=0.8)
        result = score_item(entry)
        self.assertTrue(result["is_keystone"])
        self.assertGreaterEqual(result["score"], PASS_SCORE)
        for t in result["trace"]:
            self.assertTrue(t["passed"], f"Criterion {t['rule']} should pass")

    def test_all_criteria_fail(self):
        entry = make_entry(longevity=10, regions=0, unlocks=0, dec_score=0.1,
                           evidence_q=[], claims=False)
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
        """Strong evidence clears the evidence_strength criterion."""
        result = score_item(make_entry(evidence_q=[1.0, 1.0, 1.0]))
        strength = [t for t in result["trace"] if t["rule"].startswith("evidence_strength")][0]
        self.assertTrue(strength["passed"])
        self.assertTrue(result["is_keystone"])

    def test_low_quality_reduces_score(self):
        """
        Evidence quality still moves the score — through an explicit criterion
        now rather than a multiplier, so the drop is exactly that criterion's
        weight and the trace names it.
        """
        high = score_item(make_entry(evidence_q=[1.0, 1.0, 1.0]))
        low = score_item(make_entry(evidence_q=[0.0, 0.0, 0.0]))
        self.assertLess(low["score"], high["score"])

        weight = criteria_by_name["evidence_strength"]["weight"]
        self.assertAlmostEqual(high["score"] - low["score"], weight, places=6)

        failed = [t["rule"] for t in low["trace"] if not t["passed"]]
        self.assertEqual(failed, [f"evidence_strength>={criteria_by_name['evidence_strength']['threshold']}"])


class TestTraceFormat(unittest.TestCase):
    def test_trace_has_all_criteria(self):
        """One trace row per criterion in the rule set, whatever that set holds."""
        result = score_item(make_entry())
        self.assertEqual(len(result["trace"]), len(rules["criteria"]))
        traced = [t["rule"].split(">=")[0] for t in result["trace"]]
        self.assertEqual(traced, [c["name"] for c in rules["criteria"]])

    def test_evidence_criteria_are_scored(self):
        """v1.1 reads the evidence, not just the author's numbers."""
        traced = {t["rule"].split(">=")[0] for t in score_item(make_entry())["trace"]}
        for name in ("evidence_strength", "evidence_independence", "claim_coverage"):
            self.assertIn(name, traced)

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
        """Every encoded entry must score without errors."""
        from src import corpus
        entries = corpus.load_entries()
        self.assertGreater(len(entries), 0)
        for obj in entries:
            result = score_item(obj)
            self.assertIn("id", result)
            self.assertIn("is_keystone", result)
            self.assertIn("score", result)
            self.assertIsInstance(result["score"], float)
            self.assertGreaterEqual(result["score"], 0.0)
            self.assertLessEqual(result["score"], 1.0)


if __name__ == "__main__":
    unittest.main()

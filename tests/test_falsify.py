#!/usr/bin/env python3
"""
Tests for the falsification engine.

The engine's job is to be believed when it says a claim failed, so the things
worth testing are that a test can actually fail, that a seeded test is
reproducible, and that the unknowns register keeps "we answered this" apart
from "the alarm stopped ringing".
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src import corpus, falsify


def entry(eid="a", domain="ecological", start=0, end=500, longevity=500,
          unlocks=None, basis=None):
    e = {
        "id": eid,
        "name": eid.title(),
        "domain": domain,
        "region": "Test",
        "era": {"start": start, "end": end},
        "summary": "s",
        "metrics": {"longevity_years": longevity, "replication_regions": 2,
                    "decentralization_score": 0.8},
        "claims": [{"id": "c1", "statement": "s", "evidence_refs": ["e1"]}],
        "evidence": [{"id": "e1", "type": "peer_reviewed_study", "source": "S",
                      "quality": 0.8}],
        "unlocks": unlocks if unlocks is not None else ["fam"],
    }
    if basis:
        e["longevity_basis"] = basis
    return e


def ctx(entries=None, catalogue=None, terms=None, candidates=None, rules=None):
    return {
        "entries": entries if entries is not None else [entry()],
        "catalogue": catalogue or [],
        "candidates": candidates or [],
        "lineage_terms": terms if terms is not None else [{"id": "fam", "name": "Fam"}],
        "rules": rules or corpus.load_rules(),
    }


class TestUnlockResolution(unittest.TestCase):
    def test_resolved_target_passes(self):
        self.assertTrue(falsify.t_unlock_resolution(ctx(), {})["passed"])

    def test_dangling_target_fails(self):
        r = falsify.t_unlock_resolution(ctx(terms=[]), {})
        self.assertFalse(r["passed"])
        self.assertTrue(r["unknowns"])

    def test_entry_id_resolves_as_a_target(self):
        c = ctx(entries=[entry("a", unlocks=["b"]), entry("b", unlocks=[])], terms=[])
        self.assertTrue(falsify.t_unlock_resolution(c, {})["passed"])

    def test_id_defined_as_both_entry_and_term_fails(self):
        """One id, two definitions — the graph would silently pick a winner."""
        c = ctx(entries=[entry("a", unlocks=["b"]), entry("b", unlocks=[])],
                terms=[{"id": "b", "name": "B"}])
        r = falsify.t_unlock_resolution(c, {})
        self.assertFalse(r["passed"])
        self.assertIn("collision", r["summary"])


class TestEraLongevityCoherence(unittest.TestCase):
    def test_coherent_entry_passes(self):
        c = ctx(entries=[entry(start=0, end=500, longevity=500)])
        self.assertTrue(falsify.t_era_longevity_coherence(c, {})["passed"])

    def test_incoherent_entry_fails(self):
        c = ctx(entries=[entry(start=0, end=2500, longevity=500)])
        self.assertFalse(falsify.t_era_longevity_coherence(c, {})["passed"])

    def test_declared_basis_exempts(self):
        """The escape hatch is saying what the number means, not omitting it."""
        c = ctx(entries=[entry(start=0, end=2500, longevity=500,
                               basis="persistence after abandonment")])
        self.assertTrue(falsify.t_era_longevity_coherence(c, {})["passed"])


class TestRubricDiscrimination(unittest.TestCase):
    def _rules(self, weights):
        return {"version": "test", "pass_score": 0.5,
                "criteria": [{"name": n, "description": "", "threshold": t, "weight": w}
                             for n, t, w in weights]}

    def test_saturated_rubric_fails(self):
        """Every entry at the ceiling means the rubric has no resolution left."""
        rules = self._rules([("longevity", 1, 0.5), ("replication", 1, 0.5)])
        c = ctx(entries=[entry("a"), entry("b"), entry("c")], rules=rules)
        r = falsify.t_rubric_discrimination(c, {})
        self.assertFalse(r["passed"])
        self.assertEqual(r["stats"]["ceiling_fraction"], 1.0)

    def test_real_corpus_discriminates(self):
        r = falsify.t_rubric_discrimination(falsify.build_context(), {})
        self.assertTrue(r["passed"], r["summary"])
        self.assertLessEqual(r["stats"]["ceiling_fraction"], 0.5)

    def test_retired_rubric_would_fail_this_test(self):
        """
        The point of the v1.1 revision: rules v1.0 saturate against the same
        corpus that v1.1 separates. If this ever passes, the test has stopped
        measuring what it was written to measure.
        """
        c = falsify.build_context()
        c["rules"] = corpus.load_rules("legacy/rules/keystone_rules.v1.json")
        r = falsify.t_rubric_discrimination(c, {})
        self.assertFalse(r["passed"])
        self.assertGreater(r["stats"]["ceiling_fraction"], 0.5)


class TestPhiSignificance(unittest.TestCase):
    def _ctx(self):
        return ctx(catalogue=corpus.load_catalogue())

    def test_seeded_result_is_reproducible(self):
        params = {"trials": 20, "seed": 7, "direction": "indistinguishable"}
        a = falsify.t_phi_significance(self._ctx(), params)
        b = falsify.t_phi_significance(self._ctx(), params)
        self.assertEqual(a["stats"], b["stats"])

    def test_negative_control_holds(self):
        r = falsify.t_phi_significance(
            self._ctx(), {"trials": 50, "seed": 1618, "direction": "indistinguishable"})
        self.assertTrue(r["passed"])
        self.assertGreaterEqual(r["stats"]["p"], 0.05)

    def test_original_claim_is_still_falsified(self):
        """The retired claim must stay retired, not quietly become true again."""
        r = falsify.t_phi_significance(
            self._ctx(), {"trials": 50, "seed": 1618, "direction": "exceeds_chance"})
        self.assertFalse(r["passed"])


class TestUnknownsReconciliation(unittest.TestCase):
    def setUp(self):
        self._dir = falsify.UNKNOWNS_DIR
        self._root = falsify.ROOT
        self._tmp = tempfile.TemporaryDirectory()
        falsify.UNKNOWNS_DIR = os.path.join(self._tmp.name, "unknowns")
        falsify.ROOT = self._tmp.name
        os.makedirs(falsify.UNKNOWNS_DIR)

    def tearDown(self):
        falsify.UNKNOWNS_DIR = self._dir
        falsify.ROOT = self._root
        self._tmp.cleanup()

    def _register(self):
        with open(os.path.join(falsify.UNKNOWNS_DIR, "register.json"), encoding="utf-8") as f:
            return {u["id"]: u for u in json.load(f)["unknowns"]}

    def test_raised_question_opens(self):
        falsify.reconcile_unknowns([("H001", {"question": "q?", "why": "w"})], "r1", False)
        u = self._register()["U-H001-1"]
        self.assertEqual(u["status"], "open")

    def test_same_question_keeps_its_id(self):
        q = ("H001", {"question": "q?", "why": "w"})
        falsify.reconcile_unknowns([q], "r1", False)
        falsify.reconcile_unknowns([q], "r2", False)
        self.assertEqual(list(self._register()), ["U-H001-1"])

    def test_unanswered_question_goes_dormant_not_resolved(self):
        """
        A hypothesis passing does not answer the question its failure raised.
        Auto-closing it as 'resolved' would launder silence into a finding.
        """
        falsify.reconcile_unknowns([("H001", {"question": "q?", "why": "w"})], "r1", False)
        falsify.reconcile_unknowns([], "r2", False)
        self.assertEqual(self._register()["U-H001-1"]["status"], "dormant")

    def test_written_resolution_closes_as_resolved(self):
        falsify.reconcile_unknowns([("H001", {"question": "q?", "why": "w"})], "r1", False)
        path = os.path.join(falsify.UNKNOWNS_DIR, "register.json")
        with open(path, encoding="utf-8") as f:
            reg = json.load(f)
        reg["unknowns"][0]["resolution"] = "because X"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(reg, f)
        falsify.reconcile_unknowns([], "r2", False)
        self.assertEqual(self._register()["U-H001-1"]["status"], "resolved")

    def test_pinned_questions_are_never_closed(self):
        path = os.path.join(falsify.UNKNOWNS_DIR, "register.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"unknowns": [{
                "id": "U-C-1", "question": "q?", "raised_by": "curated",
                "trigger": "t", "first_seen": "r0", "last_seen": "r0",
                "status": "open", "pinned": True, "resolution": None}]}, f)
        falsify.reconcile_unknowns([], "r1", False)
        self.assertEqual(self._register()["U-C-1"]["status"], "open")

    def test_dry_run_writes_nothing(self):
        falsify.reconcile_unknowns([("H001", {"question": "q?", "why": "w"})], "r1", True)
        self.assertFalse(os.path.exists(
            os.path.join(falsify.UNKNOWNS_DIR, "register.json")))


class TestHypothesisSuite(unittest.TestCase):
    def test_every_hypothesis_binds_to_a_known_test(self):
        for path, h in falsify.load_hypotheses():
            self.assertIn(h["test"]["kind"], falsify.TESTS,
                          f"{h['id']} names an unimplemented test kind")

    def test_every_hypothesis_has_the_required_fields(self):
        required = set(corpus.load_schema("hypothesis.schema.json")["required"])
        for path, h in falsify.load_hypotheses():
            self.assertFalse(required - set(h), f"{h['id']} missing {required - set(h)}")

    def test_suite_runs_clean_against_the_corpus(self):
        c = falsify.build_context()
        for path, h in falsify.load_hypotheses():
            r = falsify.run_hypothesis(h, c)
            self.assertIn("passed", r)
            self.assertTrue(r["summary"])


if __name__ == "__main__":
    unittest.main()

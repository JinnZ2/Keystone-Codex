#!/usr/bin/env python3
"""
Tests for the architecture layer: the integration report and the four
hypotheses that read it.

Three things are worth testing here and only one of them is ordinary.

The ordinary one: the report computes what it says it computes.

The second: the report REFUSES what it says it refuses. A per-entry score, a
ranking of members, an ordering of systems by satisfaction — these are absent
on purpose and the absence is load-bearing, because a number attached to a
part is what turns an integration measure back into a supremacy measure.
Absence is the easiest property to lose by accident, so it is asserted rather
than trusted.

The third: the new hypotheses can FAIL. A layer added without a test that can
refuse it will confirm whatever it is handed. Every architecture test is
exercised in both directions.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src import corpus, falsify, systems  # noqa: E402


def entry(eid, domain="ecological", **kw):
    e = {"id": eid, "name": eid, "domain": domain, "region": "r",
         "era": {"start": 0, "end": 100}, "summary": "s",
         "metrics": {"longevity_years": 100, "replication_regions": 1,
                     "decentralization_score": 0.5},
         "claims": [], "evidence": [], "unlocks": []}
    e.update(kw)
    return e


def system(sid="s", members=(), joints=()):
    return {"id": sid, "name": sid, "status": "illustrative",
            "membership_rule": "test fixture",
            "members": list(members), "joints": list(joints)}


ROLES = ["PSU", "CPU_MEMORY", "BUS", "IO", "FIRMWARE", "PERIPHERAL"]


class TestIntegrationReport(unittest.TestCase):
    def test_runs_on_resolves_against_a_present_member(self):
        r = systems.integration_report(
            system(members=[
                {"entry": "ground", "layer_role": "PSU", "runs_on": []},
                {"entry": "top", "layer_role": "BUS", "runs_on": ["PSU"]},
            ]),
            {"ground": entry("ground"), "top": entry("top", "governance")}, ROLES)
        self.assertEqual(r["runs_on"]["satisfied"], 1)
        self.assertEqual(r["runs_on"]["unmet"], [])
        self.assertEqual(r["runs_on"]["fraction"], 1.0)

    def test_unmet_target_is_named_with_a_reason(self):
        r = systems.integration_report(
            system(members=[{"entry": "top", "layer_role": "BUS",
                             "runs_on": ["PSU"]}]),
            {"top": entry("top", "governance")}, ROLES)
        self.assertEqual(r["runs_on"]["satisfied"], 0)
        self.assertEqual(len(r["runs_on"]["unmet"]), 1)
        self.assertIn("PSU", r["runs_on"]["unmet"][0]["why"])

    def test_a_member_cannot_satisfy_its_own_runs_on(self):
        """Otherwise a lone PSU declaring runs_on PSU reports as satisfied."""
        r = systems.integration_report(
            system(members=[{"entry": "ground", "layer_role": "PSU",
                             "runs_on": ["PSU"]}]),
            {"ground": entry("ground")}, ROLES)
        self.assertEqual(len(r["runs_on"]["unmet"]), 1)

    def test_nothing_declared_is_None_and_not_zero(self):
        """
        Zero-of-zero and zero-of-eleven are different results and a float
        cannot hold both. A 0.0 here would report an undeclared system as a
        totally unsatisfied one.
        """
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "PSU"}]),
            {"a": entry("a")}, ROLES)
        self.assertIsNone(r["runs_on"]["fraction"])
        self.assertEqual(r["runs_on"]["targets"], 0)

    def test_member_naming_a_missing_entry_is_reported_not_dropped(self):
        r = systems.integration_report(
            system(members=[{"entry": "ghost", "layer_role": "PSU"}]), {}, ROLES)
        self.assertEqual(r["missing_entries"], ["ghost"])
        self.assertEqual(r["member_count"], 1)

    def test_role_conflict_is_reported_and_neither_side_wins(self):
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "BUS"}]),
            {"a": entry("a", layer_role="IO")}, ROLES)
        m = r["members"][0]
        self.assertEqual(m["role_source"], "conflict")
        self.assertIsNone(m["layer_role"])
        self.assertIn("neither is applied", m["role_conflict"])
        self.assertEqual(len(r["conflicts"]), 1)

    def test_missing_layers_lists_roles_with_no_member(self):
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "PSU"}]),
            {"a": entry("a")}, ROLES)
        self.assertNotIn("PSU", r["missing_layers"])
        self.assertIn("FIRMWARE", r["missing_layers"])

    def test_role_domain_crosstab_detects_a_non_bijection(self):
        """
        RULE 2 as arithmetic. If role and domain were one statement the
        crosstab would be one-to-one. Two domains under one role is what says
        they are not.
        """
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "BUS"},
                            {"entry": "b", "layer_role": "BUS"}]),
            {"a": entry("a", "governance"), "b": entry("b", "ethical")}, ROLES)
        self.assertFalse(r["role_domain"]["one_to_one"])
        self.assertEqual(r["role_domain"]["domains_per_role"]["BUS"],
                         ["ethical", "governance"])

    def test_one_to_one_when_role_tracks_domain(self):
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "PSU"}]),
            {"a": entry("a", "ecological")}, ROLES)
        self.assertTrue(r["role_domain"]["one_to_one"])

    def test_empty_joints_list_survives_as_a_reading(self):
        r = systems.integration_report(system(members=[]), {}, ROLES)
        self.assertEqual(r["joints"]["count"], 0)


class TestReportRefusals(unittest.TestCase):
    """
    The absences are the design. Asserted, not trusted.
    """

    def test_report_carries_no_score_or_rank_for_any_member(self):
        r = systems.integration_report(
            system(members=[{"entry": "a", "layer_role": "PSU"}]),
            {"a": entry("a")}, ROLES)
        banned = ("score", "rank", "rating", "grade", "weight", "is_keystone")
        for m in r["members"]:
            for k in m:
                self.assertFalse(any(b in k for b in banned),
                                 f"member field '{k}' ranks a part")

    def test_module_does_not_import_the_per_entry_scorer(self):
        """
        Different measurand. If this layer ever reads prove.score_item, the
        integration report has started grading the parts.
        """
        with open(os.path.join(ROOT, "src", "systems.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("import prove", src)
        self.assertNotIn("score_item", src)

    def test_systems_are_reported_in_declared_order_not_by_satisfaction(self):
        reports = systems.all_reports()
        declared = [s["id"] for s in corpus.load_systems()]
        self.assertEqual([r["system"] for r in reports], declared)


class TestArchitectureHypotheses(unittest.TestCase):
    """Each test kind is exercised in both directions."""

    def ctx(self, entries=(), sysdefs=(), claims=None):
        return {"entries": list(entries), "systems": list(sysdefs),
                "layer_roles": ROLES, "evaluator_claims": claims}

    # -- H-ARCH-1 ---------------------------------------------------------
    def test_coverage_counts_UNSET_as_declared(self):
        res = falsify.t_layer_role_coverage(
            self.ctx([entry("a", layer_role="UNSET"), entry("b", layer_role="PSU")]),
            {"max_undeclared_fraction": 0.5})
        self.assertTrue(res["passed"])
        self.assertEqual(res["stats"]["undeclared"], 0)
        self.assertEqual(res["stats"]["unset"], 1)

    def test_coverage_fails_when_the_field_is_absent(self):
        res = falsify.t_layer_role_coverage(
            self.ctx([entry("a"), entry("b")]), {"max_undeclared_fraction": 0.5})
        self.assertIs(res["passed"], False)
        self.assertEqual(res["stats"]["undeclared_fraction"], 1.0)

    def test_coverage_on_an_empty_corpus_is_no_data(self):
        res = falsify.t_layer_role_coverage(self.ctx([]), {})
        self.assertIsNone(res["passed"])

    # -- H-ARCH-2 ---------------------------------------------------------
    def test_runs_on_hypothesis_passes_on_a_resolving_system(self):
        res = falsify.t_system_runs_on(self.ctx(
            [entry("ground"), entry("top", "governance")],
            [system(members=[{"entry": "ground", "layer_role": "PSU"},
                             {"entry": "top", "layer_role": "BUS",
                              "runs_on": ["PSU"]}])]), {})
        self.assertTrue(res["passed"])

    def test_runs_on_hypothesis_fails_on_a_dangling_target(self):
        res = falsify.t_system_runs_on(self.ctx(
            [entry("top", "governance")],
            [system(members=[{"entry": "top", "layer_role": "BUS",
                              "runs_on": ["PSU"]}])]), {})
        self.assertIs(res["passed"], False)

    def test_no_systems_is_no_data_not_a_pass(self):
        """An absent architecture layer is not a satisfied one."""
        res = falsify.t_system_runs_on(self.ctx([], []), {})
        self.assertIsNone(res["passed"])

    def test_systems_declaring_no_runs_on_is_no_data(self):
        res = falsify.t_system_runs_on(self.ctx(
            [entry("a")],
            [system(members=[{"entry": "a", "layer_role": "PSU"}])]), {})
        self.assertIsNone(res["passed"])

    # -- H-ARCH-3 ---------------------------------------------------------
    def _sys(self, sid, sat):
        """A system whose runs_on fraction is 1.0 (sat) or 0.0."""
        members = [{"entry": "ground", "layer_role": "PSU"},
                   {"entry": f"{sid}top", "layer_role": "BUS",
                    "runs_on": ["PSU" if sat else "FIRMWARE"]}]
        return system(sid, members)

    def test_saturation_fails_when_every_system_is_at_ceiling(self):
        entries = [entry("ground"), entry("atop"), entry("btop")]
        res = falsify.t_integration_saturation(
            self.ctx(entries, [self._sys("a", True), self._sys("b", True)]),
            {"min_systems": 2})
        self.assertIs(res["passed"], False)
        self.assertEqual(res["stats"]["ceiling_fraction"], 1.0)

    def test_saturation_passes_when_systems_separate(self):
        entries = [entry("ground"), entry("atop"), entry("btop")]
        res = falsify.t_integration_saturation(
            self.ctx(entries, [self._sys("a", True), self._sys("b", False)]),
            {"min_systems": 2})
        self.assertTrue(res["passed"])
        self.assertEqual(res["stats"]["spread"], 1.0)

    def test_saturation_fails_below_the_system_floor(self):
        """One reading has zero spread by construction, not by measurement."""
        res = falsify.t_integration_saturation(
            self.ctx([entry("ground"), entry("atop")], [self._sys("a", True)]),
            {"min_systems": 2})
        self.assertIs(res["passed"], False)
        self.assertIn("below the 2", res["summary"])

    def test_saturation_with_no_readings_is_no_data(self):
        res = falsify.t_integration_saturation(self.ctx([], []), {})
        self.assertIsNone(res["passed"])

    # -- H-BYPASS ---------------------------------------------------------
    def test_empty_register_is_no_data_not_supported(self):
        """
        The load-bearing one. Reporting 'supported' over zero rows turns the
        absence of a search into evidence for the thing nobody searched for.
        """
        res = falsify.t_evaluator_bypass(self.ctx(claims=[]), {"min_records": 3})
        self.assertIsNone(res["passed"])
        self.assertIn("no data", res["summary"])

    def test_absent_register_is_no_data(self):
        res = falsify.t_evaluator_bypass(self.ctx(claims=None), {})
        self.assertIsNone(res["passed"])

    def test_records_without_an_argued_equivalence_do_not_count(self):
        bare = {"id": "x", "evaluating_source": {"citation": "c"},
                "rejected": {"design": "d", "attributed_origin": "A"},
                "accepted": {"design": "d", "attributed_origin": "B"},
                "structural_equivalence": {}}
        res = falsify.t_evaluator_bypass(self.ctx(claims=[bare, bare, bare]),
                                         {"min_records": 3})
        self.assertIs(res["passed"], False)
        self.assertEqual(res["stats"]["usable"], 0)

    def test_complete_records_support_the_claim(self):
        full = {"id": "x", "evaluating_source": {"citation": "c"},
                "rejected": {"design": "d", "attributed_origin": "A",
                             "stated_reason": "r", "locator": "p1"},
                "accepted": {"design": "d", "attributed_origin": "B",
                             "locator": "p9"},
                "structural_equivalence": {"statement": "same", "basis": "why"}}
        res = falsify.t_evaluator_bypass(self.ctx(claims=[full] * 3),
                                         {"min_records": 3})
        self.assertTrue(res["passed"])


class TestRuleOne(unittest.TestCase):
    """A falsified rendering must not close its target."""

    def test_falsification_raises_the_target_as_an_unknown(self):
        h = {"id": "HX", "measures": {"target": "t", "rendering": "r",
                                      "target_question": "Does t hold?"}}
        u, note = falsify.target_unknown(h, falsify.result(False, "nope"))
        self.assertIsNotNone(u)
        self.assertEqual(u["question"], "Does t hold?")
        self.assertIsNone(note)

    def test_support_raises_nothing(self):
        h = {"id": "HX", "measures": {"target": "t", "rendering": "r",
                                      "target_question": "Does t hold?"}}
        u, _ = falsify.target_unknown(h, falsify.result(True, "yes"))
        self.assertIsNone(u)

    def test_no_data_raises_nothing(self):
        h = {"id": "HX", "measures": {"target": "t", "rendering": "r",
                                      "target_question": "Does t hold?"}}
        u, _ = falsify.target_unknown(h, falsify.no_data("nothing to read"))
        self.assertIsNone(u)

    def test_target_reached_suppresses_the_raise(self):
        h = {"id": "HX", "measures": {"target": "t", "rendering": "r",
                                      "target_question": "q",
                                      "target_reached": True}}
        u, note = falsify.target_unknown(h, falsify.result(False, "nope"))
        self.assertIsNone(u)
        self.assertIn("target_reached", note)

    def test_a_falsified_hypothesis_with_no_split_is_noted_not_silent(self):
        u, note = falsify.target_unknown({"id": "HX"}, falsify.result(False, "n"))
        self.assertIsNone(u)
        self.assertIn("RULE 1", note)

    def test_h007_carries_the_split_and_its_target_is_open(self):
        """Retroactive application, checked against the shipped files."""
        import json
        with open(os.path.join(ROOT, "hypotheses", "H007_phi_significance.json"),
                  encoding="utf-8") as f:
            h = json.load(f)
        self.assertIn("measures", h)
        self.assertFalse(h["measures"]["target_reached"])
        with open(os.path.join(ROOT, "unknowns", "register.json"),
                  encoding="utf-8") as f:
            reg = json.load(f)
        by_id = {u["id"]: u for u in reg["unknowns"]}
        self.assertEqual(by_id["U-H007-3"]["status"], "open")
        self.assertEqual(by_id["U-H007-3"]["level"], "target")
        self.assertEqual(by_id["U-H007-2"]["level"], "rendering")


class TestVerdictArithmetic(unittest.TestCase):
    def test_three_verdicts(self):
        self.assertEqual(falsify.verdict_of(falsify.result(True, "")), "supported")
        self.assertEqual(falsify.verdict_of(falsify.result(False, "")), "falsified")
        self.assertEqual(falsify.verdict_of(falsify.no_data("")), "no data")

    def test_no_data_is_not_counted_as_a_pass_anywhere(self):
        res = falsify.no_data("")
        self.assertIsNot(res["passed"], True)
        self.assertIsNot(res["passed"], False)


class TestFrameLevelUnknowns(unittest.TestCase):
    def test_nine_frame_entries_each_declare_a_frame(self):
        import json
        with open(os.path.join(ROOT, "unknowns", "register.json"),
                  encoding="utf-8") as f:
            reg = json.load(f)
        frame = [u for u in reg["unknowns"] if u.get("level") == "frame"]
        self.assertEqual(len(frame), 9)
        for u in frame:
            self.assertTrue(u.get("frame"), f"{u['id']} declares no frame")
            self.assertTrue(u.get("pinned"), f"{u['id']} is not pinned")

    def test_frame_entries_render_in_their_own_section(self):
        import json
        with open(os.path.join(ROOT, "unknowns", "register.json"),
                  encoding="utf-8") as f:
            reg = json.load(f)
        md = os.path.join(ROOT, "UNKNOWNS.md")
        before = None
        if os.path.exists(md):
            with open(md, encoding="utf-8") as f:
                before = f.read()
        try:
            falsify.render_unknowns(reg, "test-run")
            with open(md, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("## Frame-level", text)
            head, tail = text.split("## Open", 1)
            self.assertIn("### F1 ", head)
            self.assertNotIn("### F1 ", tail)
        finally:
            if before is not None:
                with open(md, "w", encoding="utf-8") as f:
                    f.write(before)


if __name__ == "__main__":
    unittest.main()

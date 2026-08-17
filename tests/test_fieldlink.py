#!/usr/bin/env python3
"""Tests for the fieldlink export module and .fieldlink.json integrity."""
import unittest
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.fieldlink_export import (
    load_fieldlink, load_items, load_candidates,
    domain_to_layer, entry_to_glyph, entry_to_protocol,
    candidate_to_glyph, validate_integrity
)


class TestFieldlinkConfig(unittest.TestCase):
    def setUp(self):
        self.fieldlink = load_fieldlink()

    def test_has_required_sections(self):
        for key in ["source", "target", "layer_map", "field_map", "glyphs", "sync"]:
            self.assertIn(key, self.fieldlink, f"Missing section: {key}")

    def test_source_repo(self):
        self.assertEqual(self.fieldlink["source"]["repo"], "JinnZ2/Keystone-Codex")

    def test_target_repo(self):
        self.assertEqual(self.fieldlink["target"]["repo"], "JinnZ2/BioGrid2.0")

    def test_all_domains_in_source(self):
        expected = {"ecological", "economic", "social", "governance",
                    "information", "material", "ethical", "infrastructure"}
        self.assertEqual(set(self.fieldlink["source"]["domains"]), expected)


class TestLayerMap(unittest.TestCase):
    def setUp(self):
        self.fieldlink = load_fieldlink()
        self.layers = self.fieldlink["layer_map"]["layers"]

    def test_six_layers(self):
        self.assertEqual(len(self.layers), 6)

    def test_all_domains_mapped(self):
        mapped = set()
        for layer in self.layers:
            mapped.update(layer["keystone_domains"])
        expected = set(self.fieldlink["source"]["domains"])
        self.assertEqual(mapped, expected)

    def test_no_domain_in_multiple_layers(self):
        seen = {}
        for layer in self.layers:
            for d in layer["keystone_domains"]:
                self.assertNotIn(d, seen,
                    f"Domain '{d}' in both '{seen.get(d)}' and '{layer['layer']}'")
                seen[d] = layer["layer"]

    def test_every_layer_has_biogrid_subsystems(self):
        for layer in self.layers:
            self.assertGreater(len(layer["biogrid_subsystems"]), 0,
                f"Layer '{layer['layer']}' has no biogrid_subsystems")

    def test_entry_ids_exist_in_data(self):
        items = load_items()
        entry_ids = {it["id"] for it in items}
        for layer in self.layers:
            for eid in layer.get("entry_ids", []):
                self.assertIn(eid, entry_ids,
                    f"Layer '{layer['layer']}' references unknown entry '{eid}'")


class TestIntegrityChecks(unittest.TestCase):
    def test_no_integrity_errors(self):
        fieldlink = load_fieldlink()
        items = load_items()
        errors = validate_integrity(fieldlink, items)
        self.assertEqual(errors, [], f"Integrity errors: {errors}")


class TestGlyphTransform(unittest.TestCase):
    def setUp(self):
        self.fieldlink = load_fieldlink()
        self.layers = self.fieldlink["layer_map"]["layers"]
        self.shapes = self.fieldlink["glyphs"]["shape_by_domain"]

    def test_entry_produces_glyph(self):
        items = load_items()
        for entry in items:
            glyph = entry_to_glyph(entry, self.layers, self.shapes)
            self.assertEqual(glyph["source_id"], entry["id"])
            self.assertEqual(glyph["label"], entry["name"])
            self.assertIn(glyph["layer"], [l["layer"] for l in self.layers])
            self.assertEqual(glyph["fill"], "solid")
            self.assertIn(glyph["shape"], self.shapes.values())

    def test_candidate_produces_dotted_glyph(self):
        candidates = load_candidates()
        for c in candidates:
            glyph = candidate_to_glyph(c, self.layers, self.shapes)
            self.assertEqual(glyph["source_id"], c["id"])
            self.assertEqual(glyph["fill"], "dotted")


class TestProtocolTransform(unittest.TestCase):
    def test_entry_produces_protocol(self):
        items = load_items()
        for entry in items:
            proto = entry_to_protocol(entry)
            self.assertEqual(proto["source_id"], entry["id"])
            self.assertEqual(proto["durability_years"], entry["metrics"]["longevity_years"])
            self.assertEqual(proto["spread_count"], entry["metrics"]["replication_regions"])
            self.assertIsInstance(proto["source_confidence"], float)
            self.assertGreater(len(proto["sources"]), 0)


class TestDomainToLayer(unittest.TestCase):
    def test_all_domains_resolve(self):
        fieldlink = load_fieldlink()
        layers = fieldlink["layer_map"]["layers"]
        for domain in fieldlink["source"]["domains"]:
            result = domain_to_layer(domain, layers)
            self.assertNotEqual(result, "unmapped", f"Domain '{domain}' is unmapped")

    def test_unknown_domain_returns_unmapped(self):
        fieldlink = load_fieldlink()
        layers = fieldlink["layer_map"]["layers"]
        self.assertEqual(domain_to_layer("nonexistent", layers), "unmapped")


class TestGlyphShapes(unittest.TestCase):
    def test_all_domains_have_shapes(self):
        fieldlink = load_fieldlink()
        shapes = fieldlink["glyphs"]["shape_by_domain"]
        for domain in fieldlink["source"]["domains"]:
            self.assertIn(domain, shapes, f"No shape for domain '{domain}'")

    def test_all_shapes_unique(self):
        fieldlink = load_fieldlink()
        shapes = fieldlink["glyphs"]["shape_by_domain"]
        values = list(shapes.values())
        self.assertEqual(len(values), len(set(values)), "Duplicate shapes found")


if __name__ == "__main__":
    unittest.main()

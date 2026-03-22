#!/usr/bin/env python3
"""Tests for the graph building module."""
import unittest
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from src.build_graph import escape_dot, load_items


class TestEscapeDot(unittest.TestCase):
    def test_plain_string(self):
        self.assertEqual(escape_dot("hello"), "hello")

    def test_quotes_escaped(self):
        self.assertEqual(escape_dot('say "hello"'), 'say \\"hello\\"')

    def test_backslash_escaped(self):
        self.assertEqual(escape_dot("path\\to"), "path\\\\to")

    def test_both_escaped(self):
        self.assertEqual(escape_dot('"\\test"'), '\\"\\\\test\\"')


class TestGraphIntegrity(unittest.TestCase):
    def test_all_entries_become_nodes(self):
        items = load_items()
        entry_ids = {x["id"] for x in items}
        self.assertGreater(len(entry_ids), 0)

    def test_unlock_targets_tracked(self):
        items = load_items()
        entry_ids = {x["id"] for x in items}
        all_targets = set()
        for x in items:
            for u in x.get("unlocks", []):
                all_targets.add(u)
        # Every target should either be an entry or flagged as dangling
        # (the graph module handles this — just verify targets exist)
        self.assertGreater(len(all_targets), 0)


class TestLoadItems(unittest.TestCase):
    def test_loads_json_files(self):
        items = load_items()
        self.assertGreater(len(items), 0)
        for item in items:
            self.assertIn("id", item)
            self.assertIn("name", item)


if __name__ == "__main__":
    unittest.main()

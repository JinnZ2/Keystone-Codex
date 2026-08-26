#!/usr/bin/env python3
"""
System health view: layer coverage, resolved links, scoring summary.

Maps keystone entries onto the BioGrid architecture layers from
SYSTEMS_ANALOGY.md and .fieldlink.json, showing which layers are
strong, which are thin, and where the integration gaps are.

Usage: python3 -m src health
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT


def load_fieldlink():
    """Load the fieldlink config."""
    with open(os.path.join(ROOT, ".fieldlink.json")) as f:
        return json.load(f)


def load_items():
    """Encoded keystone entries. See src/corpus.py for the entry/registry split."""
    return corpus.load_entries()


def load_scores():
    """Load proof traces if available."""
    path = os.path.join(ROOT, "proof_traces.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {r["id"]: r for r in json.load(f)}


def load_candidates():
    """Load candidates."""
    path = os.path.join(ROOT, "data", "candidates.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f).get("candidates", [])


def main():
    """Display system health across architecture layers."""
    fieldlink = load_fieldlink()
    items = load_items()
    scores = load_scores()
    candidates = load_candidates()

    entry_by_id = {it["id"]: it for it in items}
    entry_ids = set(entry_by_id.keys())
    candidate_by_domain = {}
    for c in candidates:
        d = c.get("suggested_domain", "unknown")
        candidate_by_domain.setdefault(d, []).append(c)

    layers = fieldlink["layer_map"]["layers"]

    # Collect all unlock targets across all entries
    all_targets = set()
    for it in items:
        all_targets.update(it.get("unlocks", []))
    resolved = all_targets & entry_ids
    dangling = all_targets - entry_ids

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                  SYSTEM HEALTH DASHBOARD                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    total_score = 0.0
    total_entries = 0
    keystone_count = 0
    non_keystone_count = 0

    for layer in layers:
        lname = layer["layer"]
        analogy = layer["analogy"]
        domains = layer["keystone_domains"]
        subsystems = layer["biogrid_subsystems"]

        # Find entries in this layer
        layer_entries = [entry_by_id[eid] for eid in layer.get("entry_ids", []) if eid in entry_by_id]
        layer_candidates = []
        for d in domains:
            layer_candidates.extend(candidate_by_domain.get(d, []))

        # Score summary for this layer
        layer_scores = [scores[e["id"]] for e in layer_entries if e["id"] in scores]
        keystones = [s for s in layer_scores if s["is_keystone"]]
        non_keystones = [s for s in layer_scores if not s["is_keystone"]]
        avg_score = sum(s["score"] for s in layer_scores) / len(layer_scores) if layer_scores else 0.0

        keystone_count += len(keystones)
        non_keystone_count += len(non_keystones)
        total_entries += len(layer_entries)
        total_score += sum(s["score"] for s in layer_scores)

        # Resolve ratio: how many unlock targets from this layer's entries are resolved
        layer_targets = set()
        for e in layer_entries:
            layer_targets.update(e.get("unlocks", []))
        layer_resolved = layer_targets & entry_ids
        resolve_pct = len(layer_resolved) / len(layer_targets) * 100 if layer_targets else 0

        # Health indicator
        if len(keystones) >= 2 and resolve_pct >= 50:
            health = "██████ STRONG"
        elif len(keystones) >= 1:
            health = "████░░ MODERATE"
        elif len(layer_entries) >= 1:
            health = "██░░░░ WEAK"
        else:
            health = "░░░░░░ EMPTY"

        print(f"┌── {lname.upper()} ──")
        print(f"│  {analogy}")
        print(f"│  Domains:    {', '.join(domains)}")
        print(f"│  Subsystems: {', '.join(subsystems)}")
        print(f"│")
        print(f"│  Entries:    {len(layer_entries)}  ({len(keystones)} keystone, {len(non_keystones)} non-keystone)")
        if layer_entries:
            for e in layer_entries:
                sc = scores.get(e["id"])
                tag = "✅" if sc and sc["is_keystone"] else "❌"
                score_str = f"{sc['score']:.3f}" if sc else "N/A"
                print(f"│    {tag} {e['id']} — {score_str}")
        print(f"│  Candidates: {len(layer_candidates)}")
        print(f"│  Avg score:  {avg_score:.3f}")
        print(f"│  Links out:  {len(layer_targets)} ({len(layer_resolved)} resolved, {resolve_pct:.0f}%)")
        print(f"│  Health:     {health}")
        print(f"└{'─' * 60}")
        print()

    # Overall summary
    avg_total = total_score / total_entries if total_entries else 0
    print("┌── OVERALL ──")
    print(f"│  Total entries:      {total_entries}")
    print(f"│  Keystones:          {keystone_count}")
    print(f"│  Non-keystones:      {non_keystone_count}")
    print(f"│  Candidates:         {len(candidates)}")
    print(f"│  Average score:      {avg_total:.3f}")
    print(f"│  Unlock targets:     {len(all_targets)}")
    print(f"│  Resolved links:     {len(resolved)} ({len(resolved)/len(all_targets)*100:.0f}%)" if all_targets else "│  Resolved links:     0")
    print(f"│  Dangling links:     {len(dangling)}")
    print(f"│  Layers:             {len(layers)}")

    # Weakest layer
    weakest = min(layers, key=lambda l: sum(
        scores.get(eid, {}).get("score", 0) for eid in l.get("entry_ids", []) if eid in entry_ids
    ))
    print(f"│  Weakest layer:      {weakest['layer']} ({', '.join(weakest['keystone_domains'])})")
    print(f"└{'─' * 60}")


if __name__ == "__main__":
    main()

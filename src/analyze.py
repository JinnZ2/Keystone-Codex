#!/usr/bin/env python3
"""
Cross-entry analysis: domain coverage, regional gaps, shared evidence, dangling unlocks.
Usage: python3 -m src analyze
"""
import os, json
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(__file__))

ALL_DOMAINS = [
    "ecological", "economic", "social", "governance",
    "information", "material", "ethical", "infrastructure"
]

def load_items():
    items = []
    data_dir = os.path.join(ROOT, "data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json") and f != "candidates.json":
                p = os.path.join(base, f)
                with open(p) as fh:
                    items.append(json.load(fh))
    return items

def load_candidates():
    path = os.path.join(ROOT, "data", "candidates.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = json.load(f)
    return {c["id"]: c for c in data.get("candidates", [])}

def main():
    items = load_items()
    if not items:
        print("No entries found.")
        return

    entry_ids = {it["id"] for it in items}

    # Domain coverage
    domain_counts = Counter(it["domain"] for it in items)
    empty_domains = [d for d in ALL_DOMAINS if d not in domain_counts]

    print("=== Domain Coverage ===")
    for d in ALL_DOMAINS:
        count = domain_counts.get(d, 0)
        bar = "█" * count
        status = " (EMPTY)" if count == 0 else ""
        print(f"  {d:20s}  {count:2d}  {bar}{status}")
    print()

    # Regional distribution
    print("=== Regional Distribution ===")
    region_counts = Counter(it["region"] for it in items)
    for region, count in region_counts.most_common():
        print(f"  {region:40s}  {count}")
    print()

    # Era span
    print("=== Era Coverage ===")
    earliest = min(it["era"]["start"] for it in items)
    latest = max(it["era"]["end"] for it in items)
    print(f"  Earliest start: {earliest}")
    print(f"  Latest end:     {latest}")
    print(f"  Total span:     {latest - earliest} years")
    print()

    # Dangling unlocks
    all_unlocks = set()
    dangling = set()
    for it in items:
        for u in it.get("unlocks", []):
            all_unlocks.add(u)
            if u not in entry_ids:
                dangling.add(u)

    candidates = load_candidates()
    tracked = dangling & set(candidates.keys())
    untracked = dangling - tracked

    print("=== Unlock Graph Integrity ===")
    print(f"  Total unlock references: {len(all_unlocks)}")
    print(f"  Resolved (have entries): {len(all_unlocks - dangling)}")
    print(f"  Tracked candidates:      {len(tracked)}")
    print(f"  Untracked (unknown):     {len(untracked)}")
    if tracked:
        print("  Candidates (awaiting full entry):")
        for cid in sorted(tracked):
            c = candidates[cid]
            print(f"    → {cid} [{c.get('suggested_domain', '?')}] — {c.get('notes', '')[:60]}")
    if untracked:
        print("  Untracked references:")
        for d in sorted(untracked):
            print(f"    ⚠ {d}")
    print()

    # Evidence type distribution
    print("=== Evidence Types ===")
    etype_counts = Counter()
    quality_sums = Counter()
    quality_counts = Counter()
    for it in items:
        for ev in it.get("evidence", []):
            t = ev.get("type", "unknown")
            etype_counts[t] += 1
            q = ev.get("quality")
            if q is not None:
                quality_sums[t] += q
                quality_counts[t] += 1
    for t, count in etype_counts.most_common():
        avg_q = quality_sums[t] / quality_counts[t] if quality_counts[t] > 0 else 0
        print(f"  {t:30s}  count={count:2d}  avg_quality={avg_q:.2f}")
    print()

    # Summary
    print("=== Summary ===")
    print(f"  Total entries:     {len(items)}")
    print(f"  Domains covered:   {len(domain_counts)}/{len(ALL_DOMAINS)}")
    if empty_domains:
        print(f"  Missing domains:   {', '.join(empty_domains)}")
    print(f"  Unique regions:    {len(region_counts)}")
    print(f"  Dangling unlocks:  {len(dangling)} ({len(tracked)} tracked, {len(untracked)} untracked)")

if __name__ == "__main__":
    main()

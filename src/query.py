#!/usr/bin/env python3
"""
Query and filter keystone entries.
Usage: python3 -m src query [--domain X] [--region X] [--era-after Y] [--era-before Y] [--min-score S] [--keystones-only]
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(__file__))

def load_items():
    items = []
    data_dir = os.path.join(ROOT, "data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(base, f)
                with open(p) as fh:
                    items.append(json.load(fh))
    return items

def load_scores():
    """Load proof traces if available, keyed by id."""
    path = os.path.join(ROOT, "proof_traces.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        traces = json.load(f)
    return {r["id"]: r for r in traces}

def parse_args(argv):
    opts = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--domain" and i + 1 < len(argv):
            opts["domain"] = argv[i + 1]; i += 2
        elif a == "--region" and i + 1 < len(argv):
            opts["region"] = argv[i + 1].lower(); i += 2
        elif a == "--era-after" and i + 1 < len(argv):
            opts["era_after"] = int(argv[i + 1]); i += 2
        elif a == "--era-before" and i + 1 < len(argv):
            opts["era_before"] = int(argv[i + 1]); i += 2
        elif a == "--min-score" and i + 1 < len(argv):
            opts["min_score"] = float(argv[i + 1]); i += 2
        elif a == "--keystones-only":
            opts["keystones_only"] = True; i += 1
        else:
            i += 1
    return opts

def matches(item, scores, opts):
    if "domain" in opts and item["domain"] != opts["domain"]:
        return False
    if "region" in opts and opts["region"] not in item["region"].lower():
        return False
    if "era_after" in opts and item["era"]["end"] < opts["era_after"]:
        return False
    if "era_before" in opts and item["era"]["start"] > opts["era_before"]:
        return False
    sid = item["id"]
    if "min_score" in opts:
        sc = scores.get(sid)
        if sc is None or sc["score"] < opts["min_score"]:
            return False
    if opts.get("keystones_only"):
        sc = scores.get(sid)
        if sc is None or not sc["is_keystone"]:
            return False
    return True

def main():
    argv = sys.argv[2:] if len(sys.argv) > 2 else sys.argv[1:]
    if not argv:
        print("Usage: python3 -m src query [--domain X] [--region X] [--era-after Y] [--era-before Y] [--min-score S] [--keystones-only]")
        print("\nRun 'python3 -m src score' first to enable score-based filtering.")
        sys.exit(0)

    opts = parse_args(argv)
    items = load_items()
    scores = load_scores()

    results = [it for it in items if matches(it, scores, opts)]
    results.sort(key=lambda x: x["era"]["start"])

    if not results:
        print("No entries match the query.")
        sys.exit(0)

    print(f"Found {len(results)} entries:\n")
    for it in results:
        sc = scores.get(it["id"])
        score_str = f"score={sc['score']}" if sc else "score=N/A"
        keystone_str = ""
        if sc:
            keystone_str = " [KEYSTONE]" if sc["is_keystone"] else ""
        s, e = it["era"]["start"], it["era"]["end"]
        print(f"  {it['id']:30s}  {it['domain']:15s}  {s:>6}→{e:<6}  {score_str}{keystone_str}")
        print(f"    {it['summary'][:90]}")
        print()

if __name__ == "__main__":
    main()

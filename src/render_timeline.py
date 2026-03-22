#!/usr/bin/env python3
"""
Render a simple markdown timeline sorted by era.start.
"""
import os, json

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

def main():
    items = load_items()
    items.sort(key=lambda x: x["era"]["start"])
    lines = ["# Timeline", ""]
    for x in items:
        s = x["era"]["start"]
        e = x["era"]["end"]
        lines.append(f"- **{s} → {e}** — **{x['name']}** ({x['domain']}, {x['region']}) — {x['summary']}")
    with open(os.path.join(ROOT, "timeline.md"), "w") as f:
        f.write("\n".join(lines))
    print("Wrote timeline.md")

if __name__ == "__main__":
    main()

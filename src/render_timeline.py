#!/usr/bin/env python3
"""
Render a markdown timeline of encoded keystones, sorted by era start.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT


def fmt_year(y):
    return f"{abs(y)} BCE" if y < 0 else f"{y} CE"


def main():
    items = corpus.load_entries()
    items.sort(key=lambda x: x["era"]["start"])

    lines = [
        "# Timeline",
        "",
        f"{len(items)} encoded keystones, ordered by first attestation. "
        "Candidates not yet encoded live in `data/shadow_catalogue.json`.",
        "",
    ]
    for x in items:
        era = x["era"]
        m = x["metrics"]
        lines.append(
            f"- **{fmt_year(era['start'])} → {fmt_year(era['end'])}** — "
            f"**{x['name']}** ({x['domain']}, {x['region']})  \n"
            f"  {x['summary']}  \n"
            f"  _longevity {m['longevity_years']}yr · "
            f"{m['replication_regions']} regions · "
            f"decentralization {m['decentralization_score']}_"
        )
    with open(os.path.join(ROOT, "timeline.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote timeline.md ({len(items)} entries)")


if __name__ == "__main__":
    main()

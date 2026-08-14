#!/usr/bin/env python3
"""
Build a nodes/edges graph from keystone unlocks.
Outputs graph.json and graph.dot (Graphviz).

An `unlocks` target is one of two things, and the graph keeps them apart:

  - the id of another keystone entry  -> a keystone->keystone edge
  - a declared lineage family term    -> a keystone->lineage edge

Anything else is a dangling target and is reported, because a chain that
points at nothing is not a lineage claim, it is a typo.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT


def main():
    items = corpus.load_entries()
    lineage_terms = corpus.load_lineage_terms()["terms"]

    known_entries = {x["id"] for x in items}
    known_lineages = {t["id"] for t in lineage_terms}
    lineage_by_id = {t["id"]: t for t in lineage_terms}

    nodes = [
        {"id": x["id"], "name": x["name"], "domain": x["domain"], "kind": "keystone"}
        for x in items
    ]

    edges = []
    used_lineages = set()
    dangling = []
    for x in items:
        for target in x.get("unlocks", []):
            if target in known_entries:
                edges.append({"source": x["id"], "target": target, "kind": "keystone"})
            elif target in known_lineages:
                used_lineages.add(target)
                edges.append({"source": x["id"], "target": target, "kind": "lineage"})
            else:
                dangling.append((x["id"], target))

    for lid in sorted(used_lineages):
        t = lineage_by_id[lid]
        nodes.append({
            "id": lid,
            "name": t["name"],
            "domain": t.get("domain", "cross-domain"),
            "kind": "lineage",
        })

    graph = {"nodes": nodes, "edges": edges, "dangling_unlocks": dangling}
    with open(os.path.join(ROOT, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    lines = ["digraph Keystone {", "  rankdir=LR;", "  node [fontname=\"Helvetica\"];"]
    for n in nodes:
        if n["kind"] == "keystone":
            lines.append(
                f'  "{n["id"]}" [label="{n["name"]}\\n({n["domain"]})", '
                f'shape=box, style=filled, fillcolor="#e8eef7"];'
            )
        else:
            lines.append(
                f'  "{n["id"]}" [label="{n["name"]}", shape=ellipse, style=dashed];'
            )
    for e in edges:
        style = "" if e["kind"] == "keystone" else " [style=dashed]"
        lines.append(f'  "{e["source"]}" -> "{e["target"]}"{style};')
    lines.append("}")
    with open(os.path.join(ROOT, "graph.dot"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote graph.json and graph.dot "
          f"({len(nodes)} nodes, {len(edges)} edges)")
    if dangling:
        print(f"  {len(dangling)} dangling unlock target(s) — "
              f"declare them in rules/lineage_terms.json or fix the id:")
        for src, target in dangling:
            print(f"    {src} -> {target}")


if __name__ == "__main__":
    main()

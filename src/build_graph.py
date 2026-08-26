#!/usr/bin/env python3
"""
Build a nodes/edges graph from keystone unlocks.
Outputs graph.json and graph.dot (Graphviz).

An `unlocks` target is one of three things, and the graph keeps them apart:

  - the id of another keystone entry  -> solid edge, solid node
  - a declared lineage family term    -> dashed edge to an ellipse
  - anything else                     -> a dangling target: rendered as a grey
                                         placeholder and reported on stdout

The third case is the one worth watching. Before lineage terms were declared,
every unlock target in the corpus fell into it, so the graph was made entirely
of nodes the repository had invented from free text.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT


def load_items():
    """Encoded keystone entries. See src/corpus.py for the entry/registry split."""
    return corpus.load_entries()


def escape_dot(s):
    """Escape characters that are special in DOT label strings."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build():
    """Return the graph dict. Separated from main() so tests can call it."""
    items = corpus.load_entries()
    lineage_terms = corpus.load_lineage_terms()["terms"]

    known_entries = {x["id"] for x in items}
    lineage_by_id = {t["id"]: t for t in lineage_terms}

    nodes = [
        {"id": x["id"], "name": x["name"], "domain": x["domain"],
         "kind": "keystone", "placeholder": False}
        for x in items
    ]

    edges = []
    used_lineages = set()
    placeholder_ids = set()
    dangling = []
    for x in items:
        for target in x.get("unlocks", []):
            if target in known_entries:
                kind = "keystone"
            elif target in lineage_by_id:
                kind = "lineage"
                used_lineages.add(target)
            else:
                kind = "dangling"
                dangling.append({"source": x["id"], "target": target})
                if target not in placeholder_ids:
                    placeholder_ids.add(target)
                    nodes.append({
                        "id": target,
                        "name": target.replace("_", " ").title(),
                        "domain": "unknown",
                        "kind": "dangling",
                        "placeholder": True,
                    })
            edges.append({"source": x["id"], "target": target, "kind": kind})

    for lid in sorted(used_lineages):
        t = lineage_by_id[lid]
        nodes.append({
            "id": lid,
            "name": t["name"],
            "domain": t.get("domain", "cross-domain"),
            "kind": "lineage",
            "placeholder": False,
        })

    return {"nodes": nodes, "edges": edges, "dangling_unlocks": dangling}


def to_dot(graph):
    lines = [
        "digraph Keystone {",
        "  rankdir=LR;",
        '  node [shape=box, style=filled, fillcolor="#e8f4f8", fontname="Helvetica"];',
    ]
    for n in graph["nodes"]:
        label = escape_dot(f"{n['name']}\\n({n['domain']})")
        nid = escape_dot(n["id"])
        if n["kind"] == "dangling":
            lines.append(f'  "{nid}" [label="{label}", style="dashed", '
                         f'fillcolor="#f0f0f0", fontcolor="#888888"];')
        elif n["kind"] == "lineage":
            lines.append(f'  "{nid}" [label="{escape_dot(n["name"])}", '
                         f'shape=ellipse, style="dashed,filled", fillcolor="#f7f3e8"];')
        else:
            lines.append(f'  "{nid}" [label="{label}"];')
    for e in graph["edges"]:
        src, tgt = escape_dot(e["source"]), escape_dot(e["target"])
        if e["kind"] == "dangling":
            lines.append(f'  "{src}" -> "{tgt}" [style=dashed, color="#aaaaaa"];')
        elif e["kind"] == "lineage":
            lines.append(f'  "{src}" -> "{tgt}" [style=dashed];')
        else:
            lines.append(f'  "{src}" -> "{tgt}";')
    lines.append("}")
    return "\n".join(lines)


def main():
    graph = build()
    with open(os.path.join(ROOT, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    with open(os.path.join(ROOT, "graph.dot"), "w", encoding="utf-8") as f:
        f.write(to_dot(graph))

    kinds = {}
    for n in graph["nodes"]:
        kinds[n["kind"]] = kinds.get(n["kind"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(kinds.items()))
    print(f"Wrote graph.json and graph.dot ({len(graph['nodes'])} nodes "
          f"[{summary}], {len(graph['edges'])} edges)")

    if graph["dangling_unlocks"]:
        print(f"  {len(graph['dangling_unlocks'])} dangling unlock target(s) — "
              f"declare them in rules/lineage_terms.json or fix the id:")
        for d in graph["dangling_unlocks"]:
            print(f"    {d['source']} -> {d['target']}")


if __name__ == "__main__":
    main()

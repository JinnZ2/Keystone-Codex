#!/usr/bin/env python3
"""
Build a nodes/edges graph from keystone unlocks.
Outputs graph.json and graph.dot (Graphviz).
Distinguishes real entries (solid) from placeholder unlock targets (dashed).
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(__file__))

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

def escape_dot(s):
    """Escape characters that are special in DOT label strings."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

def main():
    items = load_items()
    entry_ids = {x["id"] for x in items}

    nodes = [{"id": x["id"], "name": x["name"], "domain": x["domain"], "placeholder": False} for x in items]
    edges = []
    placeholder_ids = set()
    for x in items:
        for target in x.get("unlocks", []):
            edges.append({"source": x["id"], "target": target})
            if target not in entry_ids and target not in placeholder_ids:
                placeholder_ids.add(target)
                nodes.append({"id": target, "name": target.replace("_", " ").title(), "domain": "unknown", "placeholder": True})

    graph = {"nodes": nodes, "edges": edges}
    with open(os.path.join(ROOT, "graph.json"), "w") as f:
        f.write(json.dumps(graph, indent=2))

    # dot
    lines = ["digraph Keystone {", '  rankdir=LR;',
             '  node [shape=box, style=filled, fillcolor="#e8f4f8", fontname="Helvetica"];']
    for n in nodes:
        label = escape_dot(f"{n['name']}\\n({n['domain']})")
        nid = escape_dot(n["id"])
        if n["placeholder"]:
            lines.append(f'  "{nid}" [label="{label}", style="dashed", fillcolor="#f0f0f0", fontcolor="#888888"];')
        else:
            lines.append(f'  "{nid}" [label="{label}"];')
    for e in edges:
        src = escape_dot(e["source"])
        tgt = escape_dot(e["target"])
        is_dangling = e["target"] in placeholder_ids
        style = ', style=dashed, color="#aaaaaa"' if is_dangling else ""
        lines.append(f'  "{src}" -> "{tgt}" [{style}];' if style else f'  "{src}" -> "{tgt}";')
    lines.append("}")
    with open(os.path.join(ROOT, "graph.dot"), "w") as f:
        f.write("\n".join(lines))

    real = len(entry_ids)
    placeholders = len(placeholder_ids)
    print(f"Wrote graph.json and graph.dot ({real} entries, {placeholders} placeholder targets)")

if __name__ == "__main__":
    main()

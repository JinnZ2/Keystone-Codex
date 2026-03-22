#!/usr/bin/env python3
"""
Build a simple nodes/edges graph from keystone unlocks.
Outputs graph.json and graph.dot (Graphviz).
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

def escape_dot(s):
    """Escape characters that are special in DOT label strings."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

def main():
    items = load_items()
    nodes = [{"id": x["id"], "name": x["name"], "domain": x["domain"]} for x in items]
    edges = []
    for x in items:
        for target in x.get("unlocks", []):
            edges.append({"source": x["id"], "target": target})
    graph = {"nodes": nodes, "edges": edges}
    with open(os.path.join(ROOT, "graph.json"), "w") as f:
        f.write(json.dumps(graph, indent=2))
    # dot
    lines = ["digraph Keystone {", '  rankdir=LR;']
    for n in nodes:
        label = escape_dot(f"{n['name']}\\n({n['domain']})")
        nid = escape_dot(n["id"])
        lines.append(f'  "{nid}" [label="{label}"];')
    for e in edges:
        src = escape_dot(e["source"])
        tgt = escape_dot(e["target"])
        lines.append(f'  "{src}" -> "{tgt}";')
    lines.append("}")
    with open(os.path.join(ROOT, "graph.dot"), "w") as f:
        f.write("\n".join(lines))
    print("Wrote graph.json and graph.dot")

if __name__ == "__main__":
    main()

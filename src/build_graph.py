#!/usr/bin/env python3
"""
Build a simple nodes/edges graph from keystone unlocks.
Outputs graph.json and graph.dot (Graphviz).
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(__file__))

def load_items():
    items = []
    data_dir = os.path.join(ROOT,"data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(base,f)
                items.append(json.load(open(p)))
    return items

def main():
    items = load_items()
    nodes = [{"id":x["id"], "name":x["name"], "domain":x["domain"]} for x in items]
    edges = []
    for x in items:
        for target in x.get("unlocks",[]):
            edges.append({"source": x["id"], "target": target})
    graph = {"nodes":nodes, "edges":edges}
    open(os.path.join(ROOT,"graph.json"),"w").write(json.dumps(graph, indent=2))
    # dot
    lines = ["digraph Keystone {", '  rankdir=LR;']
    for n in nodes:
        lines.append(f'  "{n["id"]}" [label="{n["name"]}\\n({n["domain"]})"];')
    for e in edges:
        lines.append(f'  "{e["source"]}" -> "{e["target"]}";')
    lines.append("}")
    open(os.path.join(ROOT,"graph.dot"),"w").write("\n".join(lines))
    print("Wrote graph.json and graph.dot")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Apply keystone rules, score, and produce proof traces per item.
"""
import os, json, math, datetime

ROOT = os.path.dirname(os.path.dirname(__file__))

rules = json.load(open(os.path.join(ROOT,"rules","keystone_rules.json")))
criteria = rules["criteria"]
PASS_SCORE = rules["pass_score"]

def load_items():
    items = []
    data_dir = os.path.join(ROOT,"data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(base,f)
                obj = json.load(open(p))
                items.append(obj)
    return items

def score_item(x):
    m = x["metrics"]
    trace = []
    # Longevity
    lon = m.get("longevity_years",0)
    thr = [c for c in criteria if c["name"]=="longevity"][0]
    passed = lon >= thr["threshold"]
    trace.append({"rule":"longevity>=300","passed":passed,"details":f"longevity_years={lon}", "weight":thr["weight"]})
    # Replication
    rep = m.get("replication_regions",0)
    thr = [c for c in criteria if c["name"]=="replication"][0]
    passed_rep = rep >= thr["threshold"]
    trace.append({"rule":"replication>=2","passed":passed_rep,"details":f"replication_regions={rep}","weight":thr["weight"]})
    # Unlocks
    unlocks = x.get("unlocks",[])
    thr = [c for c in criteria if c["name"]=="unlocks_lineage"][0]
    passed_unlocks = len(unlocks) >= thr["threshold"]
    trace.append({"rule":"unlocks>=1","passed":passed_unlocks,"details":f"unlocks={len(unlocks)}","weight":thr["weight"]})
    # Decentralization
    dec = m.get("decentralization_score",0.0)
    thr = [c for c in criteria if c["name"]=="decentralization"][0]
    passed_dec = dec >= thr["threshold"]
    trace.append({"rule":"decentralization>=0.5","passed":passed_dec,"details":f"decentralization_score={dec}","weight":thr["weight"]})
    # Weighted score
    score = 0.0
    for t in trace:
        if t["passed"]:
            score += t["weight"]
    is_keystone = score >= PASS_SCORE
    return {"id": x["id"], "is_keystone": is_keystone, "score": round(score,3), "trace": trace}

def write_reports(results):
    out_dir = ROOT
    # JSON traces
    with open(os.path.join(out_dir,"proof_traces.json"),"w") as f:
        json.dump(results, f, indent=2)
    # Markdown report
    lines = ["# Proof Report", f"_Generated: {datetime.datetime.utcnow().isoformat()}Z_", ""]
    for r in results:
        lines.append(f"## {r['id']} — {'✅ Keystone' if r['is_keystone'] else '❌ Not yet'} (score {r['score']})")
        for t in r["trace"]:
            mark = "✔" if t["passed"] else "✖"
            lines.append(f"- {mark} **{t['rule']}** — {t['details']} (w={t['weight']})")
        lines.append("")
    open(os.path.join(out_dir,"proof_report.md"),"w").write("\n".join(lines))

def main():
    items = load_items()
    results = [score_item(x) for x in items]
    write_reports(results)
    print("Wrote proof_traces.json and proof_report.md")

if __name__ == "__main__":
    main()

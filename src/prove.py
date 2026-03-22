#!/usr/bin/env python3
"""
Apply keystone rules, score, and produce proof traces per item.
"""
import os, json, datetime

ROOT = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(ROOT, "rules", "keystone_rules.json")) as f:
    rules = json.load(f)

criteria_by_name = {c["name"]: c for c in rules["criteria"]}
PASS_SCORE = rules["pass_score"]

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

def evidence_quality(x):
    """Compute average evidence quality for an entry (0-1). Returns 0 if no quality scores."""
    qualities = [ev["quality"] for ev in x.get("evidence", []) if "quality" in ev]
    if not qualities:
        return 0.0
    return sum(qualities) / len(qualities)

def score_item(x):
    m = x["metrics"]
    trace = []

    # Longevity
    lon = m.get("longevity_years", 0)
    crit = criteria_by_name["longevity"]
    passed = lon >= crit["threshold"]
    trace.append({"rule": f"longevity>={crit['threshold']}", "passed": passed,
                   "details": f"longevity_years={lon}", "weight": crit["weight"]})

    # Replication
    rep = m.get("replication_regions", 0)
    crit = criteria_by_name["replication"]
    passed_rep = rep >= crit["threshold"]
    trace.append({"rule": f"replication>={crit['threshold']}", "passed": passed_rep,
                   "details": f"replication_regions={rep}", "weight": crit["weight"]})

    # Unlocks
    unlocks = x.get("unlocks", [])
    crit = criteria_by_name["unlocks_lineage"]
    passed_unlocks = len(unlocks) >= crit["threshold"]
    trace.append({"rule": f"unlocks>={crit['threshold']}", "passed": passed_unlocks,
                   "details": f"unlocks={len(unlocks)}", "weight": crit["weight"]})

    # Decentralization
    dec = m.get("decentralization_score", 0.0)
    crit = criteria_by_name["decentralization"]
    passed_dec = dec >= crit["threshold"]
    trace.append({"rule": f"decentralization>={crit['threshold']}", "passed": passed_dec,
                   "details": f"decentralization_score={dec}", "weight": crit["weight"]})

    # Weighted score (criteria pass/fail)
    raw_score = sum(t["weight"] for t in trace if t["passed"])

    # Evidence quality modifier: scales the raw score by avg evidence quality.
    # High-quality evidence preserves the score; low quality penalizes it.
    avg_quality = evidence_quality(x)
    quality_factor = 0.7 + 0.3 * avg_quality  # range [0.7, 1.0] — quality can reduce score by up to 30%
    score = raw_score * quality_factor

    is_keystone = score >= PASS_SCORE
    return {
        "id": x["id"],
        "is_keystone": is_keystone,
        "score": round(score, 3),
        "evidence_quality": round(avg_quality, 3),
        "trace": trace
    }

def write_reports(results):
    # JSON traces
    traces_path = os.path.join(ROOT, "proof_traces.json")
    with open(traces_path, "w") as f:
        json.dump(results, f, indent=2)
    # Markdown report
    lines = ["# Proof Report", f"_Generated: {datetime.datetime.utcnow().isoformat()}Z_", ""]
    for r in results:
        eq = r.get('evidence_quality', 0)
        lines.append(f"## {r['id']} — {'✅ Keystone' if r['is_keystone'] else '❌ Not yet'} (score {r['score']}, evidence quality {eq})")
        for t in r["trace"]:
            mark = "✔" if t["passed"] else "✖"
            lines.append(f"- {mark} **{t['rule']}** — {t['details']} (w={t['weight']})")
        lines.append("")
    report_path = os.path.join(ROOT, "proof_report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

def main():
    items = load_items()
    results = [score_item(x) for x in items]
    write_reports(results)
    print("Wrote proof_traces.json and proof_report.md")

if __name__ == "__main__":
    main()

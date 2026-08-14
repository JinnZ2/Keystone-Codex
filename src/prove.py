#!/usr/bin/env python3
"""
Apply keystone rules, score, and produce proof traces per item.

The criteria are read from the rule set, not hardcoded, so any archived rule
version can still be run:

    python3 src/prove.py                                        # current rules
    python3 src/prove.py --rules legacy/rules/keystone_rules.v1.json \
                         --out-suffix .v1                       # reproduce v1.0 verdicts
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT


# ── Criterion evaluators ─────────────────────────────────────────────────
# Each returns (passed, details). Keyed by the criterion "name" in the rule
# set, so adding a criterion to rules/ means adding one function here.

def _c_longevity(x, thr):
    v = x["metrics"].get("longevity_years", 0)
    return v >= thr, f"longevity_years={v}"


def _c_replication(x, thr):
    v = x["metrics"].get("replication_regions", 0)
    return v >= thr, f"replication_regions={v}"


def _c_unlocks(x, thr):
    v = len(x.get("unlocks", []))
    return v >= thr, f"unlocks={v}"


def _c_decentralization(x, thr):
    v = x["metrics"].get("decentralization_score", 0.0)
    return v >= thr, f"decentralization_score={v}"


def _c_evidence_strength(x, thr):
    qualities = [e.get("quality", 0.0) for e in x.get("evidence", [])]
    if not qualities:
        return False, "no evidence"
    mean = sum(qualities) / len(qualities)
    return mean >= thr, f"mean_evidence_quality={mean:.3f} over {len(qualities)} items"


def _c_evidence_independence(x, thr):
    types = {e.get("type") for e in x.get("evidence", []) if e.get("type")}
    return len(types) >= thr, f"distinct_evidence_types={len(types)} ({', '.join(sorted(types))})"


def _c_claim_coverage(x, thr):
    """Fraction of claims backed by at least one evidence ref that resolves."""
    claims = x.get("claims", [])
    if not claims:
        return False, "no claims"
    known = {e.get("id") for e in x.get("evidence", [])}
    backed = sum(1 for c in claims if set(c.get("evidence_refs", [])) & known)
    frac = backed / len(claims)
    return frac >= thr, f"claims_backed={backed}/{len(claims)} ({frac:.2f})"


EVALUATORS = {
    "longevity": _c_longevity,
    "replication": _c_replication,
    "unlocks_lineage": _c_unlocks,
    "decentralization": _c_decentralization,
    "evidence_strength": _c_evidence_strength,
    "evidence_independence": _c_evidence_independence,
    "claim_coverage": _c_claim_coverage,
}


def score_item(x, rules):
    trace = []
    for c in rules["criteria"]:
        evaluator = EVALUATORS.get(c["name"])
        if evaluator is None:
            raise KeyError(
                f"rule set references unknown criterion '{c['name']}'; "
                f"add an evaluator to src/prove.py"
            )
        passed, details = evaluator(x, c["threshold"])
        trace.append({
            "rule": f"{c['name']}>={c['threshold']}",
            "passed": passed,
            "details": details,
            "weight": c["weight"],
        })
    score = sum(t["weight"] for t in trace if t["passed"])
    return {
        "id": x["id"],
        "is_keystone": score >= rules["pass_score"],
        "score": round(score, 3),
        "rules_version": rules.get("version", "unknown"),
        "trace": trace,
    }


def write_reports(results, rules, suffix=""):
    with open(os.path.join(ROOT, f"proof_traces{suffix}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    passing = sum(1 for r in results if r["is_keystone"])
    lines = [
        "# Proof Report",
        f"_Rules version {rules.get('version', 'unknown')} · pass_score "
        f"{rules['pass_score']} · generated {stamp}_",
        "",
        f"**{passing}/{len(results)} entries scored as keystones.**",
        "",
    ]
    for r in sorted(results, key=lambda r: (-r["score"], r["id"])):
        verdict = "✅ Keystone" if r["is_keystone"] else "❌ Not yet"
        lines.append(f"## {r['id']} — {verdict} (score {r['score']})")
        for t in r["trace"]:
            mark = "✔" if t["passed"] else "✖"
            lines.append(f"- {mark} **{t['rule']}** — {t['details']} (w={t['weight']})")
        lines.append("")
    with open(os.path.join(ROOT, f"proof_report{suffix}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", default=None,
                    help="path to a rule set (default: rules/keystone_rules.json)")
    ap.add_argument("--out-suffix", default="",
                    help="suffix for output filenames, e.g. '.v1'")
    args = ap.parse_args()

    rules = corpus.load_rules(args.rules)
    items = corpus.load_entries()
    results = [score_item(x, rules) for x in items]
    write_reports(results, rules, args.out_suffix)

    passing = sum(1 for r in results if r["is_keystone"])
    print(f"Scored {len(results)} entries under rules v{rules.get('version')}: "
          f"{passing} keystone, {len(results) - passing} not yet")
    print(f"Wrote proof_traces{args.out_suffix}.json and proof_report{args.out_suffix}.md")


if __name__ == "__main__":
    main()

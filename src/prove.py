#!/usr/bin/env python3
"""
Apply keystone rules, score, and produce proof traces per item.

Criteria are read from the rule set rather than hardcoded, so any archived rule
version still runs:

    python3 src/prove.py                                        # current rules
    python3 src/prove.py --rules legacy/rules/keystone_rules.v1.json \
                         --out-suffix .v1                       # reproduce v1.0 verdicts

## On the two ways evidence got scored

Two branches independently found the same flaw — v1.0 scored only what an
author asserted about a technology and never the evidence behind it, so an
entry could reach a perfect 1.0 on four hand-typed numbers. They fixed it
differently:

  - a multiplier: score = raw * (0.7 + 0.3 * mean_quality)
  - explicit criteria: evidence_strength, evidence_independence, claim_coverage

Applying both would penalise evidence twice, so this file keeps the criteria
and drops the multiplier. The reason is auditability, which is the point of a
proof trace: a multiplier reports "score 0.72, evidence quality 0.8" and leaves
you to guess, while criteria report which evidence dimension failed. It also
catches things a mean cannot see — four sources of one type look identical to
four independent ones under an average, and a claim whose evidence_refs do not
resolve is invisible to it entirely.

The cost is real and worth stating: discrete thresholds are cliff-edged, so an
entry at 0.74 mean quality loses the full weight that one at 0.75 keeps. The
multiplier degraded gracefully there. `evidence_quality()` survives as the
helper behind the evidence_strength criterion.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT

# Module-level defaults, kept for callers and tests that score against the
# current rule set without threading it through.
rules = corpus.load_rules()
criteria_by_name = {c["name"]: c for c in rules["criteria"]}
PASS_SCORE = rules["pass_score"]


def load_items():
    return corpus.load_entries()


def evidence_quality(x):
    """Mean evidence quality for an entry, in [0, 1]. 0 if nothing is scored."""
    qualities = [ev["quality"] for ev in x.get("evidence", []) if "quality" in ev]
    if not qualities:
        return 0.0
    return sum(qualities) / len(qualities)


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
    n = len([e for e in x.get("evidence", []) if "quality" in e])
    if not n:
        return False, "no scored evidence"
    mean = evidence_quality(x)
    return mean >= thr, f"mean_evidence_quality={mean:.3f} over {n} items"


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


def score_item(x, rule_set=None):
    """Score one entry. Defaults to the current rule set."""
    rule_set = rule_set or rules
    trace = []
    for c in rule_set["criteria"]:
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
        "is_keystone": score >= rule_set["pass_score"],
        "score": round(score, 3),
        "evidence_quality": round(evidence_quality(x), 3),
        "rules_version": rule_set.get("version", "unknown"),
        "trace": trace,
    }


def write_reports(results, rule_set=None, suffix=""):
    rule_set = rule_set or rules
    with open(os.path.join(ROOT, f"proof_traces{suffix}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    passing = sum(1 for r in results if r["is_keystone"])
    lines = [
        "# Proof Report",
        f"_Rules version {rule_set.get('version', 'unknown')} · pass_score "
        f"{rule_set['pass_score']} · generated {stamp}_",
        "",
        f"**{passing}/{len(results)} entries scored as keystones.**",
        "",
    ]
    for r in sorted(results, key=lambda r: (-r["score"], r["id"])):
        verdict = "✅ Keystone" if r["is_keystone"] else "❌ Not yet"
        lines.append(
            f"## {r['id']} — {verdict} (score {r['score']}, "
            f"evidence quality {r.get('evidence_quality', 0)})"
        )
        for t in r["trace"]:
            mark = "✔" if t["passed"] else "✖"
            lines.append(f"- {mark} **{t['rule']}** — {t['details']} (w={t['weight']})")
        lines.append("")
    with open(os.path.join(ROOT, f"proof_report{suffix}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="prove",
        description="Score encoded keystones against a rule set.",
    )
    ap.add_argument("--rules", default=None,
                    help="path to a rule set (default: rules/keystone_rules.json)")
    ap.add_argument("--out-suffix", default="",
                    help="suffix for output filenames, e.g. '.v1'")
    args = ap.parse_args(argv)

    rule_set = corpus.load_rules(args.rules) if args.rules else rules
    items = load_items()
    results = [score_item(x, rule_set) for x in items]
    write_reports(results, rule_set, args.out_suffix)

    passing = sum(1 for r in results if r["is_keystone"])
    print(f"Scored {len(results)} entries under rules v{rule_set.get('version')}: "
          f"{passing} keystone, {len(results) - passing} not yet")
    print(f"Wrote proof_traces{args.out_suffix}.json and proof_report{args.out_suffix}.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Falsification engine — the scientific method as a runnable loop.

    hypothesize -> run -> falsified? -> edit the claim -> register unknowns -> rerun

Every hypothesis in hypotheses/ names a test kind and its parameters. This
module holds the tests. A run does four things:

  1. evaluates every hypothesis against the corpus
  2. writes the verdict back into the hypothesis file (`last_result`)
  3. appends an immutable record to ledger/runs.jsonl
  4. reconciles unknowns/register.json — new questions opened, answered
     questions closed

Falsification is not failure. The engine exits 0 even when hypotheses are
falsified; that is the loop working. Use --strict in CI if you want a
falsified hypothesis to break the build.

Usage:
    python3 src/falsify.py                # run all, update ledger + unknowns
    python3 src/falsify.py --only H002    # run one
    python3 src/falsify.py --dry-run      # report without writing anything
"""
import argparse
import datetime
import glob
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402
import prove  # noqa: E402

ROOT = corpus.ROOT
HYPOTHESIS_DIR = os.path.join(ROOT, "hypotheses")
LEDGER_DIR = os.path.join(ROOT, "ledger")
UNKNOWNS_DIR = os.path.join(ROOT, "unknowns")
PHI = (1 + math.sqrt(5)) / 2


def result(passed, summary, detail=None, unknowns=None, stats=None):
    return {
        "passed": passed,
        "summary": summary,
        "detail": detail or [],
        "unknowns": unknowns or [],
        "stats": stats or {},
    }


# ── Tests ────────────────────────────────────────────────────────────────
# Signature: test(ctx, params) -> result(). ctx carries the loaded corpus so
# a run reads the data once.

def t_id_consistency(ctx, params):
    """Catalogue ids and encoded-entry ids name the same things."""
    entries_by_id = {x["id"]: x for x in ctx["entries"]}
    problems = []
    unknowns = []

    confirmed = [c for c in ctx["catalogue"] if c.get("status") == "confirmed"]
    for c in confirmed:
        if c["id"] not in entries_by_id:
            problems.append(
                f"catalogue marks '{c['id']}' ({c['name']}) confirmed, "
                f"but no encoded entry has that id"
            )

    catalogue_ids = {c["id"] for c in ctx["catalogue"]}
    for eid, entry in sorted(entries_by_id.items()):
        if eid not in catalogue_ids:
            problems.append(
                f"encoded entry '{eid}' ({entry['name']}) is absent from the catalogue"
            )

    if problems:
        unknowns.append({
            "question": "Is the catalogue id or the entry id the canonical name "
                        "for a keystone, and what enforces the link?",
            "why": "confirmed-status catalogue rows and encoded entries drifted apart",
        })
        return result(False, f"{len(problems)} id mismatch(es) between catalogue and entries",
                      problems, unknowns, {"mismatches": len(problems)})
    return result(True, f"all {len(confirmed)} confirmed catalogue ids resolve to encoded entries",
                  stats={"confirmed": len(confirmed), "entries": len(entries_by_id)})


def t_unlock_resolution(ctx, params):
    """Every `unlocks` target resolves to an entry id or a declared lineage term."""
    known_entries = {x["id"] for x in ctx["entries"]}
    known_lineages = {t["id"] for t in ctx["lineage_terms"]}
    dangling = []
    total = 0
    for x in ctx["entries"]:
        for target in x.get("unlocks", []):
            total += 1
            if target not in known_entries and target not in known_lineages:
                dangling.append(f"{x['id']} -> '{target}' resolves to nothing")

    if dangling:
        return result(
            False,
            f"{len(dangling)}/{total} unlock targets dangle "
            f"({len(known_lineages)} lineage terms declared)",
            dangling,
            [{
                "question": "Are `unlocks` pointers to other keystones, or names of "
                            "downstream technology families? The field is being used "
                            "for both.",
                "why": "no unlock target resolves to anything the repo defines",
            }],
            {"dangling": len(dangling), "total": total},
        )
    return result(True, f"all {total} unlock targets resolve",
                  stats={"total": total, "lineage_terms": len(known_lineages)})


def t_era_longevity_coherence(ctx, params):
    """
    metrics.longevity_years should agree with era.end - era.start, unless the
    entry says in `longevity_basis` why it measures something narrower.
    """
    tolerance = params.get("tolerance", 0.25)
    basis_field = params.get("exempt_field", "longevity_basis")
    problems = []
    exempted = []
    for x in ctx["entries"]:
        span = x["era"]["end"] - x["era"]["start"]
        stated = x["metrics"].get("longevity_years", 0)
        if span <= 0:
            continue
        drift = abs(stated - span) / span
        if drift <= tolerance:
            continue
        if x.get(basis_field):
            exempted.append(f"{x['id']}: {stated}yr vs {span}yr span — "
                            f"declared basis: {x[basis_field]}")
            continue
        problems.append(
            f"{x['id']}: longevity_years={stated} but era spans {span}yr "
            f"({drift * 100:.0f}% drift), no {basis_field} given"
        )

    if problems:
        return result(
            False,
            f"{len(problems)} entries state a longevity their era does not support",
            problems + exempted,
            [{
                "question": "Does longevity_years mean attested continuous use, "
                            "survival of the artefact, or revivability? Each gives a "
                            "different number for the same technology.",
                "why": "stated longevity and era span disagree with no declared basis",
            }],
            {"incoherent": len(problems), "exempted": len(exempted)},
        )
    return result(True,
                  f"all {len(ctx['entries'])} entries coherent within {tolerance:.0%} "
                  f"({len(exempted)} by declared basis)",
                  exempted, stats={"exempted": len(exempted)})


def t_evidence_floor(ctx, params):
    """Every claim is backed by resolving evidence of adequate quality."""
    min_refs = params.get("min_refs_per_claim", 1)
    min_quality = params.get("min_mean_quality", 0.7)
    problems = []
    qualities = []
    for x in ctx["entries"]:
        known = {e.get("id") for e in x.get("evidence", [])}
        for e in x.get("evidence", []):
            qualities.append(e.get("quality", 0.0))
        for c in x.get("claims", []):
            refs = c.get("evidence_refs", [])
            resolving = [r for r in refs if r in known]
            if len(resolving) < min_refs:
                problems.append(
                    f"{x['id']}/{c['id']}: {len(resolving)} resolving ref(s), "
                    f"need {min_refs} — refs={refs}"
                )
    mean_quality = sum(qualities) / len(qualities) if qualities else 0.0
    if mean_quality < min_quality:
        problems.append(
            f"corpus mean evidence quality {mean_quality:.3f} < {min_quality}"
        )

    if problems:
        return result(
            False, f"{len(problems)} evidence shortfall(s)", problems,
            [{
                "question": "What is the minimum evidence a claim needs before the "
                            "codex will carry it?",
                "why": "claims present without evidence meeting the stated floor",
            }],
            {"mean_quality": round(mean_quality, 3)},
        )
    return result(True,
                  f"every claim backed by ≥{min_refs} resolving ref; "
                  f"mean quality {mean_quality:.3f}",
                  stats={"mean_quality": round(mean_quality, 3)})


def t_domain_coverage(ctx, params):
    """No domain in the schema sits empty in the encoded corpus."""
    min_entries = params.get("min_entries_per_domain", 1)
    schema = corpus.load_schema("keystone.schema.json")
    domains = schema["properties"]["domain"]["enum"]
    counts = {d: 0 for d in domains}
    for x in ctx["entries"]:
        counts[x["domain"]] = counts.get(x["domain"], 0) + 1

    empty = [d for d in domains if counts.get(d, 0) < min_entries]
    detail = [f"{d}: {counts.get(d, 0)} encoded" for d in domains]
    if empty:
        unknowns = [{
            "question": f"What keystone belongs in the '{d}' domain, and why has "
                        f"nothing been encoded there yet — absence of candidates, "
                        f"or absence of attention?",
            "why": f"domain '{d}' has {counts.get(d, 0)} encoded entries",
        } for d in empty]
        if "social" in empty and counts.get("governance", 0) > 0:
            unknowns.append({
                "question": "Are 'social' and 'governance' distinct domains, or one "
                            "domain listed twice in the schema enum?",
                "why": "governance is populated while social has never been used",
            })
        return result(False, f"{len(empty)}/{len(domains)} domains below {min_entries} "
                             f"encoded entries: {', '.join(empty)}",
                      detail, unknowns, {"counts": counts})
    return result(True, f"all {len(domains)} domains have ≥{min_entries} encoded entries",
                  detail, stats={"counts": counts})


def t_rubric_discrimination(ctx, params):
    """
    A rubric that admits everything measures nothing. The rule set must
    separate the corpus, not rubber-stamp it.
    """
    max_pass_fraction = params.get("max_pass_fraction", 0.9)
    min_score_spread = params.get("min_score_spread", 0.2)

    rules = ctx["rules"]
    scored = [prove.score_item(x, rules) for x in ctx["entries"]]
    if not scored:
        return result(False, "no entries to score")
    scores = [s["score"] for s in scored]
    passing = [s for s in scored if s["is_keystone"]]
    pass_fraction = len(passing) / len(scored)
    spread = max(scores) - min(scores)

    detail = [f"{s['id']}: {s['score']} "
              f"({'pass' if s['is_keystone'] else 'fail'})"
              for s in sorted(scored, key=lambda s: -s["score"])]
    detail.append(f"pass_fraction={pass_fraction:.2f} (max {max_pass_fraction}), "
                  f"score_spread={spread:.3f} (min {min_score_spread})")

    problems = []
    if pass_fraction > max_pass_fraction:
        problems.append(f"{len(passing)}/{len(scored)} entries pass — the rubric is "
                        f"not rejecting anything")
    if spread < min_score_spread:
        problems.append(f"score spread {spread:.3f} — the rubric barely separates "
                        f"the corpus")

    if problems:
        return result(
            False, "; ".join(problems), detail,
            [{
                "question": "Is the corpus genuinely uniform in quality, or is the "
                            "rubric too easy? A rubric only tested on entries chosen "
                            "because they are keystones cannot tell you.",
                "why": f"{pass_fraction:.0%} of entries pass under rules "
                       f"v{rules.get('version')}",
            }],
            {"pass_fraction": round(pass_fraction, 3), "spread": round(spread, 3)},
        )
    return result(True,
                  f"{len(passing)}/{len(scored)} pass, spread {spread:.3f} — "
                  f"rubric discriminates",
                  detail,
                  stats={"pass_fraction": round(pass_fraction, 3),
                         "spread": round(spread, 3)})


def t_phi_significance(ctx, params):
    """
    src/shadow_search.py hunts triads of technologies whose emergence gaps sit
    near the golden ratio, and suggests this "may indicate underlying systemic
    coupling". This test asks the only question that matters: does the
    catalogue contain more such triads than the same number of dates thrown at
    random into the same window?

    Null model: n years drawn uniformly from [min, max] of the observed
    starts. Seeded, so the verdict is reproducible.

    `direction` says which way the hypothesis points. "exceeds_chance" is the
    original claim; "indistinguishable" is its replacement after
    run-001-baseline, and is supported when the null model cannot be rejected.
    """
    tolerance = params.get("tolerance", 0.10)
    trials = params.get("trials", 300)
    alpha = params.get("alpha", 0.05)
    seed = params.get("seed", 1618)
    direction = params.get("direction", "exceeds_chance")

    years = sorted(e["era"]["start"] for e in ctx["catalogue"] if "era" in e)
    n = len(years)
    lo, hi = years[0], years[-1]

    def count_triads(ys):
        ys = sorted(ys)
        hits = 0
        for i in range(len(ys)):
            for j in range(i + 1, len(ys)):
                g1 = ys[j] - ys[i]
                if g1 == 0:
                    continue
                for k in range(j + 1, len(ys)):
                    g2 = ys[k] - ys[j]
                    if g2 == 0:
                        continue
                    ratio = max(g1, g2) / min(g1, g2)
                    if abs(ratio - PHI) / PHI < tolerance:
                        hits += 1
        return hits

    observed = count_triads(years)
    rng = random.Random(seed)
    null_counts = []
    for _ in range(trials):
        null_counts.append(count_triads([rng.randint(lo, hi) for _ in range(n)]))
    null_mean = sum(null_counts) / len(null_counts)
    at_least = sum(1 for c in null_counts if c >= observed)
    p = (at_least + 1) / (trials + 1)  # add-one, so p is never reported as 0

    detail = [
        f"n={n} dates spanning {lo}..{hi}",
        f"observed phi-triads (within {tolerance:.0%}): {observed}",
        f"null model mean: {null_mean:.1f} over {trials} seeded trials",
        f"null range: {min(null_counts)}..{max(null_counts)}",
        f"p = {p:.4f} (alpha {alpha})",
    ]
    stats = {"observed": observed, "null_mean": round(null_mean, 1),
             "p": round(p, 4), "trials": trials, "seed": seed,
             "direction": direction}
    significant = p < alpha

    if direction == "indistinguishable":
        if significant:
            return result(
                False,
                f"phi-triads do exceed chance after all (p={p:.4f}) — the "
                f"detector found signal and the revised claim is wrong",
                detail, [], stats,
            )
        return result(
            True,
            f"phi-triads ({observed}) indistinguishable from chance "
            f"(null mean {null_mean:.1f}, p={p:.3f}) — negative control holds",
            detail, stats=stats,
        )

    if not significant:
        return result(
            False,
            f"phi-triads ({observed}) are no more common than chance "
            f"(null mean {null_mean:.1f}, p={p:.3f})",
            detail,
            [{
                "question": "Does any temporal-spacing regularity in this corpus "
                            "survive a null model, or is every such pattern an "
                            "artefact of the number of dates and the width of the "
                            "window?",
                "why": "the phi detector's output is indistinguishable from random dates",
            }],
            stats,
        )
    return result(True, f"phi-triads exceed chance (p={p:.4f})", detail, stats=stats)


def t_taxonomy_exercised(ctx, params):
    """
    CITATIONS.md declares an evidence taxonomy. A type nobody ever uses is a
    claim about openness that the corpus does not honour — which matters most
    for the types hardest to admit, like oral tradition.
    """
    declared = params.get("declared_types", [])
    used = set()
    for x in ctx["entries"]:
        for e in x.get("evidence", []):
            if e.get("type"):
                used.add(e["type"])

    unused = [t for t in declared if t not in used]
    undeclared = sorted(t for t in used if t not in declared)
    detail = [f"declared: {len(declared)}, used: {len(used)}"]
    detail += [f"unused: {t}" for t in unused]
    detail += [f"used but undeclared in CITATIONS.md: {t}" for t in undeclared]

    if unused or undeclared:
        unknowns = []
        if "oral_tradition_encoded" in unused:
            unknowns.append({
                "question": "Under what conditions does the codex accept oral "
                            "tradition as evidence, and at what quality weight? "
                            "The type is declared but has never been used.",
                "why": "an evidence type the project claims to admit has zero uses",
            })
        if unused:
            unknowns.append({
                "question": "Is the unused half of the evidence taxonomy aspirational "
                            "or dead vocabulary?",
                "why": f"{len(unused)}/{len(declared)} declared evidence types unused",
            })
        return result(False,
                      f"{len(unused)} declared evidence type(s) unused, "
                      f"{len(undeclared)} used but undeclared",
                      detail, unknowns,
                      {"unused": unused, "undeclared": undeclared})
    return result(True, f"all {len(declared)} declared evidence types exercised", detail)


TESTS = {
    "id_consistency": t_id_consistency,
    "unlock_resolution": t_unlock_resolution,
    "era_longevity_coherence": t_era_longevity_coherence,
    "evidence_floor": t_evidence_floor,
    "domain_coverage": t_domain_coverage,
    "rubric_discrimination": t_rubric_discrimination,
    "phi_significance": t_phi_significance,
    "taxonomy_exercised": t_taxonomy_exercised,
}


# ── Engine ───────────────────────────────────────────────────────────────

def load_hypotheses():
    hs = []
    for path in sorted(glob.glob(os.path.join(HYPOTHESIS_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            hs.append((path, json.load(f)))
    return hs


def build_context():
    return {
        "entries": corpus.load_entries(),
        "catalogue": corpus.load_catalogue(),
        "rules": corpus.load_rules(),
        "lineage_terms": corpus.load_lineage_terms()["terms"],
    }


def run_hypothesis(h, ctx):
    kind = h["test"]["kind"]
    test = TESTS.get(kind)
    if test is None:
        return result(False, f"unknown test kind '{kind}'")
    return test(ctx, h["test"].get("params", {}))


def reconcile_unknowns(raised, run_id, dry_run):
    """
    Merge this run's unknowns into the register.

    Three states, and the distinction between the last two is the whole point:

      open      raised by a failing hypothesis on this run, or pinned
      resolved  somebody wrote an answer into `resolution`
      dormant   no longer raised, and nobody ever answered it

    A hypothesis passing does not answer the question its failure raised. When
    H005 stopped complaining about the empty 'ethical' domain it was because an
    entry got encoded there, not because anyone worked out what belongs in it.
    Auto-closing that as 'resolved' would launder a silence into a finding, so
    unanswered questions go dormant instead and stay legible.

    `pinned: true` marks a question added by hand rather than raised by a test.
    The engine never closes those; only a human removing the pin does.
    """
    path = os.path.join(UNKNOWNS_DIR, "register.json")
    register = {"unknowns": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            register = json.load(f)

    by_id = {u["id"]: u for u in register["unknowns"]}
    seen_now = set()

    for hid, u in raised:
        # stable, human-readable id: hypothesis + ordinal among that hypothesis
        siblings = [x for x in by_id.values() if x["raised_by"] == hid]
        existing = next((x for x in siblings if x["question"] == u["question"]), None)
        if existing:
            uid = existing["id"]
            existing["status"] = "open"
            existing["last_seen"] = run_id
            existing.pop("resolved_in", None)
        else:
            uid = f"U-{hid}-{len(siblings) + 1}"
            by_id[uid] = {
                "id": uid,
                "question": u["question"],
                "raised_by": hid,
                "trigger": u["why"],
                "first_seen": run_id,
                "last_seen": run_id,
                "status": "open",
                "resolution": None,
            }
        seen_now.add(uid)

    for uid, u in by_id.items():
        if uid in seen_now or u.get("pinned"):
            u["status"] = "open"
            continue
        if u.get("resolution"):
            u["status"] = "resolved"
            u.setdefault("closed_in", run_id)
        elif u["status"] == "open":
            u["status"] = "dormant"
            u["closed_in"] = run_id

    register["unknowns"] = sorted(by_id.values(), key=lambda u: u["id"])
    if not dry_run:
        os.makedirs(UNKNOWNS_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(register, f, indent=2)
        render_unknowns(register, run_id)
    return register


def render_unknowns(register, run_id):
    buckets = {"open": [], "resolved": [], "dormant": []}
    for u in register["unknowns"]:
        buckets.setdefault(u["status"], []).append(u)

    lines = [
        "# Unknowns Register",
        "",
        "Questions this project does not have answers to. Most were opened by a "
        "hypothesis that failed; some were pinned by hand because they matter and "
        "no test reaches them yet.",
        "",
        "**Open** — live, and worth someone's time. **Resolved** — answered, with the "
        "answer written down. **Dormant** — the test that raised it stopped asking, "
        "and nobody ever answered it. Dormant is not resolved, and the two are kept "
        "apart on purpose: a question that goes quiet because the data changed under "
        "it is still open, it just lost its alarm.",
        "",
        f"_Reconciled at `{run_id}` · {len(buckets['open'])} open · "
        f"{len(buckets['resolved'])} resolved · {len(buckets['dormant'])} dormant_",
        "",
    ]

    def render(title, items, note):
        out = [f"## {title}", ""]
        if not items:
            return out + ["_None._", ""]
        if note:
            out += [note, ""]
        for u in items:
            pin = " · **pinned**" if u.get("pinned") else ""
            out += [
                f"### {u['id']} — {u['question']}",
                f"- Raised by **{u['raised_by']}** · first seen `{u['first_seen']}`{pin}",
                f"- Trigger: {u['trigger']}",
            ]
            if u.get("resolution"):
                out.append(f"- **Resolution** (`{u.get('closed_in', run_id)}`): {u['resolution']}")
            out.append("")
        return out

    lines += render("Open", buckets["open"], None)
    lines += render("Resolved", buckets["resolved"], None)
    lines += render(
        "Dormant", buckets["dormant"],
        "_No hypothesis currently raises these. That is a fact about the tests, "
        "not about the questions._")

    with open(os.path.join(ROOT, "UNKNOWNS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def append_ledger(run_id, records, dry_run):
    """Append-only. The point of the ledger is that past runs are never edited."""
    if dry_run:
        return
    os.makedirs(LEDGER_DIR, exist_ok=True)
    with open(os.path.join(LEDGER_DIR, "runs.jsonl"), "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def render_ledger():
    path = os.path.join(LEDGER_DIR, "runs.jsonl")
    if not os.path.exists(path):
        return
    runs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            runs.setdefault(rec["run"], []).append(rec)

    lines = [
        "# Hypothesis Ledger",
        "",
        "Every falsification run, oldest first. Nothing here is edited after the "
        "fact — a claim that was falsified stays falsified in the record, and its "
        "revision appears as a later run. This is the file to read if you want to "
        "know what this project already tried and what the data did to it.",
        "",
        "Generated from `ledger/runs.jsonl` by `src/falsify.py`.",
        "",
    ]
    for run_id in sorted(runs):
        records = sorted(runs[run_id], key=lambda r: r["hypothesis"])
        falsified = [r for r in records if not r["passed"]]
        lines += [
            f"## {run_id}",
            "",
            f"{len(records) - len(falsified)} supported · {len(falsified)} falsified",
            "",
            "| Hypothesis | Verdict | Summary |",
            "| --- | --- | --- |",
        ]
        for r in records:
            verdict = "supported" if r["passed"] else "**falsified**"
            summary = r["summary"].replace("|", "\\|")
            lines.append(f"| `{r['hypothesis']}` | {verdict} | {summary} |")
        lines.append("")
    with open(os.path.join(LEDGER_DIR, "LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_report(run_id, rows):
    falsified = [r for r in rows if not r["result"]["passed"]]
    lines = [
        "# Falsification Report",
        f"_Run `{run_id}` · {len(rows) - len(falsified)} supported · "
        f"{len(falsified)} falsified_",
        "",
        "A falsified hypothesis is a result, not a bug. The loop is: state the "
        "claim, run it, and when the data says no, edit the claim rather than the "
        "data. Open questions land in `UNKNOWNS.md`; the run history is in "
        "`ledger/LEDGER.md`.",
        "",
    ]
    for row in rows:
        h, res = row["hypothesis"], row["result"]
        mark = "✅ supported" if res["passed"] else "❌ falsified"
        lines += [
            f"## {h['id']} — {mark}",
            "",
            f"**Claim.** {h['statement']}",
            "",
            f"**Prediction.** {h['prediction']}",
            "",
            f"**Test.** `{h['test']['kind']}` — {res['summary']}",
            "",
        ]
        if res["detail"]:
            lines.append("<details><summary>detail</summary>\n")
            for d in res["detail"]:
                lines.append(f"- {d}")
            lines.append("\n</details>\n")
        if h.get("revisions"):
            lines.append("**Revision history.**")
            for rev in h["revisions"]:
                lines.append(f"- `{rev['run']}` — {rev['because']}")
            lines.append("")
    with open(os.path.join(ROOT, "falsification_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=None,
                    help="run only these hypothesis ids (repeatable)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report without writing ledger, unknowns, or hypothesis files")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any hypothesis is falsified")
    ap.add_argument("--run-id", default=None, help="override the generated run id")
    args = ap.parse_args()

    run_id = args.run_id or "run-" + datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ctx = build_context()
    hypotheses = load_hypotheses()
    if args.only:
        wanted = set(args.only)
        hypotheses = [(p, h) for p, h in hypotheses if h["id"] in wanted]
    if not hypotheses:
        print("No hypotheses to run.")
        return

    rows, ledger_records, raised = [], [], []
    for path, h in hypotheses:
        res = run_hypothesis(h, ctx)
        rows.append({"hypothesis": h, "result": res})

        status = "supported" if res["passed"] else "falsified"
        mark = "✅" if res["passed"] else "❌"
        print(f"{mark} {h['id']} {status}: {res['summary']}")

        ledger_records.append({
            "run": run_id,
            "hypothesis": h["id"],
            "statement": h["statement"],
            "test": h["test"]["kind"],
            "params": h["test"].get("params", {}),
            "passed": res["passed"],
            "summary": res["summary"],
            "stats": res["stats"],
            "rules_version": ctx["rules"].get("version"),
        })
        for u in res["unknowns"]:
            raised.append((h["id"], u))

        if not args.dry_run:
            h["status"] = status
            h["last_result"] = {
                "run": run_id,
                "passed": res["passed"],
                "summary": res["summary"],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(h, f, indent=2)
                f.write("\n")

    append_ledger(run_id, ledger_records, args.dry_run)
    if not args.dry_run:
        render_ledger()
        write_report(run_id, rows)
    register = reconcile_unknowns(raised, run_id, args.dry_run)

    falsified = [r for r in rows if not r["result"]["passed"]]
    openq = [u for u in register["unknowns"] if u["status"] == "open"]
    print(f"\n{run_id}: {len(rows) - len(falsified)} supported, "
          f"{len(falsified)} falsified, {len(openq)} open unknowns")
    if not args.dry_run:
        print("Wrote falsification_report.md, UNKNOWNS.md, "
              "ledger/runs.jsonl, ledger/LEDGER.md, unknowns/register.json")

    if args.strict and falsified:
        sys.exit(1)


if __name__ == "__main__":
    main()

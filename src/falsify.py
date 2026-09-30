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
    """
    `passed` has three values, not two.

        True   the prediction held
        False  the prediction failed -- the claim is falsified
        None   the test could not reach a verdict: NO DATA

    None was added with the architecture layer. H-BYPASS reads a register that
    ships empty, and an empty register must not report as supported: a claim
    with no records against it has not been tested, it has been left alone.
    Collapsing "no data" into either verdict launders a silence into a finding,
    which is the same error the dormant/resolved split in the unknowns register
    exists to prevent.

    --strict exits 1 on False only. An untested claim does not break a build;
    it also does not count as a pass anywhere in the report or the ledger.
    """
    return {
        "passed": passed,
        "summary": summary,
        "detail": detail or [],
        "unknowns": unknowns or [],
        "stats": stats or {},
    }


def no_data(summary, detail=None, unknowns=None, stats=None):
    """A verdict of neither. See result()."""
    return result(None, summary, detail, unknowns, stats)


def verdict_of(res):
    return {True: "supported", False: "falsified"}.get(res["passed"], "no data")


def target_unknown(h, res):
    """
    RULE 1, enforced rather than requested.

    A hypothesis binds a TARGET (what it is trying to measure) to a RENDERING
    (the specific method or claim that carries the attempt). Falsifying the
    rendering does not close the target. When a hypothesis declaring both is
    falsified, its target is raised as an open unknown, unless the hypothesis
    declares `target_reached: true` -- that is, unless the test reached the
    target itself rather than only its rendering.

    Returns (unknown_or_None, note_or_None). The note fires when a falsified
    hypothesis declares no split at all, so the gap is visible in the report
    instead of being inferred from silence.
    """
    if res["passed"] is not False:
        return None, None
    m = h.get("measures")
    if not m:
        return None, (f"{h['id']} declares no target/rendering split, so what "
                      f"this falsification closes is unrecorded (CLAUDE.md RULE 1)")
    if m.get("target_reached"):
        return None, (f"{h['id']} declares target_reached -- the falsification "
                      f"reaches the target, not only the rendering")
    q = m.get("target_question")
    if not q:
        return None, (f"{h['id']} declares a target but no target_question, so "
                      f"the target cannot be raised as an unknown (CLAUDE.md RULE 1)")
    return {
        "question": q,
        "why": (f"the rendering was falsified ({res['summary']}); the target "
                f"it was aimed at -- {m.get('target')} -- is not closed by that"),
    }, None


# ── Tests ────────────────────────────────────────────────────────────────
# Signature: test(ctx, params) -> result(). ctx carries the loaded corpus so
# a run reads the data once.

def t_id_consistency(ctx, params):
    """
    A catalogue row marked 'confirmed' must resolve to an encoded entry with
    the same id. That direction is load-bearing: if it fails, 'confirmed' is
    simply a false statement about the repository.

    The reverse direction — every entry having a catalogue row — is reported
    but does not fail by default. It was a hard requirement while
    shadow_catalogue.json was the only index; there are now two registries with
    different conventions and no decision about which is canonical, so
    enforcing it would pick a winner by fiat rather than by argument.
    Set require_registry_row to turn it back into a failure.
    """
    require_row = params.get("require_registry_row", False)
    entries_by_id = {x["id"]: x for x in ctx["entries"]}
    problems = []
    notes = []
    unknowns = []

    confirmed = [c for c in ctx["catalogue"] if c.get("status") == "confirmed"]
    for c in confirmed:
        if c["id"] not in entries_by_id:
            problems.append(
                f"catalogue marks '{c['id']}' ({c['name']}) confirmed, "
                f"but no encoded entry has that id"
            )

    indexed = {c["id"] for c in ctx["catalogue"]}
    indexed |= {c.get("id") for c in ctx["candidates"]}
    unindexed = [eid for eid in sorted(entries_by_id) if eid not in indexed]

    if unindexed:
        notes.append(f"{len(unindexed)} encoded entries appear in no registry: "
                     + ", ".join(unindexed[:8])
                     + (" …" if len(unindexed) > 8 else ""))
        unknowns.append({
            "question": "Which registry indexes the encoded corpus — "
                        "data/shadow_catalogue.json, data/candidates.json, or both? "
                        "They currently overlap in zero rows.",
            "why": f"{len(unindexed)} of {len(entries_by_id)} entries are listed in neither",
        })
        if require_row:
            problems.extend(f"encoded entry '{eid}' is absent from every registry"
                            for eid in unindexed)

    if problems:
        unknowns.append({
            "question": "Is the catalogue id or the entry id the canonical name "
                        "for a keystone, and what enforces the link?",
            "why": "confirmed-status catalogue rows and encoded entries drifted apart",
        })
        return result(False, f"{len(problems)} id mismatch(es) between catalogue and entries",
                      problems + notes, unknowns, {"mismatches": len(problems)})

    summary = f"all {len(confirmed)} confirmed catalogue ids resolve to encoded entries"
    if unindexed:
        summary += f"; {len(unindexed)} entries indexed nowhere"
    return result(True, summary, notes, unknowns,
                  {"confirmed": len(confirmed), "entries": len(entries_by_id),
                   "unindexed": len(unindexed)})


def t_unlock_resolution(ctx, params):
    """
    Every `unlocks` target resolves to exactly one thing: an entry id or a
    declared lineage term, never both.

    The collision half of this matters as much as the dangling half. When a
    lineage stub and a full entry share an id, the graph silently picks a
    winner and the reader cannot tell which definition they are looking at.
    """
    known_entries = {x["id"] for x in ctx["entries"]}
    known_lineages = {t["id"] for t in ctx["lineage_terms"]}

    collisions = sorted(known_entries & known_lineages)
    dangling = []
    total = 0
    for x in ctx["entries"]:
        for target in x.get("unlocks", []):
            total += 1
            if target not in known_entries and target not in known_lineages:
                dangling.append(f"{x['id']} -> '{target}' resolves to nothing")

    problems = list(dangling)
    problems += [f"'{c}' is defined both as an encoded entry and as a lineage term"
                 for c in collisions]

    if problems:
        unknowns = []
        if dangling:
            unknowns.append({
                "question": "Are `unlocks` pointers to other keystones, or names of "
                            "downstream technology families? The field is being used "
                            "for both.",
                "why": "unlock targets resolve to nothing the repo defines",
            })
        if collisions:
            unknowns.append({
                "question": "When a technology family is promoted to a full entry, "
                            "what removes the lineage stub that named it?",
                "why": f"{len(collisions)} id(s) carry two definitions at once",
            })
        summary = []
        if dangling:
            summary.append(f"{len(dangling)}/{total} unlock targets dangle")
        if collisions:
            summary.append(f"{len(collisions)} entry/lineage id collision(s)")
        return result(False, "; ".join(summary), problems, unknowns,
                      {"dangling": len(dangling), "collisions": len(collisions),
                       "total": total})

    return result(True, f"all {total} unlock targets resolve, no id collisions",
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
    A rubric that admits everything measures nothing. But the headline pass
    rate is the wrong way to detect that, and this test used to get it wrong.

    A corpus curated to contain keystones *should* mostly pass — a high pass
    rate is the expected result of good curation, not evidence of a broken
    rubric. What actually characterised the retired v1.0 was **ceiling
    saturation**: 80% of entries scored the maximum possible, so the rubric had
    run out of resolution and could no longer rank the things it admitted.

    The numbers that forced this revision, both measured on the same corpus:

        v1.0   80% at ceiling, spread 0.60, 1 inert criterion
        v1.1   32% at ceiling, spread 0.38, 1 inert criterion

    Note that v1.0's spread is *larger*. Spread alone would have ranked the
    broken rubric above the fixed one, and pass-fraction flagged v1.1 the
    moment the corpus grew. Ceiling saturation is the measure that actually
    separates them, which is why it is the one used here.

    An inert criterion — one that fires for no entry — is reported, not failed.
    From inside a curated corpus you cannot distinguish a floor everyone
    genuinely clears from dead weight.
    """
    max_ceiling_fraction = params.get("max_ceiling_fraction", 0.5)
    min_score_spread = params.get("min_score_spread", 0.2)

    rules = ctx["rules"]
    scored = [prove.score_item(x, rules) for x in ctx["entries"]]
    if not scored:
        return result(False, "no entries to score")

    ceiling = sum(c["weight"] for c in rules["criteria"])
    scores = [s["score"] for s in scored]
    passing = [s for s in scored if s["is_keystone"]]
    at_ceiling = [s for s in scored if abs(s["score"] - ceiling) < 1e-9]
    ceiling_fraction = len(at_ceiling) / len(scored)
    spread = max(scores) - min(scores)

    bite = {}
    for c in rules["criteria"]:
        prefix = c["name"] + ">="
        fails = sum(1 for s in scored for t in s["trace"]
                    if t["rule"].startswith(prefix) and not t["passed"])
        bite[c["name"]] = fails
    inert = [name for name, fails in bite.items() if fails == 0]

    detail = [f"{s['id']}: {s['score']}{' (fail)' if not s['is_keystone'] else ''}"
              for s in sorted(scored, key=lambda s: -s["score"])]
    detail.append(f"ceiling={ceiling:.2f}, at_ceiling={len(at_ceiling)}/{len(scored)} "
                  f"({ceiling_fraction:.0%}, max {max_ceiling_fraction:.0%})")
    detail.append(f"spread={spread:.3f} (min {min_score_spread})")
    detail += [f"criterion '{n}' fails for {f}/{len(scored)} entries"
               for n, f in sorted(bite.items(), key=lambda kv: -kv[1])]

    problems = []
    if ceiling_fraction > max_ceiling_fraction:
        problems.append(f"{len(at_ceiling)}/{len(scored)} entries score the maximum — "
                        f"the rubric has run out of resolution")
    if spread < min_score_spread:
        problems.append(f"score spread {spread:.3f} — the rubric barely separates "
                        f"the corpus")
    if not any(bite.values()):
        problems.append("no criterion fails for any entry — every rule is inert")

    unknowns = []
    if inert:
        unknowns.append({
            "question": f"Are the inert criteria ({', '.join(inert)}) floors the "
                        f"corpus genuinely clears, or dead weight nobody has tested?",
            "why": f"{len(inert)} criterion/criteria fire for no entry in the corpus",
        })

    if problems:
        unknowns.append({
            "question": "Is the corpus genuinely uniform in quality, or is the "
                        "rubric too easy? A rubric only tested on entries chosen "
                        "because they are keystones cannot tell you.",
            "why": f"{ceiling_fraction:.0%} of entries sit at the ceiling under rules "
                   f"v{rules.get('version')}",
        })
        return result(False, "; ".join(problems), detail, unknowns,
                      {"ceiling_fraction": round(ceiling_fraction, 3),
                       "spread": round(spread, 3), "inert": inert})

    return result(True,
                  f"{len(passing)}/{len(scored)} pass, {ceiling_fraction:.0%} at ceiling, "
                  f"spread {spread:.3f} — rubric discriminates",
                  detail, unknowns,
                  {"ceiling_fraction": round(ceiling_fraction, 3),
                   "spread": round(spread, 3), "inert": inert})


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
    # Read the taxonomy from the schema rather than restating it here. It used
    # to live in three places — the schema, validate.py, and these params — so
    # adding a type meant editing all three and discovering at runtime which
    # one you missed.
    declared = params.get("declared_types") or corpus.evidence_types()
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


# ── Architecture-layer tests ─────────────────────────────────────────────
# Added beside the per-entry rubric, not in place of it. The rubric measures
# an entry against thresholds; these measure whether an assembly is declared
# well enough to be checked at all. Different measurand, different tests, and
# neither reads the other's output.

def t_layer_role_coverage(ctx, params):
    """
    How much of the corpus has been read for its ROLE rather than its category?

    UNSET counts as DECLARED. An entry saying "nobody has read this one for
    its role" is a different state from an entry where the field is absent,
    and only the second is a gap in coverage. The test reports the fraction
    either way; the threshold only decides whether the claim about coverage
    survives.
    """
    max_undeclared = params.get("max_undeclared_fraction", 0.5)
    roles = ctx["layer_roles"]

    declared, undeclared, unset, by_role = [], [], [], {}
    for x in ctx["entries"]:
        role = x.get("layer_role")
        if role is None:
            undeclared.append(x["id"])
            continue
        declared.append(x["id"])
        if role == "UNSET":
            unset.append(x["id"])
        else:
            by_role.setdefault(role, []).append(x["id"])

    total = len(ctx["entries"])
    if total == 0:
        return no_data("no entries to read for layer_role")
    undeclared_fraction = len(undeclared) / total

    detail = [f"{len(declared)}/{total} declare layer_role "
              f"({len(unset)} of those declare UNSET)",
              f"{len(undeclared)}/{total} undeclared "
              f"({undeclared_fraction:.0%}, max {max_undeclared:.0%})"]
    detail += [f"{r}: {len(by_role.get(r, []))} entries" for r in roles]
    if undeclared:
        detail.append("undeclared: " + ", ".join(undeclared[:10])
                      + (" …" if len(undeclared) > 10 else ""))

    stats = {"total": total, "declared": len(declared), "unset": len(unset),
             "undeclared": len(undeclared),
             "undeclared_fraction": round(undeclared_fraction, 4),
             "by_role": {r: len(by_role.get(r, [])) for r in roles}}

    if undeclared_fraction > max_undeclared:
        return result(
            False,
            f"{len(undeclared)}/{total} entries declare no layer_role "
            f"({undeclared_fraction:.0%}) — the architecture layer exists and "
            f"is empty",
            detail, [], stats)
    return result(True,
                  f"{len(declared)}/{total} entries declare a layer_role "
                  f"({len(unset)} UNSET)", detail, [], stats)


def t_system_runs_on(ctx, params):
    """
    In each declared system, does every member's runs_on resolve to a member
    that is present?

    What is NOT checked: that the resolved member is LOWER in the stack. No
    document in this repository declares a total order over layer roles, and
    inventing one to make the test stricter would settle by fiat a question
    nobody has answered. The gap is reported in every run rather than fixed
    quietly.
    """
    import systems as systems_mod

    if not ctx["systems"]:
        return no_data("no systems declared under systems/ — nothing to check",
                       ["An absent architecture layer is not a satisfied one."])

    entries_by_id = {x["id"]: x for x in ctx["entries"]}
    reports = [systems_mod.integration_report(sysdef, entries_by_id,
                                              ctx["layer_roles"])
               for sysdef in ctx["systems"]]

    problems, detail = [], []
    evaluable = 0
    for r in reports:
        ro = r["runs_on"]
        if ro["targets"] == 0:
            detail.append(f"{r['system']}: no runs_on declared by any member — "
                          f"not evaluable")
        else:
            evaluable += 1
            detail.append(f"{r['system']}: {ro['satisfied']}/{ro['targets']} "
                          f"runs_on targets resolve ({ro['fraction']:.0%})")
        for u in ro["unmet"]:
            problems.append(f"{r['system']}: {u['entry']} -> {u['target']}: {u['why']}")
        for eid in r["missing_entries"]:
            problems.append(f"{r['system']}: member '{eid}' names no encoded entry")
        for c in r["conflicts"]:
            problems.append(f"{r['system']}: {c['entry']}: "
                            + (c["role_conflict"] or c["runs_on_conflict"]))
        if r["missing_layers"]:
            detail.append(f"{r['system']}: layers with no member — "
                          + ", ".join(r["missing_layers"]))
    detail.append(systems_mod.UNCHECKED_NOTE)

    stats = {"systems": len(reports), "evaluable": evaluable,
             "unmet": sum(len(r["runs_on"]["unmet"]) for r in reports)}

    if evaluable == 0:
        return no_data(f"{len(reports)} system(s) declared, none declaring any "
                       f"runs_on — nothing to resolve", detail, [], stats)
    if problems:
        return result(False, f"{len(problems)} unresolved runs_on target(s) or "
                             f"member conflict(s)", problems + detail, [], stats)
    return result(True, f"every runs_on target in {evaluable} evaluable "
                        f"system(s) resolves to a present member", detail, [], stats)


def t_integration_saturation(ctx, params):
    """
    The same ceiling-saturation check H006 applies to the rubric, applied to
    the integration report — so the architecture layer can fail in the way the
    per-entry layer already can.

    A report that has only ever returned full satisfaction cannot distinguish
    an integrated system from an unchecked one. Saturation is the measure that
    catches that, for the reason set out in H006's revision: a high pass rate
    on a curated set is expected, and it is running out of resolution that is
    the defect.
    """
    max_ceiling_fraction = params.get("max_ceiling_fraction", 0.5)
    min_spread = params.get("min_spread", 0.2)
    min_systems = params.get("min_systems", 2)
    import systems as systems_mod

    entries_by_id = {x["id"]: x for x in ctx["entries"]}
    reports = [systems_mod.integration_report(sysdef, entries_by_id,
                                              ctx["layer_roles"])
               for sysdef in ctx["systems"]]
    fractions = [r["runs_on"]["fraction"] for r in reports
                 if r["runs_on"]["fraction"] is not None]

    if not fractions:
        return no_data("no system reports a runs_on fraction — the integration "
                       "report has produced no readings to saturate",
                       [f"{len(reports)} system(s) declared"], [],
                       {"systems": len(reports), "evaluable": 0})

    at_ceiling = [f for f in fractions if abs(f - 1.0) < 1e-9]
    ceiling_fraction = len(at_ceiling) / len(fractions)
    spread = max(fractions) - min(fractions)

    detail = [f"{r['system']}: {r['runs_on']['fraction']}"
              for r in reports if r["runs_on"]["fraction"] is not None]
    detail.append(f"at ceiling: {len(at_ceiling)}/{len(fractions)} "
                  f"({ceiling_fraction:.0%}, max {max_ceiling_fraction:.0%})")
    detail.append(f"spread: {spread:.3f} (min {min_spread})")
    detail.append(f"evaluable systems: {len(fractions)} (min {min_systems})")

    stats = {"evaluable": len(fractions),
             "ceiling_fraction": round(ceiling_fraction, 4),
             "spread": round(spread, 4)}

    problems = []
    if len(fractions) < min_systems:
        problems.append(f"{len(fractions)} evaluable system(s), below the {min_systems} "
                        f"needed for saturation to mean anything — with one reading "
                        f"the spread is zero by construction")
    if ceiling_fraction > max_ceiling_fraction:
        problems.append(f"{len(at_ceiling)}/{len(fractions)} systems report full "
                        f"satisfaction — the report cannot tell an integrated "
                        f"system from an unchecked one")
    if spread < min_spread:
        problems.append(f"spread {spread:.3f} — the report barely separates the "
                        f"systems it reads")

    if problems:
        return result(False, "; ".join(problems), detail, [], stats)
    return result(True, f"{ceiling_fraction:.0%} of {len(fractions)} systems at "
                        f"ceiling, spread {spread:.3f} — the integration report "
                        f"has resolution", detail, [], stats)


def t_evaluator_bypass(ctx, params):
    """
    Reads data/evaluator_claims.json: records of one source rejecting a design
    under one attribution and accepting the same structure under another.

    The register ships EMPTY, and an empty register returns NO DATA rather than
    a pass. SYSTEMS_ANALOGY.md's semantic-bypass section is an unmeasured claim
    until somebody puts records in this file; reporting "supported" over zero
    rows would turn the absence of a search into evidence.

    A record only counts once its structural equivalence is argued and both
    halves carry a locator. Without that it says a source liked one thing and
    not another, which is not a bypass.
    """
    min_records = params.get("min_records", 3)
    claims = ctx["evaluator_claims"]

    if claims is None:
        return no_data("data/evaluator_claims.json does not exist — the register "
                       "has not been created")
    if not claims:
        return no_data(
            "data/evaluator_claims.json exists and holds 0 records — no data",
            ["The register was created by the architecture layer and left empty.",
             "An empty register supports nothing and refutes nothing.",
             "Filling it requires, per record: one source, a rejection with a "
             "locator and the reason the source itself gives, an acceptance with "
             "a locator, and an argued structural equivalence between the two."],
            [], {"records": 0, "usable": 0})

    live = [c for c in claims if c.get("status") != "withdrawn"]
    incomplete = []
    usable = []
    for c in live:
        missing = []
        eq = c.get("structural_equivalence") or {}
        if not eq.get("statement"):
            missing.append("structural_equivalence.statement")
        if not eq.get("basis"):
            missing.append("structural_equivalence.basis")
        for half in ("rejected", "accepted"):
            if not (c.get(half) or {}).get("locator"):
                missing.append(f"{half}.locator")
        if not (c.get("rejected") or {}).get("stated_reason"):
            missing.append("rejected.stated_reason")
        if missing:
            incomplete.append(f"{c.get('id', '?')}: missing " + ", ".join(missing))
        else:
            usable.append(c.get("id", "?"))

    detail = [f"{len(claims)} record(s), {len(live)} not withdrawn, "
              f"{len(usable)} usable"] + incomplete
    stats = {"records": len(claims), "live": len(live), "usable": len(usable),
             "incomplete": len(incomplete)}

    if len(usable) < min_records:
        return result(
            False,
            f"{len(usable)} usable record(s), below the {min_records} the claim "
            f"rests on ({len(incomplete)} record(s) incomplete)",
            detail, [], stats)
    return result(True, f"{len(usable)} usable record(s) of a source rejecting a "
                        f"structure under one attribution and accepting it under "
                        f"another", detail, [], stats)


TESTS = {
    "id_consistency": t_id_consistency,
    "unlock_resolution": t_unlock_resolution,
    "era_longevity_coherence": t_era_longevity_coherence,
    "evidence_floor": t_evidence_floor,
    "domain_coverage": t_domain_coverage,
    "rubric_discrimination": t_rubric_discrimination,
    "phi_significance": t_phi_significance,
    "taxonomy_exercised": t_taxonomy_exercised,
    "layer_role_coverage": t_layer_role_coverage,
    "system_runs_on": t_system_runs_on,
    "integration_saturation": t_integration_saturation,
    "evaluator_bypass": t_evaluator_bypass,
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
        "candidates": corpus.load_candidates(),
        "rules": corpus.load_rules(),
        "lineage_terms": corpus.load_lineage_terms()["terms"],
        "systems": corpus.load_systems(),
        "layer_roles": corpus.layer_roles(),
        "evaluator_claims": corpus.load_evaluator_claims(),
    }


def score_with(entry, rules):
    """Indirection so tests can stub scoring without importing prove's globals."""
    return prove.score_item(entry, rules)


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
    """
    Four sections, not three.

    FRAME-LEVEL is separate because those questions are not about a value in
    the corpus; they are about the frame the corpus is read in — where the
    entry boundary was cut, what the rubric has no row for, what a metric is
    being read as. A frame-level question mixed into the open list reads as
    one more item of work. Kept apart, it reads as what it is: a statement
    that the instrument may be pointed at the wrong measurand. Each one
    declares whose frame raised it, because a frame-level question asked from
    inside the frame is a different object from one asked from outside it.
    """
    buckets = {"open": [], "resolved": [], "dormant": []}
    frame = []
    for u in register["unknowns"]:
        if u.get("level") == "frame":
            frame.append(u)
            continue
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
        "it is still open, it just lost its alarm. **Frame-level** — not a gap in a "
        "value but a question about the frame the values are read in; these do not "
        "resolve by filling a field, so they are listed apart rather than mixed into "
        "the work queue.",
        "",
        "Some entries are marked *target-level* or *rendering-level*. A rendering is "
        "a specific method or claim; a target is what it was aimed at. Falsifying a "
        "rendering closes the rendering. See CLAUDE.md RULE 1.",
        "",
        f"_Reconciled at `{run_id}` · {len(buckets['open'])} open · "
        f"{len(buckets['resolved'])} resolved · {len(buckets['dormant'])} dormant · "
        f"{len(frame)} frame-level_",
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
            level = ""
            if u.get("level") in ("target", "rendering"):
                level = f" · {u['level']}-level"
            out += [
                f"### {u['id']} — {u['question']}",
                f"- Raised by **{u['raised_by']}** · first seen `{u['first_seen']}`{pin}{level}",
                f"- Trigger: {u['trigger']}",
            ]
            if u.get("frame"):
                out.append(f"- Reviewer frame: {u['frame']}")
            if u.get("rendering_of"):
                out.append(f"- Rendering of: {u['rendering_of']}")
            if u.get("target_of"):
                out.append(f"- Target of: {u['target_of']}")
            if u.get("resolution"):
                out.append(f"- **Resolution** (`{u.get('closed_in', run_id)}`): {u['resolution']}")
            out.append("")
        return out

    lines += render(
        "Frame-level", frame,
        "_Questions about the frame rather than about a value in it: where the "
        "entry boundary was cut, what a metric is being read as, what the rubric "
        "has no row for. These are kept out of the Open list because they do not "
        "resolve by filling a field. Each declares the frame it was raised from._")
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
    runs, notes = {}, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("kind") == "note":
                notes.append(rec)
                continue
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
            verdict = {True: "supported", False: "**falsified**"}.get(
                r["passed"], "_no data_")
            summary = r["summary"].replace("|", "\\|")
            lines.append(f"| `{r['hypothesis']}` | {verdict} | {summary} |")
        lines.append("")

    if notes:
        lines += [
            "## Notes",
            "",
            "Corrections and clarifications appended to the ledger without "
            "rewriting the run they correct. A note never edits an earlier "
            "record; the earlier record and the note both stand, and a reader "
            "sees what was believed and what was said about it afterwards.",
            "",
        ]
        for n in sorted(notes, key=lambda r: (r.get("date", ""), r.get("id", ""))):
            lines += [f"### {n.get('id', 'note')} — {n.get('title', '')}",
                      "",
                      f"_appended {n.get('date', 'undated')}"
                      + (f" · concerns `{n['concerns']}`" if n.get("concerns") else "")
                      + "_",
                      "",
                      n.get("body", ""),
                      ""]
    with open(os.path.join(LEDGER_DIR, "LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_report(run_id, rows):
    falsified = [r for r in rows if r["result"]["passed"] is False]
    untested = [r for r in rows if r["result"]["passed"] is None]
    supported = [r for r in rows if r["result"]["passed"] is True]
    lines = [
        "# Falsification Report",
        f"_Run `{run_id}` · {len(supported)} supported · "
        f"{len(falsified)} falsified · {len(untested)} no data_",
        "",
        "A falsified hypothesis is a result, not a bug. The loop is: state the "
        "claim, run it, and when the data says no, edit the claim rather than the "
        "data. Open questions land in `UNKNOWNS.md`; the run history is in "
        "`ledger/LEDGER.md`.",
        "",
    ]
    for row in rows:
        h, res = row["hypothesis"], row["result"]
        mark = {True: "✅ supported", False: "❌ falsified"}.get(
            res["passed"], "⬜ no data")
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
        m = h.get("measures")
        if m:
            lines += [
                f"**Target.** {m.get('target', '—')}",
                "",
                f"**Rendering.** {m.get('rendering', '—')}",
                "",
            ]
            if res["passed"] is False and not m.get("target_reached"):
                lines += [
                    "**What this falsification closes.** The rendering, not the "
                    "target. The target is open in `UNKNOWNS.md`.",
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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="falsify", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=None,
                    help="run only these hypothesis ids (repeatable)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report without writing ledger, unknowns, or hypothesis files")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any hypothesis is falsified")
    ap.add_argument("--run-id", default=None, help="override the generated run id")
    args = ap.parse_args(argv)

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

        # RULE 1. A falsified rendering does not close its target.
        tu, note = target_unknown(h, res)
        if tu:
            raised.append((h["id"], tu))
            res["detail"] = list(res["detail"]) + [
                f"RULE 1: target still open — {tu['question']}"]
        if note:
            res["detail"] = list(res["detail"]) + [f"RULE 1: {note}"]
        rows.append({"hypothesis": h, "result": res, "rule1_note": note})

        status = verdict_of(res)
        mark = {True: "✅", False: "❌"}.get(res["passed"], "⬜")
        print(f"{mark} {h['id']} {status}: {res['summary']}")

        ledger_records.append({
            "run": run_id,
            "hypothesis": h["id"],
            "statement": h["statement"],
            "test": h["test"]["kind"],
            "params": h["test"].get("params", {}),
            "passed": res["passed"],
            "verdict": verdict_of(res),
            "summary": res["summary"],
            "stats": res["stats"],
            "rules_version": ctx["rules"].get("version"),
        })
        for u in res["unknowns"]:
            raised.append((h["id"], u))

        if not args.dry_run:
            h["status"] = status.replace(" ", "_")
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

    falsified = [r for r in rows if r["result"]["passed"] is False]
    untested = [r for r in rows if r["result"]["passed"] is None]
    supported = [r for r in rows if r["result"]["passed"] is True]
    openq = [u for u in register["unknowns"] if u["status"] == "open"]
    frame = [u for u in register["unknowns"] if u.get("level") == "frame"]
    print(f"\n{run_id}: {len(supported)} supported, {len(falsified)} falsified, "
          f"{len(untested)} no data, {len(openq)} open unknowns "
          f"({len(frame)} frame-level)")
    if not args.dry_run:
        print("Wrote falsification_report.md, UNKNOWNS.md, "
              "ledger/runs.jsonl, ledger/LEDGER.md, unknowns/register.json")

    # No data is not a failure and is not a pass. --strict reads False only.
    if args.strict and falsified:
        sys.exit(1)


if __name__ == "__main__":
    main()

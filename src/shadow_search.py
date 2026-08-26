#!/usr/bin/env python3
"""
Shadow Search Playground
========================
Interactive CLI for hunting hidden patterns among keystone technology candidates.

Combines the Keystone-Codex catalogue with shadow-hunting methodology:
  - Search & filter across all technology candidates
  - Detect cross-domain resonances (technologies sharing hidden connections)
  - Score shadow candidates against keystone criteria
  - Discover shadow lineages — unlock chains that cross domains
  - Phi-ratio spacing — retained as a NEGATIVE CONTROL, see below

A note on what this tool is for. Everything here generates candidate patterns;
nothing here confirms one. The phi detector is kept as the standing reminder:
its output looked like a finding until H007 put it against a null model, and
then it was noise. Run anything this playground surfaces through
`src/falsify.py` before believing it.

Usage:
    python3 src/shadow_search.py                  # interactive mode
    python3 src/shadow_search.py search <query>   # quick search
    python3 src/shadow_search.py scan             # full shadow scan
"""
import os
import re
import sys
import math
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ROOT = corpus.ROOT
PHI = (1 + math.sqrt(5)) / 2  # golden ratio ≈ 1.618

# ── Data Loading ─────────────────────────────────────────────────────────

def load_shadow_catalogue():
    """Load the unified shadow catalogue."""
    return corpus.load_catalogue()


def load_confirmed_items():
    """Load fully-encoded keystone entries from data/<domain>/."""
    return corpus.load_entries()


def load_rules():
    """Load keystone scoring rules."""
    return corpus.load_rules()


def h007_verdict():
    """
    The live verdict on the phi detector, read from the hypothesis file rather
    than hardcoded, so this tool cannot end up quoting a stale p-value at you.
    """
    import json
    path = os.path.join(ROOT, "hypotheses", "H007_phi_significance.json")
    try:
        with open(path, encoding="utf-8") as f:
            last = json.load(f).get("last_result") or {}
        return last.get("summary") or "not yet run — run src/falsify.py"
    except (OSError, ValueError):
        return "hypothesis file unavailable"


# ── Search Engine ────────────────────────────────────────────────────────

def text_search(entries, query):
    """
    Full-text search across names, descriptions, tags, domains, regions.

    Terms match at a word boundary, so 'eel' finds Budj Bim and not Damascus
    Steel. Matching is still prefix-open — 'navigat' finds 'navigation' — which
    is the behaviour you want when guessing at a tag.
    """
    terms = [t for t in query.lower().split() if t]
    patterns = [re.compile(r"\b" + re.escape(t)) for t in terms]
    results = []
    for entry in entries:
        searchable = " ".join([
            entry.get("name", ""),
            entry.get("description", ""),
            entry.get("domain", ""),
            entry.get("region", ""),
            " ".join(entry.get("tags", [])),
            entry.get("source_note", ""),
        ]).lower()
        score = sum(1 for p in patterns if p.search(searchable))
        if score > 0:
            results.append((score, entry))
    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results]


def filter_by_domain(entries, domain):
    """Filter entries by domain."""
    return [e for e in entries if e["domain"] == domain]


def filter_by_era(entries, start=None, end=None):
    """Filter entries overlapping a given era range."""
    results = []
    for e in entries:
        era = e.get("era", {})
        e_start = era.get("start", -99999)
        e_end = era.get("end", 99999)
        if start is not None and e_end < start:
            continue
        if end is not None and e_start > end:
            continue
        results.append(e)
    return results


def filter_by_status(entries, status):
    """Filter by confirmed/shadow status."""
    return [e for e in entries if e.get("status") == status]


# ── Shadow Pattern Detection ────────────────────────────────────────────

def detect_phi_clustering(entries):
    """
    Hunt for phi-ratio spacing in technology emergence timelines.

    NEGATIVE CONTROL. This detector once claimed its triads "may indicate
    underlying systemic coupling patterns". Hypothesis H007 tested that against
    a seeded uniform null model and the claim did not survive: the catalogue
    produces no more phi-spaced triads than the same number of dates thrown at
    random into the same window. The live verdict is in
    hypotheses/H007_phi_significance.json.

    The function is kept, and kept honest, because it demonstrates how much
    apparent structure a triad search manufactures from a few dozen dates —
    the failure mode every other detector in this file is also exposed to.
    """
    starts = sorted(
        [(e["era"]["start"], e) for e in entries if "era" in e],
        key=lambda x: x[0]
    )
    clusters = []
    for i in range(len(starts)):
        for j in range(i + 1, len(starts)):
            gap = abs(starts[j][0] - starts[i][0])
            if gap == 0:
                continue
            for k in range(j + 1, len(starts)):
                gap2 = abs(starts[k][0] - starts[j][0])
                if gap2 == 0:
                    continue
                ratio = max(gap, gap2) / min(gap, gap2)
                deviation = abs(ratio - PHI) / PHI
                if deviation < 0.10:  # within 10% of phi
                    clusters.append({
                        "triad": [
                            starts[i][1]["name"],
                            starts[j][1]["name"],
                            starts[k][1]["name"],
                        ],
                        "years": [starts[i][0], starts[j][0], starts[k][0]],
                        "gaps": [gap, gap2],
                        "ratio": round(ratio, 4),
                        "phi_deviation": f"{deviation * 100:.1f}%",
                    })
    # Deduplicate and return top results by closest phi match
    clusters.sort(key=lambda c: float(c["phi_deviation"].rstrip("%")))
    return clusters[:20]


def detect_cross_domain_resonance(entries):
    """
    Find technologies from different domains that share tags or emerge
    in overlapping eras and regions — hidden coupling across disciplines.
    """
    resonances = []
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            if a["domain"] == b["domain"]:
                continue
            # Tag overlap
            tags_a = set(a.get("tags", []))
            tags_b = set(b.get("tags", []))
            shared_tags = tags_a & tags_b
            if not shared_tags:
                continue
            # Era overlap
            era_a = a.get("era", {})
            era_b = b.get("era", {})
            overlap_start = max(era_a.get("start", -99999), era_b.get("start", -99999))
            overlap_end = min(era_a.get("end", 99999), era_b.get("end", 99999))
            era_overlap = max(0, overlap_end - overlap_start)
            strength = len(shared_tags) + (1 if era_overlap > 100 else 0)
            resonances.append({
                "pair": [a["name"], b["name"]],
                "domains": [a["domain"], b["domain"]],
                "shared_tags": sorted(shared_tags),
                "era_overlap_years": era_overlap,
                "strength": strength,
            })
    resonances.sort(key=lambda r: -r["strength"])
    return resonances[:25]


def detect_shadow_lineages(entries, confirmed_items):
    """
    Trace potential unlock chains from confirmed keystones through shadow
    candidates. A shadow lineage is a hypothetical chain of enabling
    relationships crossing domains.
    """
    # Build a map of tags to shadow entries
    tag_index = defaultdict(list)
    for e in entries:
        for tag in e.get("tags", []):
            tag_index[tag].append(e)

    lineages = []
    for item in confirmed_items:
        unlocks = item.get("unlocks", [])
        for unlock_id in unlocks:
            # Find shadow entries whose tags resonate with this unlock
            unlock_terms = unlock_id.replace("_", " ").split()
            candidates = []
            for term in unlock_terms:
                for shadow in tag_index.get(term, []):
                    if shadow["id"] != item["id"] and shadow not in candidates:
                        candidates.append(shadow)
            if candidates:
                lineages.append({
                    "source": item["name"],
                    "source_domain": item["domain"],
                    "unlock": unlock_id,
                    "shadow_connections": [
                        {"name": c["name"], "domain": c["domain"]}
                        for c in candidates[:5]
                    ],
                })
    return lineages


def detect_domain_gaps(entries):
    """
    Identify domains and eras with sparse coverage — shadow zones where
    keystone technologies likely exist but haven't been catalogued.
    """
    domains = ["ecological", "economic", "social", "governance",
               "information", "material", "ethical", "infrastructure"]
    era_bins = [
        ("Deep Antiquity", -50000, -3000),
        ("Bronze Age", -3000, -1200),
        ("Iron Age / Classical", -1200, 500),
        ("Medieval", 500, 1400),
        ("Early Modern", 1400, 1800),
        ("Modern", 1800, 2025),
    ]
    gaps = []
    for domain in domains:
        domain_entries = filter_by_domain(entries, domain)
        for era_name, era_start, era_end in era_bins:
            era_entries = filter_by_era(domain_entries, era_start, era_end)
            if len(era_entries) == 0:
                gaps.append({
                    "domain": domain,
                    "era": era_name,
                    "era_range": f"{era_start} to {era_end}",
                    "coverage": "EMPTY — shadow zone",
                })
            elif len(era_entries) == 1:
                gaps.append({
                    "domain": domain,
                    "era": era_name,
                    "era_range": f"{era_start} to {era_end}",
                    "coverage": f"SPARSE — only {era_entries[0]['name']}",
                })
    return gaps


# The criteria a shadow candidate can be guessed at from catalogue metadata
# alone. The rest of the rule set reads an `evidence` array, which by
# definition a shadow entry does not have.
ESTIMABLE_CRITERIA = {"longevity", "replication", "unlocks_lineage", "decentralization"}


def estimate_keystone_score(entry, rules):
    """
    Estimate a shadow candidate's keystone potential from era span and
    metadata. Speculative by construction — this is a triage score for
    deciding what to encode next, not a verdict.

    The score is normalised over the criteria it can actually estimate, then
    compared to pass_score. Without that normalisation the estimator silently
    broke when rules v1.1 landed: the four estimable criteria total 0.54 of the
    new weight, so nothing could reach a 0.70 bar and every candidate came back
    "needs more evidence" regardless of merit.
    """
    criteria = rules["criteria"]
    era = entry.get("era", {})
    longevity = era.get("end", 0) - era.get("start", 0)
    tags = entry.get("tags", [])

    trace = []
    # Longevity estimate
    thr = next(c for c in criteria if c["name"] == "longevity")
    passed = longevity >= thr["threshold"]
    trace.append({
        "rule": f"longevity>={thr['threshold']}",
        "passed": passed,
        "detail": f"era_span={longevity}yr",
        "weight": thr["weight"],
    })

    # Replication estimate (heuristic: multi-region in name/region field)
    thr = next(c for c in criteria if c["name"] == "replication")
    region = entry.get("region", "")
    # A comma is not a region separator — "Oromia, Ethiopia" is one place
    # written as place-in-country, and counting it as two made every such
    # entry look independently replicated.
    multi = any(sep in region for sep in ["/", " and ", "Global", "Eurasia"])
    passed_rep = multi
    trace.append({
        "rule": f"replication>={thr['threshold']}",
        "passed": passed_rep,
        "detail": f"region='{region}' multi={'yes' if multi else 'unknown'}",
        "weight": thr["weight"],
    })

    # Unlocks estimate (heuristic: number of tags as proxy for generativity)
    thr = next(c for c in criteria if c["name"] == "unlocks_lineage")
    passed_unlocks = len(tags) >= 3
    trace.append({
        "rule": f"unlocks>={thr['threshold']}",
        "passed": passed_unlocks,
        "detail": f"tags={len(tags)} (proxy for generativity)",
        "weight": thr["weight"],
    })

    # Decentralization estimate (heuristic from tags)
    thr = next(c for c in criteria if c["name"] == "decentralization")
    decentral_signals = {"distributed", "communal", "decentralized", "reciprocity",
                         "community", "consensus", "participatory", "commons"}
    has_signal = bool(set(tags) & decentral_signals)
    trace.append({
        "rule": f"decentralization>={thr['threshold']}",
        "passed": has_signal,
        "detail": f"decentral_tags={'yes' if has_signal else 'unknown'}",
        "weight": thr["weight"],
    })

    earned = sum(t["weight"] for t in trace if t["passed"])
    available = sum(c["weight"] for c in criteria if c["name"] in ESTIMABLE_CRITERIA)
    normalized = earned / available if available else 0.0
    return {
        "id": entry["id"],
        "name": entry["name"],
        "estimated_score": round(normalized, 3),
        "raw_score": round(earned, 3),
        "estimable_weight": round(available, 3),
        "likely_keystone": normalized >= rules["pass_score"],
        "confidence": "speculative",
        "trace": trace,
    }


# ── Display Helpers ──────────────────────────────────────────────────────

def fmt_year(y):
    """Format a year for display (negative = BCE)."""
    if y < 0:
        return f"{abs(y)} BCE"
    return str(y)


def print_entry(e, index=None):
    """Pretty-print a catalogue entry."""
    prefix = f"  [{index}] " if index is not None else "  "
    status_icon = "+" if e.get("status") == "confirmed" else "~"
    era = e.get("era", {})
    era_str = f"{fmt_year(era.get('start', 0))} - {fmt_year(era.get('end', 0))}"
    print(f"{prefix}{status_icon} {e['name']}")
    print(f"      Domain: {e['domain']}  |  Region: {e.get('region', '?')}  |  Era: {era_str}")
    print(f"      {e.get('description', '')}")
    if e.get("tags"):
        print(f"      Tags: {', '.join(e['tags'])}")
    print()


def print_divider(title=""):
    width = 70
    if title:
        pad = width - len(title) - 4
        print(f"\n{'=' * 2} {title} {'=' * max(pad, 2)}")
    else:
        print("=" * width)


def print_resonance(r, index=None):
    prefix = f"  [{index}] " if index is not None else "  "
    print(f"{prefix}{r['pair'][0]}  <-->  {r['pair'][1]}")
    print(f"      Domains: {r['domains'][0]} x {r['domains'][1]}  |  "
          f"Shared: {', '.join(r['shared_tags'])}  |  "
          f"Era overlap: {r['era_overlap_years']}yr  |  Strength: {r['strength']}")


# ── Commands ─────────────────────────────────────────────────────────────

def cmd_search(entries, query):
    """Search the catalogue."""
    results = text_search(entries, query)
    print_divider(f"Search: '{query}' ({len(results)} results)")
    if not results:
        print("  No matches found.")
        return
    for i, e in enumerate(results, 1):
        print_entry(e, i)


def cmd_domain(entries, domain):
    """List entries in a domain."""
    results = filter_by_domain(entries, domain)
    print_divider(f"Domain: {domain} ({len(results)} entries)")
    for i, e in enumerate(results, 1):
        print_entry(e, i)


def cmd_era(entries, start, end):
    """List entries in an era range."""
    results = filter_by_era(entries, start, end)
    results.sort(key=lambda e: e.get("era", {}).get("start", 0))
    print_divider(f"Era: {fmt_year(start)} to {fmt_year(end)} ({len(results)} entries)")
    for i, e in enumerate(results, 1):
        print_entry(e, i)


def cmd_resonance(entries):
    """Detect cross-domain resonances."""
    resonances = detect_cross_domain_resonance(entries)
    print_divider(f"Cross-Domain Resonances ({len(resonances)} detected)")
    print("  Technologies from different domains sharing hidden connections:\n")
    for i, r in enumerate(resonances, 1):
        print_resonance(r, i)
        print()


def cmd_phi(entries):
    """Detect phi-ratio temporal clustering."""
    clusters = detect_phi_clustering(entries)
    print_divider(f"Phi-Ratio Temporal Clusters ({len(clusters)} found)")
    print(f"  Golden ratio (phi) = {PHI:.6f}")
    print("  !! NEGATIVE CONTROL — these triads are not a finding.")
    print(f"     H007: {h007_verdict()}")
    print("     Run 'python3 src/falsify.py --only H007' to reproduce.")
    print("     Shown so you can see how convincing pure noise looks:\n")
    for i, c in enumerate(clusters, 1):
        print(f"  [{i}] {c['triad'][0]}  ->  {c['triad'][1]}  ->  {c['triad'][2]}")
        print(f"      Years: {c['years']}  |  Gaps: {c['gaps']}yr  |  "
              f"Ratio: {c['ratio']}  |  Phi deviation: {c['phi_deviation']}")
        print()


def cmd_lineages(entries, confirmed):
    """Trace shadow lineages from confirmed keystones."""
    lineages = detect_shadow_lineages(entries, confirmed)
    print_divider(f"Shadow Lineages ({len(lineages)} chains)")
    print("  Tracing unlock paths from confirmed keystones into shadow candidates:\n")
    for i, lin in enumerate(lineages, 1):
        print(f"  [{i}] {lin['source']} ({lin['source_domain']})")
        print(f"      Unlock: '{lin['unlock']}'")
        for conn in lin["shadow_connections"]:
            print(f"        -> {conn['name']} ({conn['domain']})")
        print()


def cmd_gaps(entries):
    """Identify shadow zones — underexplored domain/era combinations."""
    gaps = detect_domain_gaps(entries)
    print_divider(f"Shadow Zones ({len(gaps)} gaps)")
    print("  Domain/era combinations with missing or sparse coverage:\n")
    for g in gaps:
        print(f"  [{g['domain']:14s}] {g['era']:25s} {g['era_range']:20s} -> {g['coverage']}")


def cmd_score(entries, rules, query):
    """Estimate keystone potential for a shadow candidate."""
    results = text_search(entries, query)
    shadows = [e for e in results if e.get("status") == "shadow"]
    if not shadows:
        print(f"  No shadow candidates matching '{query}'.")
        return
    entry = shadows[0]
    result = estimate_keystone_score(entry, rules)
    verdict = "LIKELY KEYSTONE" if result["likely_keystone"] else "NEEDS MORE EVIDENCE"
    print_divider(f"Shadow Score: {result['name']}")
    print(f"  Estimated Score: {result['estimated_score']}  |  Verdict: {verdict}")
    print(f"  Confidence: {result['confidence']} — normalised over "
          f"{result['estimable_weight']} of the rule set's weight; the "
          f"evidence criteria cannot be estimated without an encoded entry.\n")
    for t in result["trace"]:
        mark = "+" if t["passed"] else "?"
        print(f"    {mark} {t['rule']:30s} {t['detail']:40s} (w={t['weight']})")
    print()


def cmd_scan(entries, confirmed, rules):
    """Full shadow scan — run all detectors and produce a combined report."""
    print_divider("SHADOW SEARCH — FULL SCAN")
    total = len(entries)
    confirmed_count = len([e for e in entries if e.get("status") == "confirmed"])
    shadow_count = total - confirmed_count
    print(f"\n  Catalogue: {total} technologies ({confirmed_count} confirmed, {shadow_count} shadow)")
    domains = set(e["domain"] for e in entries)
    print(f"  Domains: {', '.join(sorted(domains))}")
    print()

    # Shadow scores for all shadow candidates
    shadows = filter_by_status(entries, "shadow")
    scores = [estimate_keystone_score(e, rules) for e in shadows]
    likely = [s for s in scores if s["likely_keystone"]]
    likely.sort(key=lambda s: -s["estimated_score"])

    print_divider(f"High-Potential Shadow Candidates ({len(likely)}/{len(shadows)})")
    print("  Triage only: scored on era and tags, normalised over the criteria")
    print("  estimable without an encoded entry. Encode before believing.\n")
    for i, s in enumerate(likely, 1):
        print(f"  [{i:2d}] {s['name']:45s} score={s['estimated_score']:.3f}")

    # Top resonances
    resonances = detect_cross_domain_resonance(entries)
    print_divider(f"Strongest Cross-Domain Resonances (top 10 of {len(resonances)})")
    for i, r in enumerate(resonances[:10], 1):
        print(f"  [{i:2d}] {r['pair'][0]:30s} <-> {r['pair'][1]:30s}  "
              f"({r['domains'][0]} x {r['domains'][1]})  "
              f"shared: {', '.join(r['shared_tags'])}")

    # Phi clusters
    clusters = detect_phi_clustering(entries)
    print_divider(f"Phi-Ratio Clusters (top 5 of {len(clusters)}) — NEGATIVE CONTROL")
    print(f"  Not a finding. H007: {h007_verdict()}")
    for i, c in enumerate(clusters[:5], 1):
        print(f"  [{i}] {c['triad'][0]:25s} -> {c['triad'][1]:25s} -> {c['triad'][2]:25s}")
        print(f"      ratio={c['ratio']}  deviation={c['phi_deviation']}")

    # Shadow lineages
    lineages = detect_shadow_lineages(entries, confirmed)
    print_divider(f"Shadow Lineages ({len(lineages)} chains from {len(confirmed)} confirmed keystones)")
    for i, lin in enumerate(lineages, 1):
        targets = ", ".join(c["name"] for c in lin["shadow_connections"])
        print(f"  [{i:2d}] {lin['source']:35s} --[{lin['unlock']}]--> {targets}")

    # Gaps
    gaps = detect_domain_gaps(entries)
    empty_gaps = [g for g in gaps if "EMPTY" in g["coverage"]]
    print_divider(f"Shadow Zones ({len(empty_gaps)} empty domain/era slots)")
    for g in empty_gaps:
        print(f"  [{g['domain']:14s}] {g['era']:25s} -> {g['coverage']}")

    print()
    print_divider("SCAN COMPLETE")
    print()


# ── Interactive Mode ─────────────────────────────────────────────────────

HELP_TEXT = """
Shadow Search Playground — Commands:

  search <query>       Full-text search across all technologies
  domain <name>        Filter by domain (ecological, economic, governance, etc.)
  era <start> <end>    Filter by era range (use negative for BCE)
  shadows              List all shadow (unconfirmed) candidates
  confirmed            List all confirmed keystones
  score <query>        Estimate keystone potential for a shadow candidate
  resonance            Detect cross-domain hidden connections
  phi                  Hunt for phi-ratio temporal clustering
  lineages             Trace shadow lineages from confirmed keystones
  gaps                 Find shadow zones (empty domain/era slots)
  scan                 Full shadow scan — all detectors combined
  list                 List all entries
  help                 Show this help
  quit                 Exit playground
"""


def interactive_mode():
    """Run the interactive playground REPL."""
    entries = load_shadow_catalogue()
    confirmed = load_confirmed_items()
    rules = load_rules()

    print_divider("SHADOW SEARCH PLAYGROUND")
    print("  Hunt hidden patterns among keystone technology candidates.")
    print(f"  Catalogue: {len(entries)} technologies | Type 'help' for commands.")
    print()

    while True:
        try:
            raw = input("shadow> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting playground.")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print("  Exiting playground.")
            break
        elif cmd == "help":
            print(HELP_TEXT)
        elif cmd == "search":
            if not arg:
                print("  Usage: search <query>")
            else:
                cmd_search(entries, arg)
        elif cmd == "domain":
            if not arg:
                domains = sorted(set(e["domain"] for e in entries))
                print(f"  Available domains: {', '.join(domains)}")
            else:
                cmd_domain(entries, arg)
        elif cmd == "era":
            era_parts = arg.split()
            if len(era_parts) != 2:
                print("  Usage: era <start> <end>  (e.g., era -3000 500)")
            else:
                try:
                    cmd_era(entries, int(era_parts[0]), int(era_parts[1]))
                except ValueError:
                    print("  Era values must be integers.")
        elif cmd == "shadows":
            results = filter_by_status(entries, "shadow")
            print_divider(f"Shadow Candidates ({len(results)})")
            for i, e in enumerate(results, 1):
                print_entry(e, i)
        elif cmd == "confirmed":
            results = filter_by_status(entries, "confirmed")
            print_divider(f"Confirmed Keystones ({len(results)})")
            for i, e in enumerate(results, 1):
                print_entry(e, i)
        elif cmd == "score":
            if not arg:
                print("  Usage: score <technology name or keyword>")
            else:
                cmd_score(entries, rules, arg)
        elif cmd == "resonance":
            cmd_resonance(entries)
        elif cmd == "phi":
            cmd_phi(entries)
        elif cmd == "lineages":
            cmd_lineages(entries, confirmed)
        elif cmd == "gaps":
            cmd_gaps(entries)
        elif cmd == "scan":
            cmd_scan(entries, confirmed, rules)
        elif cmd == "list":
            print_divider(f"All Technologies ({len(entries)})")
            for i, e in enumerate(entries, 1):
                print_entry(e, i)
        else:
            # Treat unknown input as a search
            cmd_search(entries, raw)


# ── CLI Entry Point ──────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        interactive_mode()
        return

    cmd = args[0].lower()
    entries = load_shadow_catalogue()
    confirmed = load_confirmed_items()
    rules = load_rules()

    if cmd == "search" and len(args) > 1:
        cmd_search(entries, " ".join(args[1:]))
    elif cmd == "scan":
        cmd_scan(entries, confirmed, rules)
    elif cmd == "resonance":
        cmd_resonance(entries)
    elif cmd == "phi":
        cmd_phi(entries)
    elif cmd == "lineages":
        cmd_lineages(entries, confirmed)
    elif cmd == "gaps":
        cmd_gaps(entries)
    elif cmd == "score" and len(args) > 1:
        cmd_score(entries, rules, " ".join(args[1:]))
    elif cmd == "domain" and len(args) > 1:
        cmd_domain(entries, args[1])
    elif cmd == "help":
        print(HELP_TEXT)
    else:
        print(f"Unknown command: {cmd}")
        print("  Run with no args for interactive mode, or use: search, scan, resonance, phi, lineages, gaps, score, domain, help")


if __name__ == "__main__":
    main()

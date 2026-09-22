#!/usr/bin/env python3
"""
Integration report over declared systems.

A system is a set of entry ids plus declared joints (schema/system.schema.json).
This module reads one and reports three things, which is what the architecture
layer was asked for:

    1. is each member's runs_on satisfied by other members of the system?
       (a fraction, and the list of unmet targets)
    2. what joints are declared between entries? (a list)
    3. which layer roles have no member? (a list)

What it deliberately does NOT do
--------------------------------
No combined score. No ranking of entries. No ordering of systems by how well
they integrate. A per-entry number would make the parts comparable to each
other, and comparing the parts is the supremacy frame that SYSTEMS_ANALOGY.md
was written against; the measurand here is the ASSEMBLY, not the merit of the
pieces in it. The per-entry rubric in src/prove.py is a different instrument
aimed at a different measurand and this one does not replace it, duplicate it,
or feed it.

Refusals worth knowing about
----------------------------
* `fraction` is None when nothing was declared, never 0.0. Zero-of-zero and
  zero-of-eleven are different results and a float cannot hold both.
* A member naming an entry that does not exist is reported, not dropped.
* If an entry declares layer_role and the system declares a different one for
  the same member, the conflict is reported and neither wins. Picking one
  would settle by fiat the question of whether role belongs to the thing or to
  the assembly.
* `runs_on` targets are checked for resolving to a PRESENT member, not for
  being LOWER than the member that names them. No document in this repository
  declares a total order over the layer roles; SYSTEMS_ANALOGY.md places PSU
  at the bottom and leaves the rest unordered. Until an order is declared,
  "resolves to a present member" is the whole of what is checked, and the
  report says so.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

UNCHECKED_NOTE = (
    "runs_on targets are checked for resolving to a present member of this "
    "system. They are NOT checked for being lower in the stack: no document in "
    "this repository declares a total order over layer roles."
)


def _member_role(member, entry):
    """
    Resolve a member's role and say where it came from.

    Returns (role, source, conflict) where source is one of 'entry',
    'system', 'both-agree', 'conflict', 'undeclared'.
    """
    sys_role = member.get("layer_role")
    entry_role = (entry or {}).get("layer_role")
    if sys_role and entry_role:
        if sys_role == entry_role:
            return sys_role, "both-agree", None
        return None, "conflict", (
            f"entry declares layer_role={entry_role}, system declares "
            f"{sys_role} — neither is applied"
        )
    if entry_role:
        return entry_role, "entry", None
    if sys_role:
        return sys_role, "system", None
    return None, "undeclared", None


def _member_runs_on(member, entry):
    """runs_on declared on the entry wins nothing; both are reported."""
    sys_r = member.get("runs_on")
    entry_r = (entry or {}).get("runs_on")
    if sys_r is not None and entry_r is not None:
        if sorted(sys_r) == sorted(entry_r):
            return sys_r, "both-agree", None
        return None, "conflict", (
            f"entry declares runs_on={entry_r}, system declares {sys_r} — "
            f"neither is applied"
        )
    if entry_r is not None:
        return entry_r, "entry", None
    if sys_r is not None:
        return sys_r, "system", None
    return None, "undeclared", None


def integration_report(system, entries_by_id=None, roles=None):
    """Report one system. Pure: reads nothing, writes nothing."""
    if entries_by_id is None:
        entries_by_id = {e["id"]: e for e in corpus.load_entries()}
    if roles is None:
        roles = corpus.layer_roles()

    members = []
    missing_entries = []
    role_of = {}
    for m in system.get("members", []):
        eid = m["entry"]
        entry = entries_by_id.get(eid)
        if entry is None:
            missing_entries.append(eid)
        role, role_source, role_conflict = _member_role(m, entry)
        runs_on, runs_on_source, runs_on_conflict = _member_runs_on(m, entry)
        if role:
            role_of[eid] = role
        members.append({
            "entry": eid,
            "present_in_corpus": entry is not None,
            "domain": (entry or {}).get("domain"),
            "layer_role": role,
            "role_source": role_source,
            "role_conflict": role_conflict,
            "runs_on": runs_on,
            "runs_on_source": runs_on_source,
            "runs_on_conflict": runs_on_conflict,
        })

    member_ids = {m["entry"] for m in members}
    roles_present = {r: sorted(e for e, rr in role_of.items() if rr == r) for r in roles}
    missing_layers = [r for r in roles if not roles_present[r]]
    undeclared_role = [m["entry"] for m in members if m["layer_role"] is None]

    # runs_on satisfaction
    declared = [m for m in members if m["runs_on"] is not None]
    undeclared_runs_on = [m["entry"] for m in members if m["runs_on"] is None]
    targets = 0
    unmet = []
    for m in declared:
        for target in m["runs_on"]:
            targets += 1
            if target in roles:
                holders = [e for e in roles_present[target] if e != m["entry"]]
                if not holders:
                    unmet.append({
                        "entry": m["entry"], "target": target,
                        "why": f"no other member of this system carries the role "
                               f"'{target}'",
                    })
            elif target in member_ids:
                continue
            elif target in entries_by_id:
                unmet.append({
                    "entry": m["entry"], "target": target,
                    "why": f"'{target}' is an encoded entry but is not a member "
                           f"of this system",
                })
            else:
                unmet.append({
                    "entry": m["entry"], "target": target,
                    "why": f"'{target}' is neither a layer role nor an encoded entry",
                })
    satisfied = targets - len(unmet)
    # None, not 0.0 — nothing declared is not the same result as nothing met.
    fraction = None if targets == 0 else round(satisfied / targets, 4)

    # role/domain crosstab. A pure count: no map from domain to role is
    # asserted anywhere here. If domain and role were the same statement the
    # crosstab would be one-to-one, and it is reported whether it is.
    by_role, by_domain = {}, {}
    for m in members:
        if not m["layer_role"] or not m["domain"]:
            continue
        by_role.setdefault(m["layer_role"], set()).add(m["domain"])
        by_domain.setdefault(m["domain"], set()).add(m["layer_role"])
    one_to_one = (all(len(v) == 1 for v in by_role.values())
                  and all(len(v) == 1 for v in by_domain.values())
                  and bool(by_role))

    joints = system.get("joints", [])
    return {
        "system": system["id"],
        "name": system.get("name"),
        "status": system.get("status"),
        "membership_rule": system.get("membership_rule"),
        "member_count": len(members),
        "members": members,
        "missing_entries": missing_entries,
        "roles_present": roles_present,
        "missing_layers": missing_layers,
        "undeclared_role": undeclared_role,
        "runs_on": {
            "targets": targets,
            "satisfied": satisfied,
            "unmet": unmet,
            "fraction": fraction,
            "members_declaring": len(declared),
            "members_undeclared": undeclared_runs_on,
            "unchecked": UNCHECKED_NOTE,
        },
        "joints": {"count": len(joints), "declared": joints},
        "role_domain": {
            "domains_per_role": {r: sorted(v) for r, v in sorted(by_role.items())},
            "roles_per_domain": {d: sorted(v) for d, v in sorted(by_domain.items())},
            "one_to_one": one_to_one,
        },
        "conflicts": [m for m in members
                      if m["role_conflict"] or m["runs_on_conflict"]],
    }


def all_reports():
    entries_by_id = {e["id"]: e for e in corpus.load_entries()}
    roles = corpus.layer_roles()
    # Declared order. Never sorted by how well a system integrates.
    return [integration_report(s, entries_by_id, roles) for s in corpus.load_systems()]


def render(reports):
    out = ["# Integration Report", ""]
    out += ["Coverage and gaps over declared systems. No combined score and no "
            "ranking: the measurand is the assembly, not the merit of its parts.",
            ""]
    if not reports:
        out += ["_No systems declared under `systems/`._", ""]
        return "\n".join(out)
    for r in reports:
        out += [f"## {r['system']} — {r['name']}", "",
                f"_status: {r['status']} · {r['member_count']} members_", "",
                f"**Membership rule.** {r['membership_rule']}", ""]
        f = r["runs_on"]["fraction"]
        frac = "no runs_on declared" if f is None else f"{f:.0%}"
        out += [f"**runs_on satisfied:** {r['runs_on']['satisfied']}/"
                f"{r['runs_on']['targets']} ({frac})", ""]
        if r["runs_on"]["unmet"]:
            out += ["Unmet:", ""]
            out += [f"- `{u['entry']}` -> `{u['target']}`: {u['why']}"
                    for u in r["runs_on"]["unmet"]] + [""]
        out += [f"_{r['runs_on']['unchecked']}_", ""]
        out += [f"**Joints declared between entries:** {r['joints']['count']}", ""]
        if r["joints"]["count"]:
            out += [f"- `{j['from']}` -> `{j['to']}` ({j['kind']})"
                    for j in r["joints"]["declared"]] + [""]
        else:
            out += ["_None. Members without declared connections are a set, not "
                    "an assembly._", ""]
        out += ["**Missing layers:** "
                + (", ".join(f"`{m}`" for m in r["missing_layers"]) or "none"), ""]
        if r["missing_entries"]:
            out += ["**Members naming entries that do not exist:** "
                    + ", ".join(f"`{m}`" for m in r["missing_entries"]), ""]
        if r["undeclared_role"]:
            out += ["**Members with no declared role:** "
                    + ", ".join(f"`{m}`" for m in r["undeclared_role"]), ""]
        rd = r["role_domain"]
        out += ["**Role against domain.** "
                + ("one role per domain and one domain per role in this system"
                   if rd["one_to_one"] else
                   "not one-to-one — role and domain are carrying different "
                   "statements here"), ""]
        for role, domains in rd["domains_per_role"].items():
            out += [f"- `{role}` <- domains: " + ", ".join(f"`{d}`" for d in domains)]
        out += [""]
        if r["conflicts"]:
            out += ["**Conflicts (reported, not resolved):**", ""]
            for c in r["conflicts"]:
                for k in ("role_conflict", "runs_on_conflict"):
                    if c[k]:
                        out += [f"- `{c['entry']}`: {c[k]}"]
            out += [""]
    return "\n".join(out)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    reports = all_reports()
    if as_json:
        print(json.dumps(reports, indent=2))
    else:
        print(render(reports))
    return reports


if __name__ == "__main__":
    main()

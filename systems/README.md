# systems/

A **system** is a set of entry ids plus declared joints. It is the unit at which
integration is measured.

The per-entry rubric in `src/prove.py` asks whether one technology clears
thresholds. That is a real question and this layer does not replace it, feed it,
or read its output. The question here is a different one:
`SYSTEMS_ANALOGY.md`'s question, which is whether a set of parts is an assembly.

```
entry        one technology, scored against thresholds        src/prove.py
system       a set of entries plus joints, reported on        src/systems.py
```

## What the report emits

Per system: how many `runs_on` targets resolve to a present member, which ones
do not, which joints are declared between entries, which layer roles have no
member, and a crosstab of role against domain.

```bash
python3 -m src systems           # markdown
python3 -m src systems --json    # the same report as data
```

## What it does not emit

No combined score. No ranking of the entries in a system. No ordering of systems
by how well they integrate. A per-entry number here would make the parts
comparable to each other, and ranking the parts is the frame
`SYSTEMS_ANALOGY.md` was written against: *in machines, integration > supremacy.*
`tests/test_systems.py` asserts the absence rather than trusting it.

## Refusals built into the report

- `fraction` is `None` when nothing was declared, never `0.0`. Zero-of-zero and
  zero-of-eleven are different results.
- A member naming an entry that does not exist is reported, not dropped.
- When an entry declares a `layer_role` and the system declares a different one,
  the conflict is reported and **neither wins**. Which of the two owns the
  assignment is open at `U-ARCH-1`, and the repository already contains two
  artifacts that disagree about it: `.fieldlink.json`'s `layer_map` derives
  layers from **domain**, while `SYSTEMS_ANALOGY.md` assigns them as **roles**,
  and the two differ on `gift_economy` and `ubuntu_philosophy`. Neither file is
  changed here.
- `runs_on` targets are checked for resolving to a **present** member, not for
  being **lower** in the stack. No document in this repository declares a total
  order over layer roles — `SYSTEMS_ANALOGY.md` puts PSU at the bottom and
  leaves the rest unordered. Inventing an order to make the check stricter would
  settle by fiat a question nobody has answered, so the gap prints on every run.

## Declaring a system

Validated against `schema/system.schema.json`. `membership_rule` is required: a
set whose rule is unstated cannot be reproduced by someone else, and is a
preference rather than a claim. `status` is `illustrative`, `proposed` or
`attested`; the seeded system is `illustrative` and is not a claim that its
eleven technologies ever ran together.

Every declared `layer_role` and `runs_on` on a member carries a required basis
naming where it came from. A role with no basis is a guess with a field around
it.

# legacy/

Superseded, not discarded. **Precedence still carries.**

Nothing in this directory is dead. Each file was the working version of something
at the time it was used, and a verdict reached under it is still a verdict that was
reached — the thing to do with a rule that has been replaced is keep it runnable,
not delete it and hope nobody asks how the old numbers were produced.

The test of whether an archive is honest is whether you can still run it. All of
these can be.

## What's here

### `rules/keystone_rules.v1.json`

The original scoring rubric. Retired after `run-001-baseline` falsified **H006**:
under v1.0 every encoded entry passed and four of five scored a perfect 1.0. The
reason is structural. v1.0's four criteria — longevity, replication, unlocks,
decentralization — all read numbers the entry's author typed in, and none read the
evidence behind them. An entry could reach 1.0 on four hand-entered figures.

v1.1 keeps those four at reduced weight and adds three that read the `evidence`
array. It is not a stricter version of the same test; it measures something v1.0
did not measure at all.

Still runnable, which is the point:

```bash
python3 src/prove.py --rules legacy/rules/keystone_rules.v1.json --out-suffix .v1
```

That regenerates `proof_report.v1.md` against whatever the corpus currently holds.
`reports/proof_report.v1.md` here is a snapshot of that command, kept so the
difference between the two rubrics is legible without running anything.

### `references.md`

The original Keystone Reference Atlas — a hand-maintained prose index of roughly
sixty technologies across seven headings. Superseded in *form* by
`data/shadow_catalogue.json`, which carries the same entries as machine-readable
rows with ids, eras, tags, and status.

Superseded in form only. This file is the provenance record for most of the
catalogue: it is where those candidates were first identified, and its framing
notes — "no culture had it all", "supremacy narratives fail" — are the reasoning
the catalogue inherited without restating. It also still holds things the
catalogue does not, including the domain groupings that revealed why the schema's
`social` slot sat empty for a year (see U-H005-4 in `UNKNOWNS.md`: every prose
document here, this one included, ran *social* and *governance* together under one
heading).

Read it as the argument. Read the catalogue as the data.

### `reports/`

Proof reports generated under retired rule sets. Snapshots, not sources — the
authoritative record of what was found when is `ledger/runs.jsonl`, which is
append-only and never rewritten.

## Policy

1. **Retire, don't delete.** Anything superseded moves here with a note saying what
   replaced it and which run forced the change.
2. **Keep it runnable.** A retired rule set must still load. `src/prove.py --rules`
   exists for this reason.
3. **The ledger outranks the snapshot.** If a file here disagrees with
   `ledger/runs.jsonl`, the ledger is right — it was written at the time and is
   never edited.
4. **Nothing here is authority.** These files record what was believed and how it
   was scored. If you want to know what the codex currently claims, read the
   current rules and the latest run.

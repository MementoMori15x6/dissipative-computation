# Verification Plan

62 Python files, but not 62 verification jobs. Running a script proves it
*executes*; it does not prove it produces *the number printed in the paper*.
The second is what a reader cares about, and it is far cheaper to establish.

Work in tiers. Stop when the cost stops being worth the assurance.

---

## Tier A — automated, seconds, run it every time

    python3 verify_claims.py

Checks that all 14 banked record files load, that manuscript numbers match
their records, and that figure numbering, image paths, cross-references and
doubled words are intact.

**Why this tier matters most.** The likeliest real defect in this repo is not
a broken script. It is a number that was correct when written and then drifted
out of sync after a re-run. Executing a script cannot detect that; this can.
Re-run it after any edit to the manuscript or any re-run of an experiment.

---

## Tier B — spot reproduction

    python3 spot_check.py --quick     # ~2 minutes, 3 checks
    python3 spot_check.py             # ~12 minutes, 6 checks

Re-runs one cheap point from each banked record and compares against the banked
value. You are not re-running sweeps, only proving the pipeline still produces
what is recorded.

This works because every runner is deterministic: `np.random.default_rng(seed)`
for the initial state, `default_rng(seed + 50000 + block)` for MI sampling, and
seed sets are always `range(n_seeds)`. Same seed, same number, bit for bit.
`seed_count_recovery_results.py` already demonstrates the technique — it
recovered an unrecorded seed count purely by matching regenerated statistics
against banked ones.

| Check | Reproduces | Cost |
|---|---|---|
| demand, GoL per-cell at `D = 0.05` | `demand_convergence_results.py` | ~3 s |
| out-of-sample, Seeds at ceiling | `out_of_sample_rule_test_results.py` | ~4 s |
| out-of-sample, Life without Death | `out_of_sample_rule_test_results.py` | ~3 s |
| seed-count recovery, n = 10 | `seed_count_recovery_results.py` | ~3 min |
| flagship cost, `K = 5`, `α = 1` | `convergence_audit_results_flagship_cost.py` | ~2 min |
| same-niche, BB gated seeds 0–3 | `same_niche_extended_results.py` | ~4 min |

A mismatch here is serious: stop and investigate. A match means the banked
records regenerate from committed code, which is exactly the claim the Data and
Code Availability section makes.

**A note on why this is a committed script rather than pasted snippets.**
Earlier verification in this project was done with ad-hoc commands written for a
bash heredoc. Those carried shell escaping and quoting that broke when pasted
into a notebook. `spot_check.py` and `verify_claims.py` both use deliberately
conservative syntax — no f-strings, no nested quotes, nothing newer than Python
3.6 — and locate the repo root automatically. Run them; do not copy out of them.

---

## Tier C — read, don't run

**Record findings in `AUDIT_LOG.md` as you go**, one entry per file, positive findings as well as defects. Manuscript changes implied by a finding go into that file's open-findings section rather than being applied immediately — editing the methods section twice from partial information is worse than editing it once from a complete picture.

Eight files implement the measurement protocol rather than an experiment. A bug
here corrupts everything downstream *silently* and would not show up as a crash
or an odd-looking plot. These are worth reading line by line; the experiment
stages are not.

- `03-diffusion-limited-scarcity/stage_convergence_runner.py`
- `stage_convergence_runner_cost.py`
- `stage_convergence_runner_general.py`
- `stage_convergence_runner_gol_dn.py`
- `stage_adaptive_complexity_runner.py`
- `stage_adaptive_complexity_runner_gol_dn.py`
- `04-contestable-occupancy/stage_convergence_runner_displacement_cost.py`
- `04-contestable-occupancy/stage_convergence_runner_flagship_cost.py`

What to look for specifically:

1. **Settling criterion** — does "converged" mean what §2.3 says it means?
   Frozen configuration, extinction, or trailing average stable within
   tolerance over a full block.
2. **Drift classification** — trials hitting the cap must be classified by
   drift direction, not silently averaged in or dropped.
3. **Argument order in gated-step calls.** This is not hypothetical. The
   flagship module takes `(..., bb_cost_multiplier, flip_cost, ceiling, ...)`
   while the shared runner passes the dynamic ceiling *eighth positionally* —
   which lands on `flip_cost` and silently rescales every cost in the run.
   `stage_convergence_runner_flagship_cost.py` passes `ceiling` by keyword to
   avoid this. Check every other call site for the same trap.
4. **Warmup and check-interval scaling with `α`.** High-cost conditions need
   roughly `α / D_bg` steps of pure accumulation before the first affordable
   transition. Held fixed, those conditions never begin.

---

## Tier D — full re-run, hours, optional

Only the flagship sweeps, and only if you want to say you personally
regenerated every figure. Budget: the `α = 200` displacement cells run
50–95 s/seed, the adaptive complexity sweeps up to 40,000 steps per seed.

Run overnight, in chunks with per-seed checkpointing to disk. Background
processes are not reliable here; foreground chunks that write after each seed
are.

---

## What you can safely skip

Roughly 20 stage files are superseded by later convergence re-runs. They remain
in the repo for provenance — a reader can see what the original pass did — but
no reported number depends on them. Verifying them proves nothing about the
paper.

The 14 `*_results.py` files contain no computation. Tier A already confirms they
load and agree with the manuscript; there is nothing further to test.

---

## Recommended order

1. Tier A now, and after every subsequent change.
2. Tier C reading — the highest ratio of assurance to effort in the whole repo.
3. Tier B spot reproduction, one evening.
4. Tier D only if you want the strongest possible form of the claim.

Tiers A through C are enough to say honestly: *the banked records regenerate
from this code, and I have read the protocol that produced them.*

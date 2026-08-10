#!/usr/bin/env python3
"""
TIER B VERIFICATION -- spot reproduction.

Re-runs one cheap point from each banked record and compares the regenerated
value against the banked one. This is the check that establishes the Data and
Code Availability claim: that the records regenerate from committed code.

Every runner in this repo is deterministic -- np.random.default_rng(seed) for
the initial state, default_rng(seed + 50000 + block) for mutual-information
sampling, and seed sets are always range(n_seeds). Same seed, same number, bit
for bit.

DELIBERATELY CONSERVATIVE SYNTAX
--------------------------------
No f-strings, no nested quotes, nothing newer than Python 3.6. Earlier
verification in this project was done with ad-hoc snippets written for a bash
heredoc; those carried shell escaping and quoting that broke when pasted into a
notebook. This file is meant to be run, not copied.

USAGE
    script   : python3 spot_check.py [--quick]
    notebook : %run spot_check.py
               %run spot_check.py --quick

    --quick   runs only the checks under ~60 seconds each.

Repo root is auto-located; override with os.environ["DC_REPO"] if needed.
Approximate total runtime: --quick about 2 minutes, full about 12 minutes.
"""

import argparse
import importlib.util
import os
import pathlib
import sys
import time

MANUSCRIPT = "DC_Manuscript_Draft_v2.md"
TOL = 5e-4


def find_root():
    env = os.environ.get("DC_REPO")
    if env and (pathlib.Path(env) / MANUSCRIPT).exists():
        return pathlib.Path(env)
    try:
        here = pathlib.Path(__file__).resolve().parent
        if (here / MANUSCRIPT).exists():
            return here
    except NameError:
        pass
    cwd = pathlib.Path.cwd().resolve()
    for cand in [cwd] + list(cwd.parents):
        if (cand / MANUSCRIPT).exists():
            return cand
    hits = sorted(cwd.glob("*/" + MANUSCRIPT)) + sorted(cwd.glob("*/*/" + MANUSCRIPT))
    if hits:
        return hits[0].parent
    raise FileNotFoundError(
        "Could not find " + MANUSCRIPT + ". Set DC_REPO, e.g.\n"
        "    import os; os.environ['DC_REPO'] = '/content/dissipative-computation'")


ROOT = find_root()


def load(rel):
    """Import a module from a path, with its own directory on sys.path.

    The stage scripts use bare relative imports and expect to be run from
    inside their section directory, so that directory has to be importable.
    """
    path = ROOT / rel
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def close(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


# ----------------------------------------------------------------------------
# individual checks: each returns (label, ok, detail)
# ----------------------------------------------------------------------------

def check_demand_gol(quick):
    """Game of Life per-cell demand at D = 0.05, window 2000. ~30 s."""
    rec = load("02-landauer-gated-execution/demand_convergence_results.py")
    mod = load("02-landauer-gated-execution/stage5_demand_convergence_check.py")
    banked = rec.FLUX_PER_ACTIVE_CELL[("GoL", 0.05)]["ratio"]
    m = mod.measure("GoL", 0.05, 2000)
    got = m["phi"] / m["active_frac"]
    return ("demand: GoL per-cell at D=0.05",
            close(got, banked, 2e-3),
            "banked {0:.3f}  regenerated {1:.3f}".format(banked, got))


def check_out_of_sample_seeds(quick):
    """Seeds at the unthrottled ceiling. ~30 s."""
    rec = load("02-landauer-gated-execution/out_of_sample_rule_test_results.py")
    mod = load("02-landauer-gated-execution/stage5_demand_convergence_check.py")
    banked = rec.UNTHROTTLED_CEILING["Seeds"]["per_cell_demand"]
    m = mod.measure("Seeds", 1.0, 2000)
    got = m["phi"] / m["active_frac"]
    return ("out-of-sample: Seeds at ceiling",
            close(got, banked, 2e-3),
            "banked {0:.3f}  regenerated {1:.3f}".format(banked, got))


def check_out_of_sample_lwd(quick):
    """Life without Death at the unthrottled ceiling. ~30 s."""
    rec = load("02-landauer-gated-execution/out_of_sample_rule_test_results.py")
    mod = load("02-landauer-gated-execution/stage5_demand_convergence_check.py")
    banked = rec.UNTHROTTLED_CEILING["LifeWithoutDeath"]["per_cell_demand"]
    m = mod.measure("LifeWithoutDeath", 1.0, 2000)
    got = (m["phi"] / m["active_frac"]) if m["active_frac"] > 1e-6 else 0.0
    return ("out-of-sample: Life without Death at ceiling",
            close(got, banked, 2e-3),
            "banked {0:.3f}  regenerated {1:.3f}".format(banked, got))


def check_seed_count_recovery(quick):
    """The n=10 identification for the debiased GoL complexity sweep. ~3 min."""
    if quick:
        return None
    rec = load("03-diffusion-limited-scarcity/seed_count_recovery_results.py")
    mod = load("03-diffusion-limited-scarcity/stage_adaptive_complexity_runner_gol_dn.py")
    import numpy as np
    banked = rec.POINT_1_GOL["banked"]
    cs = []
    for s in range(10):
        r = mod.run_adaptive(D_bg=0.01, D_diff=0.01, rule_name="GoL", seed=s)
        cs.append(r["C"])
    arr = np.array(cs)
    ok = (close(round(arr.mean(), 4), banked["mean_C"])
          and close(round(arr.std(), 4), banked["sd_C"]))
    return ("seed recovery: GoL D_diff=0.01 at n=10",
            ok,
            "banked mean {0:.4f} sd {1:.4f}  regenerated mean {2:.4f} sd {3:.4f}".format(
                banked["mean_C"], banked["sd_C"], arr.mean(), arr.std()))


def check_flagship_cost(quick):
    """One cell of the flagship displacement-cost grid. ~2 min."""
    if quick:
        return None
    rec = load("04-contestable-occupancy/convergence_audit_results_flagship_cost.py")
    mod = load("04-contestable-occupancy/stage_convergence_runner_flagship_cost.py")
    banked = rec.GRID[(5, 1)]["mean"]
    got = mod.run_cell(5, 1, 10)["mean_gol_share"]
    return ("flagship cost: K=5, alpha=1, 10 seeds",
            close(got, banked, 2e-3),
            "banked {0:.4f}  regenerated {1:.4f}".format(banked, got))


def check_same_niche(quick):
    """Brian's Brain gated fixation steps, seeds 0-3. ~4 min."""
    if quick:
        return None
    rec = load("03-diffusion-limited-scarcity/same_niche_extended_results.py")
    mod = load("03-diffusion-limited-scarcity/stage6_briansbrain_neutral_tag.py")
    by_seed = rec.MATCHED_BUDGET_40K["gated"]["BB"]["by_seed"]
    banked = [by_seed[s] for s in range(4)]
    got = []
    for s in range(4):
        r = mod.run_energy_gated_trial(s, D_bg=0.05, D_diff=0.05,
                                       max_steps=40000, record_interval=20000)
        got.append(r["fixation_step"])
    ok = got == banked
    return ("same-niche: BB gated, seeds 0-3",
            ok,
            "banked (by seed) " + str(banked) + "  regenerated " + str(got))


CHECKS = [
    check_demand_gol,
    check_out_of_sample_seeds,
    check_out_of_sample_lwd,
    check_seed_count_recovery,
    check_flagship_cost,
    check_same_niche,
]


def main(quick=False):
    print("=" * 74)
    print("TIER B -- spot reproduction against banked records")
    print("repo: " + str(ROOT))
    if quick:
        print("mode: --quick (skipping checks over ~60 s)")
    print("=" * 74)

    failures = 0
    skipped = 0
    for fn in CHECKS:
        t0 = time.time()
        try:
            out = fn(quick)
        except Exception as exc:
            print("  ERROR " + fn.__name__ + ": " + repr(exc))
            failures += 1
            continue
        if out is None:
            print("  SKIP  " + (fn.__doc__ or fn.__name__).splitlines()[0])
            skipped += 1
            continue
        label, ok, detail = out
        status = "OK  " if ok else "FAIL"
        if not ok:
            failures += 1
        print("  " + status + "  " + label)
        print("          " + detail + "   [{0:.0f}s]".format(time.time() - t0))

    print("=" * 74)
    if failures:
        print("RESULT: " + str(failures) + " FAILURE(S) -- stop and investigate")
    else:
        print("RESULT: ALL REPRODUCED" + (" (" + str(skipped) + " skipped)" if skipped else ""))
    print("=" * 74)
    return 1 if failures else 0


def _in_notebook():
    try:
        return get_ipython().__class__.__name__ in ("ZMQInteractiveShell", "Shell")
    except NameError:
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="run only the checks under about 60 seconds each")
    args, _ = ap.parse_known_args()
    code = main(args.quick)
    if _in_notebook():
        print("\n(notebook run: exit code " + str(code) + " - not raising SystemExit)")
    else:
        sys.exit(code)

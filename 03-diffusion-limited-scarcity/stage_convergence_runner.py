"""
CONTESTABLE OCCUPANCY / DIFFUSION-LIMITED SCARCITY, AUDIT STAGE:
convergence-based runner for the Game of Life vs. Brian's Brain lottery
baseline (Section 4.1's flagship result) -- REVISED.

First version of this runner used a naive "both counts stop changing"
rule and found it never triggers for BB-dominant trials: tracing one
seed's full trajectory showed Game of Life's population freezes hard
and exactly (still-lifes, permanently fixed once reached), while
Brian's Brain's population FLUCTUATES around a stable mean indefinitely
(natural consequence of its own internal Firing/Refractory/OFF cycling
continuing within its own settled territory) rather than ever reaching
a literal fixed count. Requiring both counts to stop changing was
therefore the wrong criterion -- it would never fire for these trials.

REVISED STOPPING RULE:
  1. Terminal extinction: if either species' population hits exactly 0,
     it is permanently gone (neither rule can be seeded from nothing
     under this mechanism) -- stop immediately, this is unambiguous.
  2. Frontier freeze + trailing average: Game of Life's population
     count is the hard signal, since it either goes extinct or freezes
     into an exactly-fixed configuration -- it does not fluctuate the
     way Brian's Brain's count does. Once Game of Life's count has been
     UNCHANGED for FREEZE_CHECKS consecutive CHECK_INTERVAL-step windows,
     the territorial frontier is treated as decided. An additional
     AVERAGING_WINDOW steps are then run, and the reported Game-of-Life
     share is the MEAN over that window (not a single final snapshot),
     to average out Brian's Brain's natural population fluctuation
     rather than report a noisy point estimate.
  3. Safety cap: MAX_STEPS bounds worst-case runtime; a run that hits
     this cap without Game of Life's count ever freezing is flagged as
     NOT CONVERGED.
"""

import sys
import time
import numpy as np

sys.path.insert(0, ".")
from stage2_gol_vs_brians_brain import (
    N, GOL, BB_FIRING, BB_REFRACTORY, OFF, INIT_DENSITY_EACH,
    landauer_gated_step,
)

WARMUP_STEPS = 200
CHECK_INTERVAL = 1000
FREEZE_CHECKS = 3          # consecutive unchanged GoL-count checks before treating frontier as decided
AVERAGING_WINDOW = 5000    # additional steps to average BB's fluctuating count over, once frozen
MAX_STEPS = 30_000


def _counts(state):
    n_gol = int((state == GOL).sum())
    n_bb = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    return n_gol, n_bb


def run_to_convergence(D_bg, D_diff, seed, warmup=WARMUP_STEPS,
                        check_interval=CHECK_INTERVAL, freeze_checks=FREEZE_CHECKS,
                        averaging_window=AVERAGING_WINDOW, max_steps=MAX_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng)

    n_gol, n_bb = _counts(state)
    if n_gol == 0 or n_bb == 0:
        return _result(n_gol, n_bb, warmup, terminal=True, converged=True)

    steps_taken = warmup
    last_gol = n_gol
    frozen_count = 0

    while steps_taken < max_steps:
        for _ in range(check_interval):
            state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng)
        steps_taken += check_interval
        n_gol, n_bb = _counts(state)

        if n_gol == 0 or n_bb == 0:
            return _result(n_gol, n_bb, steps_taken, terminal=True, converged=True)

        if n_gol == last_gol:
            frozen_count += 1
        else:
            frozen_count = 0
        last_gol = n_gol

        if frozen_count >= freeze_checks:
            # Frontier decided -- average BB's fluctuating count (and
            # GoL's, for symmetry/robustness) over a trailing window.
            gol_samples, bb_samples = [n_gol], [n_bb]
            avg_steps_done = 0
            while avg_steps_done < averaging_window:
                for _ in range(check_interval):
                    state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng)
                avg_steps_done += check_interval
                ng, nb = _counts(state)
                if ng == 0 or nb == 0:
                    # extinction discovered during averaging -- terminal after all
                    return _result(ng, nb, steps_taken + avg_steps_done, terminal=True, converged=True)
                gol_samples.append(ng)
                bb_samples.append(nb)
            mean_gol = float(np.mean(gol_samples))
            mean_bb = float(np.mean(bb_samples))
            total_steps = steps_taken + avg_steps_done
            return _result(mean_gol, mean_bb, total_steps, terminal=False, converged=True,
                            gol_sd=float(np.std(gol_samples)), bb_sd=float(np.std(bb_samples)))

    return _result(n_gol, n_bb, steps_taken, terminal=False, converged=False)


def _result(n_gol, n_bb, steps_taken, terminal, converged, gol_sd=None, bb_sd=None):
    total = n_gol + n_bb
    frac = n_gol / total if total > 0 else None
    return {
        'n_gol_final': n_gol, 'n_bb_final': n_bb,
        'gol_territory_frac': frac,
        'steps_taken': steps_taken,
        'terminal_extinction': terminal,
        'converged': converged,
        'gol_sd': gol_sd, 'bb_sd': bb_sd,
    }


def sweep_condition(D_bg, D_diff, n_seeds, verbose=True):
    gol_total = 0
    bb_dominant_or_mixed = 0
    not_converged = 0
    shares = []
    max_steps_seen = 0
    for seed in range(n_seeds):
        r = run_to_convergence(D_bg, D_diff, seed)
        if not r['converged']:
            not_converged += 1
        if r['n_bb_final'] == 0:
            gol_total += 1
        else:
            bb_dominant_or_mixed += 1
        if r['gol_territory_frac'] is not None:
            shares.append(r['gol_territory_frac'])
        max_steps_seen = max(max_steps_seen, r['steps_taken'])
    mean_share = float(np.mean(shares)) if shares else None
    if verbose:
        print(f"D_bg={D_bg}, D_diff={D_diff}: GoL-total {gol_total}/{n_seeds}, "
              f"BB-dominant/mixed {bb_dominant_or_mixed}/{n_seeds}, "
              f"mean GoL share {mean_share:.4f}, "
              f"not-converged {not_converged}/{n_seeds}, max steps used {max_steps_seen}")
    return {'gol_total': gol_total, 'n_seeds': n_seeds, 'mean_gol_share': mean_share,
            'not_converged': not_converged, 'max_steps_seen': max_steps_seen}


if __name__ == "__main__":
    print("=== Sanity check: seed=1 (known GoL-total, should terminate fast) ===")
    t = time.time()
    r = run_to_convergence(D_bg=0.05, D_diff=0.05, seed=1)
    print(r, f"  (wall time {time.time()-t:.1f}s)")

    print("\n=== Sanity check: seed=0 (known BB-dominant, GoL freezes but BB fluctuates) ===")
    t = time.time()
    r = run_to_convergence(D_bg=0.05, D_diff=0.05, seed=0)
    print(r, f"  (wall time {time.time()-t:.1f}s)")

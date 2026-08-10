"""
CONTESTABLE OCCUPANCY / DIFFUSION-LIMITED SCARCITY, AUDIT STAGE:
convergence-based runner for Section 4.2's cost-asymmetry sweep
(Game of Life vs. Brian's Brain, Brian's Brain's transitions priced at
alpha x FLIP_COST).

Directly motivated by the flagship lottery-baseline audit
(stage_convergence_runner.py): that audit found the D_bg=0.05,
D_diff=0.05, alpha=1 condition -- exactly Section 4.2's own baseline
condition before any cost is applied -- is NOT at steady state within
the standard window, with most trials (73%) actually ending in
complete Brian's Brain extinction rather than partial coexistence.
Section 4.2's entire cost sweep uses this same D_bg/D_diff condition,
just with alpha varied, so the same problem is expected here.

ADDITIONAL WRINKLE AT HIGH ALPHA: BB's natural timescale (time to
afford a single flip) scales as roughly alpha/D_bg, same logic already
established for warmup scaling in Section 4.2's own code. This means
the convergence CHECK_INTERVAL must also scale with alpha, or a high-
alpha run could be falsely declared "frozen" simply because the check
interval was too short to observe BB's next transition, not because
the frontier is genuinely decided. This is handled below by scaling
check_interval the same way warmup is scaled in the original module.
"""

import sys
import time
import numpy as np

sys.path.insert(0, ".")
from stage3_calibrated_cost_competition import (
    N, GOL, BB_FIRING, BB_REFRACTORY, OFF, INIT_DENSITY_EACH, FLIP_COST,
    landauer_gated_step,
)

WARMUP_STEPS = 200
FREEZE_CHECKS = 3
AVERAGING_WINDOW_CHECKS = 5   # number of check_intervals to average BB's count over, once frozen
MAX_CHECKS = 30               # safety cap: max_steps = warmup + MAX_CHECKS * check_interval


def _counts(state):
    n_gol = int((state == GOL).sum())
    n_bb = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    return n_gol, n_bb


def run_to_convergence(D_bg, D_diff, seed, bb_cost_multiplier=1.0,
                        warmup=WARMUP_STEPS, freeze_checks=FREEZE_CHECKS,
                        averaging_window_checks=AVERAGING_WINDOW_CHECKS, max_checks=MAX_CHECKS):
    # Same scaling convention as the original module: ceiling and warmup
    # (and here, check_interval too) all scale with alpha/D_bg.
    dynamic_ceiling = 10.0 * max(1.0, bb_cost_multiplier)
    min_warmup_for_alpha = int(3 * bb_cost_multiplier / D_bg)
    effective_warmup = max(warmup, min_warmup_for_alpha)
    check_interval = max(1000, int(3 * bb_cost_multiplier / D_bg))

    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(effective_warmup):
        state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng,
                                                  bb_cost_multiplier=bb_cost_multiplier, ceiling=dynamic_ceiling)

    n_gol, n_bb = _counts(state)
    if n_gol == 0 or n_bb == 0:
        return _result(n_gol, n_bb, effective_warmup, terminal=True, converged=True, check_interval=check_interval)

    steps_taken = effective_warmup
    last_gol = n_gol
    frozen_count = 0
    checks_done = 0

    while checks_done < max_checks:
        for _ in range(check_interval):
            state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng,
                                                      bb_cost_multiplier=bb_cost_multiplier, ceiling=dynamic_ceiling)
        steps_taken += check_interval
        checks_done += 1
        n_gol, n_bb = _counts(state)

        if n_gol == 0 or n_bb == 0:
            return _result(n_gol, n_bb, steps_taken, terminal=True, converged=True, check_interval=check_interval)

        if n_gol == last_gol:
            frozen_count += 1
        else:
            frozen_count = 0
        last_gol = n_gol

        if frozen_count >= freeze_checks:
            gol_samples, bb_samples = [n_gol], [n_bb]
            for _ in range(averaging_window_checks):
                for _ in range(check_interval):
                    state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng,
                                                              bb_cost_multiplier=bb_cost_multiplier, ceiling=dynamic_ceiling)
                steps_taken += check_interval
                ng, nb = _counts(state)
                if ng == 0 or nb == 0:
                    return _result(ng, nb, steps_taken, terminal=True, converged=True, check_interval=check_interval)
                gol_samples.append(ng)
                bb_samples.append(nb)
            mean_gol = float(np.mean(gol_samples))
            mean_bb = float(np.mean(bb_samples))
            return _result(mean_gol, mean_bb, steps_taken, terminal=False, converged=True,
                            check_interval=check_interval,
                            gol_sd=float(np.std(gol_samples)), bb_sd=float(np.std(bb_samples)))

    return _result(n_gol, n_bb, steps_taken, terminal=False, converged=False, check_interval=check_interval)


def _result(n_gol, n_bb, steps_taken, terminal, converged, check_interval, gol_sd=None, bb_sd=None):
    total = n_gol + n_bb
    frac = n_gol / total if total > 0 else None
    return {
        'n_gol_final': n_gol, 'n_bb_final': n_bb,
        'gol_territory_frac': frac,
        'steps_taken': steps_taken,
        'terminal_extinction': terminal,
        'converged': converged,
        'check_interval': check_interval,
        'gol_sd': gol_sd, 'bb_sd': bb_sd,
    }


def sweep_alpha(D_bg, D_diff, alpha, n_seeds, max_checks=MAX_CHECKS, verbose=True):
    gol_total = 0
    not_converged_seeds = []
    shares = []
    max_steps_seen = 0
    for seed in range(n_seeds):
        r = run_to_convergence(D_bg, D_diff, seed, bb_cost_multiplier=alpha, max_checks=max_checks)
        if not r['converged']:
            not_converged_seeds.append(seed)
        if r['n_bb_final'] == 0:
            gol_total += 1
        if r['gol_territory_frac'] is not None:
            shares.append(r['gol_territory_frac'])
        max_steps_seen = max(max_steps_seen, r['steps_taken'])
    mean_share = float(np.mean(shares)) if shares else None
    if verbose:
        print(f"alpha={alpha}: GoL-total {gol_total}/{n_seeds}, mean GoL share {mean_share:.4f}, "
              f"not-converged {len(not_converged_seeds)}/{n_seeds} {not_converged_seeds if not_converged_seeds else ''}, "
              f"max steps used {max_steps_seen}")
    return {'alpha': alpha, 'gol_total': gol_total, 'n_seeds': n_seeds, 'mean_gol_share': mean_share,
            'not_converged_seeds': not_converged_seeds, 'max_steps_seen': max_steps_seen}


if __name__ == "__main__":
    print("=== Sanity check: alpha=1 should roughly match the flagship lottery-baseline audit (73% GoL-total) ===")
    t = time.time()
    sweep_alpha(D_bg=0.05, D_diff=0.05, alpha=1.0, n_seeds=10)
    print(f"  (wall time {time.time()-t:.1f}s)")

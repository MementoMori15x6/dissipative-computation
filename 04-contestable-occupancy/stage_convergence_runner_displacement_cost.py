"""
CONTESTABLE OCCUPANCY, AUDIT STAGE: convergence-based re-run of the
displacement-cost sweeps (stage6a = Day and Night vs. Brian's Brain,
stage6b = Game of Life vs. HighLife).

These two sweeps were the last displacement results measured at the
standard short window (200 warmup / 100 window) and never re-run under
the convergence audit. Given the alpha=3 critical-slowing-down finding
in the lottery cost sweep (Section 4.2), their figures were flagged
provisional. This script re-measures them to convergence, reusing each
stage6 module's own landauer_gated_step and initialization unchanged --
only the measurement (fixed window -> convergence + trailing average)
differs.

CONVERGENCE RULE (same family as stage_convergence_runner.py):
  1. Terminal extinction: either species count hits 0 -> stop, permanent.
  2. Trailing-average stability: track each species' count over
     CHECK_INTERVAL-step blocks; once consecutive block means agree to
     within REL_TOL for both species across STABLE_BLOCKS blocks, report
     the mean of the last AVG_BLOCKS blocks.
  3. Cap: MAX_STEPS; unconverged trials are classified by drift
     direction of the territory share (up/down) rather than discarded,
     the same discipline used for the alpha=3 lottery stragglers.
Check interval and warmup scale with alpha, matching the stage6 modules.
"""

import sys
import numpy as np

sys.path.insert(0, ".")

CHECK_INTERVAL_BASE = 1000
STABLE_BLOCKS = 2
AVG_BLOCKS = 3
REL_TOL = 0.05
MAX_BLOCKS = 40


def _run_module_to_convergence(mod, K, seed, cost_multiplier, a_states, b_states,
                                 warmup_base=200, check_interval_base=CHECK_INTERVAL_BASE,
                                 stable_blocks=STABLE_BLOCKS, avg_blocks=AVG_BLOCKS,
                                 rel_tol=REL_TOL, max_blocks=MAX_BLOCKS):
    """mod: the stage6 module. a_states/b_states: sets of state values for
    species A and B. Uses mod.landauer_gated_step, mod.N, mod.OFF,
    mod.INIT_DENSITY_EACH, mod.D_BG, mod.D_DIFF, and the same alpha-scaling
    the module itself uses."""
    N, OFF = mod.N, mod.OFF
    INIT = mod.INIT_DENSITY_EACH
    D_BG, D_DIFF = mod.D_BG, mod.D_DIFF

    # first state value in each species set is the initial seeding marker
    a_seed = sorted(a_states)[0]
    b_seed = sorted(b_states)[0]

    dynamic_ceiling = 10.0 * max(1.0, cost_multiplier)
    effective_warmup = max(warmup_base, int(3 * cost_multiplier / D_BG))
    check_interval = max(check_interval_base, int(3 * cost_multiplier / D_BG))

    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT] = a_seed
    state[(r >= INIT) & (r < 2 * INIT)] = b_seed
    energy = np.zeros((N, N))

    def step():
        # Cost multiplier and ceiling passed BY KEYWORD, not positionally.
        # Required interface for any module used with this runner:
        #     landauer_gated_step(state, energy, D_bg, D_diff, rng, K,
        #                         <cost_multiplier_name>, ceiling) -> (state, energy)
        # stage6a uses bb_cost_multiplier, stage6b uses b6_cost_multiplier, so the
        # multiplier stays positional; ceiling is named. The flagship module
        # (stage_cost_displacement) does NOT match -- it has flip_cost between the
        # multiplier and the ceiling, so a positional ceiling would land on flip_cost
        # and silently rescale every cost. Use stage_convergence_runner_flagship_cost
        # for that module; it wraps it in a shim.
        return mod.landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K,
                                       cost_multiplier, ceiling=dynamic_ceiling)

    def counts():
        na = int(np.isin(state, list(a_states)).sum())
        nb = int(np.isin(state, list(b_states)).sum())
        return na, nb

    for _ in range(effective_warmup):
        state, energy = step()

    na, nb = counts()
    if na == 0 or nb == 0:
        return _result(na, nb, effective_warmup, terminal=True, converged=True)

    block_means = []
    stable = 0
    steps = effective_warmup
    for _ in range(max_blocks):
        a_s, b_s = [], []
        for _ in range(check_interval):
            state, energy = step()
            na, nb = counts()
            a_s.append(na); b_s.append(nb)
        steps += check_interval
        if na == 0 or nb == 0:
            return _result(na, nb, steps, terminal=True, converged=True)
        ma, mb = float(np.mean(a_s)), float(np.mean(b_s))
        block_means.append((ma, mb))
        if len(block_means) >= 2:
            pa, pb = block_means[-2]
            if abs(ma - pa) <= max(1.0, rel_tol * pa) and abs(mb - pb) <= max(1.0, rel_tol * pb):
                stable += 1
            else:
                stable = 0
        if stable >= stable_blocks:
            recent = block_means[-avg_blocks:]
            fa = float(np.mean([x[0] for x in recent]))
            fb = float(np.mean([x[1] for x in recent]))
            return _result(fa, fb, steps, terminal=False, converged=True)

    # unconverged: classify by drift direction of A's share over last blocks
    recent = block_means[-avg_blocks:]
    fa = float(np.mean([x[0] for x in recent]))
    fb = float(np.mean([x[1] for x in recent]))
    early_share = block_means[0][0] / (block_means[0][0] + block_means[0][1] + 1e-9)
    late_share = fa / (fa + fb + 1e-9)
    drift = late_share - early_share
    return _result(fa, fb, steps, terminal=False, converged=False, drift=drift)


def _result(na, nb, steps, terminal, converged, drift=None):
    total = na + nb
    frac = na / total if total > 0 else None
    return {'n_a_final': na, 'n_b_final': nb, 'a_territory_frac': frac,
            'steps_taken': steps, 'terminal': terminal, 'converged': converged, 'drift': drift}


def sweep_6a(K_values, alpha_values, n_seeds):
    import stage6a_cost_displacement_dayandnight as m
    # A = Day and Night (variable GOL=1), B = Brian's Brain (FIRING=2, REFRACTORY=3)
    a_states, b_states = {m.GOL}, {m.BB_FIRING, m.BB_REFRACTORY}
    print("=== stage6a: Day and Night (A) vs Brian's Brain (B), convergence re-run ===")
    for K in K_values:
        for alpha in alpha_values:
            fracs, nconv, drifts = [], 0, []
            for s in range(n_seeds):
                r = _run_module_to_convergence(m, K, s, alpha, a_states, b_states)
                if r['a_territory_frac'] is not None:
                    fracs.append(r['a_territory_frac'])
                if not r['converged']:
                    nconv += 1
                    if r['drift'] is not None:
                        drifts.append(r['drift'])
            mean = np.mean(fracs) if fracs else float('nan')
            sd = np.std(fracs) if fracs else float('nan')
            dstr = f", unconv {nconv}/{n_seeds} drift(mean {np.mean(drifts):+.3f})" if nconv else ""
            print(f"  K={K}, alpha={alpha}: mean D&N share {mean:.4f} (sd {sd:.4f}){dstr}")


def sweep_6b(K_values, alpha_values, n_seeds):
    import stage6b_cost_displacement_highlife as m
    a_states, b_states = {m.SPECIES_A}, {m.SPECIES_B}
    print("=== stage6b: Game of Life (A) vs HighLife (B), convergence re-run ===")
    for K in K_values:
        for alpha in alpha_values:
            fracs, nconv, drifts = [], 0, []
            for s in range(n_seeds):
                r = _run_module_to_convergence(m, K, s, alpha, a_states, b_states)
                if r['a_territory_frac'] is not None:
                    fracs.append(r['a_territory_frac'])
                if not r['converged']:
                    nconv += 1
                    if r['drift'] is not None:
                        drifts.append(r['drift'])
            mean = np.mean(fracs) if fracs else float('nan')
            sd = np.std(fracs) if fracs else float('nan')
            dstr = f", unconv {nconv}/{n_seeds} drift(mean {np.mean(drifts):+.3f})" if nconv else ""
            print(f"  K={K}, alpha={alpha}: mean GoL share {mean:.4f} (sd {sd:.4f}){dstr}")

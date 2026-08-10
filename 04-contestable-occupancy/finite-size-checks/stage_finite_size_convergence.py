"""
FINITE-SIZE CHECK, CONVERGENCE VERSION: does the flagship diffusion-driven
competitive transition (Section 4.1) survive at larger grid sizes, measured
to genuine convergence rather than the short window?

This directly addresses the single most damaging reviewer objection: that
the flagship result rests on one grid size (N=64) and the only finite-size
check performed used the discredited short window. Here we re-run the
GoL-vs-BB competition at N=64, 128, 256 under the SAME convergence criterion
validated for the N=64 result (freeze-detection on GoL's hard-frozen count +
trailing average of both counts; terminal-extinction stop).

Reuses stage_finite_size.py's landauer_gated_step and initialization
unchanged (same GoL-vs-BB mechanism, INIT_DENSITY_EACH=0.10, 50/50 coin);
only the measurement (fixed window -> convergence) differs.

Question 1: at D_diff = 0.05 (where the corrected N=64 result has GoL
winning ~73%), does GoL still win the majority at N=128 and N=256?
Question 2: does the transition still exist (BB winning at high D_diff)
at larger sizes, i.e. does the LOCATION of the transition hold?
"""

import sys
import numpy as np

sys.path.insert(0, ".")
import stage_finite_size as m

CHECK_INTERVAL = 1000
FREEZE_CHECKS = 3
AVERAGING_WINDOW = 5000
MAX_STEPS = 30000


def run_to_convergence(D_bg, D_diff, seed, grid_n, warmup=200,
                        check_interval=CHECK_INTERVAL, freeze_checks=FREEZE_CHECKS,
                        averaging_window=AVERAGING_WINDOW, max_steps=MAX_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((grid_n, grid_n), m.OFF, dtype=int)
    r = rng.random((grid_n, grid_n))
    state[r < m.INIT_DENSITY_EACH] = m.GOL
    state[(r >= m.INIT_DENSITY_EACH) & (r < 2 * m.INIT_DENSITY_EACH)] = m.BB_FIRING
    energy = np.zeros((grid_n, grid_n))

    def counts():
        ng = int((state == m.GOL).sum())
        nb = int(((state == m.BB_FIRING) | (state == m.BB_REFRACTORY)).sum())
        return ng, nb

    for _ in range(warmup):
        state, energy, _ = m.landauer_gated_step(state, energy, D_bg, D_diff, rng)

    n_gol, n_bb = counts()
    if n_gol == 0 or n_bb == 0:
        return _result(n_gol, n_bb, warmup, True, True)

    steps = warmup
    last_gol = n_gol
    frozen = 0
    while steps < max_steps:
        for _ in range(check_interval):
            state, energy, _ = m.landauer_gated_step(state, energy, D_bg, D_diff, rng)
        steps += check_interval
        n_gol, n_bb = counts()
        if n_gol == 0 or n_bb == 0:
            return _result(n_gol, n_bb, steps, True, True)
        frozen = frozen + 1 if n_gol == last_gol else 0
        last_gol = n_gol
        if frozen >= freeze_checks:
            gs, bs = [n_gol], [n_bb]
            done = 0
            while done < averaging_window:
                for _ in range(check_interval):
                    state, energy, _ = m.landauer_gated_step(state, energy, D_bg, D_diff, rng)
                done += check_interval
                ng, nb = counts()
                if ng == 0 or nb == 0:
                    return _result(ng, nb, steps + done, True, True)
                gs.append(ng); bs.append(nb)
            return _result(float(np.mean(gs)), float(np.mean(bs)), steps + done, False, True,
                           float(np.std(gs)), float(np.std(bs)))
    return _result(n_gol, n_bb, steps, False, False)


def _result(ng, nb, steps, terminal, converged, gsd=None, bsd=None):
    total = ng + nb
    return {'n_gol': ng, 'n_bb': nb, 'gol_frac': ng / total if total > 0 else None,
            'steps': steps, 'terminal': terminal, 'converged': converged,
            'gol_sd': gsd, 'bb_sd': bsd}


def sweep(D_diff, grid_n, n_seeds, D_bg=0.05):
    fracs, gol_wins, nconv = [], 0, 0
    for s in range(n_seeds):
        r = run_to_convergence(D_bg, D_diff, s, grid_n)
        if r['gol_frac'] is not None:
            fracs.append(r['gol_frac'])
            if r['gol_frac'] > 0.5:
                gol_wins += 1
        if not r['converged']:
            nconv += 1
    return {'D_diff': D_diff, 'grid_n': grid_n, 'mean_gol_frac': float(np.mean(fracs)),
            'gol_win_rate': gol_wins / n_seeds, 'not_converged': nconv, 'n_seeds': n_seeds}


if __name__ == "__main__":
    import time
    t = time.time()
    r = run_to_convergence(D_bg=0.05, D_diff=0.05, seed=0, grid_n=128)
    print(r, f"time={time.time()-t:.1f}s")

"""
CONTESTABLE OCCUPANCY / DIFFUSION-LIMITED SCARCITY, AUDIT STAGE:
convergence-based runner for Game of Life vs. Day and Night (Section
4.3's third pairing, lottery competition, D_bg=0.05, D_diff=0.05).

Neither species here is Brian's Brain, so there is no cost-multiplier
dimension (both pay symmetric FLIP_COST throughout, matching the
original module). Uses the same trailing-average convergence criterion
as stage_convergence_runner_general.py, reimplemented directly against
stage5_gol_vs_dayandnight.py's simpler landauer_gated_step signature
(no bb_cost_multiplier/ceiling kwargs).
"""

import sys
import numpy as np

sys.path.insert(0, ".")
import stage5_gol_vs_dayandnight as m


def run_to_convergence(D_bg, D_diff, seed, warmup=200, check_interval=1000,
                        freeze_checks=3, averaging_blocks=3, rel_tol=0.05, max_checks=40):
    rng = np.random.default_rng(seed)
    state = np.full((m.N, m.N), m.OFF, dtype=int)
    r = rng.random((m.N, m.N))
    state[r < m.INIT_DENSITY_EACH] = m.SPECIES_A
    state[(r >= m.INIT_DENSITY_EACH) & (r < 2 * m.INIT_DENSITY_EACH)] = m.SPECIES_B
    energy = np.zeros((m.N, m.N))
    for _ in range(warmup):
        state, energy, _ = m.landauer_gated_step(state, energy, D_bg, D_diff, rng)

    def counts():
        return int((state == m.SPECIES_A).sum()), int((state == m.SPECIES_B).sum())

    n_a, n_b = counts()
    if n_a == 0 or n_b == 0:
        return _result(n_a, n_b, warmup, True, True)

    steps = warmup
    block_means = []
    stable = 0
    checks = 0
    while checks < max_checks:
        a_s, b_s = [], []
        for _ in range(check_interval):
            state, energy, _ = m.landauer_gated_step(state, energy, D_bg, D_diff, rng)
            na, nb = counts()
            a_s.append(na)
            b_s.append(nb)
        steps += check_interval
        checks += 1
        na, nb = counts()
        if na == 0 or nb == 0:
            return _result(na, nb, steps, True, True)
        ma, mb = float(np.mean(a_s)), float(np.mean(b_s))
        block_means.append((ma, mb))
        if len(block_means) >= 2:
            pa, pb = block_means[-2]
            if abs(ma - pa) <= max(1.0, rel_tol * pa) and abs(mb - pb) <= max(1.0, rel_tol * pb):
                stable += 1
            else:
                stable = 0
        if stable >= freeze_checks:
            recent = block_means[-averaging_blocks:]
            fa = float(np.mean([x[0] for x in recent]))
            fb = float(np.mean([x[1] for x in recent]))
            return _result(fa, fb, steps, False, True)
    return _result(na, nb, steps, False, False)


def _result(n_a, n_b, steps, terminal, converged):
    total = n_a + n_b
    share = n_a / total if total > 0 else None
    return {'n_a_final': n_a, 'n_b_final': n_b, 'a_territory_frac': share,
            'steps_taken': steps, 'terminal_extinction': terminal, 'converged': converged}


def sweep(D_bg, D_diff, n_seeds, verbose=True, **kwargs):
    a_total = 0
    not_converged = []
    shares = []
    max_steps = 0
    for seed in range(n_seeds):
        r = run_to_convergence(D_bg, D_diff, seed, **kwargs)
        if not r['converged']:
            not_converged.append(seed)
        if r['n_b_final'] == 0:
            a_total += 1
        if r['a_territory_frac'] is not None:
            shares.append(r['a_territory_frac'])
        max_steps = max(max_steps, r['steps_taken'])
    mean_share = float(np.mean(shares)) if shares else None
    if verbose:
        print(f"D_bg={D_bg}, D_diff={D_diff}: GoL-total(D&N-extinct) {a_total}/{n_seeds}, "
              f"mean GoL share {mean_share:.4f}, not-converged {len(not_converged)}/{n_seeds} "
              f"{not_converged if not_converged else ''}, max steps {max_steps}")
    return {'a_total': a_total, 'n_seeds': n_seeds, 'mean_a_share': mean_share,
            'not_converged_seeds': not_converged, 'max_steps_seen': max_steps}


if __name__ == "__main__":
    print("GoL vs Day and Night, D_bg=0.05, D_diff=0.05, 15 seeds:")
    sweep(D_bg=0.05, D_diff=0.05, n_seeds=15)

"""
CONTESTABLE OCCUPANCY, STAGE 4: extend Day and Night vs Brian's Brain
K-sweep to K=4-8 at 30 seeds.

Context: Section 3.4 / manuscript Section 4.6 replicated K=1-3 at 30
seeds for this pairing (specific combination: captured Day-and-Night
cell becomes BB_REFRACTORY rather than BB_FIRING, and only BB_FIRING
counts toward capture pressure -- BB_PRESSURE_STATES={BB_FIRING}),
catching a real overstatement at K=2 (22/30, not 30/30 as the original
10-seed pass suggested). K=4 and above were left at 10-seed estimates.
This script closes that gap using the identical combination and
identical D_bg/D_diff condition (0.05, 0.05) for direct comparability.

IMPORTANT: this script does NOT monkeypatch the Stage 1 module's
pinned constants -- those are bound as function-default arguments at
import time, so reassigning the module attributes afterward would
silently have no effect (a real bug caught while drafting this file,
same failure shape as the project's other silent-parameter bugs).
Instead every call below passes the combination explicitly.

Per project convention: verify at a known value (K=3) before trusting
the new range, then run K=4-8.
"""

import sys
import numpy as np

sys.path.insert(0, ".")
from stage2_dayandnight_vs_briansbrain_contestable import (
    N, propose_next_with_capture, diffuse_energy,
    BB_FIRING, BB_REFRACTORY, GOL, OFF,
    FLIP_COST, ENERGY_CEILING, WARMUP_STEPS, WINDOW_STEPS, INIT_DENSITY_EACH,
)

D_BG = 0.05
D_DIFF = 0.05
N_SEEDS = 30
CAPTURED_GOL_BECOMES = BB_REFRACTORY   # combination replicated for K=1-3
BB_PRESSURE_STATES = {BB_FIRING}       # combination replicated for K=1-3


def landauer_gated_step_explicit(state, energy, D_bg, D_diff, rng, K,
                                   bb_pressure_states, captured_gol_becomes,
                                   flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed, capture_direction = propose_next_with_capture(
        state, rng, K,
        bb_pressure_states=bb_pressure_states,
        captured_gol_becomes=captured_gol_becomes,
    )
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0

    state_next = np.where(actually_flips, proposed, state)

    normal_next = energy - flip_cost
    # zero-out on capture specifically (matches Stage 1's pinned
    # ENERGY_ON_CAPTURE_TRANSFER=False, not swept here)
    energy_next = np.where(actually_flips & capture_happened, 0.0,
                   np.where(actually_flips & ~capture_happened, normal_next, energy))
    energy_next = np.clip(energy_next, 0, ceiling)

    return state_next, energy_next


def run_condition_explicit(D_bg, D_diff, K, seed, bb_pressure_states, captured_gol_becomes,
                             warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy = landauer_gated_step_explicit(
            state, energy, D_bg, D_diff, rng, K, bb_pressure_states, captured_gol_becomes)

    for _ in range(window):
        state, energy = landauer_gated_step_explicit(
            state, energy, D_bg, D_diff, rng, K, bb_pressure_states, captured_gol_becomes)

    n_gol_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total_occupied = n_gol_final + n_bb_final
    gol_territory_frac = n_gol_final / total_occupied if total_occupied > 0 else None

    return {'K': K, 'n_gol_final': n_gol_final, 'n_bb_final': n_bb_final,
            'gol_territory_frac': gol_territory_frac}


def run_k_sweep(k_values, n_seeds=N_SEEDS, verbose=True):
    results = {}
    for K in k_values:
        bb_extinct = 0
        dn_extinct = 0
        gol_shares = []
        for seed in range(n_seeds):
            r = run_condition_explicit(
                D_bg=D_BG, D_diff=D_DIFF, K=K, seed=seed,
                bb_pressure_states=BB_PRESSURE_STATES,
                captured_gol_becomes=CAPTURED_GOL_BECOMES,
            )
            if r['n_bb_final'] == 0:
                bb_extinct += 1
            if r['n_gol_final'] == 0:
                dn_extinct += 1
            if r['gol_territory_frac'] is not None:
                gol_shares.append(r['gol_territory_frac'])
        mean_share = float(np.mean(gol_shares)) if gol_shares else None
        sd_share = float(np.std(gol_shares)) if gol_shares else None
        results[K] = {
            'bb_extinct': bb_extinct, 'dn_extinct': dn_extinct, 'n_seeds': n_seeds,
            'mean_dn_share': mean_share, 'sd_dn_share': sd_share,
        }
        if verbose:
            share_str = f"{mean_share:.3f} (sd {sd_share:.3f})" if mean_share is not None else "n/a (all extinct both sides)"
            print(f"K={K}: BB extinct {bb_extinct}/{n_seeds}, D&N extinct {dn_extinct}/{n_seeds}, "
                  f"mean D&N share {share_str}")
    return results


if __name__ == "__main__":
    print("=== Sanity check: K=3 should reproduce ~25/30 D&N extinctions (Section 3.4) ===")
    run_k_sweep([3], n_seeds=30)

    print("\n=== New range: K=4-8, 30 seeds each ===")
    run_k_sweep([4, 5, 6, 7, 8], n_seeds=30)

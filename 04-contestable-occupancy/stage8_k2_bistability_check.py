"""
CONTESTABLE OCCUPANCY, STAGE 8: K=2 bistability check for Day and Night
vs. Brian's Brain -- and the equilibration-time correction it led to.

Original question: does the K=2 non-determinism (22 of 30 trials showing
Brian's Brain extinction, at the standard 200-warmup/100-window
measurement) reflect genuine bistability (two distinct stable outcomes)
or continuous variation across seeds?

What was actually found: neither. Extending the measurement window
(3,000 steps, verified unchanged at 5,000 and 10,000) showed every one
of the 8 "surviving" trials at the standard window was still in the
same slow decay toward Brian's Brain's extinction as the other 22 --
just not yet finished. The true, equilibrated result at K=2 is fully
deterministic (30 of 30), not bistable and not continuously varying.

The same check, applied to every other K value in this pairing's sweep,
found the identical problem at K=3, K=4, and K=5 (all corrected toward
more-deterministic outcomes), and confirmed K=1 and K=6-8 were already
measured correctly (extinction is absorbing and permanent once reached,
so K=1's 30/30 could not un-happen; K=6-8's population counts were
checked directly against a 3,000-step window and found identical).

This script reproduces the full corrected K=1-8 table at a window long
enough to reach genuine steady state (3,000 steps), superseding the
window=100 table in stage4_dayandnight_k4to8_30seed.py.
"""

import sys
import numpy as np

sys.path.insert(0, ".")
from stage4_dayandnight_k4to8_30seed import (
    run_condition_explicit, D_BG, D_DIFF, BB_PRESSURE_STATES, CAPTURED_GOL_BECOMES,
)

EQUILIBRATED_WINDOW = 3000  # verified unchanged at 5000 and 10000 for spot-checked seeds
N_SEEDS = 30


def run_k_sweep_equilibrated(k_values, n_seeds=N_SEEDS, window=EQUILIBRATED_WINDOW, verbose=True):
    results = {}
    for K in k_values:
        dn_extinct = 0
        shares = []
        for seed in range(n_seeds):
            r = run_condition_explicit(
                D_bg=D_BG, D_diff=D_DIFF, K=K, seed=seed,
                bb_pressure_states=BB_PRESSURE_STATES,
                captured_gol_becomes=CAPTURED_GOL_BECOMES,
                window=window,
            )
            if r['n_gol_final'] == 0:
                dn_extinct += 1
            total = r['n_gol_final'] + r['n_bb_final']
            if total > 0:
                shares.append(r['n_gol_final'] / total)
        mean_share = float(np.mean(shares)) if shares else 0.0
        sd_share = float(np.std(shares)) if shares else 0.0
        results[K] = {'dn_extinct': dn_extinct, 'n_seeds': n_seeds,
                      'mean_dn_share': mean_share, 'sd_dn_share': sd_share}
        if verbose:
            print(f"K={K}: D&N extinct {dn_extinct}/{n_seeds}, mean D&N share {mean_share:.4f} (sd {sd_share:.4f})")
    return results


def check_specific_seeds_for_transient(K, seeds_and_n_at_100, long_window=2000):
    """Re-runs specific seeds (that looked non-extinct at the standard
    window) at a much longer window, to distinguish a genuine steady
    state from an unresolved transient. Returns True if any seed's
    population changed (i.e. was NOT yet at steady state)."""
    print(f"--- K={K}: checking {len(seeds_and_n_at_100)} seeds for transient decay ---")
    changed_any = False
    for seed, n_at_100 in seeds_and_n_at_100:
        r_long = run_condition_explicit(
            D_bg=D_BG, D_diff=D_DIFF, K=K, seed=seed,
            bb_pressure_states=BB_PRESSURE_STATES,
            captured_gol_becomes=CAPTURED_GOL_BECOMES,
            window=long_window,
        )
        n_at_long = r_long['n_gol_final']
        changed = n_at_long != n_at_100
        changed_any = changed_any or changed
        print(f"  seed={seed}: n_dn at window=100 was {n_at_100}, at window={long_window}: {n_at_long}"
              + ("  <-- WAS TRANSIENT" if changed else "  (genuine steady state)"))
    return changed_any


if __name__ == "__main__":
    print("=== Step 1: confirm K=6-8 were already at genuine steady state (spot check) ===")
    check_specific_seeds_for_transient(8, [(0, 4), (3, 4), (4, 4), (5, 4), (7, 4), (8, 8)], long_window=2000)

    print("\n=== Step 2: confirm K=2's 8 'surviving' seeds were transients, not a real second outcome ===")
    check_specific_seeds_for_transient(2, [(2, 4), (11, 86), (14, 4), (16, 70), (21, 6), (23, 59), (24, 1), (29, 60)])

    print("\n=== Step 3: full corrected K=1-8 sweep at equilibrated window (3000 steps, 30 seeds each) ===")
    run_k_sweep_equilibrated([1, 2, 3, 4, 5, 6, 7, 8])

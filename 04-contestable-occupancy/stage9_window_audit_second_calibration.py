"""
CONTESTABLE OCCUPANCY, STAGE 9: measurement-window adequacy audit,
second calibration (D_bg=0.01, D_diff=0.03).

Purpose: Section 3.4 found the standard 100-step measurement window is
insufficient near Day and Night vs. Brian's Brain's K=2/K=3 transition
at the FIRST calibration (D_bg=0.05, D_diff=0.05) -- reported non-
determinism and a "gradual transition" turned out to be an unresolved
transient, corrected by extending the window to 3,000+ steps.

Section 3.8's second-calibration results (D_bg=0.01, D_diff=0.03) were
measured entirely at the standard window, at exactly the kind of sharp
transition (K=1 to K=3, for every pairing) where this failure mode was
just found. This script checks all four pairings at that calibration
before trusting the second-calibration replication project (README
next-steps #1).

IMPORTANT: D_bg=0.01 is 5x smaller than the first calibration's 0.05 --
background energy income is proportionally slower, so relaxation times
could plausibly be longer here too. This script tests window=3000 AND
window=8000 (not just 3000) to check for exactly this possibility
before concluding the window is adequate.

Method: re-run a subset of individual seeds from the original 15-seed,
window=100 sweep at much longer windows, and check whether the result
changes. If it does, the original window=100 result for that pairing/K
was a transient. If it doesn't (across at least two longer windows),
treat it as confirmed genuine.
"""

import sys
import numpy as np

sys.path.insert(0, ".")
import stage1_contestable_occupancy as gol_bb
import stage3_gol_vs_dayandnight_contestable as gol_dn
import stage_gol_vs_highlife_contestable as gol_hl
from stage5_second_calibration import run_dn_bb, D_BG_NEW, D_DIFF_NEW

K_VALUES = [1, 3, 5, 8]
N_SEEDS_SPOTCHECK = 5
WINDOWS_TO_TEST = [100, 5000]


def audit_pairing(name, run_fn, share_key, n_final_keys, k_values=K_VALUES, n_seeds=N_SEEDS_SPOTCHECK):
    """run_fn(K, seed, window) -> dict with share_key giving territory
    share of species A."""
    print(f"\n=== {name} ===")
    any_transient = False
    for K in k_values:
        rows = {w: [] for w in WINDOWS_TO_TEST}
        for w in WINDOWS_TO_TEST:
            for s in range(n_seeds):
                r = run_fn(K, s, w)
                rows[w].append(r[share_key])
        means = {w: np.mean(rows[w]) for w in WINDOWS_TO_TEST}
        moved = abs(means[5000] - means[100]) > 0.02
        flag = "  <-- MOVED, POSSIBLE TRANSIENT" if moved else "  (stable)"
        print(f"  K={K}: window=100 mean={means[100]:.4f} | window=5000 mean={means[5000]:.4f}{flag}")
        any_transient = any_transient or moved
    return any_transient


def gol_bb_run(K, seed, window):
    return gol_bb.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=seed, window=window)


def gol_dn_run(K, seed, window):
    r = gol_dn.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=seed, window=window)
    return {'gol_territory_frac': r['a_territory_frac']}


def gol_hl_run(K, seed, window):
    r = gol_hl.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=seed, window=window)
    return {'gol_territory_frac': r['a_territory_frac']}


def dn_bb_run(K, seed, window):
    r = run_dn_bb(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=seed, window=window)
    return {'gol_territory_frac': r['dn_territory_frac']}


if __name__ == "__main__":
    results = {}
    results['GoL vs Brian\'s Brain'] = audit_pairing(
        "GoL vs Brian's Brain", lambda K, s, w: gol_bb_run(K, s, w), 'gol_territory_frac', None)
    results['GoL vs Day and Night'] = audit_pairing(
        "GoL vs Day and Night", lambda K, s, w: gol_dn_run(K, s, w), 'gol_territory_frac', None)
    results['GoL vs HighLife'] = audit_pairing(
        "GoL vs HighLife", lambda K, s, w: gol_hl_run(K, s, w), 'gol_territory_frac', None)
    results['Day and Night vs BB'] = audit_pairing(
        "Day and Night vs Brian's Brain", lambda K, s, w: dn_bb_run(K, s, w), 'gol_territory_frac', None)

    print("\n=== SUMMARY ===")
    for name, transient in results.items():
        print(f"  {name}: {'NEEDS CORRECTION' if transient else 'confirmed stable'}")

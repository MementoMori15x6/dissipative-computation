"""
CONTESTABLE OCCUPANCY, STAGE 5: second D_bg/D_diff calibration.

Every displacement-competition result reported so far (Sections 4.4,
4.6 of the manuscript) used one background-inflow/diffusion condition:
D_bg=0.05, D_diff=0.05, described throughout the project as "Brian's
Brain's own calibrated threshold, giving both species enough ambient
energy to attempt ignition from step zero." Section 4.1's original
lottery-competition sweep tested a SECOND condition -- background
inflow calibrated to Game of Life's own (much lower) threshold -- and
found it did not reverse the outcome (Brian's Brain won even more
decisively, 94.7-96.0%, versus 55.6-96.7% at the first condition).

That second condition's exact value is documented elsewhere in this
project (03-diffusion-limited-scarcity/stage1_gause_neutral_competition.py,
explicitly labeled "GoL's own calibrated threshold"): D_bg=0.01,
D_diff=0.03. This script re-runs all four displacement pairings at
that condition, to check whether the K-sensitivity patterns found at
D_bg=0.05 (Section 4.6) are specific to that one calibration.

Per project convention: verify each pairing reproduces its known
D_bg=0.05 result BEFORE trusting any result at the new condition.

Seed count: 15 per condition on this first pass (matching Section
4.1/4.3/4.4's original seed depth), not yet 30 -- anything that looks
dramatic or borderline here should be replicated at 30 seeds as a
follow-up, per the project's standing rule against trusting small-n
dramatic results.
"""

import sys
import numpy as np

sys.path.insert(0, ".")

import stage1_contestable_occupancy as gol_bb
import stage3_gol_vs_dayandnight_contestable as gol_dn
import stage_gol_vs_highlife_contestable as gol_hl
from stage2_dayandnight_vs_briansbrain_contestable import (
    N, propose_next_with_capture, diffuse_energy,
    BB_FIRING, BB_REFRACTORY, GOL, OFF,
    FLIP_COST, ENERGY_CEILING, WARMUP_STEPS, WINDOW_STEPS, INIT_DENSITY_EACH,
)

D_BG_NEW, D_DIFF_NEW = 0.01, 0.03   # GoL's own calibrated threshold
D_BG_OLD, D_DIFF_OLD = 0.05, 0.05   # BB's own calibrated threshold (all prior results)
K_VALUES = [1, 3, 5, 8]
N_SEEDS = 15


# --- D&N vs BB needs the explicit-parameter version (Stage 4's fix) ---
def landauer_gated_step_explicit(state, energy, D_bg, D_diff, rng, K,
                                   bb_pressure_states, captured_gol_becomes,
                                   flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed, capture_direction = propose_next_with_capture(
        state, rng, K, bb_pressure_states=bb_pressure_states,
        captured_gol_becomes=captured_gol_becomes)
    flip_mask = proposed != state
    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)
    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0
    state_next = np.where(actually_flips, proposed, state)
    normal_next = energy - flip_cost
    energy_next = np.where(actually_flips & capture_happened, 0.0,
                   np.where(actually_flips & ~capture_happened, normal_next, energy))
    energy_next = np.clip(energy_next, 0, ceiling)
    return state_next, energy_next


def run_dn_bb(D_bg, D_diff, K, seed, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL  # variable name retained; this IS Day and Night
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))
    bb_pressure_states = {BB_FIRING}
    captured_gol_becomes = BB_REFRACTORY
    for _ in range(warmup + window):
        state, energy = landauer_gated_step_explicit(
            state, energy, D_bg, D_diff, rng, K, bb_pressure_states, captured_gol_becomes)
    n_dn_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total = n_dn_final + n_bb_final
    dn_frac = n_dn_final / total if total > 0 else None
    return {'n_dn_final': n_dn_final, 'n_bb_final': n_bb_final, 'dn_territory_frac': dn_frac}


def summarize(label, values_dict, extinct_a_key, extinct_b_key, share_key, n_seeds):
    print(f"\n--- {label} ---")
    for K in K_VALUES:
        rows = values_dict[K]
        a_ext = sum(1 for r in rows if r.get(extinct_a_key) == 0)
        b_ext = sum(1 for r in rows if r.get(extinct_b_key) == 0)
        shares = [r[share_key] for r in rows if r.get(share_key) is not None]
        mean_s = np.mean(shares) if shares else None
        sd_s = np.std(shares) if shares else None
        s_str = f"{mean_s:.3f} (sd {sd_s:.3f})" if mean_s is not None else "n/a"
        print(f"  K={K}: A-extinct {a_ext}/{n_seeds}, B-extinct {b_ext}/{n_seeds}, mean A-share {s_str}")


if __name__ == "__main__":
    print("=== SANITY CHECKS: reproduce known D_bg=0.05 results before trusting new condition ===")

    r = gol_bb.run_condition(D_bg=D_BG_OLD, D_diff=D_DIFF_OLD, K=7, seed=0)
    print(f"GoL vs BB, K=7, D_bg=0.05 (expect ~0.22-0.25 GoL share): {r['gol_territory_frac']:.3f}")

    r = gol_dn.run_condition(D_bg=D_BG_OLD, D_diff=D_DIFF_OLD, K=7, seed=0)
    print(f"GoL vs D&N, K=7, D_bg=0.05 (expect ~0.996 GoL share): {r['a_territory_frac']:.3f}")

    r = gol_hl.run_condition(D_bg=D_BG_OLD, D_diff=D_DIFF_OLD, K=3, seed=0)
    print(f"GoL vs HighLife, K=3, D_bg=0.05 (expect ~0.49-0.60 GoL share): {r['a_territory_frac']:.3f}")

    r = run_dn_bb(D_bg=D_BG_OLD, D_diff=D_DIFF_OLD, K=3, seed=0)
    print(f"D&N vs BB, K=3, D_bg=0.05 (expect near-zero D&N share, most seeds extinct): {r['dn_territory_frac']}")

    print("\n=== NEW CONDITION: D_bg=0.01, D_diff=0.03 (GoL's own threshold), 15 seeds, K=1,3,5,8 ===")

    gol_bb_results = {K: [gol_bb.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=s)
                          for s in range(N_SEEDS)] for K in K_VALUES}
    summarize("GoL vs Brian's Brain", gol_bb_results, 'n_gol_final', 'n_bb_final', 'gol_territory_frac', N_SEEDS)

    gol_dn_results = {K: [gol_dn.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=s)
                          for s in range(N_SEEDS)] for K in K_VALUES}
    summarize("GoL vs Day and Night", gol_dn_results, 'n_a_final', 'n_b_final', 'a_territory_frac', N_SEEDS)

    gol_hl_results = {K: [gol_hl.run_condition(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=s)
                          for s in range(N_SEEDS)] for K in K_VALUES}
    summarize("GoL vs HighLife", gol_hl_results, 'n_a_final', 'n_b_final', 'a_territory_frac', N_SEEDS)

    dn_bb_results = {K: [run_dn_bb(D_bg=D_BG_NEW, D_diff=D_DIFF_NEW, K=K, seed=s)
                         for s in range(N_SEEDS)] for K in K_VALUES}
    summarize("Day and Night vs Brian's Brain", dn_bb_results, 'n_dn_final', 'n_bb_final', 'dn_territory_frac', N_SEEDS)

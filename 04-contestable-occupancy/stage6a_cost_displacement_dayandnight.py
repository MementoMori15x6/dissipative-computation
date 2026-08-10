"""
CONTESTABLE OCCUPANCY, STAGE 6a: cost asymmetry under displacement,
extended to Day and Night vs. Brian's Brain.

Section 4.6 of the manuscript tested whether Brian's Brain's cost-
insensitivity (Section 4.2, lottery competition) survives displacement
competition, for the flagship pairing (Game of Life vs. Brian's Brain)
only. This script runs the identical test for the second pairing:
Day and Night vs. Brian's Brain, using the same combination already
established for this pairing's main K-sweep (30-seed replication,
Sections 3.4/4.6): captured Day-and-Night cell becomes BB_REFRACTORY,
BB_PRESSURE_STATES = {BB_FIRING}.

Cost convention (identical to the flagship test): any transition
involving a Brian's Brain state -- as current state (mandatory
cycling, or being captured) or as proposed state (ignition, or
capturing an occupied Day-and-Night cell) -- costs alpha times the
base flip cost. Ceiling and warmup both scaled with alpha, verified
against alpha=1 before trusting higher values (same two corrections
required in Section 4.2's original sweep).

K values: 1, 5, 8 -- representative of the near-parity (K=1),
BB-dominant-and-strengthening (K=5), and reconverged (K=8) regimes
already characterized for this pairing in Section 4.6.
Alpha values: 1, 20, 200 (matching the flagship test).
Seeds: 10 per condition (matching the flagship test's first pass).
"""

import numpy as np

N = 64
FLIP_COST = 1.0
WARMUP_STEPS = 200
WINDOW_STEPS = 100
INIT_DENSITY_EACH = 0.10
D_BG, D_DIFF = 0.05, 0.05

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

OFF, GOL, BB_FIRING, BB_REFRACTORY = 0, 1, 2, 3  # "GOL" here is Day and Night (variable name retained)
DN_BIRTH_SET, DN_SURVIVE_SET = {3, 6, 7, 8}, {3, 4, 6, 7, 8}

CAPTURED_DN_BECOMES = BB_REFRACTORY
BB_PRESSURE_STATES = {BB_FIRING}


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next_with_capture(state, rng, K):
    dn_mask = state == GOL
    bb_firing_mask = state == BB_FIRING
    bb_refractory_mask = state == BB_REFRACTORY
    bb_pressure_mask = np.isin(state, list(BB_PRESSURE_STATES))
    off_mask = state == OFF

    dn_neighbor_count = count_neighbors(dn_mask.astype(int))
    bb_firing_neighbor_count = count_neighbors(bb_firing_mask.astype(int))
    bb_pressure_neighbor_count = count_neighbors(bb_pressure_mask.astype(int))

    proposed = np.full_like(state, OFF)

    dn_survives = dn_mask & np.isin(dn_neighbor_count, list(DN_SURVIVE_SET))
    proposed[dn_survives] = GOL
    proposed[state == BB_FIRING] = BB_REFRACTORY
    proposed[state == BB_REFRACTORY] = OFF

    dn_birth_eligible = off_mask & np.isin(dn_neighbor_count, list(DN_BIRTH_SET))
    bb_ignition_eligible = off_mask & (bb_firing_neighbor_count == 2)
    both_eligible = dn_birth_eligible & bb_ignition_eligible
    only_dn = dn_birth_eligible & ~bb_ignition_eligible
    only_bb = bb_ignition_eligible & ~dn_birth_eligible
    coin = rng.random(state.shape) < 0.5
    proposed[only_dn] = GOL
    proposed[only_bb] = BB_FIRING
    proposed[both_eligible & coin] = GOL
    proposed[both_eligible & ~coin] = BB_FIRING

    capture_direction = np.zeros_like(state)
    dn_capture_eligible = dn_mask & (bb_pressure_neighbor_count >= K)
    proposed[dn_capture_eligible] = CAPTURED_DN_BECOMES
    capture_direction[dn_capture_eligible] = 1

    bb_capturable_mask = bb_firing_mask | bb_refractory_mask  # no mid-cycle protection (Stage 1 default)
    bb_capture_eligible = bb_capturable_mask & (dn_neighbor_count >= K)
    proposed[bb_capture_eligible] = GOL
    capture_direction[bb_capture_eligible] = -1

    return proposed, capture_direction


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, K, bb_cost_multiplier, ceiling):
    proposed, capture_direction = propose_next_with_capture(state, rng, K)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    is_bb_transition = (state == BB_FIRING) | (state == BB_REFRACTORY) | (proposed == BB_FIRING)
    cost_grid = np.where(is_bb_transition, bb_cost_multiplier * FLIP_COST, FLIP_COST)

    can_afford = energy >= cost_grid
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0

    state_next = np.where(actually_flips, proposed, state)

    normal_next = energy - cost_grid
    energy_next = np.where(actually_flips & capture_happened, 0.0,
                   np.where(actually_flips & ~capture_happened, normal_next, energy))
    energy_next = np.clip(energy_next, 0, ceiling)

    return state_next, energy_next


def run_condition(K, seed, bb_cost_multiplier, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    dynamic_ceiling = 10.0 * max(1.0, bb_cost_multiplier)
    min_warmup_for_alpha = int(3 * bb_cost_multiplier / D_BG)
    effective_warmup = max(warmup, min_warmup_for_alpha)

    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(effective_warmup):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, bb_cost_multiplier, dynamic_ceiling)
    for _ in range(window):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, bb_cost_multiplier, dynamic_ceiling)

    n_dn_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total = n_dn_final + n_bb_final
    dn_frac = n_dn_final / total if total > 0 else None
    return {'n_dn_final': n_dn_final, 'n_bb_final': n_bb_final, 'dn_territory_frac': dn_frac}


if __name__ == "__main__":
    print("=== Sanity check: alpha=1 should match Section 4.6's original K-sweep at D_bg=0.05 ===")
    for K, expect in [(1, "~0.97-1.0 (BB near/total extinction)"), (5, "~0.006 (D&N near extinct)"), (8, "~0.006")]:
        shares = [run_condition(K=K, seed=s, bb_cost_multiplier=1.0)['dn_territory_frac'] for s in range(10)]
        print(f"  K={K}, alpha=1: mean D&N share {np.mean(shares):.3f} (expect {expect})")

    print("\n=== Cost sweep: K=1,5,8 x alpha=1,20,200, 10 seeds each ===")
    for K in [1, 5, 8]:
        for alpha in [1, 20, 200]:
            shares = [run_condition(K=K, seed=s, bb_cost_multiplier=alpha)['dn_territory_frac'] for s in range(10)]
            print(f"  K={K}, alpha={alpha}: mean D&N share {np.mean(shares):.3f} (sd {np.std(shares):.3f})")

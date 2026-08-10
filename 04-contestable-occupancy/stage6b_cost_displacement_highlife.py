"""
CONTESTABLE OCCUPANCY, STAGE 6b: cost asymmetry under displacement,
extended to Game of Life vs. HighLife.

Section 4.6 charged Brian's Brain's entire existence at alpha x
FLIP_COST, because Brian's Brain has no cheap mode -- every one of its
transitions is mandatory. HighLife is structurally different: it
shares Game of Life's ordinary, cheap B3/S23 behavior (birth on 3,
survival on 2-3) and additionally has a B6 birth condition that
supports a genuine self-replicator (Section 4.4). There is no
"HighLife's entire existence" to price the way there was for Brian's
Brain -- the natural, surgical analog is to price specifically the
EXTRA machinery: births triggered by the B6 condition alone, leaving
ordinary B3 births, S23 survival, and captures at base cost.

This directly extends Section 4.4's disambiguation (expansion capacity
alone is not sufficient for Brian's-Brain-style dominance) with a cost
dimension: does pricing HighLife's self-replicator erode its already-
modest rough parity with Game of Life, the way pricing Brian's Brain's
entire existence did NOT erode its dominance (Section 4.2, 4.6)?

K values: 1, 3, 8 (near-parity throughout the whole range per Section
4.4/4.6, so representative points suffice rather than a dense sweep).
Alpha values: 1, 20, 200 (matching the flagship and D&N-vs-BB tests).
Seeds: 10 per condition (matching prior cost tests' first pass).
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

OFF, SPECIES_A, SPECIES_B = 0, 1, 2   # A = Game of Life, B = HighLife
A_BIRTH, A_SURVIVE = {3}, {2, 3}
B_SURVIVE = {2, 3}
B_BIRTH_ORDINARY = {3}       # shared with Game of Life -- cheap
B_BIRTH_B6 = {6}             # HighLife's extra self-replication condition -- priced


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next_with_capture(state, rng, K):
    a_mask = state == SPECIES_A
    b_mask = state == SPECIES_B
    off_mask = state == OFF

    a_neighbor_count = count_neighbors(a_mask.astype(int))
    b_neighbor_count = count_neighbors(b_mask.astype(int))

    proposed = np.full_like(state, OFF)

    a_survives = a_mask & np.isin(a_neighbor_count, list(A_SURVIVE))
    b_survives = b_mask & np.isin(b_neighbor_count, list(B_SURVIVE))
    proposed[a_survives] = SPECIES_A
    proposed[b_survives] = SPECIES_B

    a_birth_eligible = off_mask & np.isin(a_neighbor_count, list(A_BIRTH))
    b_birth_ordinary_eligible = off_mask & np.isin(b_neighbor_count, list(B_BIRTH_ORDINARY))
    b_birth_b6_eligible = off_mask & np.isin(b_neighbor_count, list(B_BIRTH_B6))
    b_birth_eligible = b_birth_ordinary_eligible | b_birth_b6_eligible

    both_eligible = a_birth_eligible & b_birth_eligible
    only_a = a_birth_eligible & ~b_birth_eligible
    only_b = b_birth_eligible & ~a_birth_eligible
    coin = rng.random(state.shape) < 0.5
    proposed[only_a] = SPECIES_A
    proposed[only_b] = SPECIES_B
    proposed[both_eligible & coin] = SPECIES_A
    proposed[both_eligible & ~coin] = SPECIES_B

    # which cells are proposed to become B specifically VIA the B6
    # condition (and not also eligible via the ordinary B3 condition,
    # which cannot co-occur since a cell has one neighbor count) --
    # used to mark the priced transition
    b6_triggered = (proposed == SPECIES_B) & b_birth_b6_eligible

    capture_direction = np.zeros_like(state)
    a_capture_eligible = a_mask & (b_neighbor_count >= K)
    proposed[a_capture_eligible] = SPECIES_B
    capture_direction[a_capture_eligible] = 1

    b_capture_eligible = b_mask & (a_neighbor_count >= K)
    proposed[b_capture_eligible] = SPECIES_A
    capture_direction[b_capture_eligible] = -1

    return proposed, capture_direction, b6_triggered


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, K, b6_cost_multiplier, ceiling):
    proposed, capture_direction, b6_triggered = propose_next_with_capture(state, rng, K)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    # Only B6-triggered births are priced at the multiplier; every other
    # transition (A survival/death/birth, B's ordinary B3 birth and
    # S23 survival, and BOTH capture directions) stays at base cost.
    cost_grid = np.where(b6_triggered, b6_cost_multiplier * FLIP_COST, FLIP_COST)

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


def run_condition(K, seed, b6_cost_multiplier, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    dynamic_ceiling = 10.0 * max(1.0, b6_cost_multiplier)
    min_warmup_for_alpha = int(3 * b6_cost_multiplier / D_BG)
    effective_warmup = max(warmup, min_warmup_for_alpha)

    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = SPECIES_A
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = SPECIES_B
    energy = np.zeros((N, N))

    for _ in range(effective_warmup):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, b6_cost_multiplier, dynamic_ceiling)
    for _ in range(window):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, b6_cost_multiplier, dynamic_ceiling)

    n_a_final = int((state == SPECIES_A).sum())
    n_b_final = int((state == SPECIES_B).sum())
    total = n_a_final + n_b_final
    a_frac = n_a_final / total if total > 0 else None
    return {'n_a_final': n_a_final, 'n_b_final': n_b_final, 'a_territory_frac': a_frac}


if __name__ == "__main__":
    print("=== Sanity check: b6_cost_multiplier=1 should match Section 4.6's original K-sweep ===")
    for K, expect in [(1, "~0.52"), (3, "~0.49-0.60"), (8, "~0.49-0.60")]:
        shares = [run_condition(K=K, seed=s, b6_cost_multiplier=1.0)['a_territory_frac'] for s in range(10)]
        print(f"  K={K}, alpha=1: mean GoL share {np.mean(shares):.3f} (expect {expect})")

    print("\n=== Cost sweep: K=1,3,8 x alpha=1,20,200, 10 seeds each ===")
    for K in [1, 3, 8]:
        for alpha in [1, 20, 200]:
            shares = [run_condition(K=K, seed=s, b6_cost_multiplier=alpha)['a_territory_frac'] for s in range(10)]
            print(f"  K={K}, alpha={alpha}: mean GoL share {np.mean(shares):.3f} (sd {np.std(shares):.3f})")

"""
Game of Life vs. HighLife under contestable occupancy: does the
absorbing-state disambiguation (see stage_gol_vs_highlife.py) hold once
occupied cells become directly capturable, not just inherited on vacancy?

The sticky-occupancy result found Game of Life and HighLife roughly
evenly matched (54.9% vs 45.1%, no extinctions) -- unlike Brian's
Brain's total dominance over both -- despite HighLife having a genuine
directional self-replicator that Brian's Brain-style expansion capacity
was hypothesized to explain. Since HighLife shares Game of Life's exact
absorbing states (S23 survival), this supported the absorbing-state
property, not raw expansion capacity, as the true driver of
Brian's-Brain-style dominance. This module checks whether that rough
parity is also robust to genuine boundary contestation, the same test
applied to the other three pairings in Section 4.6.

State encoding: 0=OFF, 1=SPECIES_A (Game of Life), 2=SPECIES_B (Day and Night).

MUTUALLY BLIND RULES: each species' survival/birth logic counts only
its own species' neighbors. Neither rule can see or react to the other
species' presence directly -- the only channel of interaction is
through the shared energy field (depletion and diffusion).

NO MID-STATE TAKEOVERS: a cell occupied by either species evaluates
only its own species' transition logic. A cell can only change species
by first dying back to OFF, then being recolonized on a later step.

CONTESTED OFF CELLS: an OFF cell simultaneously eligible for both a
species-A birth and a species-B birth is resolved by a neutral 50/50
coin flip -- not by relative neighbor count, since the two rules'
neighbor-count conventions are not on a comparable scale.

SYMMETRIC METABOLIC COST: both species pay FLIP_COST=1.0 for any state
change; staying in the same state costs nothing.
"""

import numpy as np
from collections import Counter
import math

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 100
INIT_DENSITY_EACH = 0.10  # each species starts at this density, randomly interspersed

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

OFF, SPECIES_A, SPECIES_B = 0, 1, 2
A_BIRTH, A_SURVIVE = {3}, {2, 3}                 # Game of Life
B_BIRTH, B_SURVIVE = {3, 6}, {2, 3}               # HighLife (Thompson, 1994)


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next(state, rng, a_birth=A_BIRTH, a_survive=A_SURVIVE, b_birth=B_BIRTH, b_survive=B_SURVIVE):
    """Two genuinely symmetric Life-like rules, both with ordinary
    birth/survive logic -- neither has Brian's Brain's mandatory
    transitions. Each species' survival and birth eligibility counts
    only its own species' neighbors (mutually blind); contested OFF
    cells (eligible for both species) are resolved by an unbiased coin
    flip, exactly as in the Game-of-Life-vs-Brian's-Brain harness."""
    a_mask = state == SPECIES_A
    b_mask = state == SPECIES_B
    off_mask = state == OFF

    a_neighbor_count = count_neighbors(a_mask.astype(int))
    b_neighbor_count = count_neighbors(b_mask.astype(int))

    proposed = np.full_like(state, OFF)

    a_survives = a_mask & np.isin(a_neighbor_count, list(a_survive))
    b_survives = b_mask & np.isin(b_neighbor_count, list(b_survive))
    proposed[a_survives] = SPECIES_A
    proposed[b_survives] = SPECIES_B
    # death (mask & ~survives) -> proposed stays OFF (default)

    a_birth_eligible = off_mask & np.isin(a_neighbor_count, list(a_birth))
    b_birth_eligible = off_mask & np.isin(b_neighbor_count, list(b_birth))

    both_eligible = a_birth_eligible & b_birth_eligible
    only_a = a_birth_eligible & ~b_birth_eligible
    only_b = b_birth_eligible & ~a_birth_eligible

    coin = rng.random(state.shape) < 0.5

    proposed[only_a] = SPECIES_A
    proposed[only_b] = SPECIES_B
    proposed[both_eligible & coin] = SPECIES_A
    proposed[both_eligible & ~coin] = SPECIES_B

    return proposed


def propose_next_with_capture(state, rng, K, a_birth=A_BIRTH, a_survive=A_SURVIVE, b_birth=B_BIRTH, b_survive=B_SURVIVE):
    """As propose_next, plus direct capture: an occupied cell of one
    species becomes eligible for capture by the other if it has >= K
    neighbors of the opposing species. Unlike the Brian's-Brain
    pairings, NEITHER species here has multiple occupied sub-states, so
    the birth-state and pressure-definition ambiguities that dominated
    those results are structurally absent -- a captured cell simply
    becomes the capturing species, with no other option, and pressure
    counting is simply the opposing species' neighbor count, with no
    ambiguity about which sub-state counts. Capture takes precedence
    over the victim's own survival, consistent with the Brian's-Brain
    pairings. Returns (proposed, capture_direction), where
    capture_direction is +1 for A->B captures, -1 for B->A captures."""
    a_mask = state == SPECIES_A
    b_mask = state == SPECIES_B
    off_mask = state == OFF

    a_neighbor_count = count_neighbors(a_mask.astype(int))
    b_neighbor_count = count_neighbors(b_mask.astype(int))

    proposed = np.full_like(state, OFF)

    a_survives = a_mask & np.isin(a_neighbor_count, list(a_survive))
    b_survives = b_mask & np.isin(b_neighbor_count, list(b_survive))
    proposed[a_survives] = SPECIES_A
    proposed[b_survives] = SPECIES_B

    a_birth_eligible = off_mask & np.isin(a_neighbor_count, list(a_birth))
    b_birth_eligible = off_mask & np.isin(b_neighbor_count, list(b_birth))
    both_eligible = a_birth_eligible & b_birth_eligible
    only_a = a_birth_eligible & ~b_birth_eligible
    only_b = b_birth_eligible & ~a_birth_eligible
    coin = rng.random(state.shape) < 0.5
    proposed[only_a] = SPECIES_A
    proposed[only_b] = SPECIES_B
    proposed[both_eligible & coin] = SPECIES_A
    proposed[both_eligible & ~coin] = SPECIES_B

    # --- NEW: direct capture, takes precedence over the victim's own survival ---
    capture_direction = np.zeros_like(state)

    a_capture_eligible = a_mask & (b_neighbor_count >= K)
    proposed[a_capture_eligible] = SPECIES_B
    capture_direction[a_capture_eligible] = 1

    b_capture_eligible = b_mask & (a_neighbor_count >= K)
    proposed[b_capture_eligible] = SPECIES_A
    capture_direction[b_capture_eligible] = -1

    return proposed, capture_direction


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, K, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING,
                          energy_on_capture_transfer=False):
    """Symmetric cost: both species pay the identical flip_cost for any
    transition (death, birth, capture). No mandatory transitions on
    either side -- both are ordinary Life-like rules, unlike the
    Brian's Brain pairings. Energy on capture is zeroed out (pinned
    choice, consistent with the other contestable-occupancy pairings),
    scoped ONLY to capture events, not to ordinary flips."""
    proposed, capture_direction = propose_next_with_capture(state, rng, K)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0

    state_next = np.where(actually_flips, proposed, state)

    normal_next = energy - flip_cost
    if energy_on_capture_transfer:
        energy_next = np.where(actually_flips, normal_next, energy)
    else:
        energy_next = np.where(actually_flips & capture_happened, 0.0,
                       np.where(actually_flips & ~capture_happened, normal_next, energy))
    energy_next = np.clip(energy_next, 0, ceiling)

    return state_next, energy_next, actually_flips, actual_capture_direction


def mutual_information_discrete(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    joint = Counter(zip(x.tolist(), y.tolist()))
    total = len(x)
    px = Counter(x.tolist())
    py = Counter(y.tolist())
    mi = 0.0
    for (xi, yi), count in joint.items():
        p_xy = count / total
        p_x = px[xi] / total
        p_y = py[yi] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return max(mi, 0.0)


def boundary_energy_gap(state, energy):
    """Mean energy of OFF cells adjacent to species A only, vs. OFF cells
    adjacent to species B only -- excludes OFF cells adjacent to both,
    for a clean, uncontaminated signal per species."""
    a_mask = (state == SPECIES_A).astype(int)
    b_mask = (state == SPECIES_B).astype(int)
    adj_a = count_neighbors(a_mask) > 0
    adj_b = count_neighbors(b_mask) > 0
    off_mask = state == OFF

    off_near_a_only = off_mask & adj_a & ~adj_b
    off_near_b_only = off_mask & adj_b & ~adj_a

    e_near_a = float(energy[off_near_a_only].mean()) if off_near_a_only.any() else None
    e_near_b = float(energy[off_near_b_only].mean()) if off_near_b_only.any() else None
    return e_near_a, e_near_b


def net_boundary_flux(state, energy, D_diff):
    """At OFF cells sitting between species A and species B territory
    (adjacent to both), compute average neighbor energy on each side to
    see which direction energy is moving at the contested boundary."""
    a_mask = (state == SPECIES_A).astype(int)
    b_mask = (state == SPECIES_B).astype(int)
    adj_a = count_neighbors(a_mask) > 0
    adj_b = count_neighbors(b_mask) > 0
    contested_off = (state == OFF) & adj_a & adj_b

    if not contested_off.any():
        return None

    a_energy_sum = np.zeros_like(energy)
    a_neighbor_n = np.zeros_like(energy)
    b_energy_sum = np.zeros_like(energy)
    b_neighbor_n = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        shifted_state = np.roll(np.roll(state, dr, axis=0), dc, axis=1)
        shifted_energy = np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
        is_a_neighbor = shifted_state == SPECIES_A
        is_b_neighbor = shifted_state == SPECIES_B
        a_energy_sum += np.where(is_a_neighbor, shifted_energy, 0.0)
        a_neighbor_n += is_a_neighbor.astype(float)
        b_energy_sum += np.where(is_b_neighbor, shifted_energy, 0.0)
        b_neighbor_n += is_b_neighbor.astype(float)

    valid = contested_off & (a_neighbor_n > 0) & (b_neighbor_n > 0)
    if not valid.any():
        return None
    avg_a_side = (a_energy_sum[valid] / a_neighbor_n[valid]).mean()
    avg_b_side = (b_energy_sum[valid] / b_neighbor_n[valid]).mean()
    # positive = energy flows from A's side toward B's side (A's side is higher)
    return float(avg_a_side - avg_b_side)


def run_condition(D_bg, D_diff, K, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = SPECIES_A
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = SPECIES_B
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy, _, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng, K)

    total_a_to_b, total_b_to_a = 0, 0
    for _ in range(window):
        state, energy, _, capture_direction = landauer_gated_step(state, energy, D_bg, D_diff, rng, K)
        total_a_to_b += int((capture_direction == 1).sum())
        total_b_to_a += int((capture_direction == -1).sum())

    n_a_final = int((state == SPECIES_A).sum())
    n_b_final = int((state == SPECIES_B).sum())
    total_occupied = n_a_final + n_b_final
    a_territory_frac = n_a_final / total_occupied if total_occupied > 0 else None
    b_territory_frac = n_b_final / total_occupied if total_occupied > 0 else None
    net_capture_flux = total_b_to_a - total_a_to_b  # positive = net advantage to A (GoL)

    return {
        'K': K, 'D_bg': D_bg, 'D_diff': D_diff,
        'n_a_final': n_a_final, 'n_b_final': n_b_final,
        'a_territory_frac': a_territory_frac, 'b_territory_frac': b_territory_frac,
        'captures_a_to_b': total_a_to_b, 'captures_b_to_a': total_b_to_a,
        'net_capture_flux': net_capture_flux,
    }


if __name__ == "__main__":
    print("Sanity check: Game of Life (A) vs HighLife (B), contestable occupancy\n")
    r = run_condition(D_bg=0.05, D_diff=0.05, K=3, seed=0, warmup=200, window=100)
    for k, v in r.items():
        print(f"  {k}: {v}")

"""
Game of Life vs. HighLife: the confound-breaking pairing.

Every prior competitive result involving Brian's Brain confounds two
properties at once: it has no absorbing state (Section 3.2's structural
criterion), AND it has genuine directional expansion capacity (mandatory
ignition into new territory). Sections 4.1-4.3 attribute its dominance
to "expansion capacity"; Section 5.2's unifying account attributes the
same result to "no absorbing state." These are quietly different
explanations for one outcome, and Brian's Brain cannot separate them,
because in Brian's Brain they are the same rule.

HighLife (B36/S23, Thompson 1994) is the missing cell in the 2x2 this
confound requires. It shares Game of Life's exact survival condition
(S23), so it admits every one of Life's absorbing states -- identical
still-lifes, oscillators, and gliders behave identically in both rules.
But its additional B6 birth condition supports a genuine, well-documented
self-replicator: a small pattern that copies itself indefinitely along
a diagonal line, expanding at a fixed rate -- a real directional
expansion capacity that plain Game of Life structurally lacks (no known
small self-replicator exists in B3/S23).

    absorbing state | expansion capacity | rule
    ----------------|---------------------|------------------
    yes             | low                 | Game of Life (have)
    no              | high                | Brian's Brain (have)
    yes             | high                | HighLife (THIS TEST)

If HighLife climbs the competitive hierarchy the way Brian's Brain did,
despite sharing Game of Life's absorbing states, then directional
expansion capacity -- not absorbing-state absence -- is the true driver
of competitive dominance, and Sections 4.1-4.3's "expansion capacity"
framing and Section 5.2's "absorbing state" framing describe two
genuinely separate mechanisms. If HighLife instead behaves like Game of
Life (no meaningful dominance), the absorbing-state property is the
real, sufficient driver, and the two framings collapse into one
invariant -- unifying Sections 3.2, 4, and 5.2 under a single
structural criterion, exactly as Section 5.2 already speculates.

State encoding: 0=OFF, 1=SPECIES_A (Game of Life), 2=SPECIES_B (HighLife).

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
    flip, exactly as in the Game-of-Life-vs-Brian's-Brain harness.

    Also returns b6_specific: OFF cells eligible for a species-B birth
    via the 6-neighbor condition specifically (B_BIRTH={3,6} for
    HighLife) -- a birth mechanism categorically impossible for Game of
    Life (A_BIRTH={3} only). Used to directly verify HighLife's
    replicator-enabling mechanism is actually active during
    competition, rather than assumed from the rule definition alone."""
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
    b6_specific = off_mask & (b_neighbor_count == 6)  # HighLife-only birth condition

    both_eligible = a_birth_eligible & b_birth_eligible
    only_a = a_birth_eligible & ~b_birth_eligible
    only_b = b_birth_eligible & ~a_birth_eligible

    coin = rng.random(state.shape) < 0.5

    proposed[only_a] = SPECIES_A
    proposed[only_b] = SPECIES_B
    proposed[both_eligible & coin] = SPECIES_A
    proposed[both_eligible & ~coin] = SPECIES_B

    return proposed, b6_specific


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    """Symmetric cost: both species pay the identical flip_cost for any
    transition (death, birth). No mandatory transitions on either side --
    both are ordinary Life-like rules, unlike the Brian's Brain pairings."""
    proposed, b6_specific = propose_next(state, rng)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford

    state_next = np.where(actually_flips, proposed, state)
    energy_next = np.where(actually_flips, energy - flip_cost, energy)
    energy_next = np.clip(energy_next, 0, ceiling)

    # executed B6-specific births: HighLife's replicator-enabling mechanism,
    # categorically impossible for Game of Life, actually realized this step
    b6_births_executed = int((b6_specific & (proposed == SPECIES_B) & actually_flips).sum())

    return state_next, energy_next, actually_flips, b6_births_executed


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


def run_condition(D_bg, D_diff, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=150):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = SPECIES_A
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = SPECIES_B
    energy = np.zeros((N, N))

    extinction_step = {'A': None, 'B': None}
    b6_births_warmup = 0
    b6_births_window = 0

    for step in range(warmup):
        state, energy, _, b6 = landauer_gated_step(state, energy, D_bg, D_diff, rng)
        b6_births_warmup += b6
        n_a = int((state == SPECIES_A).sum())
        n_b = int((state == SPECIES_B).sum())
        if n_a == 0 and extinction_step['A'] is None:
            extinction_step['A'] = step
        if n_b == 0 and extinction_step['B'] is None:
            extinction_step['B'] = step

    trajectory_b = np.zeros((window, N, N), dtype=int)
    for t in range(window):
        trajectory_b[t] = state == SPECIES_B
        state, energy, _, b6 = landauer_gated_step(state, energy, D_bg, D_diff, rng)
        b6_births_window += b6
        n_a = int((state == SPECIES_A).sum())
        n_b = int((state == SPECIES_B).sum())
        if n_a == 0 and extinction_step['A'] is None:
            extinction_step['A'] = warmup + t
        if n_b == 0 and extinction_step['B'] is None:
            extinction_step['B'] = warmup + t

    n_a_final = int((state == SPECIES_A).sum())
    n_b_final = int((state == SPECIES_B).sum())
    total_occupied = n_a_final + n_b_final
    a_territory_frac = n_a_final / total_occupied if total_occupied > 0 else None
    b_territory_frac = n_b_final / total_occupied if total_occupied > 0 else None

    e_near_a, e_near_b = boundary_energy_gap(state, energy)
    flux = net_boundary_flux(state, energy, D_diff)

    rng_mi = np.random.default_rng(seed + 50000)
    mis = []
    for _ in range(n_mi_pairs):
        r_, c_ = rng_mi.integers(0, N), rng_mi.integers(0, N)
        dr, dc = rng_mi.choice([-1, 0, 1]), rng_mi.choice([-1, 0, 1])
        if dr == 0 and dc == 0:
            continue
        r2, c2 = (r_ + dr) % N, (c_ + dc) % N
        x = trajectory_b[:-1, r_, c_]
        y = trajectory_b[1:, r2, c2]
        mis.append(mutual_information_discrete(x, y))
    b_coherence = float(np.mean(mis)) if mis else 0.0

    return {
        'D_bg': D_bg, 'D_diff': D_diff,
        'n_a_final': n_a_final, 'n_b_final': n_b_final,
        'a_territory_frac': a_territory_frac, 'b_territory_frac': b_territory_frac,
        'e_near_a': e_near_a, 'e_near_b': e_near_b,
        'net_boundary_flux': flux,
        'b_coherence': b_coherence,
        'a_extinct_step': extinction_step['A'], 'b_extinct_step': extinction_step['B'],
        'b6_births_warmup': b6_births_warmup, 'b6_births_window': b6_births_window,
    }


if __name__ == "__main__":
    print("Sanity check: Game of Life (A) vs HighLife (B)\n")
    r = run_condition(D_bg=0.05, D_diff=0.05, seed=0, warmup=200, window=100, n_mi_pairs=100)
    for k, v in r.items():
        print(f"  {k}: {v}")

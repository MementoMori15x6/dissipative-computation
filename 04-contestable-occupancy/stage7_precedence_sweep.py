"""
CONTESTABLE OCCUPANCY, STAGE 7: precedence-rule sweep.

Every displacement result reported so far (Sections 4.4, 4.6) pinned
one precedence rule: capture always overrides a cell's own survival
logic. This only matters for Game of Life cells, since Brian's Brain
has no "survival" option at all -- both of its states transition
unconditionally regardless of neighbors. A Game-of-Life cell can be
BOTH capture-eligible (>= K Brian's-Brain-pressure neighbors) AND
would-otherwise-survive (2 or 3 GOL neighbors) at the same time; the
pinned rule lets capture win unconditionally in that case.

This script tests the alternative proposed early in this project but
never swept: a coin-flip resolution whenever both conditions apply --
50% of the time the cell is captured as usual, the other 50% it
survives as Game of Life would have on its own, capture pressure
notwithstanding.

Tested on the flagship pairing (Game of Life vs. Brian's Brain) at the
same representative K values used for the cost-asymmetry test (K = 1,
3, 5, 8), 15 seeds each, using the Stage 1 module's pinned defaults
for every other design choice (aggressive capture birth-state, Firing-
only pressure, no mid-cycle protection).
"""

import numpy as np

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 100
INIT_DENSITY_EACH = 0.10
D_BG, D_DIFF = 0.05, 0.05

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

OFF, GOL, BB_FIRING, BB_REFRACTORY = 0, 1, 2, 3
CAPTURED_GOL_BECOMES = BB_FIRING   # Stage 1 pinned default (aggressive)
BB_PRESSURE_STATES = {BB_FIRING}   # Stage 1 pinned default


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next_with_capture(state, rng, K, precedence):
    """precedence: 'capture_wins' (Stage 1 default) or 'coinflip' (new
    alternative -- when a GoL cell is both capture-eligible and would
    otherwise survive on its own, resolve by an unbiased coin flip
    instead of letting capture win unconditionally)."""
    gol_mask = state == GOL
    bb_firing_mask = state == BB_FIRING
    bb_refractory_mask = state == BB_REFRACTORY
    bb_pressure_mask = np.isin(state, list(BB_PRESSURE_STATES))
    off_mask = state == OFF

    gol_neighbor_count = count_neighbors(gol_mask.astype(int))
    bb_firing_neighbor_count = count_neighbors(bb_firing_mask.astype(int))
    bb_pressure_neighbor_count = count_neighbors(bb_pressure_mask.astype(int))

    proposed = np.full_like(state, OFF)

    gol_survives = gol_mask & ((gol_neighbor_count == 2) | (gol_neighbor_count == 3))
    proposed[gol_survives] = GOL
    proposed[state == BB_FIRING] = BB_REFRACTORY
    proposed[state == BB_REFRACTORY] = OFF

    gol_birth_eligible = off_mask & (gol_neighbor_count == 3)
    bb_ignition_eligible = off_mask & (bb_firing_neighbor_count == 2)
    both_eligible = gol_birth_eligible & bb_ignition_eligible
    only_gol = gol_birth_eligible & ~bb_ignition_eligible
    only_bb = bb_ignition_eligible & ~gol_birth_eligible
    coin_off = rng.random(state.shape) < 0.5
    proposed[only_gol] = GOL
    proposed[only_bb] = BB_FIRING
    proposed[both_eligible & coin_off] = GOL
    proposed[both_eligible & ~coin_off] = BB_FIRING

    capture_direction = np.zeros_like(state)

    gol_capture_eligible = gol_mask & (bb_pressure_neighbor_count >= K)
    bb_capturable_mask = bb_firing_mask
    bb_capture_eligible = bb_capturable_mask & (gol_neighbor_count >= K)

    if precedence == "capture_wins":
        # Stage 1 default: capture unconditionally overrides survival
        # (later assignment wins regardless of gol_survives).
        proposed[gol_capture_eligible] = CAPTURED_GOL_BECOMES
        capture_direction[gol_capture_eligible] = 1
        proposed[bb_capture_eligible] = GOL
        capture_direction[bb_capture_eligible] = -1
    elif precedence == "coinflip":
        # New: where a GoL cell is BOTH capture-eligible AND would
        # otherwise survive, resolve by an unbiased coin flip instead
        # of letting capture win automatically. Capture-eligible cells
        # that would NOT otherwise survive are captured unconditionally
        # (no ambiguity to resolve -- the cell was dying anyway).
        contested_gol = gol_capture_eligible & gol_survives
        uncontested_gol_capture = gol_capture_eligible & ~gol_survives
        coin_precedence = rng.random(state.shape) < 0.5  # True = capture wins

        proposed[uncontested_gol_capture] = CAPTURED_GOL_BECOMES
        capture_direction[uncontested_gol_capture] = 1
        proposed[contested_gol & coin_precedence] = CAPTURED_GOL_BECOMES
        capture_direction[contested_gol & coin_precedence] = 1
        # contested_gol & ~coin_precedence: proposed already GOL from
        # gol_survives above -- no change needed, no capture recorded.

        # BB has no survival option, so no analogous ambiguity exists
        # on that side -- capture proceeds exactly as in capture_wins.
        proposed[bb_capture_eligible] = GOL
        capture_direction[bb_capture_eligible] = -1
    else:
        raise ValueError(precedence)

    return proposed, capture_direction


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, K, precedence):
    proposed, capture_direction = propose_next_with_capture(state, rng, K, precedence)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    can_afford = energy >= FLIP_COST
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0

    state_next = np.where(actually_flips, proposed, state)

    normal_next = energy - FLIP_COST
    energy_next = np.where(actually_flips & capture_happened, 0.0,
                   np.where(actually_flips & ~capture_happened, normal_next, energy))
    energy_next = np.clip(energy_next, 0, ENERGY_CEILING)

    return state_next, energy_next


def run_condition(K, seed, precedence, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, precedence)
    for _ in range(window):
        state, energy = landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K, precedence)

    n_gol_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total = n_gol_final + n_bb_final
    gol_frac = n_gol_final / total if total > 0 else None
    return {'n_gol_final': n_gol_final, 'n_bb_final': n_bb_final, 'gol_territory_frac': gol_frac}


if __name__ == "__main__":
    print("=== Sanity check: precedence='capture_wins' should match Stage 1's known results ===")
    for K, expect in [(1, "~0.54-0.60"), (5, "~0.21-0.23"), (8, "~0.22-0.25 (average over seeds)")]:
        shares = [run_condition(K=K, seed=s, precedence="capture_wins")['gol_territory_frac'] for s in range(15)]
        print(f"  K={K}: mean GoL share {np.mean(shares):.3f} (sd {np.std(shares):.3f}), expect {expect}")

    print("\n=== New: precedence='coinflip', K=1,3,5,8, 15 seeds each ===")
    for K in [1, 3, 5, 8]:
        shares_cw = [run_condition(K=K, seed=s, precedence="capture_wins")['gol_territory_frac'] for s in range(15)]
        shares_cf = [run_condition(K=K, seed=s, precedence="coinflip")['gol_territory_frac'] for s in range(15)]
        print(f"  K={K}: capture_wins mean {np.mean(shares_cw):.3f} (sd {np.std(shares_cw):.3f}) | "
              f"coinflip mean {np.mean(shares_cf):.3f} (sd {np.std(shares_cf):.3f})")

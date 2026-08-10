"""
CONTESTABLE OCCUPANCY, STAGE 1: mechanism build.

Every prior competition test (Section 4 of the manuscript) used "sticky
occupancy": an occupied cell can only be lost by first returning to the
unoccupied state through its OWN species' internal dynamics. Neither
rule can ever directly displace an occupied cell of the other species.
This means Brian's Brain's dominance over Game of Life may reflect
which rule generates and reclaims VACANCIES fastest, not which rule
wins a genuinely CONTESTED boundary -- a materially narrower claim than
the manuscript's Section 4 currently states, flagged as the paper's
most important open question (Section 5.1, 5.4).

This module adds direct capture: an occupied cell becomes eligible to
be captured by the opposing species if enough of its neighbors belong
to that species. This is layered ON TOP OF the existing vacancy-based
mechanism (contested OFF cells still resolve via the original
birth-eligibility + coin-flip logic, unchanged), not a replacement
for it.

EVERY DESIGN CHOICE BELOW IS AN EXPLICIT, NAMED PARAMETER, NOT AN
IMPLICIT DEFAULT -- following a two-round red-team of this design that
found several choices (particularly the capture birth-state and the
capture-pressure definition) are consequential enough to silently
determine the result if left implicit, exactly the failure mode
already caught twice elsewhere in this project (a fixed energy
ceiling, and a fixed warmup duration, both silently determining a
cost-sweep's outcome before being caught and corrected).

STAGE 1 PINNED CHOICES (documented here, some deferred to a Stage 3
sweep rather than fixed permanently):

  K (CAPTURE_THRESHOLD): number of foreign-species neighbors (Moore,
    out of 8) required for an occupied cell to become capture-eligible.
    SWEPT in Stage 3, not fixed here -- Stage 1 exposes it as a
    parameter and validates the mechanism at one representative value.

  BB_PRESSURE_STATES: which Brian's Brain states count toward capture
    pressure against Game of Life. Pinned for Stage 1 to {BB_FIRING}
    only (Refractory cells exert no capture pressure) -- this is the
    MORE CONSERVATIVE choice (harder for BB to muster K), explicitly
    flagged as a Stage 3 sweep dimension, not asserted as the "right"
    definition.

  BB_MID_CYCLE_PROTECTION: whether a BB_REFRACTORY cell can be
    captured at all. Pinned for Stage 1 to FALSE (BB fully vulnerable
    -- both Firing and Refractory cells are capturable) as the more
    dramatic first test; BB_MID_CYCLE_PROTECTION=True is the Stage 3
    alternative.

  CAPTURED_GOL_BECOMES: what a captured Game-of-Life cell turns into.
    Pinned for Stage 1 to BB_FIRING (the "aggressive" default -- every
    capture directly feeds Brian's Brain's expansion engine). Born-
    Refractory is the Stage 3 alternative, expected to be nearly
    self-defeating for BB by comparison. THIS CHOICE IS NOT A
    NON-QUESTION THE WAY IT IS FOR GOL: it is the single most
    consequential unlisted parameter identified in red-teaming.

  ENERGY_ON_CAPTURE_TRANSFER: whether a captured cell's PRIOR
    accumulated energy transfers to the new occupant. Pinned for
    Stage 1 to FALSE (zero-out on capture specifically, not on
    ordinary flips) -- the more conservative, less cascade-prone
    choice, applied only to the energy at cells where a capture
    actually occurred this step, not to every executed transition.

  RESOLUTION ORDER: not applicable. All capture eligibility is computed
    from the FULL grid state at the start of the step (fully vectorized,
    synchronous update, matching every other mechanism in this project)
    and applied simultaneously -- there is no sequential/raster-order
    dependence to introduce, since a cell already owned by one species
    can only be threatened by the OTHER species' neighbor count, never
    both directions at once.

PRIMARY METRIC: net directional capture flux (captures GOL->BB minus
captures BB->GOL, tracked as a distinct event type, separate from
vacancy-fill-based territory change) -- NOT aggregate occupancy share,
which confounds the new capture channel with the pre-existing vacancy
channel and cannot on its own distinguish which is doing the work.
Aggregate territory share is still reported, but explicitly as a
secondary, confounded quantity, for continuity with prior results only.

Density-at-capture (mean same-species neighbor count among cells at the
moment they are captured) is also tracked, to check for the K-density
confound identified in red-teaming: high K may re-protect dense Game-
of-Life configurations more than sparse Brian's-Brain fronts for
reasons of packing density alone, independent of any real difference
in "contestability."
"""

import numpy as np

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 100
INIT_DENSITY_EACH = 0.10

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

OFF, GOL, BB_FIRING, BB_REFRACTORY = 0, 1, 2, 3

# --- Stage 1 pinned parameters (see module docstring for justification) ---
BB_PRESSURE_STATES = {BB_FIRING}              # Refractory exerts no pressure (Stage 1 default)
BB_MID_CYCLE_PROTECTION = False               # BB fully vulnerable (Stage 1 default)
CAPTURED_GOL_BECOMES = BB_FIRING              # aggressive default (Stage 1 default)
ENERGY_ON_CAPTURE_TRANSFER = False            # zero-out on capture specifically (Stage 1 default)


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next_with_capture(state, rng, K, bb_pressure_states=BB_PRESSURE_STATES,
                                bb_mid_cycle_protection=BB_MID_CYCLE_PROTECTION,
                                captured_gol_becomes=CAPTURED_GOL_BECOMES):
    """Returns (proposed_state, capture_direction) where capture_direction
    is +1 for GOL->BB captures, -1 for BB->GOL captures, 0 elsewhere --
    used for flux tracking, kept separate from ordinary vacancy-based
    birth/death."""
    gol_mask = state == GOL
    bb_firing_mask = state == BB_FIRING
    bb_refractory_mask = state == BB_REFRACTORY
    bb_pressure_mask = np.isin(state, list(bb_pressure_states))
    off_mask = state == OFF

    gol_neighbor_count = count_neighbors(gol_mask.astype(int))
    bb_firing_neighbor_count = count_neighbors(bb_firing_mask.astype(int))
    bb_pressure_neighbor_count = count_neighbors(bb_pressure_mask.astype(int))
    gol_pressure_neighbor_count = gol_neighbor_count  # GOL has only one "occupied" state; no ambiguity

    proposed = np.full_like(state, OFF)

    # --- ordinary same-species survival (unchanged from prior mechanism) ---
    gol_survives = gol_mask & ((gol_neighbor_count == 2) | (gol_neighbor_count == 3))
    proposed[gol_survives] = GOL
    proposed[state == BB_FIRING] = BB_REFRACTORY   # mandatory
    proposed[state == BB_REFRACTORY] = OFF          # mandatory

    # --- ordinary vacancy-based birth/ignition (unchanged) ---
    gol_birth_eligible = off_mask & (gol_neighbor_count == 3)
    bb_ignition_eligible = off_mask & (bb_firing_neighbor_count == 2)
    both_eligible = gol_birth_eligible & bb_ignition_eligible
    only_gol = gol_birth_eligible & ~bb_ignition_eligible
    only_bb = bb_ignition_eligible & ~gol_birth_eligible
    coin = rng.random(state.shape) < 0.5
    proposed[only_gol] = GOL
    proposed[only_bb] = BB_FIRING
    proposed[both_eligible & coin] = GOL
    proposed[both_eligible & ~coin] = BB_FIRING

    # --- NEW: direct capture, takes precedence over the victim's own survival ---
    capture_direction = np.zeros_like(state)  # +1 = GOL captured by BB, -1 = BB captured by GOL

    # GOL cell captured by BB: requires >= K BB-pressure neighbors
    gol_capture_eligible = gol_mask & (bb_pressure_neighbor_count >= K)
    proposed[gol_capture_eligible] = captured_gol_becomes
    capture_direction[gol_capture_eligible] = 1

    # BB cell captured by GOL: requires >= K GOL neighbors; Refractory
    # cells are exempt if BB_MID_CYCLE_PROTECTION is True
    bb_capturable_mask = bb_firing_mask | (bb_refractory_mask & (not bb_mid_cycle_protection))
    bb_capture_eligible = bb_capturable_mask & (gol_pressure_neighbor_count >= K)
    proposed[bb_capture_eligible] = GOL
    capture_direction[bb_capture_eligible] = -1

    return proposed, capture_direction


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, K,
                          flip_cost=FLIP_COST, ceiling=ENERGY_CEILING,
                          energy_on_capture_transfer=ENERGY_ON_CAPTURE_TRANSFER):
    proposed, capture_direction = propose_next_with_capture(state, rng, K)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford
    actual_capture_direction = np.where(actually_flips, capture_direction, 0)
    capture_happened = actual_capture_direction != 0

    state_next = np.where(actually_flips, proposed, state)

    # Energy accounting: every executed flip pays flip_cost out of its
    # pre-flip energy (normal accounting). ENERGY_ON_CAPTURE_TRANSFER
    # additionally controls ONLY what happens to the remainder for
    # capture events specifically -- ordinary flips (deaths, births,
    # mandatory BB transitions) are never affected by this flag.
    normal_next = energy - flip_cost
    if energy_on_capture_transfer:
        energy_next = np.where(actually_flips, normal_next, energy)
    else:
        energy_next = np.where(actually_flips & capture_happened, 0.0,
                       np.where(actually_flips & ~capture_happened, normal_next, energy))

    energy_next = np.clip(energy_next, 0, ceiling)

    return state_next, energy_next, actually_flips, actual_capture_direction


def measure_density_at_capture(state, capture_direction):
    """Mean same-species neighbor count among cells captured this step
    (measured on the PRIOR state, before the capture was applied),
    split by direction, to check the K-density confound directly."""
    gol_mask = (state == GOL).astype(int)
    bb_mask = ((state == BB_FIRING) | (state == BB_REFRACTORY)).astype(int)
    gol_neighbor_count = count_neighbors(gol_mask)
    bb_neighbor_count = count_neighbors(bb_mask)

    captured_gol_by_bb = capture_direction == 1
    captured_bb_by_gol = capture_direction == -1

    density_gol_victim = float(gol_neighbor_count[captured_gol_by_bb].mean()) if captured_gol_by_bb.any() else None
    density_bb_victim = float(bb_neighbor_count[captured_bb_by_gol].mean()) if captured_bb_by_gol.any() else None
    return density_gol_victim, density_bb_victim


def run_condition(D_bg, D_diff, K, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy, _, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng, K)

    total_captures_gol_to_bb = 0
    total_captures_bb_to_gol = 0
    density_gol_samples, density_bb_samples = [], []

    for _ in range(window):
        prior_state = state.copy()
        state, energy, actually_flips, capture_direction = landauer_gated_step(state, energy, D_bg, D_diff, rng, K)
        total_captures_gol_to_bb += int((capture_direction == 1).sum())
        total_captures_bb_to_gol += int((capture_direction == -1).sum())
        dg, db = measure_density_at_capture(prior_state, capture_direction)
        if dg is not None:
            density_gol_samples.append(dg)
        if db is not None:
            density_bb_samples.append(db)

    n_gol_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total_occupied = n_gol_final + n_bb_final
    gol_territory_frac = n_gol_final / total_occupied if total_occupied > 0 else None
    bb_territory_frac = n_bb_final / total_occupied if total_occupied > 0 else None

    net_capture_flux = total_captures_bb_to_gol - total_captures_gol_to_bb  # positive = net advantage to GOL

    return {
        'K': K, 'D_bg': D_bg, 'D_diff': D_diff,
        'n_gol_final': n_gol_final, 'n_bb_final': n_bb_final,
        'gol_territory_frac': gol_territory_frac, 'bb_territory_frac': bb_territory_frac,
        'captures_gol_to_bb': total_captures_gol_to_bb,
        'captures_bb_to_gol': total_captures_bb_to_gol,
        'net_capture_flux': net_capture_flux,
        'mean_density_gol_victim': float(np.mean(density_gol_samples)) if density_gol_samples else None,
        'mean_density_bb_victim': float(np.mean(density_bb_samples)) if density_bb_samples else None,
    }


if __name__ == "__main__":
    print("Stage 1 pilot: mechanism validation only, NOT a finding about the dominance hierarchy.\n")
    r = run_condition(D_bg=0.05, D_diff=0.05, K=3, seed=0, warmup=200, window=100)
    for k, v in r.items():
        print(f"  {k}: {v}")

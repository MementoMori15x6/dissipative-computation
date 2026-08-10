"""
BRIAN'S BRAIN NEUTRAL-TAG CONTROL.

The Game-of-Life same-niche control found two distinct drift regimes:
fast-then-frozen (unconstrained execution, population crashes to a
small static remnant, reproduction stops, drift locks in place) and
slow-but-dynamic (energy-gated diffusion, population stays large and
active, drift continues without freezing). This tests whether that
distinction is general to the substrate, or specific to Game of Life's
capacity to settle into a static configuration at all.

Brian's Brain has NO such capacity by construction -- two of its three
states have no "stay the same" option, so a Firing or Refractory cell
is mechanically forced to attempt a transition every step for as long
as any population survives. The prediction this motivates: Brian's
Brain should show ONLY the slow-but-dynamic regime, in BOTH conditions
tested, since there is no absorbing configuration for it to freeze
into, unlike Game of Life's static blocks.

Tag mechanism: each cell carries an inert Red/Blue tag. Both tags
follow the identical Brian's Brain rule, counting ALL Firing neighbors
regardless of tag (mutually aware, since this is a genuine same-niche
test, unlike the mutually-blind competitive pairings). At each
ignition (the only "reproduction-equivalent" event -- an OFF cell
becoming Firing when it has exactly 2 Firing neighbors), the new
cell's tag is resolved by an unbiased proportional draw from its
Firing neighbors' tags.
"""

import numpy as np

N = 64
MAX_STEPS = 4000
SOUP_DENSITY = 0.25  # initial fraction set to Firing, rest Ready
KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

READY, FIRING, REFRACTORY = 0, 1, 2


def brians_brain_propose_with_tags(state, tag, rng):
    firing_mask = (state == FIRING).astype(int)
    firing_count = np.zeros_like(state)
    tag_sum = np.zeros_like(state, dtype=float)
    for dr, dc in KERNEL_OFFSETS:
        shifted_firing = np.roll(np.roll(firing_mask, dr, axis=0), dc, axis=1)
        shifted_tag = np.roll(np.roll(tag, dr, axis=0), dc, axis=1)
        firing_count += shifted_firing
        tag_sum += shifted_firing * shifted_tag

    proposed = np.zeros_like(state)
    ready_mask = state == READY
    proposed[ready_mask & (firing_count == 2)] = FIRING
    proposed[ready_mask & (firing_count != 2)] = READY
    proposed[state == FIRING] = REFRACTORY   # mandatory
    proposed[state == REFRACTORY] = READY    # mandatory

    new_tag = tag.copy()
    ignited = ready_mask & (firing_count == 2)
    if ignited.any():
        p_blue = tag_sum / np.maximum(firing_count, 1)
        draw = rng.random(state.shape)
        new_tag = np.where(ignited, (draw < p_blue).astype(float), tag)

    return proposed, new_tag


def local_segregation_index(state, tag):
    """Mean fraction of each active (Firing or Refractory) cell's active
    neighbors sharing its own tag."""
    active_rs, active_cs = np.where(state != READY)
    if len(active_rs) == 0:
        return None
    same_tag_fracs = []
    for r, c in zip(active_rs.tolist(), active_cs.tolist()):
        same, total = 0, 0
        for dr, dc in KERNEL_OFFSETS:
            rr, cc = (r + dr) % N, (c + dc) % N
            if state[rr, cc] != READY:
                total += 1
                if tag[rr, cc] == tag[r, c]:
                    same += 1
        if total > 0:
            same_tag_fracs.append(same / total)
    return float(np.mean(same_tag_fracs)) if same_tag_fracs else None


def run_baseline_trial(seed, max_steps=MAX_STEPS, record_interval=100):
    """Unconstrained execution -- no energy gating at all, matching the
    bare Brian's Brain CA rule."""
    rng = np.random.default_rng(seed)
    state = np.zeros((N, N), dtype=int)
    state[rng.random((N, N)) < SOUP_DENSITY] = FIRING
    tag = (rng.random((N, N)) < 0.5).astype(float)

    trace = []
    fixation_step = None
    for step in range(max_steps):
        active_mask = state != READY
        n_active = int(active_mask.sum())
        n_blue = int((active_mask & (tag == 1)).sum())
        if step % record_interval == 0:
            seg = local_segregation_index(state, tag)
            trace.append({'step': step, 'n_active': n_active,
                          'blue_frac': n_blue / n_active if n_active > 0 else None,
                          'segregation': seg})
        if n_active > 0 and fixation_step is None:
            if n_blue == 0 or n_blue == n_active:
                fixation_step = step
        if n_active == 0:
            break
        state, tag = brians_brain_propose_with_tags(state, tag, rng)

    return {'trace': trace, 'fixation_step': fixation_step}


def run_energy_gated_trial(seed, D_bg, D_diff, max_steps=MAX_STEPS, record_interval=100,
                             flip_cost=1.0, ceiling=10.0):
    rng = np.random.default_rng(seed)
    state = np.zeros((N, N), dtype=int)
    state[rng.random((N, N)) < SOUP_DENSITY] = FIRING
    tag = (rng.random((N, N)) < 0.5).astype(float)
    energy = np.zeros((N, N))

    trace = []
    fixation_step = None
    for step in range(max_steps):
        active_mask = state != READY
        n_active = int(active_mask.sum())
        n_blue = int((active_mask & (tag == 1)).sum())
        if step % record_interval == 0:
            seg = local_segregation_index(state, tag)
            trace.append({'step': step, 'n_active': n_active,
                          'blue_frac': n_blue / n_active if n_active > 0 else None,
                          'segregation': seg})
        if n_active > 0 and fixation_step is None:
            if n_blue == 0 or n_blue == n_active:
                fixation_step = step
        if n_active == 0:
            break

        proposed_state, proposed_tag = brians_brain_propose_with_tags(state, tag, rng)
        flip_mask = proposed_state != state

        energy = energy + D_bg
        neighbor_avg = np.zeros_like(energy)
        for dr, dc in ORTHOGONAL_OFFSETS:
            neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
        neighbor_avg /= 4.0
        energy = energy + D_diff * (neighbor_avg - energy)

        can_afford = energy >= flip_cost
        actually_flips = flip_mask & can_afford

        state = np.where(actually_flips, proposed_state, state)
        tag = np.where(actually_flips, proposed_tag, tag)
        energy = np.where(actually_flips, energy - flip_cost, energy)
        energy = np.clip(energy, 0, ceiling)

    return {'trace': trace, 'fixation_step': fixation_step}


if __name__ == "__main__":
    print("Sanity check: baseline (unconstrained BB) vs energy-gated (D_bg=0.05, D_diff=0.05)\n")
    r_base = run_baseline_trial(seed=0, max_steps=1000)
    print(f"Baseline: fixation_step={r_base['fixation_step']}, final={r_base['trace'][-1]}")
    r_energy = run_energy_gated_trial(seed=0, D_bg=0.05, D_diff=0.05, max_steps=1000)
    print(f"Energy-gated: fixation_step={r_energy['fixation_step']}, final={r_energy['trace'][-1]}")

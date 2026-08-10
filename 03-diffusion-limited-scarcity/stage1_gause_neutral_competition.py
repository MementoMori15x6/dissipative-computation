"""
GAUSE PRINCIPLE TEST: genuine same-niche competition.

Unlike the GoL-vs-Brian's-Brain test (different survival strategies,
mutually blind neighbor counting -- different niches by construction),
this tests Gause's actual claim: two competitors with IDENTICAL
strategy and IDENTICAL resource use, distinguished only by an arbitrary,
mechanistically meaningless tag (Red/Blue). Both tags follow the exact
same GoL survival/birth rule, counting ALL live neighbors regardless of
tag (mutually AWARE, not blind -- genuine same-niche competitors cannot
ignore each other). At each birth (exactly 3 live neighbors), the new
cell's tag is resolved by an unbiased proportional draw from its 3
parents' tags -- a neutral genetic-drift model, no fitness difference
between tags anywhere in the mechanism.

Two conditions:
  BASELINE -- plain GoL, no energy constraint at all (unconstrained
    execution, matching the "default expectation from drift theory"
    case: population is small and finite, so one tag should eventually
    fix, purely from drift). This is the necessary control, not the
    interesting result by itself.
  ENERGY-GATED -- the diffusive Landauer-gated substrate validated
    earlier in this section (background inflow D_bg + diffusion D_diff), at GoL's own
    calibrated threshold. Tests whether scarcity and diffusion-limited
    resource sharing change fixation dynamics relative to baseline --
    faster (smaller effective population, stronger drift) or slower
    (semi-isolated local pockets drifting independently, extending a
    spatial mosaic phase) are both plausible, competing predictions.

METRICS: time to fixation (one tag reaching 100% of the live
population), and a local segregation index (mean fraction of each live
cell's live neighbors sharing its own tag -- high = clustered/
segregated, low = well-mixed) tracked over time, to directly test for
an extended spatial mosaic phase rather than just the final outcome.
"""

import numpy as np

N = 64
MAX_STEPS = 4000
SOUP_DENSITY = 0.25
KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

GOL_BIRTH, GOL_SURVIVE = {3}, {2, 3}


def gol_propose_with_tags(life, tag, rng):
    """Standard GoL rule; births resolve tag via unbiased proportional
    draw from the 3 live parent neighbors' tags. Surviving cells keep
    their existing tag unchanged (no fitness effect anywhere)."""
    neighbor_count = np.zeros_like(life)
    tag_sum = np.zeros_like(life, dtype=float)  # sum of tags (0/1) among live neighbors
    for dr, dc in KERNEL_OFFSETS:
        shifted_life = np.roll(np.roll(life, dr, axis=0), dc, axis=1)
        shifted_tag = np.roll(np.roll(tag, dr, axis=0), dc, axis=1)
        neighbor_count += shifted_life
        tag_sum += shifted_life * shifted_tag

    proposed_life = np.zeros_like(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)
    proposed_life[survives] = 1
    proposed_life[born] = 1

    # tag resolution for births: proportional draw (tag_sum / 3 = fraction Blue among 3 parents)
    new_tag = tag.copy()
    if born.any():
        p_blue = tag_sum / np.maximum(neighbor_count, 1)  # fraction of live neighbors that are "Blue" (tag=1)
        draw = rng.random(life.shape)
        new_tag = np.where(born, (draw < p_blue).astype(float), tag)

    return proposed_life, new_tag


def local_segregation_index(life, tag):
    """Mean fraction of each live cell's live neighbors sharing its own
    tag. ~0.5 = well-mixed (random); higher = clustered/segregated."""
    live_rs, live_cs = np.where(life == 1)
    if len(live_rs) == 0:
        return None
    same_tag_fracs = []
    for r, c in zip(live_rs.tolist(), live_cs.tolist()):
        same, total = 0, 0
        for dr, dc in KERNEL_OFFSETS:
            rr, cc = (r + dr) % N, (c + dc) % N
            if life[rr, cc] == 1:
                total += 1
                if tag[rr, cc] == tag[r, c]:
                    same += 1
        if total > 0:
            same_tag_fracs.append(same / total)
    return float(np.mean(same_tag_fracs)) if same_tag_fracs else None


def run_baseline_trial(seed, max_steps=MAX_STEPS, record_interval=100):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    tag = (rng.random((N, N)) < 0.5).astype(float)  # 50/50 Red(0)/Blue(1) among initial live cells

    trace = []
    fixation_step = None
    for step in range(max_steps):
        live_mask = life == 1
        n_live = int(live_mask.sum())
        n_blue = int((live_mask & (tag == 1)).sum())
        if step % record_interval == 0:
            seg = local_segregation_index(life, tag)
            trace.append({'step': step, 'n_live': n_live, 'blue_frac': n_blue / n_live if n_live > 0 else None,
                          'segregation': seg})
        if n_live > 0 and fixation_step is None:
            if n_blue == 0 or n_blue == n_live:
                fixation_step = step
        if n_live == 0:
            break
        life, tag = gol_propose_with_tags(life, tag, rng)

    return {'trace': trace, 'fixation_step': fixation_step}


def run_energy_gated_trial(seed, D_bg, D_diff, max_steps=MAX_STEPS, record_interval=100,
                             flip_cost=1.0, ceiling=10.0):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    tag = (rng.random((N, N)) < 0.5).astype(float)
    energy = np.zeros((N, N))

    trace = []
    fixation_step = None
    for step in range(max_steps):
        live_mask = life == 1
        n_live = int(live_mask.sum())
        n_blue = int((live_mask & (tag == 1)).sum())
        if step % record_interval == 0:
            seg = local_segregation_index(life, tag)
            trace.append({'step': step, 'n_live': n_live, 'blue_frac': n_blue / n_live if n_live > 0 else None,
                          'segregation': seg})
        if n_live > 0 and fixation_step is None:
            if n_blue == 0 or n_blue == n_live:
                fixation_step = step
        if n_live == 0:
            break

        proposed_life, proposed_tag = gol_propose_with_tags(life, tag, rng)
        flip_mask = proposed_life != life

        energy = energy + D_bg
        # diffusion
        neighbor_avg = np.zeros_like(energy)
        for dr, dc in ORTHOGONAL_OFFSETS:
            neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
        neighbor_avg /= 4.0
        energy = energy + D_diff * (neighbor_avg - energy)

        can_afford = energy >= flip_cost
        actually_flips = flip_mask & can_afford

        life = np.where(actually_flips, proposed_life, life)
        tag = np.where(actually_flips, proposed_tag, tag)
        energy = np.where(actually_flips, energy - flip_cost, energy)
        energy = np.clip(energy, 0, ceiling)

    return {'trace': trace, 'fixation_step': fixation_step}


if __name__ == "__main__":
    print("Sanity check: baseline (plain GoL) vs energy-gated (D_bg=0.01, D_diff=0.03)\n")
    r_base = run_baseline_trial(seed=0, max_steps=1000)
    print(f"Baseline: fixation_step={r_base['fixation_step']}, final_trace_entry={r_base['trace'][-1]}")
    r_energy = run_energy_gated_trial(seed=0, D_bg=0.01, D_diff=0.03, max_steps=1000)
    print(f"Energy-gated: fixation_step={r_energy['fixation_step']}, final_trace_entry={r_energy['trace'][-1]}")

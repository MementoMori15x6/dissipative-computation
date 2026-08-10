"""
SURROGATE BIAS CHECK ON THE SECTION 3.2 EFFICIENCY RATIO (C / Phi)

WHY
---
Section 3.2 reports Brian's Brain's complexity-per-unit-flux as substantially
higher than the saturating rules', and defends the number against the known
plug-in mutual-information bias by arguing that the bias "inflates every rule's
numerator alike over the same window."

That defence is not safe as stated. The estimator is a plug-in over a joint
contingency table, and its finite-sample bias grows with the number of table
cells. In these single-rule experiments Brian's Brain carries a THREE-state
alphabet (0 = ready/off, 1 = firing, 2 = refractory) while Game of Life carries
TWO. That is nine joint cells versus four, at the same sample size -- so the
bias floor is LARGER for Brian's Brain, the rule reported as more efficient.
The confound points the same direction as the conclusion.

Sample size here is small enough for this to matter: WINDOW_STEPS = 75 gives
x = trajectory[:-1] and y = trajectory[1:], i.e. 74 paired samples per estimate.

METHOD
------
For each rule and each D, run the SAME condition the paper ran (same warmup,
window, and MI pair sampling, reusing each stage script's own functions so the
observed values reproduce exactly). For every sampled pair (x, y), also compute
a SURROGATE mutual information in which y is independently permuted in time.
Permutation destroys the temporal dependence while preserving each series'
marginal distribution and the sample size, so the surrogate's true MI is zero
and the plug-in estimate of it is precisely the bias floor for that rule's
alphabet and marginals at this N.

    C_observed   -- what the paper reports
    C_surrogate  -- estimated bias floor (mean over N_PERM permutations)
    C_corrected  -- max(C_observed - C_surrogate, 0)

The ratio is then recomputed with the corrected numerator. Phi is untouched:
realized flux is a direct count and carries no estimator bias.

This is a diagnostic, not a re-measurement. It does not replace any banked
number; it tests whether the qualitative contrast in Section 3.2 survives
removal of a per-rule bias floor.
"""

import numpy as np

import stage1_landauer_gate as gol
import stage3_brians_brain as bb

N_PERM = 20          # permutations per pair for the surrogate estimate
SEEDS = [0, 1, 2]    # the paper's sweeps are single-seed; average over a few here
D_VALUES = [0.3, 0.5, 0.7, 1.0]


def _pairs(module, trajectory, seed, n_mi_pairs=200):
    """Regenerate exactly the pair list the stage script would sample."""
    rng_mi = np.random.default_rng(seed + 50000)
    out = []
    for _ in range(n_mi_pairs):
        r, c = rng_mi.integers(0, module.N), rng_mi.integers(0, module.N)
        dr, dc = rng_mi.choice([-1, 0, 1]), rng_mi.choice([-1, 0, 1])
        if dr == 0 and dc == 0:
            continue
        r2, c2 = (r + dr) % module.N, (c + dc) % module.N
        out.append((trajectory[:-1, r, c], trajectory[1:, r2, c2]))
    return out


def _trajectory_gol(D, seed):
    rng = np.random.default_rng(seed)
    life = (rng.random((gol.N, gol.N)) < gol.SOUP_DENSITY).astype(int)
    energy = np.zeros((gol.N, gol.N))
    for _ in range(gol.WARMUP_STEPS):
        life, energy, _ = gol.landauer_gated_step(life, energy, D)
    traj = np.zeros((gol.WINDOW_STEPS, gol.N, gol.N), dtype=int)
    flips_total = 0
    for t in range(gol.WINDOW_STEPS):
        traj[t] = life
        life, energy, flips = gol.landauer_gated_step(life, energy, D)
        flips_total += int(flips.sum())
    phi = flips_total * gol.FLIP_COST / (gol.WINDOW_STEPS * gol.N * gol.N)
    return traj, phi


def _trajectory_bb(D, seed):
    rng = np.random.default_rng(seed)
    state = np.zeros((bb.N, bb.N), dtype=int)
    state[rng.random((bb.N, bb.N)) < bb.SOUP_DENSITY] = 1
    energy = np.zeros((bb.N, bb.N))
    for _ in range(bb.WARMUP_STEPS):
        state, energy, _ = bb.landauer_gated_step_bb(state, energy, D)
    traj = np.zeros((bb.WINDOW_STEPS, bb.N, bb.N), dtype=int)
    flips_total = 0
    for t in range(bb.WINDOW_STEPS):
        traj[t] = state
        state, energy, flips = bb.landauer_gated_step_bb(state, energy, D)
        flips_total += int(flips.sum())
    phi = flips_total * bb.FLIP_COST / (bb.WINDOW_STEPS * bb.N * bb.N)
    return traj, phi


def analyse(rule_name, D, seed):
    if rule_name == "GoL":
        traj, phi = _trajectory_gol(D, seed)
        module, mi_fn = gol, gol.mutual_information_binary
    else:
        traj, phi = _trajectory_bb(D, seed)
        module, mi_fn = bb, bb.mutual_information_discrete

    rng_perm = np.random.default_rng(seed + 99000)
    obs, sur = [], []
    n_states = set()
    for x, y in _pairs(module, traj, seed):
        n_states.update(np.unique(x).tolist())
        n_states.update(np.unique(y).tolist())
        obs.append(mi_fn(x, y))
        sur.append(np.mean([mi_fn(x, rng_perm.permutation(y)) for _ in range(N_PERM)]))

    c_obs = float(np.mean(obs)) if obs else 0.0
    c_sur = float(np.mean(sur)) if sur else 0.0
    c_cor = max(c_obs - c_sur, 0.0)
    return {
        "rule": rule_name, "D": D, "seed": seed, "phi": phi,
        "C_observed": c_obs, "C_surrogate": c_sur, "C_corrected": c_cor,
        "ratio_observed": (c_obs / phi) if phi > 0 else None,
        "ratio_corrected": (c_cor / phi) if phi > 0 else None,
        "alphabet_size_seen": len(n_states),
        "n_samples_per_pair": traj.shape[0] - 1,
    }


if __name__ == "__main__":
    print(f"Surrogate bias check | window={gol.WINDOW_STEPS} steps "
          f"({gol.WINDOW_STEPS - 1} paired samples), {N_PERM} permutations/pair\n")
    header = (f"{'rule':>5} {'D':>5} {'alpha':>6} {'phi':>8} {'C_obs':>8} "
              f"{'C_surr':>8} {'C_corr':>8} {'C/phi obs':>10} {'C/phi corr':>11}")
    print(header); print("-" * len(header))
    rows = []
    for rule in ["GoL", "BB"]:
        for D in D_VALUES:
            recs = [analyse(rule, D, s) for s in SEEDS]
            m = {k: float(np.mean([r[k] for r in recs]))
                 for k in ["phi", "C_observed", "C_surrogate", "C_corrected"]}
            ratio_o = m["C_observed"] / m["phi"] if m["phi"] > 0 else float("nan")
            ratio_c = m["C_corrected"] / m["phi"] if m["phi"] > 0 else float("nan")
            alpha = max(r["alphabet_size_seen"] for r in recs)
            print(f"{rule:>5} {D:>5} {alpha:>6} {m['phi']:>8.5f} {m['C_observed']:>8.5f} "
                  f"{m['C_surrogate']:>8.5f} {m['C_corrected']:>8.5f} "
                  f"{ratio_o:>10.3f} {ratio_c:>11.3f}")
            rows.append((rule, D, alpha, m, ratio_o, ratio_c))
    print()
    for rule in ["GoL", "BB"]:
        rs = [r for r in rows if r[0] == rule and r[3]["phi"] > 0]
        if rs:
            print(f"{rule}: C/phi observed {min(r[4] for r in rs):.3f}-{max(r[4] for r in rs):.3f}"
                  f" | corrected {min(r[5] for r in rs):.3f}-{max(r[5] for r in rs):.3f}"
                  f" | bias floor {min(r[3]['C_surrogate'] for r in rs):.5f}"
                  f"-{max(r[3]['C_surrogate'] for r in rs):.5f}")

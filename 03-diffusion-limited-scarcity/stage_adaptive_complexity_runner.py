"""
CONTESTABLE OCCUPANCY / DIFFUSION-LIMITED SCARCITY, AUDIT STAGE:
adaptive-stopping runner for Section 3.3's complexity metric C(D_diff),
Brian's Brain flagship re-sweep.

Full flatness (as used for population-count convergence elsewhere in
this audit) is impractically expensive for C, which is a slow-relaxing
kinetic variable (confirmed directly: D_diff=0.05 moved from C=0.082
at window=5,000 to C=0.049 at window=50,000, with a single window=50,000
seed taking ~44 seconds).

ADAPTIVE STOPPING RULE (per direction from this project's owner):
  - Evaluate C over successive 10,000-step blocks (after a 200-step
    warmup, matching the rest of this project's convention).
  - Stop once the relative change between consecutive block estimates
    is < 5%, OR a hard cap of 40,000 steps (4 blocks) is reached.
  - This is a pragmatic, explicitly-documented relaxation of full
    flatness -- appropriate because the O(1/N) finite-sample MI bias
    (the dominant, previously-undiagnosed error source) is already
    below ~0.001 by N=5,000-10,000; residual drift beyond that is
    genuine (much slower) dynamical relaxation, and a 5% tolerance
    preserves relative curve shape while bounding runtime.
"""

import sys
import time
import numpy as np

sys.path.insert(0, ".")
import stage1_diffusive_brians_brain as m

WARMUP = 200
BLOCK = 10000
REL_TOL = 0.05
MAX_BLOCKS = 4  # hard cap: 40,000 steps past warmup


def run_adaptive(D_bg, D_diff, seed, n_mi_pairs=100, warmup=WARMUP, block=BLOCK,
                  rel_tol=REL_TOL, max_blocks=MAX_BLOCKS):
    rng = np.random.default_rng(seed)
    state = np.zeros((m.N, m.N), dtype=int)
    state[rng.random((m.N, m.N)) < m.SOUP_DENSITY] = 1
    energy = np.zeros((m.N, m.N))
    for _ in range(warmup):
        state, energy, _ = m.landauer_gated_step_diffusive(state, energy, D_bg, D_diff)

    block_Cs = []
    total_steps = warmup
    for b in range(max_blocks):
        trajectory = np.zeros((block, m.N, m.N), dtype=int)
        for t in range(block):
            trajectory[t] = state
            state, energy, _ = m.landauer_gated_step_diffusive(state, energy, D_bg, D_diff)
        total_steps += block

        rng_mi = np.random.default_rng(seed + 50000 + b)
        mis = []
        for _ in range(n_mi_pairs):
            r, c = rng_mi.integers(0, m.N), rng_mi.integers(0, m.N)
            dr, dc = rng_mi.choice([-1, 0, 1]), rng_mi.choice([-1, 0, 1])
            if dr == 0 and dc == 0:
                continue
            r2, c2 = (r + dr) % m.N, (c + dc) % m.N
            x = trajectory[:-1, r, c]
            y = trajectory[1:, r2, c2]
            mis.append(m.mutual_information_discrete(x, y))
        c_block = float(np.mean(mis)) if mis else 0.0
        block_Cs.append(c_block)

        if len(block_Cs) >= 2:
            prev = block_Cs[-2]
            if prev > 0 and abs(c_block - prev) / prev < rel_tol:
                return {'C': c_block, 'blocks_used': b + 1, 'steps_taken': total_steps,
                        'converged': True, 'block_history': block_Cs}
            if prev == 0 and c_block == 0:
                return {'C': 0.0, 'blocks_used': b + 1, 'steps_taken': total_steps,
                        'converged': True, 'block_history': block_Cs}

    return {'C': block_Cs[-1], 'blocks_used': max_blocks, 'steps_taken': total_steps,
            'converged': False, 'block_history': block_Cs}


def sweep(D_bg, D_diff_values, n_seeds, verbose=True):
    results = {}
    for D_diff in D_diff_values:
        Cs = []
        not_converged = 0
        max_steps = 0
        for seed in range(n_seeds):
            r = run_adaptive(D_bg, D_diff, seed)
            Cs.append(r['C'])
            if not r['converged']:
                not_converged += 1
            max_steps = max(max_steps, r['steps_taken'])
        mean_C, sd_C = float(np.mean(Cs)), float(np.std(Cs))
        results[D_diff] = {'mean_C': mean_C, 'sd_C': sd_C, 'not_converged': not_converged, 'max_steps': max_steps}
        if verbose:
            print(f"D_diff={D_diff}: mean C={mean_C:.4f} (sd {sd_C:.4f}), "
                  f"not-converged {not_converged}/{n_seeds}, max steps {max_steps}")
    return results


if __name__ == "__main__":
    t = time.time()
    r = run_adaptive(D_bg=0.05, D_diff=0.05, seed=0)
    print(r, f"time={time.time()-t:.1f}s")

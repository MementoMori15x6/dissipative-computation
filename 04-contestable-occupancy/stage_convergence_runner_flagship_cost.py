"""
CONTESTABLE OCCUPANCY, AUDIT STAGE: convergence re-run of the FLAGSHIP
displacement-cost sweep (Game of Life vs. Brian's Brain).

This is the residual short-window gap identified in Section 5.4. The other two
displacement-cost pairings (stage6a = Day and Night vs. Brian's Brain, stage6b =
Game of Life vs. HighLife) were re-run by
stage_convergence_runner_displacement_cost.py; the flagship never was, and its
short-window figures were removed from Section 4.6 rather than reported.

WHY A SHIM RATHER THAN A DIRECT REUSE
-------------------------------------
stage_cost_displacement (the flagship module) does not present the same
interface as the stage6 modules, in three ways that would each fail silently or
loudly if the existing runner were pointed at it directly:

  1. its landauer_gated_step returns FOUR values
     (state, energy, actually_flips, actual_capture_direction),
     where the stage6 modules return two;
  2. it has no module-level D_BG / D_DIFF (the runner reads mod.D_BG);
  3. its signature is (..., bb_cost_multiplier, flip_cost, ceiling, ...), so the
     runner's eighth positional argument -- intended as the dynamic ceiling --
     would land on flip_cost instead, silently rescaling every cost in the run.

The shim below adapts the flagship module to the interface the existing runner
expects, and does nothing else. The convergence logic, tolerances, block
structure, alpha-scaling of warmup and check interval, and drift classification
are all inherited UNCHANGED from stage_convergence_runner_displacement_cost, so
the flagship result is directly comparable to the two pairings already re-run.

CONDITION
---------
D_bg = 0.05, D_diff = 0.05 -- the first calibration, matching the condition the
flagship pairing was characterized at throughout Sections 4.1-4.6.

GRID
----
K in {1, 5, 8} x alpha in {1, 20, 200}, matching STAGE6A/STAGE6B so the three
pairings can be compared cell for cell.
"""

import sys
import numpy as np

sys.path.insert(0, ".")

import stage_cost_displacement as flagship
import stage_convergence_runner_displacement_cost as runner

D_BG = 0.05
D_DIFF = 0.05


class FlagshipShim:
    """Presents stage_cost_displacement with the stage6 module interface."""

    N = flagship.N
    OFF = flagship.OFF
    INIT_DENSITY_EACH = flagship.INIT_DENSITY_EACH
    D_BG = D_BG
    D_DIFF = D_DIFF

    # species state sets, in the runner's (a_states, b_states) convention
    A_STATES = {flagship.GOL}                                    # Game of Life
    B_STATES = {flagship.BB_FIRING, flagship.BB_REFRACTORY}      # Brian's Brain

    @staticmethod
    def landauer_gated_step(state, energy, D_bg, D_diff, rng, K, cost_multiplier, ceiling):
        """Two-value adapter. ceiling passed by KEYWORD so it cannot land on
        flip_cost; the discarded third and fourth returns are per-step
        diagnostics the convergence runner does not use."""
        state_next, energy_next, _flips, _capture_dir = flagship.landauer_gated_step(
            state, energy, D_bg, D_diff, rng, K,
            bb_cost_multiplier=cost_multiplier, ceiling=ceiling)
        return state_next, energy_next


def run_cell(K, alpha, n_seeds):
    fracs, nconv, drifts, steps = [], 0, [], []
    for s in range(n_seeds):
        r = runner._run_module_to_convergence(
            FlagshipShim, K, s, alpha, FlagshipShim.A_STATES, FlagshipShim.B_STATES)
        if r['a_territory_frac'] is not None:
            fracs.append(r['a_territory_frac'])
        steps.append(r['steps_taken'])
        if not r['converged']:
            nconv += 1
            if r['drift'] is not None:
                drifts.append(r['drift'])
    return {
        'K': K, 'alpha': alpha, 'n_seeds': n_seeds,
        'mean_gol_share': float(np.mean(fracs)) if fracs else float('nan'),
        'sd': float(np.std(fracs)) if fracs else float('nan'),
        'n_converged': n_seeds - nconv,
        'unconverged': nconv,
        'mean_drift_if_unconverged': float(np.mean(drifts)) if drifts else None,
        'max_steps': int(max(steps)) if steps else 0,
    }


def sweep(K_values=(1, 5, 8), alpha_values=(1, 20, 200), n_seeds=10, verbose=True):
    if verbose:
        print("=== FLAGSHIP: Game of Life (A) vs Brian's Brain (B), "
              f"displacement-cost convergence re-run, D_bg={D_BG}, D_diff={D_DIFF} ===")
    out = {}
    for K in K_values:
        for alpha in alpha_values:
            r = run_cell(K, alpha, n_seeds)
            out[(K, alpha)] = r
            if verbose:
                d = (f", unconv {r['unconverged']}/{n_seeds} "
                     f"drift(mean {r['mean_drift_if_unconverged']:+.3f})") if r['unconverged'] else ""
                print(f"  K={K}, alpha={alpha}: mean GoL share {r['mean_gol_share']:.4f} "
                      f"(sd {r['sd']:.4f}), max steps {r['max_steps']}{d}", flush=True)
    return out


if __name__ == "__main__":
    import json
    res = sweep()
    json.dump({f"{k[0]}_{k[1]}": v for k, v in res.items()},
              open("flagship_cost_displacement_raw.json", "w"), indent=2)
    print("\nRaw results written to flagship_cost_displacement_raw.json")

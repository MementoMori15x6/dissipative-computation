"""
CONTESTABLE OCCUPANCY / DIFFUSION-LIMITED SCARCITY, AUDIT STAGE:
general-purpose convergence runner, for pairings where NEITHER species
necessarily freezes into an exactly-fixed population (unlike Game of
Life, which settles into still-lifes with a hard-frozen count -- Day
and Night has near-100% turnover among survivors even in its own
steady state (Section 3.3), so its population count can fluctuate the
same way Brian's Brain's does).

CONVERGENCE RULE:
  1. Terminal extinction: either species' count hits exactly 0 -> stop
     immediately (permanent, absorbing, per the same logic as the
     other convergence runners in this project).
  2. Trailing-average stability: track the MEAN of each species' count
     over each CHECK_INTERVAL-step block (not a single end-of-block
     snapshot). Once two consecutive block-means are within REL_TOL
     (relative) of each other for BOTH species, across FREEZE_CHECKS
     consecutive checks, treat the run as converged and report the
     mean over the last AVERAGING_BLOCKS blocks.
  3. Safety cap: MAX_CHECKS bounds worst-case runtime; flagged as NOT
     CONVERGED if reached without meeting the above.

This is a strictly more general version of the freeze-detection method
used in stage_convergence_runner.py (which is a special case where one
species' block-mean has essentially zero variance).
"""

import sys
import numpy as np


def make_runner(mechanism_module, species_a_states, species_b_states):
    """Returns a run_to_convergence function bound to the given
    mechanism module's landauer_gated_step/propose_next and state
    encoding. species_a_states / species_b_states are sets of state
    values (e.g. {GOL} or {BB_FIRING, BB_REFRACTORY})."""

    N = mechanism_module.N
    OFF = mechanism_module.OFF
    INIT_DENSITY_EACH = mechanism_module.INIT_DENSITY_EACH
    landauer_gated_step = mechanism_module.landauer_gated_step

    # first state in species_a_states is used as the initial-seed marker
    a_seed_state = sorted(species_a_states)[0]
    b_seed_state = sorted(species_b_states)[0]

    def _counts(state):
        n_a = int(np.isin(state, list(species_a_states)).sum())
        n_b = int(np.isin(state, list(species_b_states)).sum())
        return n_a, n_b

    def run_to_convergence(D_bg, D_diff, seed, bb_cost_multiplier=1.0,
                            warmup=200, check_interval_base=1000,
                            freeze_checks=3, averaging_blocks=3,
                            rel_tol=0.05, max_checks=40, **step_kwargs):
        dynamic_ceiling = 10.0 * max(1.0, bb_cost_multiplier)
        min_warmup_for_alpha = int(3 * bb_cost_multiplier / D_bg)
        effective_warmup = max(warmup, min_warmup_for_alpha)
        check_interval = max(check_interval_base, int(3 * bb_cost_multiplier / D_bg))

        rng = np.random.default_rng(seed)
        state = np.full((N, N), OFF, dtype=int)
        r = rng.random((N, N))
        state[r < INIT_DENSITY_EACH] = a_seed_state
        state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = b_seed_state
        energy = np.zeros((N, N))

        for _ in range(effective_warmup):
            state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng,
                                                      bb_cost_multiplier=bb_cost_multiplier,
                                                      ceiling=dynamic_ceiling, **step_kwargs)

        n_a, n_b = _counts(state)
        if n_a == 0 or n_b == 0:
            return _result(n_a, n_b, effective_warmup, True, True)

        steps_taken = effective_warmup
        block_means = []  # list of (mean_a, mean_b) per check_interval block
        stable_count = 0
        checks_done = 0

        while checks_done < max_checks:
            a_samples, b_samples = [], []
            for _ in range(check_interval):
                state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng,
                                                          bb_cost_multiplier=bb_cost_multiplier,
                                                          ceiling=dynamic_ceiling, **step_kwargs)
                n_a, n_b = _counts(state)
                a_samples.append(n_a)
                b_samples.append(n_b)
            steps_taken += check_interval
            checks_done += 1

            if n_a == 0 or n_b == 0:
                return _result(n_a, n_b, steps_taken, True, True)

            mean_a, mean_b = float(np.mean(a_samples)), float(np.mean(b_samples))
            block_means.append((mean_a, mean_b))

            if len(block_means) >= 2:
                prev_a, prev_b = block_means[-2]
                tol_a = max(1.0, rel_tol * prev_a)
                tol_b = max(1.0, rel_tol * prev_b)
                if abs(mean_a - prev_a) <= tol_a and abs(mean_b - prev_b) <= tol_b:
                    stable_count += 1
                else:
                    stable_count = 0
            if stable_count >= freeze_checks:
                recent = block_means[-averaging_blocks:]
                final_a = float(np.mean([x[0] for x in recent]))
                final_b = float(np.mean([x[1] for x in recent]))
                return _result(final_a, final_b, steps_taken, False, True,
                                a_sd=float(np.std([x[0] for x in recent])),
                                b_sd=float(np.std([x[1] for x in recent])))

        return _result(n_a, n_b, steps_taken, False, False)

    return run_to_convergence


def _result(n_a, n_b, steps_taken, terminal, converged, a_sd=None, b_sd=None):
    total = n_a + n_b
    frac = n_a / total if total > 0 else None
    return {
        'n_a_final': n_a, 'n_b_final': n_b,
        'a_territory_frac': frac,
        'steps_taken': steps_taken,
        'terminal_extinction': terminal,
        'converged': converged,
        'a_sd': a_sd, 'b_sd': b_sd,
    }


def sweep(run_fn, D_bg, D_diff, n_seeds, verbose=True, **kwargs):
    a_total = 0
    not_converged = []
    shares = []
    max_steps_seen = 0
    for seed in range(n_seeds):
        r = run_fn(D_bg, D_diff, seed, **kwargs)
        if not r['converged']:
            not_converged.append(seed)
        if r['n_b_final'] == 0:
            a_total += 1
        if r['a_territory_frac'] is not None:
            shares.append(r['a_territory_frac'])
        max_steps_seen = max(max_steps_seen, r['steps_taken'])
    mean_share = float(np.mean(shares)) if shares else None
    if verbose:
        print(f"D_bg={D_bg}, D_diff={D_diff}: species-A-total {a_total}/{n_seeds}, "
              f"mean A share {mean_share:.4f}, not-converged {len(not_converged)}/{n_seeds} "
              f"{not_converged if not_converged else ''}, max steps used {max_steps_seen}")
    return {'a_total': a_total, 'n_seeds': n_seeds, 'mean_a_share': mean_share,
            'not_converged_seeds': not_converged, 'max_steps_seen': max_steps_seen}

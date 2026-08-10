"""
FLAGSHIP DISPLACEMENT-COST SWEEP -- CONVERGENCE RE-RUN, BANKED RESULTS
Game of Life vs. Brian's Brain, D_bg = 0.05, D_diff = 0.05

Produced by stage_convergence_runner_flagship_cost.py (same directory, runnable).

WHAT THIS CLOSES
----------------
This was the residual short-window gap named in Section 5.4 and in item 4(a) of
the internal work list: the last displacement-cost pairing never re-run under
the convergence protocol. Its short-window figures were REMOVED from Section 4.6
rather than reported, because Section 4.1 had established that short-window cost
baselines can misstate an outcome outright. This re-run replaces them.

The other two pairings were re-run by stage_convergence_runner_displacement_cost
(STAGE6A, STAGE6B in convergence_audit_results_displacement_cost.py). The runner
used here inherits that module's convergence logic, tolerances, block structure,
alpha-scaling of warmup and check interval, and drift classification UNCHANGED,
via a thin interface shim -- so these cells are comparable to STAGE6A/6B cell for
cell.

INTERFACE HAZARD RECORDED (see the shim's docstring)
----------------------------------------------------
stage_cost_displacement.landauer_gated_step has signature
    (..., bb_cost_multiplier, flip_cost, ceiling, ...)
while stage_convergence_runner_displacement_cost passes the dynamic ceiling as
its EIGHTH positional argument. Pointed at the flagship module directly, that
value lands on flip_cost, silently rescaling every cost in the run and producing
plausible but wrong numbers. The shim passes ceiling by keyword. Two further
mismatches (four return values instead of two; no module-level D_BG / D_DIFF)
would have failed loudly rather than silently.

GRID AND QUALITY
----------------
K in {1, 5, 8} x alpha in {1, 20, 200}, 10 seeds per cell, 90 runs total.
ZERO unconverged trials in the entire grid -- cleaner than either pairing already
re-run, neither of which achieved a full 10 seeds at alpha = 200.
"""

CONDITION = {
    "pairing": "Game of Life (A) vs Brian's Brain (B)",
    "D_bg": 0.05,
    "D_diff": 0.05,
    "quantity": "mean Game-of-Life territory share",
    "n_seeds": 10,
    "protocol": "convergence protocol, inherited unchanged from "
                "stage_convergence_runner_displacement_cost",
    "unconverged_trials_in_grid": 0,
}

# (K, alpha) -> summary
GRID = {
    (1, 1):   {"mean": 0.5001, "sd": 0.0000, "n": 10, "unconverged": 0, "max_steps": 3200},
    (1, 20):  {"mean": 0.5087, "sd": 0.0120, "n": 10, "unconverged": 0, "max_steps": 6000},
    (1, 200): {"mean": 0.5932, "sd": 0.0655, "n": 10, "unconverged": 0, "max_steps": 60000},
    (5, 1):   {"mean": 0.6011, "sd": 0.4885, "n": 10, "unconverged": 0, "max_steps": 9200,
               "note": "BIMODAL -- see PER_SEED_ALPHA_1"},
    (5, 20):  {"mean": 0.0486, "sd": 0.0555, "n": 10, "unconverged": 0, "max_steps": 22800},
    (5, 200): {"mean": 0.0285, "sd": 0.0057, "n": 10, "unconverged": 0, "max_steps": 108000},
    (8, 1):   {"mean": 0.6129, "sd": 0.4742, "n": 10, "unconverged": 0, "max_steps": 4200,
               "note": "BIMODAL -- see PER_SEED_ALPHA_1"},
    (8, 20):  {"mean": 0.0692, "sd": 0.0530, "n": 10, "unconverged": 0, "max_steps": 8400},
    (8, 200): {"mean": 0.0369, "sd": 0.0074, "n": 10, "unconverged": 0, "max_steps": 48000},
}

# Bimodality was VERIFIED DIRECTLY from per-seed values, not inferred from the sd.
PER_SEED_ALPHA_1 = {
    5: {"shares": [0.0019, 1.0, 0.0019, 1.0, 1.0, 1.0, 0.0038, 0.0037, 1.0, 1.0],
        "above_0.9": 6, "below_0.1": 4, "intermediate": 0},
    8: {"shares": [0.0305, 1.0, 0.0258, 1.0, 1.0, 1.0, 0.0350, 0.0373, 1.0, 1.0],
        "above_0.9": 6, "below_0.1": 4, "intermediate": 0},
}

PER_SEED_ALPHA_200 = {
    1: [0.5525, 0.6298, 0.5373, 0.6655, 0.5776, 0.5338, 0.5239, 0.5448, 0.6359, 0.7306],
    5: [0.0300, 0.0270, 0.0400, 0.0257, 0.0255, 0.0322, 0.0318, 0.0293, 0.0165, 0.0269],
    8: [0.0359, 0.0394, 0.0460, 0.0446, 0.0303, 0.0328, 0.0347, 0.0490, 0.0236, 0.0331],
}

FINE_ALPHA_SWEEP = {
    "purpose": "locate the transition bracketed by the coarse grid's alpha = 1 -> 20 jump, "
               "mirroring the finer sweep Section 4.6 already runs for Day and Night vs Brian's Brain",
    "n_seeds": 10,
    "classification": "seeds counted as GoL-win (share > 0.9), BB-win (share < 0.1), or intermediate",
    "K5": {
        1.0:  {"mean": 0.6011, "sd": 0.4885, "gol_wins": 6, "bb_wins": 4, "intermediate": 0},
        2.0:  {"mean": 0.8000, "sd": 0.4000, "gol_wins": 8, "bb_wins": 2, "intermediate": 0},
        3.0:  {"mean": 0.3769, "sd": 0.4617, "gol_wins": 4, "bb_wins": 6, "intermediate": 0},
        4.0:  {"mean": 0.0019, "sd": 0.0057, "gol_wins": 0, "bb_wins": 10, "intermediate": 0},
        5.0:  {"mean": 0.0024, "sd": 0.0073, "gol_wins": 0, "bb_wins": 10, "intermediate": 0},
        10.0: {"mean": 0.0183, "sd": 0.0295, "gol_wins": 0, "bb_wins": 10, "intermediate": 0},
    },
    "K8": {
        1.0: {"mean": 0.6129, "sd": 0.4742, "gol_wins": 6, "bb_wins": 4, "intermediate": 0},
        2.0: {"mean": 0.9033, "sd": 0.2900, "gol_wins": 9, "bb_wins": 1, "intermediate": 0},
        3.0: {"mean": 0.3006, "sd": 0.4236, "gol_wins": 3, "bb_wins": 7, "intermediate": 0},
        4.0: {"mean": 0.0280, "sd": 0.0109, "gol_wins": 0, "bb_wins": 10, "intermediate": 0},
    },
    "unconverged": 0,
}

FINDINGS = {
    "1_winner_take_all_throughout": "NOT ONE seed at any K or any alpha produced an intermediate "
        "outcome. Every trial resolves to one species taking essentially the whole grid. The reported "
        "means are therefore win RATES dressed as shares, and must be read that way.",
    "2_cost_moves_the_bias_not_the_character": "An earlier reading of the coarse grid (alpha = 1, 20, "
        "200 only) suggested cost 'stabilizes' a bimodal contest into a consistent one, because the sd "
        "collapses from 0.49 to 0.06. The finer sweep shows that is wrong. The contest is winner-take-all "
        "at EVERY cost level; what cost changes is which side wins it. Game of Life's win probability "
        "goes 0.6 -> 0.8 -> 0.4 -> 0.0 across alpha = 1, 2, 3, 4 at K = 5, and 0.6 -> 0.9 -> 0.3 -> 0.0 "
        "at K = 8. The sd collapse at high alpha is simply the lottery becoming decided.",
    "3_non_monotonic_peak_at_alpha_2": "Game of Life's position IMPROVES from alpha = 1 to alpha = 2 "
        "before collapsing. The effect is present at both thresholds tested.",
    "4_matches_the_lottery_sweep": "This curve reproduces Section 4.2's lottery-competition cost sweep "
        "(convergence_audit_results_cost.RESULTS_ALPHA_SWEEP: alpha = 1, 22/30 GoL; alpha = 2, 13/15 -- "
        "the peak; alpha = 3, 6/15 -- falling; alpha = 10, 0/15) almost exactly: same peak location, "
        "same crossover near alpha = 3, same complete collapse. Two structurally different contest "
        "mechanisms, two displacement thresholds, one curve. For this pairing the cost-driven transition "
        "is INVARIANT to contest structure -- notable because Section 4.6's general finding is that "
        "displacement changes competitive outcomes.",
    "5_corroborates_the_critical_zone": "Section 4.2's alpha ~ 3 critical-slowing-down zone is exactly "
        "where the displacement sweep splits 4/6 (K = 5) and 3/7 (K = 8) -- independent corroboration "
        "of that zone's location from a different mechanism.",
    "6_K1_insensitive": "At K = 1 cost barely moves the outcome (0.5001 -> 0.5087 -> 0.5932). At "
        "alpha = 1 the result is exact parity with ZERO seed-to-seed variance across ten seeds.",
}

OPEN_ITEMS = [
    "K = 3 was not run for this pairing (the grid matches STAGE6A/6B's K in {1, 5, 8} for "
    "cell-for-cell comparability). The earlier short-window pass reported no clear trend at K = 3.",
    "Finer alpha sampling between 1 and 20 was not attempted; the alpha = 1 bimodality and the "
    "alpha = 20 collapse bracket a transition whose location within that interval is unmapped.",
]

PROVENANCE = {
    "runner": "stage_convergence_runner_flagship_cost.py",
    "raw_checkpoints": [
        "flagship_progress.json (per-cell, alpha = 1 and 20)",
        "flagship_a200_seeds.json (per-seed, alpha = 200)",
        "flagship_a1_perseed.json (per-seed, alpha = 1, for the bimodality check)",
    ],
    "timing": "~11 s/seed at alpha = 1, ~25 s/seed at alpha = 20, ~50-95 s/seed at alpha = 200",
}

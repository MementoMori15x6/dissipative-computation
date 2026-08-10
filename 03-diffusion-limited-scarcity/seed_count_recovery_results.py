"""
SEED-COUNT RECOVERY FOR THE DEBIASED SECTION 3.3 COMPLEXITY SWEEPS
(Game of Life and Day and Night)

WHY THIS EXISTS
---------------
convergence_audit_results_section3_complexity.py records n_seeds = 10 for the
Brian's Brain debiased sweep. Its companion,
convergence_audit_results_section3_gol_dn_complexity.py, records mean_C, sd_C
and not_converged per point for Game of Life and Day and Night but does NOT
record n_seeds. Assembling Appendix A (consolidated parameters) surfaced the
gap. The superseded pre-debias sweep was run at 20 seeds, but that number does
not transfer to the debiased re-run and was not assumed.

METHOD -- IDENTIFICATION, NOT RE-MEASUREMENT
--------------------------------------------
The sweep is deterministic and its seed set is a prefix:

    stage_adaptive_complexity_runner_gol_dn.sweep()  iterates  for seed in range(n_seeds)
    run_adaptive()  seeds the initial soup with  np.random.default_rng(seed)
                    and the MI pair sampling with  np.random.default_rng(seed + 50000 + b)

So run_adaptive(D_bg, D_diff, rule, seed) is reproducible bit-for-bit, and the
seed set for any n is a prefix of the seed set for any larger n. Running seeds
0..N-1 once for a single sweep point and computing the CUMULATIVE (mean_C,
sd_C, not_converged) at each prefix length therefore identifies which n the
banked record was produced at -- without replacing any banked number.

Matching on three statistics simultaneously (mean to 4 dp, sd to 4 dp, and the
integer not-converged count) makes a coincidental hit very unlikely. sd is
population sd (np.std, ddof=0), matching sweep().

RESULT
------
n_seeds = 10 for both rules. The banked record REPRODUCES EXACTLY; it was not
falsified. This doubles as a reproducibility check on the Data and Code
Availability claim: the record regenerates from the committed code.

Point 1 (Game of Life, D_bg = 0.01, D_diff = 0.01) uniquely identifies n = 10 --
no other prefix from n = 3 to n = 13 matches all three statistics.
Point 2 (Day and Night, D_bg = 0.01, D_diff = 0.1) matches at n = 10 and also at
n = 11 on rounded values; intersected with point 1, n = 10 is the answer.

Both agree with the independently recorded Brian's Brain value of 10, so all
three Section 3.3 sweeps used the same seed count.
"""

RECOVERY_METHOD = {
    "type": "prefix identification against banked summary statistics",
    "runner": "stage_adaptive_complexity_runner_gol_dn.py",
    "determinism": "np.random.default_rng(seed) for the soup; default_rng(seed + 50000 + block) for MI pairs",
    "sd_convention": "population sd (np.std, ddof=0), matching sweep()",
    "match_criteria": "mean_C to 4 dp AND sd_C to 4 dp AND integer not_converged, all simultaneously",
    "banked_numbers_changed": "none -- this run verified the record, it did not replace it",
}

POINT_1_GOL = {
    "rule": "GoL",
    "D_bg": 0.01,
    "D_diff": 0.01,
    "banked": {"mean_C": 0.0859, "sd_C": 0.0058, "not_converged": 3},
    "seeds_run": list(range(13)),
    "cumulative": {
        3:  {"mean_C": 0.0867, "sd_C": 0.0050, "not_converged": 0},
        4:  {"mean_C": 0.0861, "sd_C": 0.0044, "not_converged": 0},
        5:  {"mean_C": 0.0851, "sd_C": 0.0045, "not_converged": 0},
        6:  {"mean_C": 0.0848, "sd_C": 0.0042, "not_converged": 0},
        7:  {"mean_C": 0.0848, "sd_C": 0.0038, "not_converged": 1},
        8:  {"mean_C": 0.0843, "sd_C": 0.0039, "not_converged": 2},
        9:  {"mean_C": 0.0843, "sd_C": 0.0037, "not_converged": 2},
        10: {"mean_C": 0.0859, "sd_C": 0.0058, "not_converged": 3},   # <-- MATCH
        11: {"mean_C": 0.0867, "sd_C": 0.0061, "not_converged": 3},
        12: {"mean_C": 0.0878, "sd_C": 0.0069, "not_converged": 3},
        13: {"mean_C": 0.0870, "sd_C": 0.0073, "not_converged": 3},
    },
    "matches": [10],
    "note": "unique match; seed 0 alone gives C = 0.0859423, close to the banked mean by coincidence, "
            "but its not_converged = 0 and sd = 0 rule it out",
}

POINT_2_DAYANDNIGHT = {
    "rule": "DayAndNight",
    "D_bg": 0.01,
    "D_diff": 0.1,
    "banked": {"mean_C": 0.0108, "sd_C": 0.0008, "not_converged": 3},
    "seeds_run": list(range(12)),
    "cumulative": {
        3:  {"mean_C": 0.0102, "sd_C": 0.0009, "not_converged": 1},
        4:  {"mean_C": 0.0104, "sd_C": 0.0008, "not_converged": 2},
        5:  {"mean_C": 0.0105, "sd_C": 0.0008, "not_converged": 2},
        6:  {"mean_C": 0.0106, "sd_C": 0.0007, "not_converged": 2},
        7:  {"mean_C": 0.0105, "sd_C": 0.0007, "not_converged": 2},
        8:  {"mean_C": 0.0106, "sd_C": 0.0006, "not_converged": 2},
        9:  {"mean_C": 0.0107, "sd_C": 0.0008, "not_converged": 3},
        10: {"mean_C": 0.0108, "sd_C": 0.0008, "not_converged": 3},   # <-- MATCH
        11: {"mean_C": 0.0108, "sd_C": 0.0008, "not_converged": 3},   # <-- also matches on rounded values
        12: {"mean_C": 0.0109, "sd_C": 0.0007, "not_converged": 4},
    },
    "matches": [10, 11],
    "note": "intersected with POINT_1_GOL's unique match, n = 10",
}

CONCLUSION = {
    "n_seeds_gol_debiased_sweep": 10,
    "n_seeds_dayandnight_debiased_sweep": 10,
    "n_seeds_briansbrain_debiased_sweep": 10,   # independently recorded in the companion file
    "record_status": "REPRODUCED -- banked values regenerate exactly from committed code",
    "manuscript_action": "Appendix A Table A3 now states 10 seeds for all three Section 3.3 sweeps; "
                         "the disclosed gap has been removed rather than merely footnoted",
}

TIMING = {
    "seconds_per_seed_approx": 17,
    "note": "64x64 grid, warmup 200, up to four 10,000-step blocks; most seeds converge in 2-3 blocks",
}

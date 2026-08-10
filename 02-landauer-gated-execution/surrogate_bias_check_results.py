"""
SURROGATE BIAS CHECK ON THE SECTION 3.2 EFFICIENCY RATIO -- BANKED RESULTS

Produced by stage4_surrogate_bias_check.py (same directory, runnable).

WHAT PROMPTED IT
----------------
Section 3.2 originally defended its C/Phi values against the known plug-in
mutual-information bias by asserting that the bias "inflates every rule's
numerator alike over the same window." That assertion is false. The plug-in
estimator's finite-sample bias grows with the number of joint contingency-table
cells, and in the single-rule experiments Brian's Brain carries a three-state
alphabet (0 ready/off, 1 firing, 2 refractory) against Game of Life's two --
nine joint cells versus four, at the same 74 paired samples (WINDOW_STEPS = 75).
The bias is therefore LARGER for the rule reported as more efficient: a confound
pointing the same direction as the conclusion.

METHOD
------
For each sampled neighbouring pair (x, y), recompute the estimate with y
independently permuted in time. Permutation preserves both marginals and the
sample size while setting the true mutual information to zero, so the plug-in
estimate on the surrogate IS the bias floor for that rule's alphabet and
marginals at this N. 20 permutations per pair; 200 pairs per condition, sampled
with the same RNG stream the stage scripts use, so observed values reproduce the
stage scripts exactly. Phi is untouched -- realized flux is a direct count and
carries no estimator bias.

RESULT
------
The predicted asymmetry is confirmed: Brian's Brain's bias floor is roughly 2.7x
Game of Life's, tracking alphabet size. The qualitative conclusion nonetheless
SURVIVES the correction -- Brian's Brain remains two to four times more efficient
after each rule's own floor is subtracted. Section 3.2's defence sentence was
replaced with this measured account rather than the (incorrect) equal-bias claim.

Note on convention: the stage scripts are single-seed (seed = 0). Single-seed
values reproduce the range Section 3.2 reports (C/Phi about 0.85-1.9 for Brian's
Brain); the three-seed averages below are smoother and narrower. Both are given.
"""

METHOD = {
    "surrogate": "independent temporal permutation of y; preserves marginals and N, true MI = 0",
    "permutations_per_pair": 20,
    "pairs_per_condition": 200,
    "window_steps": 75,
    "paired_samples_per_estimate": 74,
    "phi_treatment": "untouched -- direct flip count, no estimator bias",
    "banked_numbers_changed": "none -- diagnostic only; Section 3.2's prose was corrected, not its values",
}

# Three-seed means (seeds 0, 1, 2).
THREE_SEED_MEAN = {
    "GoL": [
        {"D": 0.30, "alphabet": 2, "phi": 0.05112, "C_obs": 0.01742, "C_surr": 0.00402, "C_corr": 0.01340, "ratio_obs": 0.341, "ratio_corr": 0.262},
        {"D": 0.35, "alphabet": 2, "phi": 0.05703, "C_obs": 0.02613, "C_surr": 0.00432, "C_corr": 0.02180, "ratio_obs": 0.458, "ratio_corr": 0.382},
        {"D": 0.40, "alphabet": 2, "phi": 0.06548, "C_obs": 0.02276, "C_surr": 0.00486, "C_corr": 0.01791, "ratio_obs": 0.348, "ratio_corr": 0.273},
        {"D": 0.50, "alphabet": 2, "phi": 0.04211, "C_obs": 0.01650, "C_surr": 0.00312, "C_corr": 0.01338, "ratio_obs": 0.392, "ratio_corr": 0.318},
        {"D": 0.70, "alphabet": 2, "phi": 0.04977, "C_obs": 0.02335, "C_surr": 0.00367, "C_corr": 0.01968, "ratio_obs": 0.469, "ratio_corr": 0.395},
        {"D": 1.00, "alphabet": 2, "phi": 0.05092, "C_obs": 0.01892, "C_surr": 0.00379, "C_corr": 0.01513, "ratio_obs": 0.372, "ratio_corr": 0.297},
    ],
    "BB": [
        {"D": 0.30, "alphabet": 1, "phi": 0.0, "C_obs": 0.0, "C_surr": 0.0, "C_corr": 0.0, "ratio_obs": None, "ratio_corr": None, "note": "extinct at this D in all three seeds"},
        {"D": 0.32, "alphabet": 1, "phi": 0.0, "C_obs": 0.0, "C_surr": 0.0, "C_corr": 0.0, "ratio_obs": None, "ratio_corr": None, "note": "extinct"},
        {"D": 0.35, "alphabet": 1, "phi": 0.0, "C_obs": 0.0, "C_surr": 0.0, "C_corr": 0.0, "ratio_obs": None, "ratio_corr": None, "note": "extinct"},
        {"D": 0.40, "alphabet": 3, "phi": 0.04703, "C_obs": 0.04081, "C_surr": 0.00824, "C_corr": 0.03257, "ratio_obs": 0.868, "ratio_corr": 0.693},
        {"D": 0.45, "alphabet": 3, "phi": 0.06387, "C_obs": 0.05804, "C_surr": 0.01011, "C_corr": 0.04793, "ratio_obs": 0.909, "ratio_corr": 0.750},
        {"D": 0.50, "alphabet": 3, "phi": 0.06007, "C_obs": 0.06952, "C_surr": 0.01090, "C_corr": 0.05863, "ratio_obs": 1.157, "ratio_corr": 0.976},
        {"D": 0.70, "alphabet": 3, "phi": 0.06448, "C_obs": 0.06431, "C_surr": 0.01093, "C_corr": 0.05338, "ratio_obs": 0.997, "ratio_corr": 0.828},
        {"D": 1.00, "alphabet": 3, "phi": 0.05628, "C_obs": 0.04834, "C_surr": 0.00905, "C_corr": 0.03929, "ratio_obs": 0.859, "ratio_corr": 0.698},
    ],
}

# Single seed (seed = 0), matching the stage scripts' own convention.
SINGLE_SEED_BB = [
    {"D": 0.40, "phi": 0.12227, "C_obs": 0.09217, "C_surr": 0.02222, "C_corr": 0.06995, "ratio_obs": 0.754, "ratio_corr": 0.572},
    {"D": 0.50, "phi": 0.06396, "C_obs": 0.06236, "C_surr": 0.01144, "C_corr": 0.05092, "ratio_obs": 0.975, "ratio_corr": 0.796},
    {"D": 0.60, "phi": 0.03735, "C_obs": 0.06958, "C_surr": 0.00600, "C_corr": 0.06359, "ratio_obs": 1.863, "ratio_corr": 1.703},
    {"D": 0.80, "phi": 0.09497, "C_obs": 0.08271, "C_surr": 0.01683, "C_corr": 0.06589, "ratio_obs": 0.871, "ratio_corr": 0.694},
    {"D": 1.00, "phi": 0.01165, "C_obs": 0.01527, "C_surr": 0.00204, "C_corr": 0.01323, "ratio_obs": 1.311, "ratio_corr": 1.136},
]

CONCLUSION = {
    "bias_floor_GoL": "0.0031-0.0049 (two-state alphabet, four joint cells)",
    "bias_floor_BB": "0.0082-0.0222 (three-state alphabet, nine joint cells)",
    "asymmetry": "roughly 2.7x larger for Brian's Brain at three-seed means; the direction predicted "
                 "from alphabet size, and unfavourable to the reported comparison",
    "equal_bias_claim": "FALSIFIED -- Section 3.2's original defence sentence was wrong",
    "qualitative_contrast": "SURVIVES -- after subtracting each rule's own floor, Brian's Brain retains "
                            "roughly 0.6-1.7 against Game of Life's 0.26-0.40, a factor of two to four",
    "reported_range_reproduces": "single-seed C/Phi for Brian's Brain spans 0.75-1.86, consistent with the "
                                 "0.85-1.9 stated in Section 3.2",
    "manuscript_action": "Section 3.2's equal-bias sentence replaced with the measured per-rule floors and "
                         "the corrected ratios; values not changed",
    "residual_caveat": "the single-seed spread (0.75 to 1.86 across D) is wide, so the reported range partly "
                       "reflects seed and D sampling rather than a systematic trend in efficiency",
}

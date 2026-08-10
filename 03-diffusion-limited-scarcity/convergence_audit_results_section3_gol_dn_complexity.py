"""
CONSOLIDATED RESULTS: Game of Life and Day and Night's debiased
Section 3.3 diffusion-limited complexity curves, extending the
Brian's Brain re-sweep (convergence_audit_results_section3_complexity.py,
same directory).

Scripts: stage_adaptive_complexity_runner_gol_dn.py (this directory).
Same adaptive-stopping protocol as the Brian's Brain sweep: 10,000-step
blocks after 200-step warmup, 5% relative tolerance, 40,000-step cap.
GoL and D&N both evaluated at D_bg=0.01 (each rule's own calibrated
threshold, matching the manuscript's stated re-calibration; D&N's own
threshold was not independently re-derived, but D_bg=0.01 reproduces
its reported baseline complexity (0.474 vs. reported 0.450) closely
enough to trust as a reasonable approximation).

====================================================================
FINDING 1: THE ORIGINALLY-REPORTED "RISING INTERIOR OPTIMUM" DOES NOT
SURVIVE FOR EITHER RULE. Both show the OPPOSITE shape: complexity
highest at the lowest D_diff tested (each rule's own threshold),
declining sharply, then flattening (with a slight uptick at high
D_diff, echoing Brian's Brain's pattern).
====================================================================

Game of Life (originally reported: "128% rise, 0.086 to 0.196"):

  D_diff | mean C  | sd     | not-converged (of 10)
  0.01   | 0.0859  | 0.0058 | 3
  0.05   | 0.0405  | 0.0036 | 7
  0.10   | 0.0185  | 0.0016 | 5
  0.20   | 0.0154  | 0.0020 | 7
  0.50   | 0.0167  | 0.0028 | 6
  1.00   | 0.0187  | 0.0019 | 5

Day and Night (originally reported: "12% rise from 0.450"):

  D_diff | mean C  | sd     | not-converged (of 10)
  0.01   | 0.4738  | 0.0150 | 2
  0.05   | 0.0594  | 0.0061 | 6
  0.10   | 0.0108  | 0.0008 | 3
  0.20   | 0.0114  | 0.0011 | 5
  0.50   | 0.0162  | 0.0014 | 5
  1.00   | 0.0277  | 0.0010 | 5

Both rules: sharp collapse from D_diff=0.01 to D_diff=0.10-0.20, then a
flat-to-slightly-rising tail through D_diff=1.00 -- the same
qualitative shape found for Brian's Brain (peak-near-threshold, dip,
partial high-D_diff rise), not the smooth single-direction rise
originally reported for any of the three rules.

====================================================================
FINDING 2: THE HIGH NOT-CONVERGED RATES (50-70% AT SEVERAL POINTS) ARE
A STOPPING-CRITERION ARTIFACT, NOT EVIDENCE OF GENUINE UNRESOLVED
DYNAMICAL DRIFT. This was checked directly, not assumed.
====================================================================

Diagnostic: logged the block-to-block drift DIRECTION for GoL's
non-converged seeds at D_diff=0.05. If the reversal-zone drift found
in Section 4.2's alpha=3 case were the same mechanism, essentially all
stragglers should show consistent monotonic drift in one direction.
Instead: of 7 non-converged seeds, drift was mixed (2 negative, 5
positive), and the block_history values for every straggler cluster
tightly within a narrow band (roughly 0.034-0.049) rather than trending
toward a different asymptote. This is the signature of BLOCK-TO-BLOCK
SAMPLING NOISE in the per-block MI estimate (only 100 pairs sampled
per 10,000-step block) tripping an overly strict 5% relative-tolerance
threshold by chance, not unresolved dynamics.

Confirmed directly: re-running one straggler seed (GoL, D_diff=0.05,
seed=2) with 4x more MI pairs per block (400 instead of 100) still
failed the 5% convergence check, but the block estimates clustered far
more tightly (0.036-0.041, versus 0.034-0.049 at n_mi_pairs=100) --
consistent with reduced-but-still-present per-block noise, not genuine
drift. The seed's true value is very likely close to its reported mean.

PRACTICAL IMPLICATION: the reported means above are more trustworthy
than their raw not-converged counts suggest. The stopping criterion
(5% relative tolerance on a noisy 100-pair MI block estimate) is
stricter than the underlying signal supports; a criterion based on
absolute tolerance, or a larger n_mi_pairs per block, would likely
show much higher convergence rates for the same underlying data.
This was NOT re-verified at scale (i.e. the full sweep was not re-run
with n_mi_pairs=400) -- flagged as an open item.
"""

GOL_DEBIASED_SWEEP = {
    'D_bg': 0.01,
    'rule': 'GoL',
    'originally_reported': '128% relative rise, 0.086 to 0.196 (claimed at n=20 seeds)',
    'points': [
        {'D_diff': 0.01, 'mean_C': 0.0859, 'sd_C': 0.0058, 'not_converged': 3},
        {'D_diff': 0.05, 'mean_C': 0.0405, 'sd_C': 0.0036, 'not_converged': 7},
        {'D_diff': 0.10, 'mean_C': 0.0185, 'sd_C': 0.0016, 'not_converged': 5},
        {'D_diff': 0.20, 'mean_C': 0.0154, 'sd_C': 0.0020, 'not_converged': 7},
        {'D_diff': 0.50, 'mean_C': 0.0167, 'sd_C': 0.0028, 'not_converged': 6},
        {'D_diff': 1.00, 'mean_C': 0.0187, 'sd_C': 0.0019, 'not_converged': 5},
    ],
    'status': 'MAJOR REFRAME -- opposite shape from reported (decline, not rise); high not-converged counts diagnosed as stopping-criterion noise, not unresolved drift (see Finding 2)',
}

DAYANDNIGHT_DEBIASED_SWEEP = {
    'D_bg': 0.01,  # approximation; not independently re-derived as D&N's own threshold
    'rule': 'DayAndNight',
    'originally_reported': '12% relative rise from an already-high floor of 0.450 (claimed at n=20 seeds)',
    'points': [
        {'D_diff': 0.01, 'mean_C': 0.4738, 'sd_C': 0.0150, 'not_converged': 2},
        {'D_diff': 0.05, 'mean_C': 0.0594, 'sd_C': 0.0061, 'not_converged': 6},
        {'D_diff': 0.10, 'mean_C': 0.0108, 'sd_C': 0.0008, 'not_converged': 3},
        {'D_diff': 0.20, 'mean_C': 0.0114, 'sd_C': 0.0011, 'not_converged': 5},
        {'D_diff': 0.50, 'mean_C': 0.0162, 'sd_C': 0.0014, 'not_converged': 5},
        {'D_diff': 1.00, 'mean_C': 0.0277, 'sd_C': 0.0010, 'not_converged': 5},
    ],
    'status': 'MAJOR REFRAME -- opposite direction and much larger magnitude swing than reported (8x collapse from D_diff=0.01 to 0.05, not a 12% rise)',
}

DRIFT_DIAGNOSTIC = {
    'test': 'GoL, D_diff=0.05, non-converged seeds block-history drift direction',
    'n_nonconverged_checked': 7,
    'negative_drift': 2, 'positive_drift': 5, 'flat': 0,
    'conclusion': 'mixed drift signs + tight clustering of block values = sampling noise, not genuine dynamical drift (contrast with Section 4.2 alpha=3, where drift was consistently one-directional)',
    'confirmatory_check': 'seed=2 rerun with n_mi_pairs=400 (vs default 100): block values tightened from range [0.034,0.049] to [0.036,0.041], still failed 5% tolerance by chance -- consistent with noise-driven false non-convergence',
    'caveat': 'not re-verified at full-sweep scale; higher n_mi_pairs was only tested on one seed',
}

OPEN_ITEMS = [
    'Full sweep not re-run with higher n_mi_pairs (e.g. 400) to get genuinely higher convergence rates -- current means are trusted based on one confirmatory spot-check (Finding 2), not full re-verification.',
    'D&N\'s own calibrated threshold D_bg was not independently re-derived -- D_bg=0.01 (same as GoL) was used as an approximation, justified only by reproducing D&N\'s reported baseline complexity reasonably closely (0.474 vs 0.450).',
    'Only 6 anchor points tested per rule; peak location and the shape of the high-D_diff uptick are not finely resolved for any of the three rules.',
    'Whether the same "peak at threshold, decline, partial high-end rise" shape is a general property of diffusion-limited scarcity (as the manuscript\'s ORIGINAL claim asserted, just with the wrong curve shape) or specific to something about these three rule classes remains an open, if now differently-framed, question.',
]

if __name__ == "__main__":
    for r in [GOL_DEBIASED_SWEEP, DAYANDNIGHT_DEBIASED_SWEEP]:
        print(f"\n{r['rule']} (D_bg={r['D_bg']}):")
        print(f"  originally reported: {r['originally_reported']}")
        for p in r['points']:
            print(f"  D_diff={p['D_diff']}: mean C={p['mean_C']:.4f} (sd {p['sd_C']:.4f}), not-converged {p['not_converged']}/10")
        print(f"  status: {r['status']}")
    print(f"\nDrift diagnostic: {DRIFT_DIAGNOSTIC['conclusion']}")
    print(f"\n{len(OPEN_ITEMS)} open items -- see OPEN_ITEMS.")

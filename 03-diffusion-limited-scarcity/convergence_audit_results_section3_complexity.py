"""
CONSOLIDATED RESULTS: Section 3.3's diffusion-limited interior
complexity optimum, re-measured after discovering a severe finite-
sample mutual-information estimator bias in the standard 75-100 step
measurement window used throughout Sections 3.1-4.6.

This is a DATA RECORD, not a script to re-derive the numbers from
scratch. Scripts: stage_adaptive_complexity_runner.py (this directory)
for the debiased sweep; stage1_diffusive_brians_brain.py for the
underlying mechanism.

====================================================================
PART 1: THE MI ESTIMATOR BIAS FINDING (affects Sections 3.1-3.3 at
minimum; Section 4's reported numbers are population-count-based and
NOT affected -- confirmed by direct check of manuscript text).
====================================================================

Control test: mutual_information_discrete() applied to PURE
INDEPENDENT RANDOM NOISE (true MI = 0 by construction, 3-symbol
alphabet, matching the CA state encoding):

  window=75:    measured MI = 0.080  (should be 0)
  window=500:   measured MI = 0.003
  window=5000:  measured MI = 0.0006
  window=40000: measured MI = 0.0000

This confirms a severe O(1/N) positive bias at the standard window
(N=75-100) used throughout the paper -- large enough, on its own, to
produce apparent "complexity" readings comparable to some previously-
reported real values.

Miller-Madow analytical bias correction was tested as a possible
retroactive fix and found NOT adequate for this data:
  - On pure synthetic noise: recovered ~50% of the bias at N=75,
    ~100% by N=500+.
  - On ACTUAL Brian's Brain trajectory data: recovered only ~2% of
    the bias at N=75 (raw C=0.6267 -> MM-corrected C=0.6137, vs. the
    true long-window value of ~0.03-0.06). The real data's joint
    distribution is far more skewed/sparse than uniform noise, so the
    standard correction formula (which depends on observed joint-
    symbol diversity) badly underestimates the true empirical bias.

CONCLUSION: no analytical shortcut exists. Historical short-window
numbers cannot be retroactively corrected (raw trajectories were not
archived); only genuine long-window remeasurement is trustworthy.

====================================================================
PART 2: DEBIASED RE-SWEEP, BRIAN'S BRAIN, D_bg=0.05 (its own
calibrated threshold), Section 3.3's flagship rule.
====================================================================

METHOD: adaptive stopping (not fixed window) -- 10,000-step blocks
after a 200-step warmup, stopping when consecutive block estimates
differ by <5% relative, hard cap 40,000 steps. This was a deliberate,
explicit relaxation of full-flatness convergence (used elsewhere in
this audit for population counts), justified because C is a much
slower-relaxing kinetic variable than population size -- confirmed
directly: a single D_diff=0.05 trajectory moved from C=0.082 (N=5,000)
to C=0.056 (N=20,000) to C=0.049 (N=50,000), with the N=50,000 run
alone taking ~44 seconds -- and because the O(1/N) bias itself is
already below ~0.001 by N=5,000-10,000, so residual drift beyond that
is genuine slow dynamics, not estimator artifact.

RESULT (10 seeds per point):

  D_diff | mean C  | sd     | not-converged (of 10)
  0.01   | 0.0000  | 0.0000 | 0
  0.05   | 0.0630  | 0.0018 | 3
  0.10   | 0.0173  | 0.0011 | 5
  0.20   | 0.0056  | 0.0004 | 2
  0.50   | 0.0100  | 0.0005 | 1
  1.00   | 0.0175  | 0.0010 | 0

FINDING: the originally-reported curve (smooth single peak at
D_diff=0.10-0.12, magnitude 0.63, declining smoothly to 0.22 by
D_diff=1.0) does NOT hold. The debiased picture:
  - A real, reproducible peak exists, but at roughly 1/10th the
    reported magnitude (0.063, not 0.63) and located at D_diff~0.05
    (near the extinction threshold), not 0.10-0.12.
  - The curve is NOT monotonically declining after the peak: it drops
    through D_diff=0.10-0.20, then RISES again from 0.20 through 1.00
    (0.006 -> 0.010 -> 0.018) -- a feature not previously reported at
    all, plausibly masked in the original analysis by the bias
    inflating mid-range points relative to it.

CAVEATS (stated plainly, not smoothed over):
  - D_diff=0.05 and D_diff=0.10 -- the two most important points for
    locating the peak -- still show 30-50% of seeds not meeting the
    5% adaptive-stopping criterion within the 40,000-step cap. The
    reported means are a solid first pass, not a fully resolved final
    answer; tighter convergence (higher step cap, or more seeds to
    average out residual per-seed drift) would sharpen this.
  - Only 6 anchor points were tested; the exact peak location (is it
    at 0.05, or between 0.03-0.07?) and the shape of the high-D_diff
    rise are not finely resolved.
  - The proposed mechanistic explanations for WHY the curve has this
    shape -- e.g. "criticality at the activation edge" for the low-
    D_diff peak, "fast-mixing spatiotemporal recurrences" for the
    high-D_diff rise -- are PLAUSIBLE NARRATIVE, NOT VERIFIED
    MECHANISM. No test has been run to distinguish these from other
    possible explanations (e.g. finite-size effects, a genuinely
    different relaxation timescale at each regime, or residual
    estimator bias not yet fully eliminated at these seed counts).
    These should not be stated as established mechanism in the
    manuscript without further work.
  - Game of Life and Day and Night (the other two rules in Section
    3.3's original claim) have NOT been re-swept at all. Whether
    their reported peaks (128% relative rise for GoL, 12% for D&N)
    survive the same debiasing is completely unknown.
"""

MI_BIAS_CONTROL = {
    'pure_noise_mi_by_window': {75: 0.080, 500: 0.003, 5000: 0.0006, 40000: 0.0000},
    'true_value': 0.0,
    'miller_madow_recovery_on_pure_noise_at_n75': 'approx 50%',
    'miller_madow_recovery_on_real_bb_data_at_n75': 'approx 2% -- NOT adequate',
    'conclusion': 'no analytical shortcut; long-window remeasurement required',
}

BRIANS_BRAIN_DEBIASED_SWEEP = {
    'D_bg': 0.05,
    'method': 'adaptive stopping, 10000-step blocks, 5% relative tolerance, 40000-step cap',
    'n_seeds': 10,
    'points': [
        {'D_diff': 0.01, 'mean_C': 0.0000, 'sd_C': 0.0000, 'not_converged': 0},
        {'D_diff': 0.05, 'mean_C': 0.0630, 'sd_C': 0.0018, 'not_converged': 3},
        {'D_diff': 0.10, 'mean_C': 0.0173, 'sd_C': 0.0011, 'not_converged': 5},
        {'D_diff': 0.20, 'mean_C': 0.0056, 'sd_C': 0.0004, 'not_converged': 2},
        {'D_diff': 0.50, 'mean_C': 0.0100, 'sd_C': 0.0005, 'not_converged': 1},
        {'D_diff': 1.00, 'mean_C': 0.0175, 'sd_C': 0.0010, 'not_converged': 0},
    ],
    'originally_reported': '0.31 at threshold, peak 0.63 at D_diff=0.10-0.12, smooth decline to 0.22 by D_diff=1.0',
    'status': 'PARTIALLY CONFIRMED, MAJOR REFRAME NEEDED -- peak is real but ~10x smaller and at a different location; curve shape is not a simple single peak (unreported rise at high D_diff); GoL and D&N not yet checked',
}

OPEN_ITEMS = [
    'GoL and Day & Night debiased sweeps not started -- whether their reported interior peaks survive is unknown.',
    'D_diff=0.05 and 0.10 have high not-converged rates (30-50%) -- these specific points would benefit from a higher step cap or more seeds before being treated as final.',
    'Peak location only bracketed to within [0.01, 0.10] -- intermediate points (0.03, 0.07) not tested.',
    'High-D_diff rise (0.20 to 1.00) only has 3 points -- shape between and beyond these is unknown (e.g. does it keep rising past D_diff=1.0?).',
    'Mechanistic explanations for the curve shape are speculative narrative, not verified -- flagged explicitly above, should not be stated as established fact in the manuscript.',
]

if __name__ == "__main__":
    print("MI estimator bias (control test):")
    for w, v in MI_BIAS_CONTROL['pure_noise_mi_by_window'].items():
        print(f"  window={w}: measured MI on pure noise = {v} (true = 0)")
    print(f"\nBrian's Brain debiased C(D_diff) sweep, D_bg={BRIANS_BRAIN_DEBIASED_SWEEP['D_bg']}:")
    for p in BRIANS_BRAIN_DEBIASED_SWEEP['points']:
        print(f"  D_diff={p['D_diff']}: mean C={p['mean_C']:.4f} (sd {p['sd_C']:.4f}), "
              f"not-converged {p['not_converged']}/{BRIANS_BRAIN_DEBIASED_SWEEP['n_seeds']}")
    print(f"\nStatus: {BRIANS_BRAIN_DEBIASED_SWEEP['status']}")
    print(f"\n{len(OPEN_ITEMS)} open items -- see OPEN_ITEMS.")

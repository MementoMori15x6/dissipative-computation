"""
CONSOLIDATED RESULTS: convergence-based re-measurement of three
additional lottery-only baselines from Sections 4.3 and 4.4, extending
the audit begun with the flagship GoL-vs-BB pairing (see
03-diffusion-limited-scarcity/convergence_audit_results.py and
convergence_audit_results_cost.py).

This is a DATA RECORD, not a script to re-derive the numbers from
scratch. Scripts used: stage_convergence_runner_general.py +
stage4_dayandnight_vs_briansbrain.py (D&N vs BB), 03-diffusion-limited-
scarcity/stage_convergence_runner_gol_dn.py (GoL vs D&N), and
04-contestable-occupancy/stage_convergence_runner_highlife.py (GoL vs
HighLife, this directory).

SUMMARY OF FINDINGS:

1. Day and Night vs. Brian's Brain (Section 4.3, second pairing):
   CONFIRMED CLEAN. Convergence-checked result matches the originally
   reported figure closely -- no correction needed.
     - D&N extinct: 8/30 (27%), vs. originally reported 5/15 (33%)
     - mean D&N share (survivors): ~0.003-0.004, consistent with the
       reported 0.35%
     - Cost-insensitivity claim (alpha=1 to alpha=20) also confirmed
       clean: alpha=20 gives D&N extinct 3/15, mean share 0.0039,
       essentially unchanged from baseline.
     - All seeds converged within 1,200-6,000 steps -- no long-
       relaxation transition-zone behavior found here, unlike the
       flagship pairing.

2. Game of Life vs. Day and Night (Section 4.3, third pairing):
   CONFIRMED CLEAN. Matches the originally reported figure closely.
     - D&N extinct: 3/30 (10%), vs. originally reported 1/15 (6.7%)
     - mean GoL share: ~0.993-0.995, consistent with the reported 99.49%
     - All seeds converged within 200-4,200 steps.

3. Game of Life vs. HighLife (Section 4.4, disambiguation pairing):
   NEEDS CORRECTION. The originally reported "roughly even, 54.9% to
   45.1%, no extinctions on either side" does NOT hold at proper
   convergence. True result, 30 seeds, all cleanly converged (200 to
   17,200 steps, no long-relaxation stragglers):
     - Strong Game-of-Life dominance (share > 0.9): 26/30 (87%)
     - Genuine middling coexistence (share ~0.34-0.36): 2/30 (7%),
       individually verified stable (unchanged when re-run to 100
       check-intervals rather than the default 40)
     - Strong HighLife dominance (share < 0.02): 2/30 (7%)
   This is a wide, effectively multi-modal distribution, not a stable
   near-50/50 split. It does NOT overturn Section 4.4's qualitative
   conclusion (HighLife never achieves anything like Brian's Brain's
   total, near-deterministic dominance -- the disambiguation in favor
   of the absorbing-state property over raw expansion capacity still
   holds), but the specific evidence cited (stable near-parity, no
   extinctions) is wrong: extinction-like outcomes (>97% or <2% share)
   are actually the norm, not the exception, and the true character is
   much closer to the flagship pairing's high-variance, transition-
   prone behavior than to a settled coexistence.
"""

RESULTS_DN_VS_BB = {
    'pairing': 'Day and Night vs Brian\'s Brain',
    'D_bg': 0.05, 'D_diff': 0.05,
    'baseline_alpha1': {'species_a_extinct': 8, 'n_seeds': 30, 'mean_a_share_survivors': 0.0035,
                         'originally_reported': '5/15 (33%), mean share 0.35%'},
    'cost_alpha20': {'species_a_extinct': 3, 'n_seeds': 15, 'mean_a_share': 0.0039,
                      'originally_reported': 'cost-insensitivity claimed, alpha=1 to alpha=20'},
    'max_steps_seen': 6000,
    'status': 'CONFIRMED CLEAN -- no correction needed',
}

RESULTS_GOL_VS_DN = {
    'pairing': 'Game of Life vs Day and Night',
    'D_bg': 0.05, 'D_diff': 0.05,
    'baseline': {'dn_extinct': 3, 'n_seeds': 30, 'mean_gol_share': 0.994,
                 'originally_reported': '1/15 (6.7%), mean share 99.49%'},
    'max_steps_seen': 4200,
    'status': 'CONFIRMED CLEAN -- no correction needed',
}

RESULTS_GOL_VS_HIGHLIFE = {
    'pairing': 'Game of Life vs HighLife',
    'D_bg': 0.05, 'D_diff': 0.05,
    'baseline': {
        'gol_heavy_dominance_gt_0.9': 26,
        'middling_coexistence_034_036': 2,
        'highlife_heavy_dominance_lt_0.02': 2,
        'n_seeds': 30,
        'originally_reported': 'roughly even, 54.9%/45.1%, no extinctions on either side',
    },
    'individual_middling_seeds_verified_stable': [
        {'seed': 2, 'share': 0.3632, 'verified_at_max_checks': 100},
        {'seed': 6, 'share': 0.3398, 'verified_at_max_checks': 100},
    ],
    'max_steps_seen': 17200,
    'status': 'NEEDS CORRECTION -- true result is wide/multi-modal, not stable near-parity. Qualitative conclusion (no Brian\'s-Brain-style total dominance) survives; the specific cited evidence does not.',
}

if __name__ == "__main__":
    for r in [RESULTS_DN_VS_BB, RESULTS_GOL_VS_DN, RESULTS_GOL_VS_HIGHLIFE]:
        print(f"{r['pairing']}: {r['status']}")

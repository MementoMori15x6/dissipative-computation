"""
CONSOLIDATED RESULTS: Game of Life vs. Brian's Brain lottery baseline,
convergence-based re-measurement of Section 4.1's flagship result.

Generated using stage_convergence_runner.py (same directory). Every
value below was produced by run_to_convergence() / sweep_condition(),
30 seeds per point, with zero not-converged stragglers remaining in
any final tally (any seed that did not converge at the default cap
was individually re-run at a higher max_steps until it converged,
before being included here).

This file is a DATA RECORD, not a script to re-derive the numbers from
scratch -- it exists so these results survive independently of this
conversation. To regenerate any point from first principles, call
stage_convergence_runner.sweep_condition(D_bg, D_diff, n_seeds=30).

Background: Section 4.1 originally reported Brian's Brain winning
55.6%-96.7% of contested territory at D_bg=0.05 (increasing with
diffusion rate) and 94.7%-96.0% at D_bg=0.01 ("Game of Life's own
calibrated threshold"), both measured at the standard 200-warmup/
100-window. Auditing this at proper convergence found the true
long-run picture is very different at low-to-moderate diffusion
rates: most trials end in COMPLETE Brian's Brain extinction (Game of
Life takes the entire grid), not partial coexistence favoring Brian's
Brain. The standard-window numbers were mid-collapse snapshots of
trajectories almost all still heading toward one of two absorbing
outcomes (BB-total-extinct or, less often, a genuine stable BB-
dominant coexistence with a small frozen Game-of-Life remnant).

Metric definitions:
  gol_total_rate    -- fraction of 30 seeds ending in COMPLETE Brian's
                        Brain extinction (n_bb_final == 0), i.e. Game
                        of Life takes 100% of contested territory.
  mean_gol_share    -- mean, across all 30 seeds, of Game of Life's
                        final territory share (1.0 for GoL-total
                        trials; for BB-dominant trials, a trailing-
                        window average of Game of Life's frozen count
                        over Brian's Brain's fluctuating count, per
                        the convergence runner's averaging procedure).
  not_converged     -- always 0 in this file; any straggler was
                        individually resolved at a higher step cap
                        before being included.
"""

RESULTS_D_BG_0_05 = [
    # D_diff, gol_total_rate (x/30), mean_gol_share
    {'D_diff': 0.01, 'gol_total': 22, 'n_seeds': 30, 'mean_gol_share': 0.7423},
    {'D_diff': 0.03, 'gol_total': 25, 'n_seeds': 30, 'mean_gol_share': 0.8383},
    {'D_diff': 0.05, 'gol_total': 22, 'n_seeds': 30, 'mean_gol_share': 0.7417},
    {'D_diff': 0.07, 'gol_total': 23, 'n_seeds': 30, 'mean_gol_share': 0.7742},
    {'D_diff': 0.08, 'gol_total': 18, 'n_seeds': 30, 'mean_gol_share': 0.6112},
    {'D_diff': 0.09, 'gol_total': 16, 'n_seeds': 30, 'mean_gol_share': 0.5472},
    {'D_diff': 0.10, 'gol_total': 13, 'n_seeds': 30, 'mean_gol_share': 0.4493},
    {'D_diff': 0.12, 'gol_total': 4,  'n_seeds': 30, 'mean_gol_share': 0.1598},
    {'D_diff': 0.15, 'gol_total': 0,  'n_seeds': 30, 'mean_gol_share': 0.0280},
    {'D_diff': 0.20, 'gol_total': 0,  'n_seeds': 30, 'mean_gol_share': 0.0314},
]

RESULTS_D_BG_0_01 = [
    {'D_diff': 0.01, 'gol_total': 17, 'n_seeds': 30, 'mean_gol_share': 0.5792},
    {'D_diff': 0.02, 'gol_total': 4,  'n_seeds': 30, 'mean_gol_share': 0.160},  # approx; one straggler (seed 22) individually resolved to share=0.0194
    {'D_diff': 0.03, 'gol_total': 0,  'n_seeds': 30, 'mean_gol_share': 0.0289},
]

# Individually-resolved stragglers (seeds that did not converge at the
# default max_steps and were re-run at a higher cap before being
# folded into the tallies above) -- kept here for full traceability.
RESOLVED_STRAGGLERS = [
    {'D_bg': 0.05, 'D_diff': 0.05, 'seed': 0, 'note': 'BB-dominant, GoL frozen at 64, BB fluctuates ~1800-2260; converged at 8200 steps once trailing-average criterion was used (not a straggler under final runner, but the case that motivated the averaging-window redesign)'},
    {'D_bg': 0.01, 'D_diff': 0.01, 'seed': 1, 'note': 'not converged at max_steps=30000 (share=0.972 mid-collapse); resolved at max_steps=100000, steps_taken=31200, terminal GoL-total (BB extinct)'},
    {'D_bg': 0.01, 'D_diff': 0.01, 'seed': 4, 'note': 'not converged at max_steps=30000 (share=0.171 mid-collapse); resolved at max_steps=100000, steps_taken=49200, BB-dominant, share=0.0172'},
    {'D_bg': 0.01, 'D_diff': 0.02, 'seed': 22, 'note': 'not converged at max_steps=60000 (share=0.176 mid-collapse); resolved at max_steps=150000, BB-dominant, share=0.0194'},
]

if __name__ == "__main__":
    print("D_bg=0.05 sweep:")
    for row in RESULTS_D_BG_0_05:
        pct = 100 * row['gol_total'] / row['n_seeds']
        print(f"  D_diff={row['D_diff']:.2f}: GoL-total {row['gol_total']}/{row['n_seeds']} ({pct:.0f}%), mean GoL share {row['mean_gol_share']:.4f}")
    print("\nD_bg=0.01 sweep:")
    for row in RESULTS_D_BG_0_01:
        pct = 100 * row['gol_total'] / row['n_seeds']
        print(f"  D_diff={row['D_diff']:.2f}: GoL-total {row['gol_total']}/{row['n_seeds']} ({pct:.0f}%), mean GoL share {row['mean_gol_share']:.4f}")
    print(f"\n{len(RESOLVED_STRAGGLERS)} individually-resolved stragglers -- see RESOLVED_STRAGGLERS for detail.")

"""
CONSOLIDATED RESULTS: Section 4.2's cost-asymmetry sweep, convergence-
based re-measurement (Game of Life vs. Brian's Brain, D_bg=0.05,
D_diff=0.05, Brian's Brain's transitions priced at alpha x FLIP_COST).

Generated using stage_convergence_runner_cost.py (same directory).
This is a DATA RECORD, not a script to re-derive the numbers from
scratch -- it exists so these results survive independently of any
one conversation.

BACKGROUND: Section 4.2 originally reported Brian's Brain's territorial
dominance surviving (and, if anything, strengthening) across a 200-fold
increase in its own cost, alpha=1 to alpha=200, at the standard 200-
warmup/100-window measurement. The flagship lottery-baseline audit
(stage_convergence_runner.py, see 03-diffusion-limited-scarcity/
convergence_audit_results.py) found alpha=1 at this exact D_bg/D_diff
condition is NOT at steady state within that window: 73% of trials
actually end in complete Brian's Brain extinction. This file extends
that audit across the cost sweep.

FINDING: cost's effect on the reversal phenomenon is non-monotonic and
has a critical-slowing-down transition, not a simple threshold:

  alpha=1:  73% GoL-total (22/30)  -- confirmed, matches lottery-baseline audit exactly
  alpha=2:  87% GoL-total (13/15)  -- HIGHER than alpha=1; a peak, not a monotonic function of cost
  alpha=3:  40% GoL-total (6/15)   -- genuine transition zone; see METHODOLOGY note below
  alpha=10:  0% GoL-total (0/15)  -- stress-tested to 300,000 steps, confirmed robust
  alpha=20:  0% GoL-total (0/15)  -- confirmed
  alpha=200: 0% GoL-total (0/10)  -- confirmed

The transition boundary sits between alpha=3 and alpha=10. alpha=4-9
were NOT mapped (see OPEN below) -- deliberately deferred as a
resolution-enhancement / follow-up item rather than pursued further,
given the compute cost of resolving trials in this zone (see below).

METHODOLOGY NOTE -- why alpha=3 needed special handling:
A first pass at alpha=3 (15 seeds, max_checks=40, i.e. up to ~40,000
steps past warmup) reported 0/15 GoL-total, with 6 of 15 seeds flagged
as not-converged at shares of 0.07-0.18 -- looking, at that point,
similar to alpha=10's genuinely-BB-dominant stragglers. Pushing those
6 seeds to 86,000-100,000+ steps found all 6 were actually still
heading toward COMPLETE Game-of-Life takeover (final shares 0.999-1.0,
n_bb = 0-2), not settling into BB-dominant coexistence. The true
alpha=3 rate is therefore 6/15 (40%), not 0/15.

This was distinguished from alpha=10's stragglers (which also showed
elevated, slowly-changing shares, e.g. seed 12: 0.146 -> 0.119 -> 0.047
across escalating step caps up to 300,000) by the SIGN of the drift:
alpha=3's stragglers trended upward toward 1.0 (heading to Game-of-Life
victory); alpha=10's stragglers trended downward toward 0 (heading to
Brian's-Brain-dominant coexistence, just slowly). Classifying by drift
direction rather than a fixed step cap is what caught this -- a fixed
40,000-step cap alone would have reported alpha=3 as "0% reversal,"
the wrong answer, with no visible sign of error in the reported number.

This means: near a transition, do not trust a single step-cap number
without checking which direction any unresolved stragglers are moving.
"""

RESULTS_ALPHA_SWEEP = [
    # alpha, gol_total, n_seeds, mean_gol_share, notes
    {'alpha': 1,   'gol_total': 22, 'n_seeds': 30, 'mean_gol_share': 0.7417, 'notes': 'matches lottery-baseline audit exactly (same underlying condition)'},
    {'alpha': 2,   'gol_total': 13, 'n_seeds': 15, 'mean_gol_share': 0.8706, 'notes': 'peak of the reversal curve; higher than alpha=1'},
    {'alpha': 3,   'gol_total': 6,  'n_seeds': 15, 'mean_gol_share': None,  'notes': 'critical-slowing-down zone; corrected from an initial (wrong) 0/15 reading -- see METHODOLOGY note above. Mean share not reported: 6 seeds resolved via drift direction to near-1.0 rather than a stable trailing average, remaining 9 seeds genuinely BB-dominant at share 0.01-0.04.'},
    {'alpha': 10,  'gol_total': 0,  'n_seeds': 15, 'mean_gol_share': 0.05,  'notes': 'stress-tested: highest-share stragglers pushed to 300,000 steps, confirmed trending toward 0 (genuine BB dominance), not a hidden reversal'},
    {'alpha': 20,  'gol_total': 0,  'n_seeds': 15, 'mean_gol_share': 0.06,  'notes': 'confirmed'},
    {'alpha': 200, 'gol_total': 0,  'n_seeds': 10, 'mean_gol_share': 0.037, 'notes': 'confirmed; cleanly converged, low variance (0.024-0.048)'},
]

# Individually-resolved stragglers, kept for full traceability.
RESOLVED_STRAGGLERS = [
    {'alpha': 3, 'seed': 3,  'note': 'not converged at 40,000 steps (share=0.094); at 100,000+ steps: share=0.9994, n_bb=1 -- effectively GoL-total'},
    {'alpha': 3, 'seed': 4,  'note': 'not converged at 40,000 steps; at 94,200 steps: share=1.0000, n_bb=0 -- confirmed GoL-total'},
    {'alpha': 3, 'seed': 5,  'note': 'not converged at 40,000 steps; at 86,200 steps: share=1.0000, n_bb=0 -- confirmed GoL-total'},
    {'alpha': 3, 'seed': 11, 'note': 'not converged at 40,000 steps; at 100,200 steps: share=0.9989, n_bb=2 -- effectively GoL-total'},
    {'alpha': 3, 'seed': 13, 'note': 'not converged at 40,000 steps; at 100,200 steps: share=0.9995, n_bb=1 -- effectively GoL-total'},
    {'alpha': 3, 'seed': 14, 'note': 'not converged at 40,000 steps; at 100,200 steps: share=0.9994, n_bb=1 -- effectively GoL-total'},
    {'alpha': 10, 'seed': 3,  'note': 'not converged even at 150,600 steps (share hovering 0.07-0.09 across checks); classified BB-dominant by consistent low, non-increasing share -- not chased to full precision'},
    {'alpha': 10, 'seed': 12, 'note': 'stress-tested to 300,000 steps: share trended DOWNWARD (0.146 -> 0.119 -> 0.047) -- confirmed genuine slow convergence toward BB dominance, not a hidden reversal'},
    {'alpha': 10, 'seed': 14, 'note': 'not converged at 150,000 steps; share trending downward (0.128 -> 0.061) -- same pattern as seed 12, treated as confirmed BB-dominant'},
]

OPEN_ITEMS = [
    'alpha=4 through alpha=9 not mapped -- the transition boundary is bounded between alpha=3 (40%) and alpha=10 (0%) but its exact shape in between is unknown. Given alpha=3 required up to 100,000 steps per seed to resolve, this range should be expected to need similar or greater compute per seed. Deliberately deferred rather than pursued further this session.',
    'alpha=1 (73%) vs alpha=2 (87%) non-monotonicity is reported but not mechanistically explained.',
    'The D_bg=0.05, D_diff sweep (see convergence_audit_results.py) showed a similar unexplained non-monotonic wobble (D_diff=0.05 at 73% vs D_diff=0.07 at 77%) -- whether these two non-monotonicities share a common cause is untested.',
]

if __name__ == "__main__":
    print("Section 4.2 cost-asymmetry sweep, convergence-verified:")
    for row in RESULTS_ALPHA_SWEEP:
        pct = 100 * row['gol_total'] / row['n_seeds']
        share_str = f"{row['mean_gol_share']:.3f}" if row['mean_gol_share'] is not None else "n/a (see notes)"
        print(f"  alpha={row['alpha']:>3}: GoL-total {row['gol_total']}/{row['n_seeds']} ({pct:.0f}%), mean share {share_str}")
    print(f"\n{len(RESOLVED_STRAGGLERS)} individually-resolved stragglers -- see RESOLVED_STRAGGLERS for detail.")
    print(f"{len(OPEN_ITEMS)} open items -- see OPEN_ITEMS.")

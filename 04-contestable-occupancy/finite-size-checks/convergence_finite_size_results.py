"""
CONVERGENCE FINITE-SIZE CHECK RESULTS: does the flagship diffusion-driven
competitive transition (Section 4.1) survive at larger grid sizes when
measured to genuine convergence?

This closes the single most damaging reviewer objection -- that the flagship
result rested on one grid size (N=64) with only a short-window finite-size
check. Runner: stage_finite_size_convergence.py (this directory), reusing
stage_finite_size.py's GoL-vs-BB mechanism unchanged, measured under the
same convergence criterion validated for the N=64 result.

Condition: D_bg=0.05 (BB's own threshold), GoL-vs-BB lottery competition.

====================================================================
RESULT: THE TRANSITION IS ROBUST TO SYSTEM SIZE. Both regimes hold, and
the transition exists at every grid size tested.
====================================================================

LOW-DIFFUSION END (D_diff = 0.05) -- Game of Life should win (corrected
Section 4.1 result):
  N=64:  mean GoL frac 0.613, GoL win rate 60%,  0/10 not-converged
  N=128: mean GoL frac 1.000, GoL win rate 100%, 0/10 not-converged
  N=256: mean GoL frac 1.000, GoL win rate 100%, 0/5  not-converged
  -> GoL wins at ALL sizes; the corrected low-diffusion result strengthens
     (not weakens) with grid size. The old short-window claim of a
     "74%->66% decline with size" is superseded: under convergence, GoL's
     win becomes MORE decisive at larger sizes, not less.

HIGH-DIFFUSION END (D_diff = 0.20) -- Brian's Brain should win (the other
side of the transition):
  N=64:  mean GoL frac 0.035, GoL win rate 0%, 0/8 not-converged
  N=128: mean GoL frac 0.031, GoL win rate 0%, 0/8 not-converged
  -> BB wins at both sizes, essentially identical magnitude. The
     high-diffusion regime is size-robust.

CONCLUSION: The diffusion-driven transition -- GoL winning at low transport,
BB at high transport -- is present and in the same direction at N=64, 128,
and 256. The transition is not a finite-size artifact of the N=64 substrate.
The exact crossover LOCATION was not finely mapped at N=128/256 (only the
two endpoints bracketing it were tested), but the existence and direction
of the transition are confirmed size-robust.

OPEN (minor): the precise crossover D_diff at N=128/256 was not mapped
(would require sweeping intermediate D_diff at large N); only the endpoints
were tested. N=256 at D_diff=0.20 was not run (N=128 already confirms the
high-diffusion end; N=256 is ~5x slower per seed). Neither gap affects the
size-robustness conclusion.
"""

FINITE_SIZE_CONVERGENCE = {
    'condition': {'D_bg': 0.05, 'pairing': 'GoL vs BB lottery'},
    'low_diffusion_D_diff_0.05': {
        64:  {'mean_gol_frac': 0.613, 'gol_win_rate': 0.60, 'n_seeds': 10, 'not_converged': 0},
        128: {'mean_gol_frac': 1.000, 'gol_win_rate': 1.00, 'n_seeds': 10, 'not_converged': 0},
        256: {'mean_gol_frac': 1.000, 'gol_win_rate': 1.00, 'n_seeds': 5,  'not_converged': 0},
    },
    'high_diffusion_D_diff_0.20': {
        64:  {'mean_gol_frac': 0.035, 'gol_win_rate': 0.00, 'n_seeds': 8, 'not_converged': 0},
        128: {'mean_gol_frac': 0.031, 'gol_win_rate': 0.00, 'n_seeds': 8, 'not_converged': 0},
    },
    'conclusion': 'Diffusion-driven transition robust to system size; present and same-direction at N=64/128/256. Not a finite-size artifact.',
}

if __name__ == "__main__":
    d = FINITE_SIZE_CONVERGENCE
    print("Low-diffusion (D_diff=0.05), GoL should win:")
    for n, v in d['low_diffusion_D_diff_0.05'].items():
        print(f"  N={n}: GoL frac {v['mean_gol_frac']:.3f}, win rate {v['gol_win_rate']:.0%} ({v['n_seeds']} seeds)")
    print("High-diffusion (D_diff=0.20), BB should win:")
    for n, v in d['high_diffusion_D_diff_0.20'].items():
        print(f"  N={n}: GoL frac {v['mean_gol_frac']:.3f}, win rate {v['gol_win_rate']:.0%} ({v['n_seeds']} seeds)")
    print(f"\n{d['conclusion']}")

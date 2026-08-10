"""
CONVERGENCE CHECK ON SECTION 3.2'S ENERGETIC-DEMAND CURVES

WHY THIS EXISTS
---------------
Section 3.2 is load-bearing: the absorbing-state criterion is identified there,
and Sections 4 and 5 rest on it. But Section 3.2's sweeps were measured over the
standard short window (75 steps past a 200-step warmup), and the convergence
audit (Section 2.3) established that short windows can misreport results near a
transition -- in Section 4.1 severely enough to invert the qualitative outcome.

Section 6 discloses that Section 3's results were never re-checked. That is the
paper's most exposed point: the criterion's own foundation is measured the way
the paper elsewhere says is unsafe. This script closes it.

WHAT IS ACTUALLY AT RISK
------------------------
NOT the C/Phi magnitudes -- those are already flagged provisional, and the
complexity numerator's bias is handled separately (Section 3.3, Appendix A).

The load-bearing claim is the SHAPE of the demand curve: rules admitting an
absorbing state saturate, and Brian's Brain, which admits none, rises
monotonically with supply until the accounting scheme's own ceiling. That claim
is about realized flux Phi, which is a direct count of executed transitions and
carries no estimator bias. It is, however, exposed to slow relaxation: a 75-step
window may catch a system still settling toward its steady demand.

METHOD
------
For each rule and each supply level D, measure Phi over a sequence of windows of
increasing length past the same warmup:

    75 (the published window), 500, 2000, 10000 steps

If the published shape is real, Phi should stabilize as the window grows and the
saturating/non-saturating distinction should hold at every window. If the short
window was misreporting, either the values drift without settling, or the
qualitative distinction changes with window length.

Also recorded per condition:
  - active_frac    : fraction of cells in a non-quiescent state
  - throttled_frac : fraction of PROPOSED transitions denied for lack of energy.
                     This is the direct measure of whether the gate is binding.
                     A rule that has reached an absorbing configuration proposes
                     almost nothing, so both Phi and throttling fall to zero; a
                     rule that cannot stop proposing keeps both non-zero.

Deterministic per seed: rng = np.random.default_rng(seed), matching the stage
scripts, so published short-window values reproduce exactly at window=75.
"""

import sys
import numpy as np

sys.path.insert(0, ".")

import stage1_landauer_gate as gol          # Game of Life
import stage2_chaotic_comparison as multi   # rule-parameterized (Day and Night)
import stage3_brians_brain as bb            # Brian's Brain

WINDOWS = [75, 500, 2000, 10000]
SEEDS = [0, 1, 2]


def _run_binary(module, D, seed, window, birth=None, survive=None):
    """Game of Life (stage1) or a RULES-parameterized rule (stage2)."""
    rng = np.random.default_rng(seed)
    life = (rng.random((module.N, module.N)) < module.SOUP_DENSITY).astype(int)
    energy = np.zeros((module.N, module.N))

    def step(l, e):
        if birth is None:
            return module.landauer_gated_step(l, e, D)
        return module.landauer_gated_step(l, e, D, birth, survive)

    for _ in range(module.WARMUP_STEPS):
        life, energy, _ = step(life, energy)

    flips = proposed = 0
    active = 0
    for _ in range(window):
        prev = life
        life, energy, did = step(life, energy)
        flips += int(did.sum())
        if birth is None:
            want = module.gol_propose(prev) != prev
        else:
            want = module.rule_propose(prev, birth, survive) != prev
        proposed += int(want.sum())
        active += int(life.sum())

    cells = module.N * module.N
    return {
        "phi": flips * module.FLIP_COST / (window * cells),
        "active_frac": active / (window * cells),
        "throttled_frac": (proposed - flips) / proposed if proposed else 0.0,
    }


def _run_bb(D, seed, window):
    rng = np.random.default_rng(seed)
    state = np.zeros((bb.N, bb.N), dtype=int)
    state[rng.random((bb.N, bb.N)) < bb.SOUP_DENSITY] = 1
    energy = np.zeros((bb.N, bb.N))
    for _ in range(bb.WARMUP_STEPS):
        state, energy, _ = bb.landauer_gated_step_bb(state, energy, D)

    flips = proposed = active = 0
    for _ in range(window):
        prev = state
        state, energy, did = bb.landauer_gated_step_bb(state, energy, D)
        flips += int(did.sum())
        proposed += int((bb.brians_brain_propose(prev) != prev).sum())
        active += int((state != 0).sum())

    cells = bb.N * bb.N
    return {
        "phi": flips * bb.FLIP_COST / (window * cells),
        "active_frac": active / (window * cells),
        "throttled_frac": (proposed - flips) / proposed if proposed else 0.0,
    }


def measure(rule, D, window, seeds=SEEDS):
    out = []
    for s in seeds:
        if rule == "GoL":
            out.append(_run_binary(gol, D, s, window))
        elif rule == "BB":
            out.append(_run_bb(D, s, window))
        else:
            r = multi.RULES[rule]
            out.append(_run_binary(multi, D, s, window, r["birth"], r["survive"]))
    return {k: float(np.mean([o[k] for o in out])) for k in out[0]}


def sweep(rule, D_values, windows=WINDOWS):
    print(f"\n=== {rule} ===")
    print(f"{'D':>6} " + " ".join(f"{'phi@'+str(w):>11}" for w in windows)
          + f" {'throttled@max':>14}")
    rows = {}
    for D in D_values:
        vals = [measure(rule, D, w) for w in windows]
        rows[D] = vals
        print(f"{D:>6} " + " ".join(f"{v['phi']:>11.5f}" for v in vals)
              + f" {vals[-1]['throttled_frac']:>14.3f}", flush=True)
    return rows


if __name__ == "__main__":
    sweep("GoL", [0.05, 0.1, 0.3, 0.6, 1.0])
    sweep("DayAndNight", [0.05, 0.1, 0.3, 0.6, 1.0])
    sweep("BB", [0.3, 0.4, 0.6, 1.0])

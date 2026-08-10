# Open Questions — Deliberately Deferred

Ideas that came out of the Dissipative Computation work, judged worth pursuing
but **deliberately not pursued before submission**, because each opens a new
front and the paper was converging. Recorded in enough detail to be picked up
cold, by future-me or a fresh collaborator, without reconstructing the reasoning.

---

## 1. A candidate mechanism for the shared complexity shape (§3.3)

**Status:** hypothesis with a concrete test. Not run. Highest-value item here.

### The open question as the paper leaves it

Section 3.3 reports that structural complexity peaks at or near each rule's own
energetic threshold and decays as diffusion rises, and that **the same shape
appears in all three rule classes** — differing in magnitude, not in kind. The
paper offers no mechanism for it. The excitable-medium reading was withdrawn
when debiasing moved the peak from an interior location to the threshold edge,
and nothing replaced it. Section 5.3 states plainly that whether the shared
shape reflects one common mechanism or a coincidence of three different ones is
untested.

### The hypothesis

**Complexity is maximized where the energy gate binds but does not strangle.**

At each rule's threshold, some but not all proposed transitions are denied. The
gate acts as a filter: it suppresses cheap, high-turnover churn while leaving
persistent, coherent structure intact — structure that by definition proposes
fewer transitions per cell and so pays less. Far below threshold nothing runs
at all; far above it, energy is free and everything fires, so no filtering
occurs and coherent structure is not preferentially retained.

If this is right, the peak is not located by diffusion rate as such. It is
located by **throttled fraction** — the proportion of proposed transitions
denied for lack of energy — and the rules differ in *where* that fraction is
achieved, not in what value of it maximizes complexity.

### Why this is now testable, and cheaply

`02-landauer-gated-execution/stage5_demand_convergence_check.py` already
measures `throttled_frac` alongside flux and active fraction. That instrument
did not exist when Section 3.3 was written.

### The test

Measure `C` and `throttled_frac` together across the `D_diff` sweep for all
three rule classes, under the adaptive long-window protocol (§2.3).

- **Confirming outcome:** the complexity maximum coincides with a *common*
  intermediate throttled fraction across all three rules, despite occurring at
  three different `D_diff` values. That would be a mechanism, and it would
  explain the shared shape — which is exactly the question Section 3.3 leaves
  open.
- **Disconfirming outcome:** the peak throttled fraction differs by rule, or
  complexity does not track throttling at all. Then the shared shape has no
  single mechanism and the paper's agnosticism was correct.

Either result is publishable. The disconfirming one is worth recording too.

### Cost and risk

The complexity measurement is the expensive part — 10,000-step blocks to a
40,000-step cap, per point, per seed. Budget an hour-plus of compute for a
first exploratory pass at a few points per rule. Do **not** start with a full
sweep; check whether the correlation is obviously there before committing.

**Risk to be honest about:** if it confirms, it does not close cleanly. It
would want more points, a fit, probably its own figure, and rewrites of both
§3.3 and §5.3. That is why it was deferred rather than attempted.

---

## 2. Universality class of the active-to-absorbing transition (§5.3)

**Status:** posed in the manuscript as an open question with a named test. Not run.

Section 5.3 observes that gated execution produces a transition with the
qualitative form of an absorbing-state phase transition — an active phase, an
absorbing phase, a threshold between them — and asks whether it belongs to the
directed-percolation universality class (Hinrichsen, 2000).

**The test:** measure how the density of active cells scales with distance from
the threshold and compare the exponent against the directed-percolation value.

**The honest difficulty, already stated in the manuscript:** directed
percolation is conventionally formulated for *stochastic* dynamics with a unique
absorbing configuration. These rules are deterministic; randomness enters only
through initial conditions and the shared field. The answer is not obvious in
either direction, which is what makes it worth measuring.

This is a paper of its own, not an addition to this one.

---

## 3. Is the absorbing-state criterion binary or graded? (§6)

**Status:** disclosed as a limitation. Untested.

Section 4.3 found Day and Night more fragile under scarcity than Game of Life
*despite both admitting absorbing states* — its broader survival condition keeps
it in continual internal cycling rather than letting it settle into a
low-turnover quiescent configuration.

The out-of-sample test (`out_of_sample_rule_test_results.py`) sharpens this
considerably. At the unthrottled ceiling the absorbing-state rules do not
cluster; they spread across the whole range below 1.0:

    Life without Death   0.000
    Game of Life         0.456
    Day and Night        0.837

That ordering looks like **how readily a rule reaches its absorbing
configuration**, expressed as a number. Life without Death freezes immediately
and completely; Game of Life settles into still-lifes but keeps oscillators
running; Day and Night barely settles at all.

**The question:** is per-cell demand at the unthrottled ceiling the graded
version of the criterion — a continuous measure of absorbing-configuration
reachability — rather than a binary property with a threshold at 1.0?

**Why this is attractive:** it would convert a binary structural criterion into
a continuous one measurable for any rule, and it would predict that a rule's
competitive fragility under scarcity tracks its ceiling value. That is directly
testable against the Section 4 competition results already banked.

**Why it was not pursued:** it needs more rules to establish that the ordering
means anything, and it would restructure Section 5.2's central claim.

---

## 4. Finite-size behaviour of Brian's Brain's population decay (§3.2)

**Status:** disclosed. Small, cheap, low priority.

Brian's Brain's active population declines over long windows on a 64×64
periodic grid (active fraction 0.038 → 0.0086 at `D = 1.0` over 10,000 steps).
Whether this is intrinsic or a finite-size effect is untested at larger `N`.

It does not affect the per-cell criterion, which is population-normalized. It
does affect any future claim about total demand. One run at `N = 128` and
`N = 256` would settle it.

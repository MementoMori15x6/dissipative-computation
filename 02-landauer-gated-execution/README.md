# Landauer-Gated Execution Across Rule Classes

Does sustained energetic demand depend on a cellular automaton rule's own structure? This section tests a mechanism genuinely different from Section 1: energy gates whether a proposed state transition can *execute at all*, not merely whether its result survives afterward.

## Method

Each step, the rule's proposed next state is computed without being applied. Any cell whose proposed state differs from its current state is a bit flip, following Landauer's formulation: a state change that must be paid for, with a static cell (no proposed change) costing nothing. A cell can only execute its proposed flip if local energy covers a fixed cost; otherwise it is frozen, regardless of what the rule proposed. Energy accumulates via unconditional per-cell inflow `D` each step, capped to bound growth. Because updates are synchronous and a cell can flip at most once per step, `D = 1.0` (equal to the flip cost) is a mathematically guaranteed ceiling — every value of `D ≥ 1.0` is identical to `D = 1.0` for any rule, verified directly by extending the sweep to `D = 8.0` and finding bit-for-bit identical results.

**Metrics**: flux (realized flip cost per cell per step) and complexity — mean time-lagged mutual information between neighboring cells' trajectories, deliberately chosen over Lempel-Ziv or Kolmogorov-style complexity measures, which increase monotonically with randomness and cannot distinguish genuine structure from incoherent noise.

**Three rule classes tested**: Conway's Game of Life; Day and Night (a rule with a broader survival condition); and Brian's Brain (Silverman, 1984; first published in Toffoli & Margolus, 1987), a three-state rule (Ready → Firing → Refractory → Ready) in which two of the three states have no "stay the same" option — a Firing or Refractory cell is mechanically forced to attempt a transition every step, regardless of neighbors.

## Results

**Game of Life and Day and Night both saturate early.** Each shows a sharp early spike in flux and complexity at very low `D` (traced to a real, measurable asymmetry: death-transitions are attempted more often but succeed at less than half the rate of birth-transitions at this energy level, confirmed by direct counting, not assumed), followed by a decline to a low, stable plateau that holds regardless of how much further `D` increases. Neither rule's demand for energy scales with the amount available past this point.

**Brian's Brain shows a sharp threshold, then genuinely unsaturating demand.** Every measured quantity is exactly zero for `D` from 0 through 0.25 (complete extinction during warmup). Past `D ≈ 0.3`, flux and complexity rise monotonically all the way to the model's own mathematical ceiling at `D = 1.0`, with no early saturation and no decline — the only rule tested whose demand was still increasing at the point where the energy-accounting scheme itself stops being able to represent further scaling.

## Interpretation

Sustained energetic demand under this gating scheme depends on a specific, identifiable structural property: whether a rule's own dynamics permit a configuration in which no cell needs to change state. Game of Life and Day and Night both have such configurations (static survivors) and reliably find them once minimally unthrottled; Brian's Brain's mandatory two-of-three forced transitions mean no such configuration exists, and its demand for energy scales with whatever is available, up to the limit of what this accounting scheme can represent.

## Scope limits

- The `D = 1.0` ceiling is a property of this specific energy-accounting scheme (synchronous updates, at most one flip per cell per step), not a general physical law. Whether Brian's Brain's demand continues rising under a scheme permitting more than one flip-cost unit of consumption per cell per step (e.g., asynchronous updates or a continuous-time formulation) is untested.
- The Game of Life / Day and Night birth-death asymmetry mechanism was verified directly for Game of Life specifically; a matching direct verification for Day and Night was not performed, though the same qualitative spike appears (more extreme, in fact).
- Three rule classes tested, one grid size, one set of protocol parameters.

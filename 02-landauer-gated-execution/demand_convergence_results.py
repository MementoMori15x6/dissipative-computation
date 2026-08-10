"""
CONVERGENCE CHECK ON SECTION 3.2'S DEMAND CURVES -- BANKED RESULTS

Produced by stage5_demand_convergence_check.py (same directory, runnable).
This closes the gap Section 6 named as the paper's largest: Section 3.2, which
identifies the absorbing-state criterion the rest of the paper rests on, had
never been re-checked against the slow-relaxation failure mode.

FINDING 1 -- THE PUBLISHED DEMAND CURVES DO NOT SURVIVE AS STATED
-----------------------------------------------------------------
Total realized flux decays substantially with window length for BOTH rule
classes, so the short window overstates it in the energy-abundant regime:

  GoL, D = 1.0 : phi = 0.0509 (w=75) -> 0.0160 (w=2000) -> 0.0100 (w=10000)
  BB,  D = 1.0 : phi = 0.0563 (w=75) -> 0.0233 (w=2000) -> 0.0130 (w=10000)
  BB,  D = 0.4 : phi = 0.0470 (w=75) -> 0.0061 (w=2000) -> 0.0041 (w=10000)

Two different causes. Game of Life settles toward still-lifes and oscillators
once it can afford to (active fraction 0.066 -> 0.029). Brian's Brain's
population slowly DECAYS on a finite periodic grid (active 0.038 -> 0.0086 at
D = 1.0; 0.032 -> 0.0028 at D = 0.4), so its flux falls with its population
rather than because its cells stop demanding.

Consequence: "saturating versus monotonically rising total demand" is not
supportable at long window. Total flux is confounded by population dynamics.

FINDING 2 -- THE CRITERION SURVIVES, IN A SHARPER FORM
-------------------------------------------------------
Normalizing by the active population removes the confound. Flux per active
cell at window = 2000:

  rule           D=0.05   D=0.3    D=0.4    D=1.0
  GoL            0.146    0.533             0.456
  Day and Night  0.100    0.283             0.837
  Brian's Brain                    1.496    1.501

Brian's Brain sits at ~1.50 essentially INDEPENDENT of supply, across a 2.5x
change in D. Both absorbing-state rules vary with supply and stay below 1.0.

This is the structural claim measured directly: a rule admitting an absorbing
configuration has per-cell demand that varies with what it is given and can
fall arbitrarily low, because its cells are permitted to rest. A rule admitting
none has per-cell demand pinned by its transition table regardless of supply,
because its cells are not. The invariant is a property of the rule, not of the
population it happens to sustain on a finite grid.

FINDING 3 -- THE SCARCE REGIME WAS ALREADY CONVERGED
-----------------------------------------------------
Where gating actually binds, the published measurement was fine:

  GoL, D = 0.05 (80% of proposed transitions denied):
    phi = 0.0545 (w=75) -> 0.0504 (w=2000) -> 0.0501 (w=10000)
    active fraction 0.279 -> 0.345 -> 0.342

Stable to within 8% from the short window out to 10,000 steps. Energy scarcity
prevents Game of Life from reaching its absorbing configuration at all, holding
it in a genuine non-equilibrium steady state. The short window misleads only in
the abundant regime, where the system is still relaxing toward rest.

OPEN
----
Brian's Brain's population decay on a 64x64 periodic grid may be a finite-size
effect; it was not tested at larger N. That matters for Finding 1's second
cause but not for Finding 2, which is population-normalized.
"""

WINDOWS = [75, 500, 2000, 10000]
N_SEEDS = 3

TOTAL_FLUX = {
    ("GoL", 0.05): {75: 0.05452, 500: 0.05117, 2000: 0.05038, 10000: 0.05007, "throttled": 0.800},
    ("GoL", 0.3):  {75: 0.05112, 500: 0.04222, 2000: 0.02572, 10000: 0.00517, "throttled": 0.004},
    ("GoL", 1.0):  {75: 0.05092, 500: 0.03570, 2000: 0.01598, 10000: 0.00997, "throttled": 0.000},
    ("BB", 0.4):   {75: 0.04703, 500: 0.01326, 2000: 0.00606, 10000: 0.00414, "throttled": 0.003},
    ("BB", 1.0):   {75: 0.05628, 500: 0.04980, 2000: 0.02325, 10000: 0.01295, "throttled": 0.000},
}

ACTIVE_FRACTION = {
    ("GoL", 0.05): {75: 0.27899, 2000: 0.34548, 10000: 0.34233},
    ("GoL", 1.0):  {75: 0.06625, 2000: 0.03503, 10000: 0.02940},
    ("BB", 0.4):   {75: 0.03163, 2000: 0.00405, 10000: 0.00276},
    ("BB", 1.0):   {75: 0.03754, 2000: 0.01549, 10000: 0.00863},
}

# The load-bearing quantity. Window = 2000, three seeds.
FLUX_PER_ACTIVE_CELL = {
    ("GoL", 0.05):         {"phi": 0.05038, "active": 0.34548, "ratio": 0.146, "throttled": 0.7999},
    ("GoL", 0.3):          {"phi": 0.02572, "active": 0.04831, "ratio": 0.533, "throttled": 0.0039},
    ("GoL", 1.0):          {"phi": 0.01598, "active": 0.03503, "ratio": 0.456, "throttled": 0.0000},
    ("DayAndNight", 0.05): {"phi": 0.04994, "active": 0.49995, "ratio": 0.100, "throttled": 0.8050},
    ("DayAndNight", 0.3):  {"phi": 0.00015, "active": 0.00053, "ratio": 0.283, "throttled": 0.0307},
    ("DayAndNight", 1.0):  {"phi": 0.00586, "active": 0.00700, "ratio": 0.837, "throttled": 0.0000},
    ("BB", 0.4):           {"phi": 0.00606, "active": 0.00405, "ratio": 1.496, "throttled": 0.0029},
    ("BB", 1.0):           {"phi": 0.02325, "active": 0.01549, "ratio": 1.501, "throttled": 0.0000},
}

CONCLUSION = {
    "published_total_flux_curves": "NOT SUPPORTED at long window -- confounded by population dynamics",
    "absorbing_state_criterion": "SUPPORTED, and more cleanly, when demand is normalized per active cell",
    "scarce_regime_measurements": "ALREADY CONVERGED -- stable to within 8% from w=75 to w=10000",
    "manuscript_action": "PENDING AUTHOR DECISION -- Section 3.2 would need restating in per-cell terms",
}

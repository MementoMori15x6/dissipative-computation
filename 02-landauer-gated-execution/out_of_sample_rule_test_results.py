"""
OUT-OF-SAMPLE TEST OF THE ABSORBING-STATE CRITERION -- BANKED RESULTS

Two rules absent from the rest of the paper were classified BY INSPECTION of
their transition tables, the prediction recorded, and only then measured.

  Seeds (B2/S)                     no cell survives, so no live cell can hold
                                   its state -> NO non-trivial absorbing
                                   configuration -> predicted PINNED demand.
  Life without Death (B3/S0-8)     every live cell survives, so a live cell's
                                   proposed state equals its current one ->
                                   absorbing configurations abundant ->
                                   predicted LOW, collapsible demand.

Both predictions were correct as to class. The measurement also corrected the
FORM in which Section 3.2 had stated the criterion (see below).

RESULT -- at the unthrottled ceiling (D = 1.0, zero transitions denied),
window 2000, three seeds:

  rule                 class        per-cell demand
  Life without Death   absorbing              0.000
  Game of Life         absorbing              0.456
  Day and Night        absorbing              0.837
  Brian's Brain        none                   1.501
  Seeds                none                   2.000

Five rules, two classes, clean separation at 1.0. The two rules added here sit
at the extremes, which is the strongest placement for an out-of-sample test:
Life without Death at exactly zero, Seeds at exactly 2.0.

The 1.0 boundary has a direct reading. A rule whose cells cannot hold their
state must, at the unthrottled ceiling, execute at least one transition per
active cell per step. A rule whose cells may rest cannot be forced above that,
and drops as far below it as its absorbing configurations allow -- to exactly
zero for Life without Death, which freezes completely.

CORRECTION TO SECTION 3.2'S FORMULATION
----------------------------------------
Section 3.2 stated the criterion as SUPPLY-INDEPENDENCE: Brian's Brain pinned
at ~1.50 across supply, absorbing-state rules varying with supply. This test
shows that framing is not right, and that the earlier comparison was uneven:

  1. Seeds is NOT supply-independent. Its per-cell demand rises 0.195 (D=0.05,
     85% throttled) -> 1.338 (D=0.3, 27% throttled) -> 2.000 (D=1.0, 0%).
     Under throttling ANY rule's per-cell demand falls, because transitions are
     denied regardless of what the rule wants.
  2. Brian's Brain looked supply-independent only because both points at which
     it was measured (D = 0.4 and D = 1.0) are effectively unthrottled. It
     cannot be measured under heavy throttling at all -- it goes extinct below
     D = 0.3.
  3. Life without Death is supply-independent at 0.000, on the ABSORBING side,
     which the supply-independence framing would have misclassified.

The defensible statement is about the UNTHROTTLED CEILING value, not about
variation across supply: where energy is not limiting, a rule admitting no
absorbing configuration demands at least one transition per active cell per
step, and a rule admitting one demands less. Throttled measurements are
comparable only against other throttled measurements at matched throttling.
"""

PREDICTION_REGISTERED_BEFORE_MEASUREMENT = {
    "Seeds": "no non-trivial absorbing configuration -> pinned demand, >= 1",
    "LifeWithoutDeath": "absorbing configurations abundant -> low, collapsible demand, < 1",
    "outcome": "both correct as to class",
}

UNTHROTTLED_CEILING = {   # D = 1.0, throttled fraction 0.0000, window 2000, 3 seeds
    "LifeWithoutDeath": {"class": "absorbing", "per_cell_demand": 0.000},
    "GoL":              {"class": "absorbing", "per_cell_demand": 0.456},
    "DayAndNight":      {"class": "absorbing", "per_cell_demand": 0.837},
    "BB":               {"class": "none",      "per_cell_demand": 1.501},
    "Seeds":            {"class": "none",      "per_cell_demand": 2.000},
}

SUPPLY_SWEEP = {
    ("Seeds", 0.05):            {"phi": 0.04941, "active": 0.25315, "per_cell": 0.195, "throttled": 0.8508},
    ("Seeds", 0.3):             {"phi": 0.29909, "active": 0.22360, "per_cell": 1.338, "throttled": 0.2717},
    ("Seeds", 1.0):             {"phi": 0.42157, "active": 0.21078, "per_cell": 2.000, "throttled": 0.0000},
    ("LifeWithoutDeath", 0.05): {"phi": 0.0, "active": 0.68978, "per_cell": 0.0, "throttled": 0.0},
    ("LifeWithoutDeath", 0.3):  {"phi": 0.0, "active": 0.68978, "per_cell": 0.0, "throttled": 0.0},
    ("LifeWithoutDeath", 1.0):  {"phi": 0.0, "active": 0.68978, "per_cell": 0.0, "throttled": 0.0},
}

CONCLUSION = {
    "criterion": "SUPPORTED out of sample -- 5 rules, 2 classes, separation at 1.0",
    "formulation": "CORRECTED -- state it at the unthrottled ceiling, not as supply-independence",
    "manuscript_action": "PENDING AUTHOR DECISION -- Section 3.2's supply-independence wording needs replacing",
}

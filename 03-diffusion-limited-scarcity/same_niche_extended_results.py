"""
EXTENDED-DURATION CHECK ON THE SECTION 4.5 SAME-NICHE CONTROLS

WHY
---
Section 6 named the first-calibration lottery baselines as the paper's last
unchecked category. Auditing that turned out two things.

First, the named baselines are ALREADY convergence-checked: the Section 4.1
diffusion sweep (RESULTS_D_BG_0_05, 30 seeds/point), the Section 4.2 cost sweep
(RESULTS_ALPHA_SWEEP), and all three Section 4.3/4.4 lottery baselines
(convergence_audit_results_dn_and_highlife.py, 30 seeds each, max_steps
recorded). Section 6's statement was stale.

Second, the genuinely unchecked experiment was Section 4.5's same-niche
controls, which run on a FIXED 4,000-step budget (MAX_STEPS in
stage1_gause_neutral_competition.py and stage6_briansbrain_neutral_tag.py) with
a single 20,000-step extension for the unconstrained condition only -- never
under the convergence protocol.

FINDING -- THE GATED GAME-OF-LIFE CLAIM DOES NOT SURVIVE
---------------------------------------------------------
Section 4.5 states that Game of Life's energy-gated same-niche drift "never
completed fixation within any duration tested", and Sections 5.2 and 7 use the
Game-of-Life-freezes / Brian's-Brain-completes contrast as the paper's strongest
evidential argument.

Extended to 40,000 steps, Game of Life's gated drift DOES complete in a
substantial minority of seeds:

    seeds 0-3   : fixation at 12783, 19468, none, none   -> 2/4
    seeds 4-11  : fixation at 24435, 25508, 17348        -> 3/8
    combined    : 5 of 12 seeds fixed, all beyond step 12,000

Every fixation occurs at least three times later than the 4,000-step budget the
published figure used, so the original measurement could not have seen them.

FINDING -- THE UNCONSTRAINED CLAIM HOLDS
-----------------------------------------
Unconstrained Game of Life, extended to 40,000 steps, 6 seeds: NO fixation in
any trial. Populations collapse to a small low-turnover remnant (107-168 live
cells) and the tag fraction sits mid-range (0.16-0.50) without resolving. This
is the genuine freeze the absorbing-state property predicts -- reproduction
effectively ceases, so drift has no mechanism left to resolve through.

WHAT THIS MEANS FOR THE CRITERION
----------------------------------
The qualitative claim survives in the UNCONSTRAINED condition and fails in the
GATED one, and the reason is the Section 3.2 result: energy gating PREVENTS Game
of Life from reaching an absorbing configuration. Under gating the population
stays large and churning (~1,800 cells), so births and deaths continue and drift
retains a mechanism to resolve through. It resolves slowly, but it resolves.

The contrast with Brian's Brain is therefore quantitative under gating, not
qualitative:

    Brian's Brain, gated : 12/15 fixed within 4,000 steps, mean step 1,603
    Game of Life,  gated : 0/12 fixed within 4,000 steps; 5/12 by 40,000,
                           earliest fixation step 12,783

Brian's Brain fixes at least an order of magnitude faster. That is a real,
structurally explicable difference and it remains good evidence. It is not the
"cannot complete versus completes" contrast the manuscript currently asserts.

MANUSCRIPT ACTION -- PENDING AUTHOR DECISION
---------------------------------------------
Section 4.5's gated Game-of-Life claim needs restating, and Sections 5.2 and 7
need checking, since both lean on this as one of two predicted-in-advance
results.
"""

GOL_GATED_40K = {
    "condition": {"D_bg": 0.05, "D_diff": 0.05, "max_steps": 40000},
    "fixation_step_by_seed": {0: 12783, 1: 19468, 2: None, 3: None,
                              4: None, 5: None, 6: None, 7: 24435,
                              8: None, 9: None, 10: 25508, 11: 17348},
    "fixed": 5, "n_seeds": 12,
    "earliest_fixation": 12783,
    "published_budget": 4000,
    "note": "every fixation lies beyond 3x the published budget",
}

GOL_UNCONSTRAINED_40K = {
    "condition": {"max_steps": 40000},
    "fixation_step_by_seed": {s: None for s in range(6)},
    "fixed": 0, "n_seeds": 6,
    "final_population": [129, 108, 107, 168, 113, 111],
    "final_tag_fraction": [0.4419, 0.2222, 0.1589, 0.5000, 0.4513, 0.4685],
    "note": "genuine freeze -- reproduction ceases, drift has no mechanism left",
}

BB_PUBLISHED_4K = {
    "gated": {"fixed": 12, "n_seeds": 15, "mean_fixation_step": 1603, "budget": 4000},
    "unconstrained": {"fixed": 9, "n_seeds": 15, "mean_fixation_step": 173, "budget": 4000},
    "source": "Section 4.5 as originally published, 4,000-step budget",
    "superseded_by": "MATCHED_BUDGET_40K, which re-runs Brian's Brain at 40,000 steps. "
                     "The longer window turns 12/15 into 10/10 gated: the three trials the "
                     "short budget missed all fixed by step 5,487.",
}

# Retained under the old name so external references keep resolving.
BB_REFERENCE = BB_PUBLISHED_4K

CONCLUSION_FIRST_PASS = {
    "section_6_claim": "STALE -- the named lottery baselines were already convergence-checked",
    "actual_gap": "Section 4.5's same-niche controls, fixed 4,000-step budget",
    "unconstrained_claim": "HOLDS at 40,000 steps",
    "gated_claim": "FAILS -- 5 of 12 seeds fix, earliest at step 12,783",
    "criterion_status": "survives unconstrained; quantitative rather than qualitative under gating",
    "SUPERSEDED": "This was written before Brian's Brain was re-run at the matched budget, and "
                  "therefore compared Game of Life at 40,000 steps against Brian's Brain at "
                  "4,000. Read MATCHED_BUDGET_CONCLUSION instead: at equal budget the gated "
                  "ranges do not overlap, which is stronger than 'quantitative'.",
}

# ---------------------------------------------------------------------------
# MATCHED-BUDGET COMPARISON (added after the first pass, which compared Game of
# Life at 40,000 steps against Brian's Brain at the published 4,000 -- an uneven
# comparison of exactly the kind this project has flagged elsewhere).
# Both rules re-run at 40,000 steps, same conditions, same seed convention.
# ---------------------------------------------------------------------------

MATCHED_BUDGET_40K = {
    "gated": {
        "condition": {"D_bg": 0.05, "D_diff": 0.05, "max_steps": 40000},
        "BB":  {"fixed": 10, "n_seeds": 10,
                # BY SEED. The sorted list below is derived from this and kept only
                # for readability -- a spot check must compare against by_seed, not
                # against a slice of the sorted list.
                "by_seed": {0: 4013, 1: 4112, 2: 151, 3: 3868, 4: 2340,
                            5: 5487, 6: 1052, 7: 151, 8: 2858, 9: 2200},
                "fixation_steps": [151, 151, 1052, 2200, 2340, 2858, 3868, 4013, 4112, 5487],
                "latest": 5487},
        "GoL": {"fixed": 5, "n_seeds": 12,
                # BY SEED (None = no fixation within 40,000 steps).
                "by_seed": {0: 12783, 1: 19468, 2: None, 3: None, 4: None, 5: None,
                            6: None, 7: 24435, 8: None, 9: None, 10: 25508, 11: 17348},
                "fixation_steps": [12783, 17348, 19468, 24435, 25508],
                "earliest": 12783},
        "separation": "NON-OVERLAPPING -- every Brian's Brain fixation (max 5,487) precedes "
                      "every Game of Life fixation (min 12,783), a factor of 2.3 between the "
                      "closest pair and far more at the medians",
    },
    "unconstrained": {
        "condition": {"max_steps": 40000},
        "BB":  {"fixed": 7, "n_seeds": 10,
                "fixation_steps": [118, 125, 154, 177, 186, 199, 242], "latest": 242},
        "GoL": {"fixed": 0, "n_seeds": 6,
                "fixation_steps": [],
                "final_population": [129, 108, 107, 168, 113, 111],
                "final_tag_fraction": [0.4419, 0.2222, 0.1589, 0.5000, 0.4513, 0.4685]},
        "separation": "QUALITATIVE -- Brian's Brain completes in 7 of 10 by step 242; "
                      "Game of Life completes in none of 6 by step 40,000",
    },
}

MATCHED_BUDGET_CONCLUSION = {
    "unconstrained": "qualitative contrast, as originally claimed: freeze versus completion",
    "gated": "quantitative contrast, but with NON-OVERLAPPING ranges at matched budget -- "
             "stronger evidence than the published 4,000-step framing, not weaker",
    "registered_prediction": "INTACT. The prediction recorded in Section 4.5 was about Brian's "
                             "Brain -- that its populations cannot freeze, so fixation should be "
                             "directly observable rather than only asymptotically approached. "
                             "That held in every condition and at every budget tested (10/10 "
                             "gated, 7/10 unconstrained at 40,000 steps). What failed was the "
                             "comparative gloss added around it, that Game of Life 'never "
                             "completed fixation within any duration tested'.",
}


CAVEATS = {
    "fixation_rates_are_window_limited": (
        "5 of 12 gated Game-of-Life seeds fixed BY 40,000 steps. That is a lower bound on the "
        "eventual rate, not an asymptotic value -- three of the five fixations occurred after "
        "step 19,000, so a longer budget would plausibly add more. The same applies to Brian's "
        "Brain unconstrained (7 of 10). Claims in the manuscript are phrased as counts at a "
        "stated budget for this reason, and should stay that way. This is the identical failure "
        "mode this record exists to document; it is bounded here, not eliminated."),
    "seed_sets_are_not_matched": (
        "Matched BUDGET, not matched SEEDS. Gated: Game of Life seeds 0-11 (n=12), Brian's Brain "
        "seeds 0-9 (n=10). Unconstrained: Game of Life seeds 0-5 (n=6), Brian's Brain seeds 0-9 "
        "(n=10). Seed k does not denote a comparable initial condition across two different "
        "rules in any case, so this affects statistical power rather than validity."),
    "unconstrained_GoL_n_is_small": (
        "The qualitative freeze claim rests on 6 seeds with zero fixations. The effect is stark "
        "-- populations collapse to 107-168 cells and tag fractions sit mid-range -- but n=6 is "
        "thin for a claim the manuscript leans on. Cheap to extend if challenged."),
    "sorted_lists_are_not_seed_indexed": (
        "fixation_steps is SORTED across seeds. A spot check that compares its first k "
        "entries against seeds 0..k-1 will fail spuriously -- this happened once. Compare "
        "against by_seed, which was added afterwards for exactly this reason."),
    "duplicated_data": (
        "GOL_GATED_40K and MATCHED_BUDGET_40K['gated']['GoL'] hold the same five fixation steps. "
        "Verified identical at the time of writing. If either is ever edited, edit both."),
}

AUTHORITATIVE = {
    "read_this_first": "MATCHED_BUDGET_40K and MATCHED_BUDGET_CONCLUSION",
    "superseded": ["CONCLUSION_FIRST_PASS", "BB_PUBLISHED_4K"],
    "manuscript_status": (
        "APPLIED. Section 4.5 now separates the unconstrained and gated regimes and reports "
        "matched-budget numbers; Sections 5.2 and 7 state the registered prediction (Brian's "
        "Brain cannot freeze, so its fixation is observable) rather than the comparative gloss. "
        "Section 6's largest-open-item paragraph was replaced."),
}

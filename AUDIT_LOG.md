# Protocol Audit Log — Tier C

Line-by-line read of the runner/protocol files, per `VERIFICATION.md` Tier C.

These files implement the measurement protocol rather than an experiment. A bug
here corrupts everything downstream *silently* — the numbers would still
reproduce perfectly and still be wrong, which is precisely the failure mode
`spot_check.py` cannot detect. That is why this tier is reading rather than
running, and why it is worth doing carefully.

Read by D.H. Yoo. Findings recorded as they are made, so that the §2.3 rewrite
happens once against the complete picture rather than piecemeal.

---

## Progress

| # | File | Read |
|---|---|---|
| 1 | `03/stage_convergence_runner.py` | done |
| 2 | `03/stage_convergence_runner_cost.py` | done |
| 3 | `03/stage_convergence_runner_general.py` | done |
| 4 | `03/stage_convergence_runner_gol_dn.py` | done |
| 5 | `03/stage_adaptive_complexity_runner.py` | done |
| 6 | `03/stage_adaptive_complexity_runner_gol_dn.py` | done |
| 7 | `04/stage_convergence_runner_displacement_cost.py` | done |
| 8 | `04/stage_convergence_runner_flagship_cost.py` | done |
| 9 | `04/stage_convergence_runner_highlife.py` | done |

Four things to check in each, from `VERIFICATION.md`:

1. **Settling criterion** — does "converged" mean what §2.3 says it means?
2. **Drift classification at cap** — are unresolved trials classified by drift
   direction, or only flagged?
3. **Ceiling / flip_cost argument order** — the flagship module's signature is
   `(..., bb_cost_multiplier, flip_cost, ceiling, ...)`, so a positionally-passed
   ceiling lands on `flip_cost` and silently rescales every cost in the run.
4. **Warmup and check-interval scaling with α** — high-cost conditions need
   roughly `α / D_bg` steps of pure accumulation before the first affordable
   transition; held fixed, those conditions never begin.

---

## Entries

### 1. `03-diffusion-limited-scarcity/stage_convergence_runner.py`

| Check | Finding |
|---|---|
| Settling criterion | Specialised but intentional for the GoL-vs-BB lottery |
| Drift classification at cap | **Only flags `converged=False`; no drift direction** |
| Ceiling / flip_cost order | N/A — no cost or ceiling arguments |
| Warmup scaling with α | N/A — no α |

---

### 2. `03-diffusion-limited-scarcity/stage_convergence_runner_cost.py`

| Check | Finding |
|---|---|
| Settling criterion | Same specialised rule as the lottery runner (GoL freeze + average); appropriate for this pairing |
| Drift classification at cap | **Only flags `converged=False`; no drift direction** |
| Ceiling / cost arguments | Safe — both passed by keyword |
| Warmup & check-interval scaling with α | Correct — both scale as `~α / D_bg` |

**Verified positive.** `min_warmup_for_alpha = int(3 * bb_cost_multiplier / D_bg)`,
and `check_interval` scales the same way. This confirms the Appendix A Table A2
row on warmup scaling. The file's own comment states the reason: without scaling
the check interval, a high-α run could be falsely declared frozen simply because
the check fires before anything can happen.

---

### 3. `03-diffusion-limited-scarcity/stage_convergence_runner_general.py`

| Check | Finding |
|---|---|
| Settling criterion | **Matches §2.3 more closely** — trailing-average stability of the measured quantity |
| Drift classification at cap | Only flags `converged=False`; no drift direction |
| Ceiling / cost arguments | Safe — keywords |
| Warmup & check-interval scaling with α | Yes |

**Verified positive.** `rel_tol = 0.05`, with `tol = max(1.0, rel_tol * prev)`
applied to both species' block means, requiring agreement over consecutive
checks. The floor of 1.0 cell is a sensible guard: without it, a species at a
count of 2 would need to hold within 0.1 cells, which is unachievable in a
discrete population and would prevent convergence being declared at all.

The file's own docstring states it is "a strictly more general version of the
freeze-detection method" used by runners 1 and 2 — written because Day and Night
does not freeze into an exactly-fixed population the way Game of Life does.

---

### 4. `03-diffusion-limited-scarcity/stage_convergence_runner_gol_dn.py`

| Check | Finding |
|---|---|
| Settling criterion | **Closest match to §2.3 so far** — trailing block-mean stability within relative tolerance for both species, plus extinction |
| Drift classification at cap | Only sets `converged=False`. **Non-converged trials must not be averaged into reported means by the caller.** |
| Ceiling / flip_cost order | N/A — this module's `landauer_gated_step` takes no cost or ceiling arguments |
| Warmup / check-interval scaling with α | N/A — symmetric cost only; fixed warmup and interval are appropriate |

The delegated responsibility flagged here turned out to be the most consequential
finding of the audit. See F3.

---

### 5. `03-diffusion-limited-scarcity/stage_adaptive_complexity_runner.py`

| Check | Finding |
|---|---|
| Settling criterion | **Deliberate, documented relaxation.** §2.3's population-style rule is replaced by successive-block agreement of `C` within 5%, hard-capped at 40,000 steps. Matches the adaptive complexity protocol as described in §2.3 and §3.3. |
| Drift classification at cap | Only flags `converged=False`; no drift-direction classification. Callers must not treat capped seeds as fully settled without noting them — the paper does mark open rings for high not-converged points. |
| Ceiling / flip_cost order | N/A — single-rule diffusive step, no cost multiplier or dynamic ceiling in this path |
| Warmup / interval scaling with α | N/A — no cost asymmetry |

---

### 6. `03-diffusion-limited-scarcity/stage_adaptive_complexity_runner_gol_dn.py`

| Check | Finding |
|---|---|
| Settling criterion | Same documented adaptive rule as entry 5 — successive-block agreement of `C` within 5%, hard cap 40,000 steps. Matches the manuscript's adaptive complexity protocol. |
| Drift classification at cap | Only flags `converged=False`; no drift-direction classification. High not-converged points should be marked, as Figure 2's open rings do. |
| Ceiling / flip_cost order | N/A — single-rule diffusive step; birth/survive sets passed explicitly; no cost multiplier or dynamic ceiling |
| Warmup / interval scaling with α | N/A — no cost asymmetry |

---

### 7. `04-contestable-occupancy/stage_convergence_runner_displacement_cost.py`

| Check | Finding |
|---|---|
| Settling criterion | Strong match to §2.3 — extinction, or trailing block-mean stability within relative tolerance for both species |
| Drift classification at cap | **Yes.** Unconverged trials get `drift = late_share − early_share`. First runner in the set that implements the §2.3 drift-direction rule rather than only flagging non-convergence. |
| Ceiling / flip_cost order | **Positional, and safe — but only by coincidence of matching signatures.** See F4. |
| Warmup / check-interval scaling with α | Yes — both scale as `~α / D_bg`, consistent with the cost-asymmetry runners |

---

### 8. `04-contestable-occupancy/stage_convergence_runner_flagship_cost.py`

| Check | Finding |
|---|---|
| Settling criterion | Inherited from the displacement-cost runner — extinction or trailing block-mean stability within relative tolerance. Good match. |
| Drift classification at cap | Yes, inherited; unconverged trials carry `drift = late − early share` |
| Ceiling / flip_cost order | **Fixed by design.** The shim passes `ceiling` and the cost multiplier by keyword, so the eighth-position trap of F4 cannot occur. |
| Warmup / check-interval scaling with α | Yes — inherited from the shared runner, `~α / D_bg` |

**Note on provenance.** This file was written by the AI assistant during the
flagship re-run; entries 1–7 and 9 audit pre-existing code. It is therefore the
one file where author and auditor differ, which is the right way round.

**Additional check performed: cross-module comparability.** The shim omits the
flagship's `energy_on_capture_transfer` argument, taking its default. If the
stage6 modules implemented a different capture-energy convention, the three
pairings compared in §4.7 would not be strictly comparable. Verified line by
line — all three are identical:

```python
energy_next = np.where(actually_flips & capture_happened, 0.0,
               np.where(actually_flips & ~capture_happened, normal_next, energy))
```

Stage6a and 6b hardcode this; the flagship has it as the
`energy_on_capture_transfer = False` branch, which is its default and therefore
what the shim inherits. Shared constants also match across all three:
`N = 64`, `FLIP_COST = 1.0`, `WARMUP_STEPS = 200`, `INIT_DENSITY_EACH = 0.10`,
with the ceiling supplied by the caller in every case.

**§4.7's three-pairing comparison is sound.**

---

### 9. `04-contestable-occupancy/stage_convergence_runner_highlife.py`

| Check | Finding |
|---|---|
| Settling criterion | Good match to §2.3 — extinction or trailing block-mean stability within relative tolerance for both species |
| Drift classification at cap | No — only flags `converged=False`. Cap trials must not be averaged in without an explicit policy. |
| Ceiling / flip_cost order | N/A — no cost multiplier or dynamic ceiling. **Four-value return handled by an explicit four-way unpack** |
| Warmup / check-interval scaling with α | N/A — symmetric cost only |

**Verified positive.** The explicit four-way unpack is the correct handling of a
module whose step returns four values, and is exactly the assumption whose
absence created the flagship trap in F4. Its banked results
(`RESULTS_GOL_VS_HIGHLIFE` and companions) carry no unconverged trials, so the
delegated averaging policy is untested but also unexercised.

---

## F4 — RESOLVED, fix applied and verified

`stage_convergence_runner_displacement_cost.py` line 67 now passes `ceiling` by
keyword and carries a comment stating the interface any module used with this
runner must present, including an explicit warning that the flagship module does
not match and needs the shim.

**Verified no behaviour change.** STAGE6A cell `(K=1, α=1)`, 10 seeds, re-run
after the edit:

    banked      mean 1.0000  sd 0.0000
    after fix   mean 1.0000  sd 0.0000   -> IDENTICAL

---

## AUDIT COMPLETE — 9 of 9 protocol files read

**No wrong numbers were found in the paper.** Every banked result stands.

| Finding | Nature | Status |
|---|---|---|
| F1 | §2.3 describes one straggler treatment; three exist | **resolved** — closed by the §2.4 rewrite |
| F2 | §2.3 describes one settling detector; two (in fact three) exist | **resolved** — closed by the §2.4 rewrite |
| F3 | §3.3 understates how many points carry unconverged seeds | **resolved** — closed by the §3.3 rewrite |
| F4 | Undocumented positional-argument convention | **resolved** — fix applied and verified |

**All four findings are now resolved.** F1–F3 were closed by the consolidated
manuscript rewrite that moved the convergence protocol into its own §2.4 and
restated §3.3: the protocol is now described as the three-detector, three-straggler-
treatment procedure the code actually implements (§2.4 states plainly that "Three
detectors are therefore used"), and §3.3 now reports that 16 of 18 points carry
unconverged seeds at 1–7 of 10 each, with the drift-direction diagnostic and the
Figure 2 open-ring disclosure. F4 was fixed in code (keyword-passing) and verified
byte-identical on a banked cell. Nothing below is outstanding; the entries are
retained as the record of what the audit found and how each was closed.

Three of the four findings are the same defect in different places: the methods
section describes the protocol as more uniform than the code implements it. In
every case the code's variation is a *deliberate and correct* response to the
situation — an exact-freeze detector where a rule admits absorbing
configurations and a tolerance detector where it does not; extension to
resolution where stragglers were few and automated drift classification where
they were many. The paper undersells its own methodological care by describing
a single procedure.

**F2 is worth more than a correction.** (The audit originally identified two
freeze detectors; the §2.4 rewrite that closed the finding ultimately described
three — see the status table above. The point below stands unchanged.) The reason
distinct freeze detectors exist is that Game of Life reaches absorbing
configurations readily and Day and Night does not — the same property §3.2 now quantifies at 0.456 against 0.837, and that §6
raises as the binary-versus-graded question. Stating that in §2.3 turns an
apparent inconsistency into evidence for the paper's central claim.

**Positive findings recorded** (an audit showing only defects is a bug list, not
an audit): α-scaling correct in entries 2, 3, 7 and 8; the one-cell tolerance
floor in entry 3; identical capture-energy accounting across all three §4.7
pairings in entry 8; correct four-way unpack in entry 9.

The consolidated manuscript rewrite described above — touching §2.3, §3.3, §4.2
and §6, and promoting the convergence protocol to its own §2.4 — has been
completed. F1–F3 are closed by it (see the status table above).

---

## F4 (original entry). A positional call convention that is load-bearing and undocumented

**Status:** resolved (fix applied and verified byte-identical on a banked cell; see
the status table above). No wrong numbers. The text below is the original entry,
retained as the record of the hazard that was found and corrected.

Line 67 calls the module's step function with eight positional arguments:

```python
mod.landauer_gated_step(state, energy, D_BG, D_DIFF, rng, K,
                        cost_multiplier, dynamic_ceiling)
```

Verified against every module this runner targets:

| Module | Signature | Matches? |
|---|---|---|
| `stage6a_cost_displacement_dayandnight.py` | `(state, energy, D_bg, D_diff, rng, K, bb_cost_multiplier, ceiling)` | yes |
| `stage6b_cost_displacement_highlife.py` | `(state, energy, D_bg, D_diff, rng, K, b6_cost_multiplier, ceiling)` | yes |
| `stage_cost_displacement.py` (flagship) | `(..., bb_cost_multiplier=1.0, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING, ...)` | **NO** |

**STAGE6A and STAGE6B are correct.** Both targets match the call, so the banked
displacement-cost results are sound.

**The flagship does not match, and the mismatch is silent.** `flip_cost` sits
between the multiplier and the ceiling in its signature, so the eighth positional
argument — intended as the dynamic ceiling — lands on `flip_cost` and rescales
every cost in the run. It would not raise; it would produce plausible, wrong
numbers. This is why `stage_convergence_runner_flagship_cost.py` wraps the
flagship in a shim that passes `ceiling` by keyword.

**Assessment.** Nothing is broken. But the correctness of a whole family of
results rests on an argument-order convention that is written down nowhere, and
one module in the same directory already violates it. Anyone adding a fifth
pairing has a good chance of reproducing the trap.

**Proposed fix — code hygiene, not a manuscript change:**

1. Pass `cost_multiplier` and `ceiling` by keyword at line 67, as the flagship
   runner already does. Both stage6 modules accept the names, so this is a
   two-line change that makes the call self-validating.
2. Add a one-line comment stating the required interface for any module used
   with this runner.

No re-run needed — keyword passing resolves to the identical arguments.

---

## F1 — RESOLVED. The drift check exists; it was hand-performed and recorded

Six of nine runners read. Neither complexity runner automates drift
classification, but the check itself was performed and is documented in
`convergence_audit_results_section3_gol_dn_complexity.py`:

```
'test': 'GoL, D_diff=0.05, non-converged seeds block-history drift direction'
'negative_drift': 2, 'positive_drift': 5, 'flat': 0
'conclusion': 'mixed drift signs + tight clustering of block values =
               sampling noise, not genuine dynamical drift (contrast with
               Section 4.2 alpha=3, where drift was consistently one-directional)'
```

The reasoning is sound and the contrast with §4.2 is the right control: a
genuine unresolved transition drifts one way, sampling noise does not.

**Three different straggler treatments exist, all defensible, none matching
§2.3's single uniform description:**

| Site | Treatment | Evidence |
|---|---|---|
| §4.2, `α ≈ 3` | Extended individually to resolution, past 100,000 steps | `RESOLVED_STRAGGLERS` |
| §3.3 complexity | Hand-performed drift-direction diagnostic | `FINDING_2` in the gol_dn record |
| §4.6/4.7 displacement-cost | Automated drift classification in the runner | 14 and 6 mentions in those two runners |

**Residual issue — scope.** §3.3 and §6 both say "a drift-direction check
indicates residual sampling noise", generalising across every threshold-edge
point of all three rules. The check was run on **one point of one rule** — Game
of Life at `D_diff = 0.05`, 7 seeds. That is a reasonable spot diagnostic and
its conclusion is probably right, but the manuscript states it as though it
covered the affected points generally.

Fix: say what was checked. "A drift-direction diagnostic on the worst-affected
Game of Life point (7 of 10 seeds unconverged) found mixed drift signs and
tightly clustered block values, indicating sampling noise rather than unresolved
dynamics; the same was not separately checked at every affected point."

---

## Consolidated manuscript rewrite — ready to apply

All three findings are now settled for the §3 sections. Remaining entries 7–9
are the `04/` runners, which are the ones that *do* implement drift
classification, so they can only confirm F1 rather than change it.

**§2.3** — replace the single uniform settling rule and the blanket
drift-classification sentence with what was actually done: settling detected by
whichever signal the pairing makes available (exact frontier freeze where a rule
admits one, block-mean stability otherwise, successive-block agreement for the
complexity measure), and stragglers handled by extension to resolution, by
hand-performed drift diagnostic, or by automated drift classification depending
on how many there were. Note that which freeze detector applies is itself
determined by the absorbing-state property under study (F2).

**§3.3** — replace "several debiased points, particularly near each rule's
threshold" with the actual counts (16 of 18 points; 7 of 10 seeds at the worst),
state that means include unconverged trials, point at Figure 2's open rings as
the per-point indicator, and narrow the drift-check claim to the one point it
covers.

**§4.2** — replace "classified by drift direction (§2.3)" with extension to
resolution, pointing at `RESOLVED_STRAGGLERS`.

**§6** — same narrowing of the drift-check claim as §3.3.

**Appendix A** — optionally add the per-point unconverged counts.

---

## F3 — SEVERITY REVISED DOWN after entry 5

The parenthetical in entry 5 (that the paper marks open rings) was checked
against `make_figures.py` and is correct. This materially changes F3.

`make_figures.py` line 166 draws open rings for points where ≥40% of seeds had
not converged, and Figure 2's caption states the rule explicitly. Which points
that marks:

| Sweep | not-converged per point | Ringed (≥4/10) | Affected but unringed |
|---|---|---|---|
| Game of Life | 3, 7, 5, 7, 6, 5 | 5 of 6 | 1 (at 3/10) |
| Day and Night | 2, 6, 3, 5, 5, 5 | 4 of 6 | 2 (at 2/10, 3/10) |
| Brian's Brain | 0, 3, 5, 2, 1, 0 | 1 of 6 | 3 (at 3/10, 2/10, 1/10) |

So **10 of 18 points are visibly marked**, including both 7-of-10 Game of Life
cases. The six affected-but-unringed points all sit at 1–3 unconverged seeds of
10, which is within the tolerance the ring threshold was chosen to express.

**Revised assessment.** The disclosure exists, in the figure, at the point of
use, with a stated threshold. That is better practice than a prose caveat. What
remains wrong is narrower than first logged:

- §3.3's prose says *"several debiased points, particularly near each rule's
  threshold"*. Neither half is accurate: 16 of 18 points carry some unconverged
  seeds, and the ringed ones are not concentrated at thresholds — Game of Life
  rings every point except the first.
- The prose does not state that reported means *include* unconverged trials.
  A reader could take the rings to mean those points were excluded or handled
  differently, rather than averaged in like the rest.

**Revised fix — prose only, no re-run:**

1. §3.3: replace "several points, particularly near each rule's threshold" with
   the actual counts, and state plainly that means include unconverged trials.
2. Point at Figure 2's rings as the per-point indicator, which already exists.
3. Optionally put the full per-point counts in Appendix A.

Downgraded from "highest severity, re-run may be required" to "prose accuracy,
cheap fix". Recording the downgrade rather than editing the original entry: an
audit that only ever escalates is not being read critically.

---

## F1 — nearly resolved

Entry 5 confirms `stage_adaptive_complexity_runner.py` does **not** classify by
drift direction. Combined with the grep (`_gol_dn` variant: zero mentions), the
"drift-direction check" that §3.3 and §6 both cite has no implementation in
either complexity runner.

Remaining possibilities: it was performed by hand and recorded somewhere, or it
is an overstatement carried over from the displacement-cost runners where drift
classification genuinely does exist. **Entry 6 settles it.** If no code and no
record turns up, the phrase must go from both §3.3 and §6.

---

### F3. Unconverged trials are averaged into reported means, and §3.3's disclosure understates how often

**Status:** open. **Highest severity of the findings so far.** Manuscript edit
required; a re-run may or may not be.

**The mechanism.** Every sweep-level aggregator appends the trial's share
unconditionally and reports `not_converged` as a *separate count* alongside:

```python
shares.append(r['a_territory_frac'])      # unconditional
...
if not r['converged']:
    not_converged.append(seed)            # counted, not excluded
mean_share = float(np.mean(shares))       # includes unconverged trials
```

So a reported mean is over all seeds, converged or not. Entry 4's caveat — that
the caller must exclude them — is not honoured anywhere.

**Scope: Section 4 is clean, Section 3.3 is not.** Scanning every banked record
for cells with a non-zero unconverged count:

| Record | Cells with unconverged trials folded into the mean |
|---|---|
| `convergence_audit_results.py` (§4.1) | none |
| `convergence_audit_results_cost.py` (§4.2) | none |
| `convergence_audit_results_dn_and_highlife.py` (§4.3/4.4) | none |
| `convergence_audit_results_displacement_cost.py` (§4.6/4.7) | none |
| `convergence_audit_results_flagship_cost.py` (§4.7) | none |
| **§3.3 complexity sweeps** | **16 of 18 points** |

Every competitive result in the paper is unaffected. The problem is confined to
the debiased complexity profiles, which are plotted in Figure 2.

**The rates, per point, out of 10 seeds:**

| Sweep | Unconverged per point |
|---|---|
| Game of Life | 3, 7, 5, 7, 6, 5 — **6 of 6 points affected** |
| Day and Night | 2, 6, 3, 5, 5, 5 — **6 of 6 points affected** |
| Brian's Brain | 0, 3, 5, 2, 1, 0 — 4 of 6 points affected |

**Why this is a disclosure problem.** §3.3 currently says:

> Several debiased points, particularly near each rule's threshold, retain
> unconverged seeds at the 40,000-step cap.

"Several ... particularly near each rule's threshold" describes a minority
concentrated at the edges. The reality is 16 of 18 points, spread across the
whole sweep, with **7 of 10 seeds unconverged** at two Game of Life points. A
majority-unconverged mean is being plotted as a data point without that being
visible to the reader.

**What is not wrong.** The unconverged trials are not garbage — they are runs
that had not met the 5% relative-tolerance criterion at the 40,000-step cap,
which for a slowly-relaxing complexity measure is a demanding test. Including
them is a defensible choice. Reporting it as "several points near the threshold"
is not.

**Proposed fix, in order of preference:**

1. **Restate §3.3 accurately** — give the actual counts, state that means include
   unconverged trials, and say why that is defensible. Cheapest, honest,
   probably sufficient.
2. **Add the counts to Figure 2** — the caption already flags open rings for
   points where ≥40% of seeds had not converged; extend that to all points, or
   put the per-point count in Appendix A.
3. **Re-run at a higher cap** to see whether the profile shape moves. Expensive
   (the complexity measurement is the costly one) and unlikely to change the
   qualitative result, but it is the only route that removes the caveat rather
   than describing it.

**Unresolved dependency.** §3.3 and §6 both refer to "a drift-direction check"
supporting the claim that these are sampling noise rather than unresolved
dynamics. `stage_adaptive_complexity_runner.py` contains a single mention of
drift and `stage_adaptive_complexity_runner_gol_dn.py` contains none. Entries 5
and 6 must establish whether that check exists in code, was done by hand, or is
an overstatement. **Do not edit §3.3 until that is settled** — F1 and F3 both
land on the same sentences.

---

### F2. §2.3 states one settling criterion; the runners implement two, for a good reason it does not give

**Status:** open, manuscript edit pending. Fold into the same §2.3 rewrite as F1.

§2.3 currently reads:

> A trial counts as settled when one of three things happens: the configuration
> freezes, one species goes extinct, or the trailing average of the measured
> quantity stops changing to within a fixed relative tolerance over a long block.

That is accurate as a *disjunction of what appears somewhere in the codebase*,
but it hides that two structurally different detectors exist and that which one
applies depends on the pairing:

| Detector | Runners | Mechanism |
|---|---|---|
| Frontier freeze + trailing average | 1, 2 | Game of Life's count is the hard signal — it either goes extinct or freezes exactly. Once frozen for `FREEZE_CHECKS` consecutive checks, Brian's Brain's fluctuating count is averaged over a 5,000-step window. |
| Block-mean stability | 3 | Both species' block means must agree within `rel_tol = 0.05` (floored at 1 cell) across consecutive checks. |

**Why the split exists, and why it is legitimate.** Game of Life settles into
still-lifes with a hard-frozen count, so an exact-freeze test is both available
and sharper than a tolerance test. Day and Night does not — its broader survival
condition keeps it cycling — so an exact-freeze detector would never fire and the
run would always hit the cap. Runner 3's docstring says exactly this.

This is a good design decision. The issue is only that §2.3 presents a single
uniform criterion, so a reader comparing the methods section against runner 1
finds a pairing-specific freeze detector that the text does not mention.

**Note the connection to §3.2.** The reason Game of Life freezes exactly and Day
and Night does not is the same absorbing-configuration-reachability difference
that §3.2's ceiling values now quantify (0.456 versus 0.837) and that §6 raises
as the binary-versus-graded question. The two detectors are not an
implementation inconvenience; they are a consequence of the paper's own
criterion. Saying so in §2.3 would turn an apparent inconsistency into a point
in the paper's favour.

**Proposed fix:** in the same §2.3 rewrite as F1, state that settling is
detected by whichever signal the pairing makes available — exact frontier freeze
where a rule admits it, block-mean stability otherwise — and note that which
applies is itself determined by the absorbing-state property under study.

### F1. §2.3 describes drift classification as a general property of the protocol; the code does not implement it that way

**Status:** open, manuscript edit pending, do not fix piecemeal.

§2.3 currently reads:

> Trials that reach the cap without settling are neither discarded nor averaged
> in blindly. Each is classified instead by the *direction* it is drifting — the
> outcome it is still moving toward.

Grep across all nine runners for drift handling:

| Runner | Mentions of `drift` |
|---|---|
| `04/stage_convergence_runner_displacement_cost.py` | 14 |
| `04/stage_convergence_runner_flagship_cost.py` | 6 |
| `03/stage_adaptive_complexity_runner.py` | 1 |
| the other six | 0 |

So drift classification is implemented in **2 of 9** runners. The rest only set
`converged=False`.

**What actually happened instead, and it is defensible.** For the §4.2 `α ≈ 3`
zone the stragglers were resolved *individually, by extension* rather than by an
automated rule, and each is documented in
`convergence_audit_results_cost.RESOLVED_STRAGGLERS` — for example seed 3 at
`α = 3`, unconverged at 40,000 steps with share 0.094, re-run past 100,000 steps
to share 0.9994 with a single Brian's Brain cell remaining. Six such at `α = 3`,
all resolving to Game-of-Life-total. One at `α = 10` was classified from a
consistently low, non-increasing share rather than chased to full precision.

Extending a trial until it actually resolves is *stronger* evidence than
classifying its drift direction at a cap. The problem is not the method; it is
that the paper describes a different method from the one used.

**Why this matters more than a wording slip.** §4.2 says: *"trials still
undecided at the protocol cap are classified by drift direction (§2.3)."* The
runner that produced those very numbers — entry 2 above — does not implement
drift classification. The claim is wrong at the specific site that cites it, not
merely loose in the abstract.

**Proposed fix, to be applied once the remaining seven files are read:**

- §2.3 — describe both routes: stragglers extended individually to resolution
  where few, with each recorded in the banked audit files; automated
  drift-direction classification in the displacement-cost runners where
  stragglers were numerous.
- §4.2 — replace "classified by drift direction" with extension to resolution,
  pointing at `RESOLVED_STRAGGLERS`.
- §3.3 and §6 — check the phrase "a drift-direction check" against whichever
  runner actually produced those threshold-edge stragglers
  (`stage_adaptive_complexity_runner*.py`, entries 5 and 6, not yet read).

---

## Notes on method

Add an entry per file as it is read. Record positive findings as well as
defects — a verified-correct α-scaling is worth as much to a referee as a
caught bug, and it is the only evidence that the check was actually performed.

Where a finding implies a manuscript change, add it to the open-findings section
rather than editing immediately. Editing §2.3 twice from partial information is
how a methods section ends up describing neither what was done nor what was
intended.

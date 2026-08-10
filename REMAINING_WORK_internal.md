# DC — Remaining Work (internal reminder, NOT part of manuscript)

This is a working checklist kept out of the submitted paper. All *scientific* limitations
(flagship displacement-cost sweep provisional, C/Phi not re-measured, crossover/N=256 gaps,
lottery baselines, 3.1 not re-verified) are already stated in the manuscript's Section 5.4 —
deleting this list from the paper loses no disclosure.

---

## Open items before submission

1. **Figures**: COMPLETE. Eight figures, numbered by order of first mention, all placed in the manuscript with call-outs and captions. Figure 1 is the Landauer-gate schematic (TikZ, `figures/fig1_schematic.tex`, compiles standalone); Figures 2–8 are generated reproducibly from the banked convergence-audit records by `make_figures.py`, which also carries the LaTeX caption text in its `CAPTIONS` dict (keys `fig1`–`fig8`). Remaining: nothing, beyond dropping the PDFs into the LaTeX build.

2. **Consolidated parameters table**: COMPLETE. Appendix A holds three tables — shared parameters, measurement windows and stopping criteria, and seed counts by experiment — assembled from the experiment scripts and banked audit records rather than from the prose. Assembling it surfaced one gap (no seed count recorded for the debiased Section 3.3 GoL/D&N sweeps), which is now CLOSED: recovered as n = 10 by prefix identification, banked in `03-diffusion-limited-scarcity/seed_count_recovery_results.py`. The banked records reproduced exactly, which doubles as a reproducibility check on the Data and Code Availability claim.

3. **Displacement-competition follow-up work**: COMPLETE. Cost asymmetry under displacement has now been tested and re-run to convergence for all three pairings where a natural cost convention applies. The flagship (Game of Life vs. Brian's Brain) was the last one outstanding and is closed: `K = 1, 5, 8` x `alpha = 1, 20, 200` at 10 seeds, plus a finer sweep through `alpha = 2, 3, 4, 5, 10` at `K = 5` and `K = 8`, 130 runs with zero unconverged trials. Banked in `04-contestable-occupancy/convergence_audit_results_flagship_cost.py`; runner in `stage_convergence_runner_flagship_cost.py`. Two findings went into Section 4.6: outcomes are winner-take-all at every cost level (cost moves the bias, not the character), and the resulting curve reproduces Section 4.2's lottery cost sweep almost exactly, so for this pairing the cost transition is invariant to contest structure.

4. **Measurement-window adequacy audit**. Split by whether the gap affects something the paper REPORTS or only something the dataset lacks.

   *Affects a reported claim:* nothing outstanding. Item 4(a), the flagship displacement-cost sweep, is closed by item 3. Section 3.2's `C/Phi` defence was falsified by a surrogate test and replaced with the measured per-rule bias floors. Section 3.2's demand curves — the criterion's own foundation, and previously the paper's most exposed point — have been re-run under the long-window protocol (`02-landauer-gated-execution/demand_convergence_results.py`). That check changed the quantity the criterion is stated in, from total flux to demand per active cell at the unthrottled ceiling, and confirmed the criterion itself. An out-of-sample test on two rules absent from the rest of the paper, classified by transition-table inspection with the prediction recorded before measurement, put Life without Death at 0.000 and Seeds at 2.000 — both correct as to class, both at the extremes (`out_of_sample_rule_test_results.py`).

   *Dataset gaps that do not undercut a stated claim — disclosed, not blocking:* the precise crossover `D_diff` at N = 128/256, with the high-diffusion endpoint confirmed at 128 but not 256; Section 3.1's causal-insulation result, which uses the more bias-robust differential histogram estimator, not re-verified at long window; the two thin spots inside the earlier displacement-cost re-runs; `K = 3` for the flagship, omitted so the grid matches the other two; the unsampled `alpha = 1` to `alpha = 2` interval where the flagship's win-rate peak sits; and Brian's Brain's population decay on 64x64, which may be finite-size and was not tested at larger N. Several debiased Section 3.3 points near each rule's threshold retain unconverged seeds at the 40,000-step cap; a drift-direction check indicates sampling noise rather than unresolved dynamics, so those magnitudes are approximate.

   *Still genuinely open:* the lottery-only baselines in Sections 4.1-4.4 at the first background-inflow calibration have not been checked against the short-window failure mode. This is now the sole remaining item in this category and is stated in Section 6.

5. **arXiv category and formatting**: primary category (nlin.CG, cross-listed with cond-mat.stat-mech and possibly q-bio.PE) and LaTeX vs. clean-PDF pipeline not yet finalized.
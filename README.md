# Dissipative Computation

Code and findings supporting *"Dissipative Computation: Energetic Gating of Structure Formation and Competitive Dynamics in Discrete Systems."*

**[`DC_Manuscript.md`](DC_Manuscript.md) — full manuscript, Sections 1–5.** Its Section 5.4 states the scope and measurement limitations in full, including which results are convergence-verified and which remain open.

Physical computation is inherently dissipative: any process that changes a system's state does thermodynamic work, a constraint formalized for irreversible operations by Landauer's principle (Landauer, 1961). This repository investigates the consequences of that constraint for pattern formation, persistence, and multi-species competition in cellular automata, using a framework in which local energy availability gates whether a proposed state transition can execute at all. The framework is a deliberately simplified analogue of Landauer's principle — a fixed cost charged for state-changing transitions, with no temperature or thermal bath — rather than a physical realization of the `kT ln 2` bound.

## Repository structure

```
01-structure-formation/
    Does spontaneous structure formation require genuine non-equilibrium
    driving, or does it occur under fluctuation alone? Tested in a
    reaction-diffusion system and replicated on a discrete cellular
    automaton substrate. A separate extension tests whether attractor
    selection under simple attrition requires the same driving.

02-landauer-gated-execution/
    Does sustained energetic demand depend on a rule's own structure?
    An explicit Landauer-gated execution scheme -- energy gates whether
    a proposed transition can execute, not merely whether its result
    survives -- applied across three cellular automaton rule classes.

03-diffusion-limited-scarcity/
    Extends the gating mechanism to a shared, diffusing energy field
    rather than independent per-cell income. Findings include: structural
    complexity peaking near each rule's own energetic threshold and
    declining as the diffusion rate rises (a shared profile across rule
    classes, measured after correcting a finite-sample estimator bias);
    a diffusion-driven competitive transition and its refuge-effect
    mechanism; a cost-scaling sweep showing metabolic cost acts as a
    second control parameter that can itself reverse the outcome; further
    pairings mapping the regime-dependent competitive outcomes; and
    same-niche controls (on two different substrates) isolating the
    mechanism responsible for the competitive outcome.

04-contestable-occupancy/
    Tests whether the competitive outcomes from Section 03 survive
    once occupied territory becomes directly capturable under genuine
    displacement competition, not merely inherited upon vacancy under
    the original lottery-competition regime (terminology adopted from
    Levins & Culver, 1971; Tilman, 1994; Yu & Wilson, 2001). Finds the
    competitive ranking does not survive intact across the pairings
    tested -- one implementation choice reverses an entire pairing's
    outcome to complete extinction. A fourth, purpose-built pairing
    (Game of Life vs. HighLife) then disambiguates directional expansion
    capacity from absorbing-state absence -- a confound none of the
    Brian's Brain pairings could resolve on their own -- and supports
    absorbing-state absence, not expansion capacity, as the operative
    property. Integrated into the manuscript as Section 4.4
    (disambiguation), Section 4.6 (displacement competition), and the
    revised Sections 5.1/5.2/5.4. Includes the convergence-audit data
    records, the code-audit record, and the finite-size robustness check.
```

Each section contains its own README with method, results, and honest scope limits, and is independently runnable (dependencies are duplicated across sections rather than shared, so any single section can be reproduced without the rest of the repository). Publication figures are generated reproducibly from the banked data records by `make_figures.py`.

## A note on process

Several results in this repository were revised after further testing overturned an initial conclusion, and all are documented in place rather than removed from the record: an early "interior optimum" reading of the diffusion-scarcity complexity peak was corrected once a finite-sample mutual-information bias was identified and removed, relocating the peak to each rule's energetic threshold; an initial "resource exploitation" interpretation of the competition result was tested directly and replaced by a better-supported refuge-effect mechanism; a cost-scaling sweep's first pass was invalidated by two compounding artifacts (a fixed energy ceiling and a fixed warmup duration, both of which silently penalized high-cost conditions) before the corrected version could be trusted; a premature single-seed reading of the Brian's Brain same-niche control was overturned by full replication; and, most consequentially, the flagship competition result was reshaped by a convergence audit which found the standard short measurement window reported transient states rather than steady ones — inverting the original "Brian's Brain dominates" reading into a diffusion-driven transition. The manuscript's own Discussion also initially identified a fundamental limitation of the competitive-dynamics results as an open question — that the underlying mechanism rewards claiming vacant territory rather than directly contesting occupied territory — and this was subsequently tested directly (Section 04, manuscript Section 4.6) rather than left unresolved, confirming the concern was justified.

## Code and analysis audit

The load-bearing simulation mechanics were audited for both correctness (known-answer tests) and smuggled behavior (label-swap symmetry tests confirming no hidden species bias): the base energetic gate, the competition/capture mechanics, the cost-multiplier mechanism, the diffusion kernel (verified to conserve energy exactly), the mutual-information estimator (verified against analytic values), and the convergence runner. The audit record is included in `04-contestable-occupancy/`.

## External reviews

`figures/` contains the publication figure set (PDF + PNG) generated by `make_figures.py`, together with the TikZ source for the Landauer-gate schematic (`fig1_schematic.tex`, compiles standalone).

`reviews/` contains external red-team passes (Claude Opus 4.8, conducted in separate conversation threads) that shaped this manuscript significantly: a prior-art and positioning review that surfaced the competition-colonization and voter-model literature now cited throughout, and a methodology audit that caught an unverified assumption in the HighLife disambiguation (Section 4.4) and an internal contradiction between Section 4.1's original header and the paper's actual conclusion. Both are preserved in full, with a disposition note at the top of each describing what was and wasn't acted on.

## Use of AI tools

This work was carried out with the assistance of an AI system (Anthropic's Claude), used for drafting and editing, for writing and running simulation and audit code, for a systematic code audit, and for citation verification. All results, code, and claims were reviewed and verified by the author, who takes full responsibility for the entire content irrespective of how any part was produced; every reported number traces to a runnable data record, and every citation was verified against its primary source. See the manuscript's "Use of AI Tools" section for the full statement.

## Citations

- Bennett, C. H. (1973). Logical Reversibility of Computation. *IBM Journal of Research and Development*, 17(6), 525–532.
- Bérut, A., Arakelyan, A., Petrosyan, A., Ciliberto, S., Dillenschneider, R., & Lutz, E. (2012). Experimental verification of Landauer's principle linking information and thermodynamics. *Nature*, 483(7388), 187–189.
- Clifford, P., & Sudbury, A. (1973). A model for spatial conflict. *Biometrika*, 60(3), 581–588.
- Gause, G. F. (1934). *The Struggle for Existence*. Williams & Wilkins.
- Gray, P., & Scott, S. K. (1983). Autocatalytic reactions in the isothermal, continuous stirred tank reactor: isolas and other forms of multistability. *Chemical Engineering Science*, 38(1), 29–43.
- Gray, P., & Scott, S. K. (1984). Autocatalytic reactions in the isothermal continuous stirred tank reactor: oscillations and instabilities in the system A+2B→3B; B→C. *Chemical Engineering Science*, 39(6), 1087–1097.
- Guha, S., Ryan, S. D., & Karamched, B. R. (2026). Macroscopic Dominance from Microscopic Extremes: Symmetry Breaking in Spatial Competition. *EPL (Europhysics Letters)*, 155(4), 47003. https://doi.org/10.1209/0295-5075/ae83e1
- Hastings, A. (1980). Disturbance, coexistence, history, and competition for space. *Theoretical Population Biology*, 18(3), 363–373.
- Hinrichsen, H. (2000). Non-equilibrium critical phenomena and phase transitions into absorbing states. *Advances in Physics*, 49(7), 815–958.
- Hubbell, S. P. (2001). *The Unified Neutral Theory of Biodiversity and Biogeography*. Princeton University Press.
- Landauer, R. (1961). Irreversibility and Heat Generation in the Computing Process. *IBM Journal of Research and Development*, 5(3), 183–191.
- Levins, R., & Culver, D. (1971). Regional coexistence of species and competition between rare species. *Proceedings of the National Academy of Sciences*, 68(6), 1246–1248.
- Martinez-Garcia, R., López, C., & Vázquez, F. (2021). Species exclusion and coexistence in a noisy voter model with a competition-colonization tradeoff. *Physical Review E*, 103(3), 032406.
- Nicolis, G., & Prigogine, I. (1977). *Self-Organization in Nonequilibrium Systems: From Dissipative Structures to Order through Fluctuations*. Wiley.
- Ofria, C., & Wilke, C. O. (2004). Avida: A software platform for research in computational evolutionary biology. *Artificial Life*, 10(2), 191–229.
- Pearson, J. E. (1993). Complex Patterns in a Simple System. *Science*, 261(5118), 189–192.
- Pomorski, K., & Kotula, D. (2023). Thermodynamics in Stochastic Conway's Game of Life. *Condensed Matter*, 8(2), 47. https://doi.org/10.3390/condmat8020047
- Ray, T. S. (1991). An Approach to the Synthesis of Life. In *Artificial Life II, Santa Fe Institute Studies in the Sciences of Complexity*, Vol. XI (eds. C. Langton, C. Taylor, J. D. Farmer, & S. Rasmussen), 371–408. Addison-Wesley.
- Tilman, D. (1994). Competition and biodiversity in spatially structured habitats. *Ecology*, 75(1), 2–16.
- Toffoli, T., & Margolus, N. (1987). *Cellular Automata Machines: A New Environment for Modeling*. MIT Press.
- Turing, A. M. (1952). The Chemical Basis of Morphogenesis. *Philosophical Transactions of the Royal Society B*, 237(641), 37–72.
- Vasilyeva, M., Wang, Y., Stepanov, S., & Sadovski, A. (2022). Numerical investigation and factor analysis of the spatial-temporal multi-species competition problem. *WSEAS Transactions on Mathematics*, 21, 731–755. https://doi.org/10.37394/23206.2022.21.85
- Winfree, A. T. (1972). Spiral Waves of Chemical Activity. *Science*, 175(4022), 634–636.
- Wolfram, S. (1984). Universality and complexity in cellular automata. *Physica D: Nonlinear Phenomena*, 10(1-2), 1–35.
- Yu, D. W., & Wilson, H. B. (2001). The competition-colonization trade-off is dead; long live the competition-colonization trade-off. *American Naturalist*, 158(1), 49–63.
- Zaikin, A. N., & Zhabotinsky, A. M. (1970). Concentration wave propagation in two-dimensional liquid-phase self-oscillating system. *Nature*, 225(5232), 535–537.

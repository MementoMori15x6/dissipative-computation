# Structure Formation and Attractor Selection Under Attrition

Does spontaneous structure formation require genuine non-equilibrium driving, or does it occur under fluctuation alone? This section tests that question on two substrates, then asks a related but distinct question: does the tendency of a population to settle toward stable configurations under simple attrition require the same driving, or is it a property of the local update rule alone?

## Method

**Reaction-diffusion substrate**: the Gray-Scott model (Gray & Scott, 1983, 1984), parameterized following Pearson (1993). A uniform medium is perturbed with noise and allowed to evolve; the question is whether it spontaneously organizes into stable, bounded structures, and if so, whether those structures are genuinely causally distinct from their surroundings (not merely visually distinct).

**Metric**: time-lagged mutual information between adjacent cells' trajectories, classified by position (interior of a structure, boundary, or background). Genuine causal insulation predicts higher mutual information within a structure's interior than across its boundary.

**Discrete substrate replication** (`discrete-substrate-replication/`): the same ignition-and-insulation test repeated on Conway's Game of Life, to check whether the finding is specific to continuous reaction-diffusion chemistry or generalizes to a discrete, rule-based substrate.

**Attractor selection under attrition** (`attractor-selection-under-attrition/`): a population evolving under Game of Life's rule alone, with no imposed selection mechanism, is tracked for whether it drifts toward a small set of persistent configurations (an independently-validated "confidence" measure built from which structural sizes historically persist). The question here is whether this drift requires an energetic cost of persistence (a metabolic-style penalty for staying alive) or occurs from the discrete update rule by itself.

## Results

**Structure formation requires genuine dissipative flux.** Removing the driving that keeps the reaction-diffusion system away from equilibrium, while holding diffusion and reaction terms otherwise constant, collapses structure entirely rather than merely weakening it. Restoring that driving restores structure at a sharp, reproducible threshold (paired t = 769.5, n = 15 seeds). A finer sweep found the transition is not a single point but a narrow, high-sensitivity band: below it, every trial stays quiet; above it, every trial reliably organizes; within it, outcomes are highly sensitive to initial conditions rather than cleanly bimodal.

**The finding replicates on a discrete substrate.** The same ignition-threshold and causal-insulation methodology, applied to Game of Life, found an analogous sharp ignition threshold (cleaner and more monotonic than the reaction-diffusion case) and, restricted to the subset of outcomes retaining genuine dynamic activity after settling (a necessary precondition — fully static remnants carry no time-varying signal to measure), a causal-insulation result unanimous across every qualifying trial (8 of 8).

**Attractor selection under attrition does not require the same driving.** A population left to evolve under Game of Life's rule alone, with zero energetic cost for persisting, still drifted toward the same handful of stable, high-persistence configurations found in the energetically-costed case — arriving more slowly and settling at a larger population size, but reaching a comparable final state (confidence 0.643 versus 0.657, populations of 77.0 versus 15.3). A follow-up sweep of intermediate energetic costs found this is a threshold effect, not a smooth gradient: three consecutive cost levels produced bit-for-bit identical population trajectories despite genuinely different underlying energy values, confirmed by direct measurement, not assumed.

## Interpretation

Structure formation (in the reaction-diffusion sense tested here) requires genuine non-equilibrium driving; attractor selection under simple attrition does not, though driving accelerates and sharpens it. This is a real, specific asymmetry between two related but distinct phenomena often treated as interchangeable instances of "self-organization" — one is a necessary consequence of the discrete update rule alone, the other is not achievable without genuine thermodynamic throughput.

## Scope limits

- One reaction-diffusion parameterization, one discrete substrate (Game of Life). Generalization to other rule classes for the discrete replication is untested.
- The discrete causal-insulation result rests on 8 qualifying seeds (out of a larger sample filtered for retained dynamic activity), smaller than the reaction-diffusion result's 15-seed replication.
- The threshold-versus-gradient finding for attractor selection was tested at one substrate, one held-out seed set; a systematic sweep of cost values beyond the five tested is not reported here.

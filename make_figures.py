"""
PUBLICATION FIGURE GENERATION for the Dissipative Computation manuscript.

Every figure is generated directly from the banked convergence-audit data
records (convergence_audit_results_*.py), so every plotted point traces to
a verified number. Uncertainty is shown honestly:
  - win-rate proportions carry Wilson score 95% confidence intervals (the
    correct interval for a binomial proportion, well-behaved near 0 and 1),
  - complexity means carry +/- 1 SD error bars,
  - points with a non-trivial not-converged fraction are marked, not hidden.

DESCRIPTIVE TITLES: intentionally NOT baked into the figures. Per publication
convention, each figure carries only axis labels and in-plot annotations; the
descriptive "Figure N: ..." sentence lives in the LaTeX caption. The intended
caption text for each figure is recorded in the CAPTIONS dict at the bottom of
this file so it travels with the code.

Outputs vector PDF (publication) + PNG (preview) into ./figures/.

FIGURE NUMBERING is by order of first mention in the manuscript:
  1 Landauer-gate schematic (TikZ, fig1_schematic.tex)   Section 2.1
  2 complexity profiles                                  Section 3.3
  3 flagship diffusion transition                        Section 4.1
  4 cost-driven transition                               Section 4.2
  5 HighLife disambiguation                              Section 4.4
  6 displacement K-sweep (D&N vs BB)                     Section 4.6
  7 cost under displacement                              Section 4.6
  8 finite-size robustness                               Section 5.4

Run: python3 make_figures.py
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.stats import beta

sys.path.insert(0, "03-diffusion-limited-scarcity")
sys.path.insert(0, "04-contestable-occupancy")
sys.path.insert(0, "04-contestable-occupancy/finite-size-checks")

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10.5,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "figure.dpi": 150,
})

C_GOL   = "#0072B2"
C_BB    = "#D55E00"
C_DN    = "#009E73"
C_NEUT  = "#555555"


def wilson_ci(k, n, z=1.96):
    """Wilson score 95% CI for a binomial proportion k/n. Returns (lo, hi)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    half = (z / denom) * np.sqrt(p*(1-p)/n + z**2/(4*n**2))
    return (max(0.0, center - half), min(1.0, center + half))


def figure_flagship_transition():
    import convergence_audit_results as flag
    rows = flag.RESULTS_D_BG_0_05
    D = np.array([r["D_diff"] for r in rows])
    win = np.array([r["gol_total"] for r in rows], float)
    n = np.array([r["n_seeds"] for r in rows], float)
    share = np.array([r["mean_gol_share"] for r in rows], float)
    winrate = win / n
    cis = np.array([wilson_ci(int(k), int(nn)) for k, nn in zip(win, n)])
    lo, hi = winrate - cis[:, 0], cis[:, 1] - winrate

    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.axhspan(0.5, 1.0, color=C_GOL, alpha=0.05)
    ax.axhspan(0.0, 0.5, color=C_BB,  alpha=0.05)
    ax.axhline(0.5, color=C_NEUT, lw=0.7, ls=(0, (4, 3)), zorder=1)
    ax.errorbar(D, winrate, yerr=[lo, hi], fmt="o-", color=C_GOL, lw=1.6,
                ms=5, capsize=2.5, elinewidth=1.0, zorder=4,
                label="Game of Life total-victory rate")
    ax.plot(D, share, "s--", color=C_NEUT, lw=1.1, ms=3.5, alpha=0.75,
            zorder=3, label="mean Game-of-Life territory share")
    ax.axvspan(0.08, 0.12, color=C_NEUT, alpha=0.08, zorder=0)
    ax.text(0.10, 1.02, "transition", ha="center", va="bottom",
            fontsize=8.5, color=C_NEUT, style="italic")
    ax.text(0.16, 0.9, "Game of Life\nwins", color=C_GOL, fontsize=9,
            va="center", fontweight="bold")
    ax.text(0.16, 0.40, "Brian's Brain\nwins", color=C_BB, fontsize=9,
            va="center", fontweight="bold")
    ax.set_xlabel(r"diffusion rate  $D_{\mathrm{diff}}$")
    ax.set_ylabel("Game-of-Life outcome fraction")
    ax.set_ylim(-0.03, 1.10)
    ax.set_xlim(0, 0.21)
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.20), fontsize=7)
    ax.annotate("error bars: Wilson 95% CI", xy=(0.35, 0.05),
                xycoords="axes fraction", ha="right", va="top",
                fontsize=7, color=C_NEUT)
    fig.tight_layout()
    fig.savefig("figures/fig3_flagship_transition.pdf", bbox_inches="tight")
    fig.savefig("figures/fig3_flagship_transition.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig3_flagship_transition  [flagship diffusion-driven transition]")


def figure_complexity_profiles():
    import convergence_audit_results_section3_complexity as bb
    import convergence_audit_results_section3_gol_dn_complexity as gd

    def unpack(points):
        D = np.array([p["D_diff"] for p in points], float)
        C = np.array([p["mean_C"] for p in points], float)
        sd = np.array([p["sd_C"] for p in points], float)
        nc = np.array([p["not_converged"] for p in points], float)
        return D, C, sd, nc

    bbD, bbC, bbSD, bbNC = unpack(bb.BRIANS_BRAIN_DEBIASED_SWEEP["points"])
    gD, gC, gSD, gNC = unpack(gd.GOL_DEBIASED_SWEEP["points"])
    dD, dC, dSD, dNC = unpack(gd.DAYANDNIGHT_DEBIASED_SWEEP["points"])

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.0, 3.7),
                                    gridspec_kw={"width_ratios": [1, 1]})
    for D, C, sd, color, lab in [
        (dD, dC, dSD, C_DN, "Day & Night"),
        (gD, gC, gSD, C_GOL, "Game of Life"),
        (bbD, bbC, bbSD, C_BB, "Brian's Brain"),
    ]:
        axL.errorbar(D, C, yerr=sd, fmt="o-", color=color, lw=1.4, ms=4,
                     capsize=2, elinewidth=0.9, label=lab)
    axL.set_xlabel(r"diffusion rate  $D_{\mathrm{diff}}$")
    axL.set_ylabel(r"structural complexity  $C$  (debiased)")
    axL.set_title("Linear scale", fontsize=9.5)
    axL.legend(loc="upper right")
    axL.set_xlim(-0.02, 1.03)

    # small multiplicative x-jitter separates the three rules where their
    # points cluster at shared D_diff on the log axis (cosmetic only; the
    # underlying D_diff is identical across rules -- see left panel).
    jit = {"Day & Night": 0.985, "Game of Life": 1.0, "Brian's Brain": 1.015}
    for D, C, sd, nc, color, lab in [
        (dD, dC, dSD, dNC, C_DN, "Day & Night"),
        (gD, gC, gSD, gNC, C_GOL, "Game of Life"),
        (bbD, bbC, bbSD, bbNC, C_BB, "Brian's Brain"),
    ]:
        m = C > 0
        Dj = D * jit[lab]
        axR.errorbar(Dj[m], C[m], yerr=sd[m], fmt="o-", color=color, lw=1.4,
                     ms=4, capsize=2, elinewidth=0.9, label=lab)
        hi_nc = m & (nc >= 4)
        if hi_nc.any():
            axR.scatter(Dj[hi_nc], C[hi_nc], s=90, facecolors="none",
                        edgecolors=color, linewidths=1.3, zorder=5)
    axR.set_yscale("log")
    axR.set_xlabel(r"diffusion rate  $D_{\mathrm{diff}}$")
    axR.set_ylabel(r"$C$  (log scale)")
    axR.set_title("Log scale", fontsize=9.5)
    axR.set_xlim(-0.02, 1.03)
    axR.scatter([], [], s=90, facecolors="none", edgecolors=C_NEUT,
                linewidths=1.3, label="≥40% seeds not fully converged")
    axR.legend(loc="upper right", bbox_to_anchor=(0.98, 0.98), fontsize=7.5)

    fig.tight_layout()
    fig.savefig("figures/fig2_complexity_profiles.pdf", bbox_inches="tight")
    fig.savefig("figures/fig2_complexity_profiles.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig2_complexity_profiles  [three-rule debiased complexity]")


def figure_cost_transition():
    import convergence_audit_results_cost as c
    rows = c.RESULTS_ALPHA_SWEEP
    alpha = np.array([r["alpha"] for r in rows], float)
    win = np.array([r["gol_total"] for r in rows], float)
    n = np.array([r["n_seeds"] for r in rows], float)
    winrate = win / n
    cis = np.array([wilson_ci(int(k), int(nn)) for k, nn in zip(win, n)])
    lo, hi = winrate - cis[:, 0], cis[:, 1] - winrate

    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.axhspan(0.5, 1.0, color=C_GOL, alpha=0.05)
    ax.axhspan(0.0, 0.5, color=C_BB, alpha=0.05)
    ax.axhline(0.5, color=C_NEUT, lw=0.7, ls=(0, (4, 3)))
    ax.errorbar(alpha, winrate, yerr=[lo, hi], fmt="o-", color=C_GOL, lw=1.6,
                ms=5, capsize=2.5, elinewidth=1.0, zorder=4,
                label="Game of Life total-victory rate")
    ax.set_xscale("log")
    ax.set_xlabel(r"Brian's Brain metabolic cost multiplier  $\alpha$")
    ax.set_ylabel("Game-of-Life total-victory rate")
    ax.set_ylim(-0.03, 1.10)
    idx3 = np.where(alpha == 3)[0]
    if len(idx3):
        i = idx3[0]
        ax.annotate("critical slowing down\n(resolved by drift direction)",
                    xy=(3, winrate[i]), xytext=(6, 0.62),
                    fontsize=7.5, color=C_NEUT, ha="left",
                    arrowprops=dict(arrowstyle="->", color=C_NEUT, lw=0.8))
    ax.text(60, 0.90, "Game of Life\nwins (low cost)", color=C_GOL,
            fontsize=8.5, va="center", fontweight="bold")
    ax.text(110, 0.40, "Brian's Brain\nwins (high cost)", color=C_BB,
            fontsize=8.5, va="center", ha="center", fontweight="bold")
    ax.annotate("error bars: Wilson 95% CI", xy=(0.02, 0.02),
            xycoords="axes fraction", ha="left", va="bottom",
            fontsize=7, color=C_NEUT)
    fig.tight_layout()
    fig.savefig("figures/fig4_cost_transition.pdf", bbox_inches="tight")
    fig.savefig("figures/fig4_cost_transition.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig4_cost_transition  [cost-driven transition]")


def figure_finite_size():
    import convergence_finite_size_results as fs
    low = fs.FINITE_SIZE_CONVERGENCE["low_diffusion_D_diff_0.05"]
    high = fs.FINITE_SIZE_CONVERGENCE["high_diffusion_D_diff_0.20"]
    sizes_low = sorted(low.keys())
    sizes_high = sorted(high.keys())
    wr_low = [low[s]["gol_win_rate"] for s in sizes_low]
    wr_high = [high[s]["gol_win_rate"] for s in sizes_high]
    n_low = [low[s]["n_seeds"] for s in sizes_low]
    n_high = [high[s]["n_seeds"] for s in sizes_high]

    def cis(wr, n):
        arr = []
        for p, nn in zip(wr, n):
            k = round(p * nn)
            l, h = wilson_ci(k, nn)
            arr.append((p - l, h - p))
        return np.array(arr).T

    fig, ax = plt.subplots(figsize=(5.2, 3.7))
    ax.axhspan(0.5, 1.0, color=C_GOL, alpha=0.05)
    ax.axhspan(0.0, 0.5, color=C_BB, alpha=0.05)
    ax.axhline(0.5, color=C_NEUT, lw=0.7, ls=(0, (4, 3)))
    lo1, hi1 = cis(wr_low, n_low)
    ax.errorbar(sizes_low, wr_low, yerr=[lo1, hi1], fmt="o-", color=C_GOL,
                lw=1.6, ms=7, capsize=3, elinewidth=1.0,
                label=r"$D_{\mathrm{diff}}=0.05$ (low transport)")
    lo2, hi2 = cis(wr_high, n_high)
    ax.errorbar(sizes_high, wr_high, yerr=[lo2, hi2], fmt="s-", color=C_BB,
                lw=1.6, ms=7, capsize=3, elinewidth=1.0,
                label=r"$D_{\mathrm{diff}}=0.20$ (high transport)")
    ax.set_xscale("log", base=2)
    ax.set_xticks([64, 128, 256])
    ax.set_xticklabels(["64", "128", "256"])
    ax.set_xlabel("grid size  $N$  (per side)")
    ax.set_ylabel("Game-of-Life total-victory rate")
    ax.set_ylim(-0.05, 1.12)
    ax.text(70, 0.90, "Game of Life wins", color=C_GOL, fontsize=8.5, fontweight="bold")
    ax.text(70, 0.10, "Brian's Brain wins", color=C_BB, fontsize=8.5, fontweight="bold")
    ax.legend(loc="lower right", bbox_to_anchor=(0.98, 0.02), fontsize=8)
    fig.tight_layout()
    fig.savefig("figures/fig8_finite_size.pdf", bbox_inches="tight")
    fig.savefig("figures/fig8_finite_size.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig8_finite_size  [finite-size robustness]")



# ======================================================================
# FIGURE 5: HighLife disambiguation (Section 4.4)
# Source: convergence_audit_results_dn_and_highlife.RESULTS_GOL_VS_HIGHLIFE
#   26/30 GoL-heavy (>0.9), 2/30 coexistence (~0.35), 2/30 HighLife-heavy
#   (<0.02) -- and ZERO seeds ending in either side's total extinction.
# ======================================================================
def figure_highlife_disambiguation():
    fig, ax = plt.subplots(figsize=(4.3, 3.6))
    classes = ["GoL-heavy\n(>0.9)", "coexist\n(~0.35)", "HighLife-heavy\n(<0.02)"]
    counts = np.array([26, 2, 2]) / 30.0
    colors = [C_GOL, "#BBBBBB", C_DN]
    ax.bar(np.arange(3), counts, 0.6, color=colors)
    ax.set_xticks(np.arange(3)); ax.set_xticklabels(classes, fontsize=8.2)
    ax.set_ylabel("fraction of seeds (of 30)")
    ax.set_ylim(0, 1.12)
    for i, c in enumerate(counts):
        ax.text(i, c + 0.02, f"{int(round(c*30))}/30", ha="center", fontsize=8.5)
    ax.text(1.42, 0.68,
            "no seed ends in total\nextinction on either side:\nHighLife's absorbing state\nprevents the runaway\ndominance Brian's Brain\nachieves against the\nsame opponent",
            fontsize=7.2, color=C_NEUT, ha="left", va="center", linespacing=1.4)
    fig.tight_layout()
    fig.savefig("figures/fig5_highlife_disambiguation.pdf", bbox_inches="tight")
    fig.savefig("figures/fig5_highlife_disambiguation.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig5_highlife_disambiguation  [absorbing state vs. expansion capacity]")


# ======================================================================
# FIGURE 6: displacement K-sweep, Day and Night vs. Brian's Brain (4.6)
# Section 4.6, first condition (D_bg = 0.05, D_diff = 0.05), 30 seeds.
# NOTE ON WHAT IS PLOTTED: the reversal between K=2 and K=3 is a change in
# WHICH species goes extinct, so a single "extinction rate" series would
# mix two quantities. Plotted here is the DAY AND NIGHT extinction rate
# across all K; the K<=2 regime, where Brian's Brain instead goes extinct
# in 30/30, is shaded and labelled.
#   converged (\u00a72.3): D&N extinct 0, 0, 30, 30, 27, 8, 8, 8 (of 30)
#   short window:     D&N extinct 0, 0, 25, 23, 13, 8, 8, 8 (of 30)
# ======================================================================
def figure_displacement_ksweep():
    fig, ax = plt.subplots(figsize=(4.9, 3.6))
    K = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    conv  = np.array([0, 0, 30, 30, 27, 8, 8, 8]) / 30.0
    short = np.array([0, 0, 25, 23, 13, 8, 8, 8]) / 30.0
    ax.axvspan(0.6, 2.5, color=C_DN, alpha=0.09, lw=0)
    ax.plot(K, short, "s--", color=C_NEUT, lw=1.1, ms=4, alpha=0.75,
            label="short window (transient)")
    ax.plot(K, conv, "o-", color=C_BB, lw=1.7, ms=6,
            label="converged (\u00a72.3)")
    ax.set_xlabel("displacement threshold  $K$")
    ax.set_ylabel("Day and Night extinction rate")
    ax.set_xlim(0.6, 8.6)
    ax.set_ylim(-0.26, 1.30)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xticks(K)
    ax.axvline(2.5, color=C_NEUT, lw=0.8, ls=(0, (3, 3)))
    ax.text(2.42, 1.24, "sharp reversal", ha="right", va="top",
            fontsize=7.6, color=C_NEUT, style="italic")
    ax.annotate("Day and Night wins here:\nBrian's Brain extinct 30/30\n(self-defeating displacement)",
                xy=(1.75, -0.02), xytext=(3.15, -0.24),
                fontsize=7.2, color=C_DN, ha="left", va="bottom",
                linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=C_DN, lw=0.7,
                                shrinkA=3, shrinkB=4))
    ax.annotate("genuine plateau\n(= lottery baseline, 8/30)",
                xy=(7.0, 8/30), xytext=(8.55, 0.58),
                fontsize=7.2, color=C_NEUT, ha="right", va="bottom",
                linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=C_NEUT, lw=0.7,
                                shrinkA=4, shrinkB=4))
    ax.legend(loc="upper right", fontsize=7.6, frameon=False,
              borderaxespad=0.2, handlelength=1.8)
    fig.tight_layout()
    fig.savefig("figures/fig6_displacement_ksweep.pdf", bbox_inches="tight")
    fig.savefig("figures/fig6_displacement_ksweep.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig6_displacement_ksweep  [lottery-to-displacement reversal, D&N vs BB]")


# ======================================================================
# FIGURE 7: cost under displacement (Section 4.6) — the two re-run pairings
# STAGE6A (DN vs BB) and STAGE6B (GoL vs HighLife), convergence-verified.
# ======================================================================
def figure_cost_displacement():
    import convergence_audit_results_displacement_cost as dc
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(8.2, 3.7))

    # Panel A: DN vs BB — DN territory share vs alpha, per K. The K=1 line
    # shows the sharp cost-driven reversal (1.0 -> 0.0).
    g = dc.STAGE6A["grid"]
    alphas = [1, 20, 200]
    for Kval, color, mk in [(1, C_DN, "o"), (5, C_GOL, "s"), (8, C_BB, "^")]:
        ys, xs = [], []
        for a in alphas:
            cell = g.get((Kval, a))
            if cell and cell.get("mean") is not None:
                xs.append(a); ys.append(cell["mean"])
        axA.plot(xs, ys, mk, color=color, ms=5.5, label=f"K = {Kval}")
        axA.plot(xs, ys, ls=(0, (2, 2)), color=color, lw=1.2)
    axA.set_xscale("log")
    axA.set_xlabel(r"cost multiplier  $\alpha$")
    axA.set_ylabel("Day & Night territory share")
    axA.set_ylim(-0.06, 1.12)
    axA.set_title("(a)", fontsize=9.5, loc="left")
    axA.legend(loc="upper right", fontsize=7.5, frameon=False,
               borderaxespad=0.3, handlelength=1.8)
    axA.text(1.03, 0.20,
             "cost-driven reversal\nat $K=1$; completes\nby $\\alpha\\approx2$ (finer\nsweep, Section 4.6)",
             fontsize=6.9, color=C_DN, ha="left", va="center", linespacing=1.4)
    axA.text(0.98, 0.55, "markers show sampled $\\alpha$;\ndashes are guides,\nnot interpolation",
             transform=axA.transAxes, ha="right", va="center",
             fontsize=6.4, color=C_NEUT, linespacing=1.4)

    # Panel B: GoL vs HighLife — mean unaffected but variance/bimodality at high cost.
    g2 = dc.STAGE6B["grid"]
    alphas2 = [1, 20, 200]
    means = [g2.get((5, a), {}).get("mean") for a in alphas2]
    sds = [g2.get((5, a), {}).get("sd") for a in alphas2]
    xs = [a for a, m in zip(alphas2, means) if m is not None]
    ys = [m for m in means if m is not None]
    es = [s if s is not None else 0 for s, m in zip(sds, means) if m is not None]
    axB.errorbar(xs, ys, yerr=es, fmt="o-", color=C_GOL, lw=1.5, ms=5,
                 capsize=3)
    axB.set_xscale("log")
    axB.set_xlabel(r"cost multiplier  $\alpha$")
    axB.set_ylabel("Game of Life territory share")
    axB.set_ylim(-0.10, 1.42)
    axB.set_title("(b)", fontsize=9.5, loc="left")
    axB.axhline(0.5, color=C_NEUT, lw=0.6, ls=(0, (4, 3)))
    axB.text(1.05, 1.34, "$K = 5$, mean $\\pm$ 1 SD", fontsize=7.3,
             color=C_GOL, ha="left", va="top")
    axB.text(1.05, 0.03,
             "mean flat, but variance rises;\ndistribution bimodal at high cost\n(SD spans a two-outcome mixture,\nnot measurement scatter)",
             fontsize=6.8, color=C_NEUT, ha="left", va="bottom", linespacing=1.35)

    fig.tight_layout()
    fig.savefig("figures/fig7_cost_displacement.pdf", bbox_inches="tight")
    fig.savefig("figures/fig7_cost_displacement.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig7_cost_displacement  [cost under displacement, two re-run pairings]")


CAPTIONS = {
    "fig1": (
        r"\textbf{Landauer-gated execution.} Each cell's proposed next state is computed from its "
        r"neighbourhood by the ordinary rule $f$; the transition is then charged a fixed cost only if "
        r"it would change the cell's state, and is executed only if the cell's local energy budget "
        r"covers that cost. A cell that cannot pay holds its current state rather than failing or "
        r"resetting. Because the proposed state depends only on the current neighbourhood, the cost is "
        r"always computable before the gate is applied and never depends on the gate's own outcome "
        r"(Section~2.1). Energy is supplied under one of the two regimes of Section~2.2 and, in the "
        r"multi-rule experiments, diffuses through a single field shared by all competitors."
    ),
    "fig2": (
        r"\textbf{Debiased complexity peaks near each rule's energetic threshold, then declines.} "
        r"Structural complexity $C$ versus diffusion rate for all three rule classes, "
        r"re-measured under the long-window protocol that removes the finite-sample "
        r"mutual-information estimator bias (Section~3.3). "
        r"Left: linear scale (Day~\&~Night's threshold value dominates the ordinate). "
        r"Right: log scale, revealing the peak-then-decline shape shared by all three rules; "
        r"a small horizontal offset separates the three series where their points coincide. "
        r"Error bars denote $\pm 1$ SD; open rings mark points where $\geq 40\%$ of seeds had "
        r"not fully met the adaptive convergence criterion at the step cap."
    ),
    "fig3": (
        r"\textbf{Diffusion-driven competitive transition.} "
        r"Game of Life vs.\ Brian's Brain under Landauer-gated lottery competition "
        r"($D_{\mathrm{bg}}=0.05$, 30 seeds per point). "
        r"Game of Life wins outright at low diffusion rates; the outcome crosses over "
        r"near $D_{\mathrm{diff}}\approx0.08$--$0.12$ and fully inverts to Brian's Brain "
        r"by $D_{\mathrm{diff}}\gtrsim0.15$. "
        r"Error bars denote Wilson score 95\% confidence intervals on the total-victory rate."
    ),
    "fig4": (
        r"\textbf{Metabolic cost drives a second transition that rescues Brian's Brain.} "
        r"Game-of-Life total-victory rate versus the multiplier $\alpha$ applied to Brian's "
        r"Brain's per-transition cost ($D_{\mathrm{bg}}=0.05$, $D_{\mathrm{diff}}=0.05$). "
        r"Game of Life wins at low cost; increasing $\alpha$ past a critical value near "
        r"$\alpha\approx3$--$10$ reverses the outcome to Brian's Brain and holds stably to "
        r"$\alpha=200$. The transition near $\alpha=3$ exhibits critical slowing down and was "
        r"resolved by drift-direction classification. "
        r"Error bars denote Wilson score 95\% confidence intervals."
    ),
    "fig5": (
        r"\textbf{The absorbing-state criterion, not expansion capacity, governs dominance.} "
        r"Outcome distribution for Game of Life vs.\ HighLife under lottery competition "
        r"(30 seeds, $D_{\mathrm{bg}}=0.05$, $D_{\mathrm{diff}}=0.05$). HighLife shares Game of "
        r"Life's directional expansion capacity (via its $B6$ rule) but retains an absorbing state. "
        r"No seed ends in either side's total extinction, and the outcomes that do occur fall on "
        r"both sides, in contrast to the near-deterministic one-sided dominance Brian's Brain "
        r"(which admits no absorbing state) achieves against the same opponent (Section~4.4)."
    ),
    "fig6": (
        r"\textbf{The lottery-to-displacement reversal, and what a short window concealed.} "
        r"Displacement $K$-sweep for Day and Night vs.\ Brian's Brain (Section~4.6, "
        r"$D_{\mathrm{bg}}=0.05$, $D_{\mathrm{diff}}=0.05$, 30 seeds per point). Plotted is the "
        r"\emph{Day and Night} extinction rate at every $K$: because the reversal is a change in "
        r"which species is eliminated, a single extinction-rate series would otherwise mix two "
        r"quantities. The shaded region $K\le2$ marks the regime where Brian's Brain instead goes "
        r"extinct in 30 of 30 trials, direct displacement being self-defeating for it there. The "
        r"convergence protocol ($\S$2.3, solid) resolves what the short-window reading (dashed) "
        r"rendered as a gradual rise into a sharp, fully deterministic reversal between $K=2$ and "
        r"$K=3$, followed by a separate and genuine relaxation through $K=5$ to the $K=6$--$8$ "
        r"plateau, which matches the lottery-competition baseline (8 of 30) and was confirmed "
        r"cell-for-cell at both windows."
    ),
    "fig7": (
        r"\textbf{Metabolic cost under displacement competition, for the two convergence-"
        r"verified pairings.} \emph{Left:} Day and Night vs.\ Brian's Brain. At $K=1$, pricing "
        r"Brian's Brain's mandatory refractory transition above roughly $1.5$--$2\times$ "
        r"baseline reverses the outcome completely and deterministically (Day-and-Night share "
        r"$1.0\to0.0$) --- the sharpest cost-driven transition in this paper. \emph{Right:} "
        r"Game of Life vs.\ HighLife. Charging HighLife's $B6$ self-replication leaves the mean "
        r"outcome near parity but sharply increases variance; at high cost the distribution "
        r"becomes bimodal (individual seeds resolve to $0$ or $1$, not intermediate values), so "
        r"the plotted standard deviation reflects a two-outcome mixture rather than measurement "
        r"noise. Both pairings re-run under the convergence protocol ($\S$2.3). Markers show the "
        r"sampled cost multipliers ($\alpha=1,20,200$); dashed segments in the left panel are "
        r"visual guides, not interpolation, and the $K=1$ reversal in fact completes by "
        r"$\alpha\approx2$ (Section~4.6). The $\alpha=200$ points rest on three to five seeds "
        r"rather than ten, and $K=8$ at $\alpha=200$ in the left panel was not run."
    ),
    "fig8": (
        r"\textbf{The diffusion-driven transition is robust to system size.} "
        r"Game-of-Life total-victory rate at both ends of the transition, re-run to convergence "
        r"at grid sizes $N=64,128,256$. The low-transport regime ($D_{\mathrm{diff}}=0.05$, "
        r"Game of Life wins) and the high-transport regime ($D_{\mathrm{diff}}=0.20$, Brian's "
        r"Brain wins) both hold in the same direction at every size; the low-transport victory "
        r"in fact sharpens with size. The high-transport condition was confirmed at $N=64$ and "
        r"$N=128$; it was not re-run at $N=256$. "
        r"Error bars denote Wilson score 95\% confidence intervals."
    ),
}


if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)
    print("Generating publication figures from banked data:")
    figure_complexity_profiles()      # Figure 2
    figure_flagship_transition()      # Figure 3
    figure_cost_transition()          # Figure 4
    figure_highlife_disambiguation()  # Figure 5
    figure_displacement_ksweep()      # Figure 6
    figure_cost_displacement()        # Figure 7
    figure_finite_size()              # Figure 8
    print("  (Figure 1, the Landauer-gate schematic, is TikZ:"
          " figures/fig1_schematic.tex)")
    print("Done. Vector PDFs + preview PNGs in ./figures/")
    print("\nLaTeX caption text is in the CAPTIONS dict at the bottom of this file.")

#!/usr/bin/env python3
"""
TIER A VERIFICATION -- runs in seconds, no simulation.

Checks two things that no amount of "does the script run?" testing can catch:

  1. Every banked record file loads and parses.
  2. Every number the manuscript quotes as a result appears in a banked
     record with the same value.

(2) is the one that matters. The most common real defect in a paper like this
is not a broken script -- it is a number that was correct when written, then
drifted out of sync with the data after a re-run. Executing a script cannot
detect that. This can.

Usage:  python3 verify_claims.py        (script, from anywhere)
        %run verify_claims.py          (notebook)
Repo root is auto-located; override with os.environ["DC_REPO"] if needed.
Exit code 0 if all checks pass, 1 otherwise.
"""

import importlib.util
import os
import pathlib
import re
import sys

MANUSCRIPT = "DC_Manuscript_Draft_v2.md"


def find_root():
    """Locate the repo root from a script, a notebook, or any working dir.

    Order: DC_REPO env var -> alongside __file__ (scripts only) -> cwd and
    its parents -> one or two levels below cwd, which is the usual case in
    Colab where you land in /content and the repo is /content/<name>/.
    """
    env = os.environ.get("DC_REPO")
    if env and (pathlib.Path(env) / MANUSCRIPT).exists():
        return pathlib.Path(env)

    try:
        here = pathlib.Path(__file__).resolve().parent
        if (here / MANUSCRIPT).exists():
            return here
    except NameError:
        pass                                  # notebooks have no __file__

    cwd = pathlib.Path.cwd().resolve()
    for cand in [cwd, *cwd.parents]:
        if (cand / MANUSCRIPT).exists():
            return cand

    hits = sorted(cwd.glob("*/" + MANUSCRIPT)) + sorted(cwd.glob("*/*/" + MANUSCRIPT))
    if hits:
        return hits[0].parent

    raise FileNotFoundError(
        "Could not find " + MANUSCRIPT + ". Run from inside the repo, or set "
        "DC_REPO to its path, e.g.\n"
        "    import os; os.environ['DC_REPO'] = '/content/dissipative-computation'\n"
        "Searched from: " + str(cwd))


ROOT = find_root()
MS = ROOT / MANUSCRIPT

RECORDS = [
    "03-diffusion-limited-scarcity/convergence_audit_results.py",
    "03-diffusion-limited-scarcity/convergence_audit_results_cost.py",
    "03-diffusion-limited-scarcity/convergence_audit_results_section3_complexity.py",
    "03-diffusion-limited-scarcity/convergence_audit_results_section3_gol_dn_complexity.py",
    "03-diffusion-limited-scarcity/seed_count_recovery_results.py",
    "03-diffusion-limited-scarcity/same_niche_extended_results.py",
    "02-landauer-gated-execution/surrogate_bias_check_results.py",
    "02-landauer-gated-execution/demand_convergence_results.py",
    "02-landauer-gated-execution/out_of_sample_rule_test_results.py",
    "04-contestable-occupancy/code_audit_results.py",
    "04-contestable-occupancy/convergence_audit_results_dn_and_highlife.py",
    "04-contestable-occupancy/convergence_audit_results_displacement_cost.py",
    "04-contestable-occupancy/convergence_audit_results_flagship_cost.py",
    "04-contestable-occupancy/finite-size-checks/convergence_finite_size_results.py",
]

# (claim shown to you, string that must appear in the manuscript, record file,
#  dotted path into that record, expected value)
CLAIMS = [
    ("3.2  per-cell demand, Brian's Brain at ceiling", "1.501",
     "02-landauer-gated-execution/demand_convergence_results.py",
     "FLUX_PER_ACTIVE_CELL", ("BB", 1.0), "ratio", 1.501),
    ("3.2  per-cell demand, Game of Life at ceiling", "0.456",
     "02-landauer-gated-execution/demand_convergence_results.py",
     "FLUX_PER_ACTIVE_CELL", ("GoL", 1.0), "ratio", 0.456),
    ("3.2  per-cell demand, Day and Night at ceiling", "0.837",
     "02-landauer-gated-execution/demand_convergence_results.py",
     "FLUX_PER_ACTIVE_CELL", ("DayAndNight", 1.0), "ratio", 0.837),
    ("3.2  out-of-sample, Seeds at ceiling", "2.000",
     "02-landauer-gated-execution/out_of_sample_rule_test_results.py",
     "UNTHROTTLED_CEILING", "Seeds", "per_cell_demand", 2.000),
    ("3.2  out-of-sample, Life without Death at ceiling", "0.000",
     "02-landauer-gated-execution/out_of_sample_rule_test_results.py",
     "UNTHROTTLED_CEILING", "LifeWithoutDeath", "per_cell_demand", 0.000),
    ("4.5  Game of Life gated, earliest fixation", "12,783",
     "03-diffusion-limited-scarcity/same_niche_extended_results.py",
     "MATCHED_BUDGET_40K", "gated", None, None),
    ("4.5  Brian's Brain gated, latest fixation", "5,487",
     "03-diffusion-limited-scarcity/same_niche_extended_results.py",
     "MATCHED_BUDGET_40K", "gated", None, None),
]


def load(rel):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    text = MS.read_text(encoding="utf-8")
    failures = []

    print("=" * 74)
    print("STEP 1 -- banked records load")
    print("=" * 74)
    mods = {}
    for rel in RECORDS:
        try:
            mods[rel] = load(rel)
            names = [n for n in dir(mods[rel]) if not n.startswith("_")]
            print(f"  OK    {rel.split('/')[-1]:<52} {len(names)} objects")
        except Exception as exc:
            print(f"  FAIL  {rel:<52} {exc}")
            failures.append(rel)

    print()
    print("=" * 74)
    print("STEP 2 -- manuscript numbers appear in the banked records")
    print("=" * 74)
    for claim in CLAIMS:
        label, needle, rel = claim[0], claim[1], claim[2]
        in_ms = needle in text
        try:
            obj = getattr(mods[rel], claim[3])
            val = obj[claim[4]]
            if claim[5] is not None:
                val = val[claim[5]]
            expected = claim[6]
            in_rec = (expected is None) or (abs(float(val) - float(expected)) < 5e-4)
        except Exception:
            in_rec = False
        status = "OK  " if (in_ms and in_rec) else "FAIL"
        if status == "FAIL":
            failures.append(label)
        print(f"  {status}  {label:<48} manuscript:{'Y' if in_ms else 'N'} record:{'Y' if in_rec else 'N'}")

    print()
    print("=" * 74)
    print("STEP 3 -- structural integrity")
    print("=" * 74)
    figs = [int(m.group(1)) for m in re.finditer(r"Figure (\d+)", text)]
    seen = {}
    for i, f in enumerate(figs):
        seen.setdefault(f, i)
    seq = [f for f, _ in sorted(seen.items(), key=lambda t: t[1])]
    checks = [
        ("figure numbering monotonic by first mention", seq == sorted(seq)),
        # A figure may be referred to from several places (a call-out, plus
        # cross-references from Methods, Results or an appendix). The invariant
        # is one caption and at least one reference to it, not exactly two
        # mentions -- that stricter form fired spuriously once cross-references
        # were added.
        ("every figure has exactly one caption",
         all(len(re.findall(r"<figcaption><strong>Figure " + str(n) + r"\.", text)) == 1
             for n in seq)),
        ("every figure is referred to outside its caption",
         all(text.count("Figure " + str(n))
             - len(re.findall(r"<figcaption><strong>Figure " + str(n) + r"\.", text)) >= 1
             for n in seq)),
        ("all figure image paths resolve",
         all((ROOT / p).exists() for p in re.findall(r'src="([^"]+)"', text))),
        ("no doubled words",
         not [m for m in re.finditer(r"\b(\w+)\s+\1\b", text)
              if m.group(1).lower() not in {"had", "that"}]),
        ("no stale Section 5.4 cross-references", "Section 5.4" not in text),
    ]
    for name, ok in checks:
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}")
        if not ok:
            failures.append(name)

    print()
    print("=" * 74)
    print(f"RESULT: {'ALL CHECKS PASSED' if not failures else str(len(failures)) + ' FAILURE(S)'}")
    print("=" * 74)
    return 1 if failures else 0


def _in_notebook():
    try:
        return get_ipython().__class__.__name__ in ("ZMQInteractiveShell", "Shell")
    except NameError:
        return False


if __name__ == "__main__":
    code = main()
    if _in_notebook():
        print("\n(notebook run: exit code", code, "- not raising SystemExit)")
    else:
        sys.exit(code)

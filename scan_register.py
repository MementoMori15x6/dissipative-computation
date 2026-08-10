#!/usr/bin/env python3
"""
REGISTER SCAN -- flag places where the manuscript states a finding in the
grammar of confession rather than the grammar of result.

This is a WRITING check, not a correctness check. It cannot decide anything on
its own: a limitation honestly stated uses the same grammar as an achievement
undersold. It only surfaces candidates for a human to judge.

Section 6 (Scope and Limitations) is excluded -- apologetic grammar is correct
there by definition.

Usage:  python3 scan_register.py
"""
import re
import pathlib

MANUSCRIPT = "DC_Manuscript_Draft_v2.md"
ROOT = pathlib.Path(__file__).parent
if not (ROOT / MANUSCRIPT).exists():
    ROOT = pathlib.Path.cwd()

PATTERNS = [
    ("A. opens on a negation",
     re.compile(r"^(No |Neither |Nothing |None of |Unfortunately|Regrettably)", re.I)),
    ("B. disclaims a result",
     re.compile(r"(we (offer|make|claim) no|is (accordingly )?withdrawn|no such reading|"
                r"does not establish|cannot be repaired|is not available|was not possible|"
                r"we were unable|no verified|nothing can be)", re.I)),
    ("C. stacked hedges (3+)",
     re.compile(r"\b(only|merely|simply|just|however|although|though|but|nonetheless|"
                r"nevertheless|admittedly)\b", re.I)),
    ("D. concessive opener",
     re.compile(r"^(Although|While |Whilst|Despite|It should be noted|It must be|"
                r"It is worth noting|Admittedly|Granted)", re.I)),
    ("E. defends against an unraised charge",
     re.compile(r"(rather than (a )?(post-hoc|describing|being|merely|simply)|"
                r"not (a|an) (post-hoc|artifact|coincidence)|"
                r"is not (a|an) claim|makes no claim|we do not claim)", re.I)),
    ("F. undercuts its own number",
     re.compile(r"(remain provisional|are provisional|only approximate|approximate in exact|"
                r"should be read as approximate|rests on a single|thin for)", re.I)),
]


def sections(text):
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^#{2,3} (.+)$", text, re.M)]
    out = []
    for i, (pos, name) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        out.append((name, text[pos:end]))
    return out


def main():
    text = (ROOT / MANUSCRIPT).read_text(encoding="utf-8")
    text = re.sub(r"<figure>.*?</figure>", "", text, flags=re.S)
    hits = []
    for name, body in sections(text):
        if name.startswith("6.") or name.startswith("Appendix"):
            continue
        for para in body.split("\n\n"):
            if para.strip().startswith(("|", "#", "**Table")):
                continue
            for sent in re.split(r"(?<=[.!?])\s+", para):
                sent = sent.strip()
                if len(sent.split()) < 6:
                    continue
                for label, pat in PATTERNS:
                    if label.startswith("C."):
                        if len(pat.findall(sent)) >= 3:
                            hits.append((name, label, sent))
                    elif pat.search(sent):
                        hits.append((name, label, sent))

    print("=" * 76)
    print("REGISTER SCAN -- candidates for re-evaluation")
    print("Section 6 and appendices excluded (confession grammar is correct there)")
    print("=" * 76)
    cur = None
    for name, label, sent in hits:
        if name != cur:
            print("\n--- " + name[:70])
            cur = name
        print("  [" + label[0] + "] " + sent[:190])
    print()
    print("=" * 76)
    print("TOTAL: " + str(len(hits)) + " candidates")
    print("A=opens on negation  B=disclaims a result  C=stacked hedges")
    print("D=concessive opener  E=defends unraised charge  F=undercuts own number")
    print("=" * 76)
    print("None of these is automatically wrong. Judge each: is it stating a")
    print("limitation (keep) or reporting a finding in limitation grammar (revise)?")


if __name__ == "__main__":
    main()

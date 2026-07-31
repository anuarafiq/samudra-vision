"""Triage datasets/wikimedia-rmn/ into the "local" (RMN) set the classifier can train on.

Run:   uv run python scripts/wikimedia_rmn_triage.py          -> writes triage.csv
       uv run python scripts/wikimedia_rmn_triage.py --sheets -> also writes contact sheets

Why this is metadata-driven and not eyeball-driven: **a Commons category means "associated
with X", not "shows X"**. `Category:Lekiu class frigate` contains US carriers, German
frigates and Australian fleet-review shots, because a photo taken during a multinational
exercise that a Lekiu attended gets filed under Lekiu. Judging nationality from a 175px
thumbnail is guesswork -- a Kasturi corvette and a foreign corvette look alike at that size.
The *filename* is the Commons page title, and it almost always names the ship or the event,
which is a far stronger signal: `USS_`, `JS_`, `HMNZS_`, `RIMPAC`, `RAN-IFR` are unambiguous.

Verdicts:
  rmn      -- confirmed Royal Malaysian Navy: `KD ` (Kapal Diraja), `TLDM`, or a named RMN hull
  foreign  -- confirmed another navy, or a multinational-formation/fleet-review shot
  mmea     -- Malaysian, but coast guard / enforcement, not navy (`KM `, `KA `, "Coast Guard")
  detail   -- Malaysian *and* naval, but the frame is a weapon/radar/boarding-action close-up
              with no hull silhouette, so it can't teach a local-vs-foreign classifier
  unknown  -- filename carries no nationality signal; needs an eyeball pass

`detail` is matched on filename too (`57mm`, `A_ShM`, `radar`, PASKAL boarding sequences),
*not* on eyeballing thumbnails. A contact-sheet review at 175px turned out to misalign labels
to cells often enough that hand-indexed verdicts weren't trustworthy; filename signals are
reproducible and auditable. This catches the obvious detail shots only -- `rmn` still needs a
careful per-image visual pass for hull visibility before training. Treat `rmn` as an upper
bound, not a final count.

Per the 2026-07-30 decision the classifier trains on `rmn` only -- see TODO.md's "Military
classification approach". `mmea` is kept in the CSV rather than deleted so the decision can be
revisited without re-downloading.

Nothing is moved or deleted; this only writes a verdict column. Downstream crop code should
read triage.csv and filter, never glob the folders.
"""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "datasets" / "wikimedia-rmn"

# Ordered: first match wins, so the explicit foreign-navy prefixes beat the looser
# Malaysian hints (a file can name both, e.g. a US photo of a Malaysian ship).
RULES = [
    ("foreign", re.compile(
        r"\b(USS|USNS|HMAS|HMS|INS|JS|RSS|KRI|BRP|ROKS|HMCS|HMNZS|HNLMS|KDB|ARM|BAP|MV)[ _]"
        r"|RIMPAC|RAN-IFR|Kakadu|Multinational|German[ _]|sails[ _]in[ _]formation"
        r"|break[ _]formation|breakaway|Defense\.gov|US[ _]Navy|U\.S\._Navy", re.I)),
    ("mmea", re.compile(
        r"\b(KM|KA)[ _]|Coast[ _]Guard|Maritime[ _]Enforcement|APMM|Jelajah[ _]Wira"
        r"|Musytari|Banggi|Marikh|Tun[ _]Azizan|Semporna.*Ship-PA", re.I)),
    # Detail/close-up shots: Malaysian and naval, but no hull in frame. Checked before `rmn`
    # so a `KD_Lekiu_57mm.jpg` lands here rather than in the trainable set.
    ("detail", re.compile(
        r"57mm|A_ShM|ShM\.|main_radar|fire_control|Oerlikon|Mortar_Limbo|torpedo"
        r"|breaching|breached|boarding|strike_team|climbs_up", re.I)),
    ("rmn", re.compile(
        r"\bKD[ _]|KD-|KDKasturi|TLDM|Tldm|RMN|Royal[ _]Malaysian|Malaysian[ _]Navy"
        r"|Laksamana|Kasturi|Kedah-class|Kris-class|Scorpene|Tunku[ _]Abdul[ _]Rahman"
        r"|Tun[ _]Razak|Perak[ _]F173|NGPV|Gagah[ _]Samudera|PASKAL|Lekiu|Jebat"
        r"|Hang[ _]Tuah|Maharajalela|Rahmat|Sri-Perlis|Sri-Johor|Selangor", re.I)),
]


def verdict(name):
    probe = " " + name.replace("_", " ")
    for label, pat in RULES:
        if pat.search(probe):
            return label
    return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", action="store_true", help="write contact sheets per verdict")
    args = ap.parse_args()

    rows = []
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        for f in sorted(d.iterdir()):
            rows.append({"file": f"{d.name}/{f.name}", "hull_class": d.name,
                         "verdict": verdict(f.name)})

    counts = Counter(r["verdict"] for r in rows)
    print(f"{'verdict':<10}{'n':>5}")
    for k in ("rmn", "detail", "foreign", "mmea", "unknown"):
        print(f"  {k:<8}{counts[k]:>5}")
    print(f"  {'TOTAL':<8}{len(rows):>5}")

    print("\nby hull_class folder:")
    per = {}
    for r in rows:
        per.setdefault(r["hull_class"], Counter())[r["verdict"]] += 1
    print(f"  {'folder':<20}{'rmn':>5}{'foreign':>8}{'mmea':>6}{'unk':>5}")
    for k in sorted(per):
        c = per[k]
        print(f"  {k:<20}{c['rmn']:>5}{c['foreign']:>8}{c['mmea']:>6}{c['unknown']:>5}")

    out = ROOT / "triage.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "hull_class", "verdict"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out.relative_to(REPO)}")

    if args.sheets:
        import cv2
        import numpy as np
        for v in ("rmn", "unknown", "detail", "foreign", "mmea"):
            fs = [ROOT / r["file"] for r in rows if r["verdict"] == v]
            if not fs:
                continue
            cols, cell = 8, 175
            nrows = (len(fs) + cols - 1) // cols
            sheet = np.full((nrows * (cell + 18), cols * cell, 3), 25, np.uint8)
            for i, f in enumerate(fs):
                im = cv2.imread(str(f))
                if im is None:
                    continue
                h, w_ = im.shape[:2]
                s = min(cell / w_, cell / h)
                im = cv2.resize(im, (max(int(w_ * s), 1), max(int(h * s), 1)))
                r_, c_ = divmod(i, cols)
                oy, ox = r_ * (cell + 18), c_ * cell
                sheet[oy:oy + im.shape[0], ox:ox + im.shape[1]] = im
                cv2.putText(sheet, str(i), (ox + 2, oy + cell + 13),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 235, 150), 1)
            cv2.imwrite(str(ROOT / f"_sheet_{v}.jpg"), sheet)
            print(f"  sheet: _sheet_{v}.jpg ({len(fs)} images)")


if __name__ == "__main__":
    main()

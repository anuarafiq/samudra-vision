"""Per-image visual triage of wikimedia_rmn_triage.py's `rmn`-verdict images.

That script's own docstring says `rmn` is an upper bound, not a final count: filename
rules catch obvious foreign/mmea/detail signals, but hull visibility still needs "a
careful per-image visual pass". All 51 `rmn` images were opened and judged 2026-09-11.
13 don't hold up, for two kinds of reason:

- 5 are equipment/interior close-ups with no hull in frame -- the same failure mode the
  `detail` verdict already covers, just missed by its filename regex (radar/mast/torpedo-
  tube/bridge shots, and one bridge-nameplate close-up that reads "Pahang" despite its
  filename claiming Kelantan). These get reclassified to `detail`.
- 8 are new failure modes with no existing bucket: a museum scale-model in a display case
  (the shot TODO.md predicted), a misfiled/duplicate image, a busy multi-ship formation
  with 3 unidentified vessels, a hull under construction in red primer, a hull mostly
  hidden by ceremonial smoke, and two Scorpene photos with no RMN markings at all (generic
  submarine hull, also operated by India/Chile/Brazil, shot during French sea trials).
  These get a new verdict, `rmn_reject`.

Nothing is moved or deleted; this only rewrites triage.csv's verdict column for these 13
rows. Downstream crop code should keep reading triage.csv and filter on verdict=="rmn",
never glob the folders.

Run: uv run python scripts/wikimedia_rmn_visual_triage.py
"""

import csv
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSV_PATH = REPO / "datasets" / "wikimedia-rmn" / "triage.csv"

# rmn -> detail: equipment/interior close-ups, no hull silhouette in frame.
DETAIL_ADD = {
    "kedah_opv/Royal_Malaysian_Navy_Offshore_Patrol_Vessel_KD_Kelantan__175_.jpg":
        "bridge/superstructure close-up only, no hull or waterline visible "
        '(in-frame nameplate reads "Pahang", not Kelantan)',
    "kedah_opv/TRS-3D_on_KD_Pahang.jpg":
        "radar/mast equipment close-up, no hull visible",
    "lekiu_frigate/KD_Lekiu_DA08_radar.jpg":
        "radar equipment close-up, no hull visible",
    "lekiu_frigate/KD_Lekiu_anti_sub.jpg":
        "torpedo-tube close-up, no hull visible",
    "lekiu_frigate/KD_Lekiu_bridge.jpg":
        "bridge interior, no hull visible",
}

# rmn -> rmn_reject: new failure modes, no existing verdict fits.
REJECT = {
    "kedah_opv/Kris-class_patrol_craft_and_Kedah-class_offshore_patrol_vessel.jpg":
        "museum scale-model in a glass display case, not a real vessel photo",
    "laksamana_corvette/Sandakan_Sabah_Laksamana-Muhammad-Amin-01.jpg":
        "misfiled -- pictures hull 29 (KD Jebat, Lekiu-class) in Sydney, not a "
        "Laksamana-class vessel; duplicates "
        "lekiu_frigate/KD_Jebat__29__in_Elizabeth_Bay.jpg",
    "lekiu_frigate/Malaysian_Navy_ships_1016119215.jpg":
        "busy 4-ship formation, 3 of 4 vessels unidentified/unconfirmed nationality",
    "lekiu_frigate/Pembinaan_kapal_tentera_di_TLDM_Lumut.jpg":
        "hull under construction in red primer + scaffolding, atypical coloring "
        "vs. an operational grey hull",
    "patrol/Sandakan_Sabah_Naval-Base-KD-Sri-Perlis-02.jpg":
        "hull majority obscured by dense ceremonial smoke",
    "scorpene_submarine/Scorpene_malaisien_2_vue_de_trois_quart_arriere_2.jpg":
        "no RMN markings visible (no flag/nameplate); generic Scorpene-class hull "
        "also operated by India/Chile/Brazil; French sea-trials backdrop",
    "scorpene_submarine/Scorpene_malaisien_vue_de_trois_quart_arriere_2.jpg":
        "same as above, near-duplicate angle",
    "scorpene_submarine/Tun_Razak.JPG":
        "hull majority obscured by shipyard scaffolding, no RMN markings visible",
}

# Verified 2026-09-11 against the downloaded dataset. If these stop matching, either the
# dataset or DETAIL_ADD/REJECT changed -- investigate before trusting output.
EXPECTED = {"rmn": 38, "detail": 14, "rmn_reject": 8, "foreign": 90, "mmea": 55, "unknown": 15}


def main():
    rows = list(csv.DictReader(CSV_PATH.open()))

    before = Counter(r["verdict"] for r in rows)
    for r in rows:
        if r["verdict"] != "rmn":
            continue
        if r["file"] in DETAIL_ADD:
            r["verdict"] = "detail"
        elif r["file"] in REJECT:
            r["verdict"] = "rmn_reject"
    after = Counter(r["verdict"] for r in rows)

    print(f"{'verdict':<12}{'before':>8}{'after':>8}")
    for k in ("rmn", "detail", "rmn_reject", "foreign", "mmea", "unknown"):
        print(f"  {k:<10}{before[k]:>8}{after[k]:>8}")

    assert dict(after) == EXPECTED, dict(after)
    assert len(DETAIL_ADD) + len(REJECT) == 13

    with CSV_PATH.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "hull_class", "verdict"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {CSV_PATH.relative_to(REPO)}, matches verified counts")


if __name__ == "__main__":
    main()

"""Convert KFGOD (KOMPSAT Fine-Grained Object Detection dataset) to YOLO format.

Source: datasets/huggingface-KFGOD/{train,val}/{images,labels}/
        (KOMPSAT-3/3A satellite imagery, 0.55-0.7m GSD, KARI, CC BY-SA 4.0)
        https://huggingface.co/datasets/ohhan777/kfgod
Output: datasets/converted-kfgod-yolo/{train,val,test}/{images,labels}/ + data.yaml

Run:  uv run python scripts/kfgod_to_yolo.py
Check: uv run python scripts/kfgod_to_yolo.py --check   (verifies counts, writes nothing)

KFGOD ships 33 classes with normalised YOLO-OBB labels (class_id x1 y1 x2 y2 x3 y3 x4 y4,
four rotated corner points, already in [0,1]). This project's merged dataset uses plain
axis-aligned YOLO boxes everywhere else (matches vhrships_to_yolo.py), so each OBB is
collapsed to the min/max extent of its four corners rather than kept as a rotated box.

Only two of KFGOD's raw splits are downloadable (train/val, 3073/470 images) -- KFGOD's own
test split is withheld by the authors for their own benchmarking. Our train/val/test therefore
keeps KFGOD's train as-is and splits KFGOD's val 50/50 into our val/test, rather than reshuffling
everything (KFGOD's own split was built stratified per-class, no reason to throw that away).

speedboat is a capped random subsample of KFGOD's `motorboat` class (raw total 34,574 across
train+val alone), not a straight 1:1 map. motorboat is KOMPSAT's catch-all for small
motor-powered craft, not confirmed recreational-speedboat-specific the way VHRShips'
944-instance `smallBoat` class turned out (on inspection) to be barges/utility boats, not
speedboats, and got excluded outright. Decision made 2026-07-30 (user-approved): map it, but
cap the sample so this one KOMPSAT-only class doesn't dwarf every other aerial class in the
merged dataset and skew the model toward KOMPSAT's specific resolution/colour signature for
'speedboat'. See GUIDELINES.md's Findings section for the full writeup.
"""

import argparse
import random
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "datasets" / "huggingface-KFGOD"
OUT = REPO / "datasets" / "converted-kfgod-yolo"

# Canonical project taxonomy order, from GUIDELINES.md "Mandatory class taxonomy".
# Must match vhrships_to_yolo.py exactly -- class IDs need to line up when these get merged.
CLASSES = [
    "container_ship",
    "tanker",
    "cargo",
    "passenger_ferry",
    "yacht",
    "speedboat",
    "fishing_boat",
    "military",
]
CLASS_ID = {name: i for i, name in enumerate(CLASSES)}

# KFGOD's 33 raw classes, in class-index order (0-32). Verified two ways: cross-referenced a
# DOTA-format label file (which uses literal class names, not numeric IDs) against the YOLO
# numeric IDs for the same objects, then confirmed every raw class's summed train+val instance
# count against the paper's Table 5 Total column minus its Test column (paper: Lee et al.,
# Remote Sensing 2025, Table 4 for the class list, Table 5 for per-class counts).
KFGOD_ORDER = [
    "MB", "SB", "TB", "BG", "FB", "FR", "CS", "OT", "DS", "WS",   # Ship (10)
    "FA", "LM", "SC", "LC", "HC",                                  # Aircraft (5)
    "SV", "TR", "BS", "TN",                                        # Vehicle (4)
    "CT", "CG",                                                    # Container (2)
    "CR", "BR", "DM", "ST", "SF", "SD", "SP", "RA", "HP", "WT", "AF", "MR",  # Infrastructure (12)
]

# Raw KFGOD abbreviation -> our bucket. Only classes with a clean, established or
# explicitly-approved mapping are included; everything else is dropped deliberately:
# SB (sailboat), TB (tugboat), BG (barge), DS (drill ship) have no clean bucket in our
# taxonomy, consistent with VHRShips excluding tug/barge/drill-adjacent raw classes.
MAP = {
    "FB": "fishing_boat",
    "WS": "military",
    "CS": "container_ship",   # bonus volume, container_ship already cleared without this
    "OT": "tanker",           # bonus volume, tanker already cleared without this
    "FR": "passenger_ferry",  # bonus volume, passenger_ferry already cleared without this
    "MB": "speedboat",        # capped subsample, see SPEEDBOAT_CAP and the module docstring
}

# Cap applied to motorboat -> speedboat after random subsampling (fixed seed, see --seed).
# Picked from the user-approved "roughly 1,000-1,500" range, 2026-07-30.
SPEEDBOAT_CAP = 1200

# Verified 2026-07-30 by summing every label file's raw class counts and checking against
# the KFGOD paper's Table 5 (Total minus Test, since only train+val are downloadable).
# If these ever stop matching, the source data or KFGOD_ORDER drifted, stop and investigate.
EXPECTED_TOTAL_PARSED = 784153  # all 33 classes, train+val combined
EXPECTED_RAW_COUNTS = {
    "MB": 34574, "FB": 4769, "WS": 386, "CS": 952, "OT": 212, "FR": 1873,
}


def obb_to_axis_aligned(coords):
    """[x1,y1,x2,y2,x3,y3,x4,y4] normalised OBB corners -> normalised cx,cy,w,h, clamped."""
    xs, ys = coords[0::2], coords[1::2]
    x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)
    cx, cy, w, h = (x_min + x_max) / 2, (y_min + y_max) / 2, x_max - x_min, y_max - y_min
    return tuple(min(max(v, 0.0), 1.0) for v in (cx, cy, w, h))


def parse_labels(raw_split):
    """-> {stem: [(bucket, cx, cy, w, h), ...]}, raw_counts, mb_candidates (image stem, box).

    mb_candidates is kept separate from the per-image dict so the speedboat cap can be
    applied globally before merging sampled instances back into their source images.
    """
    per_image, raw_counts, mb_candidates = {}, Counter(), []
    label_dir = SRC / raw_split / "labels"
    for path in sorted(label_dir.glob("*.txt")):
        stem = path.stem
        kept = []
        for line in path.read_text().splitlines():
            parts = line.split()
            if not parts:
                continue
            class_id, coords = int(parts[0]), list(map(float, parts[1:9]))
            raw = KFGOD_ORDER[class_id]
            raw_counts[raw] += 1
            bucket = MAP.get(raw)
            if bucket is None:
                continue
            box = obb_to_axis_aligned(coords)
            if bucket == "speedboat":
                mb_candidates.append((stem, box))
            else:
                kept.append((bucket, *box))
        if kept:
            per_image[stem] = kept
    return per_image, raw_counts, mb_candidates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify counts only, write nothing")
    ap.add_argument("--seed", type=int, default=1337)
    args = ap.parse_args()

    per_image = {}
    raw_counts = Counter()
    mb_candidates = []  # (stem, box) across both raw splits, capped together
    stem_to_raw_split = {}
    for raw_split in ("train", "val"):
        pi, rc, mb = parse_labels(raw_split)
        for stem in pi:
            stem_to_raw_split[stem] = raw_split
        for stem, box in mb:
            stem_to_raw_split[stem] = raw_split
        per_image.update(pi)
        raw_counts.update(rc)
        mb_candidates.extend(mb)

    total_parsed = sum(raw_counts.values())
    print(f"raw instances parsed (all 33 classes, train+val): {total_parsed}")
    print(f"motorboat candidates before cap: {len(mb_candidates)}")

    assert total_parsed == EXPECTED_TOTAL_PARSED, \
        f"parsed {total_parsed}, expected {EXPECTED_TOTAL_PARSED}"
    for raw, want in EXPECTED_RAW_COUNTS.items():
        got = raw_counts[raw]
        assert got == want, f"{raw}: got {got}, expected {want}"
    print("raw per-class counts match the verified table")

    # Cap motorboat -> speedboat via a fixed-seed random subsample, then merge the sampled
    # instances back into their source images' kept lists.
    rng = random.Random(args.seed)
    sampled = mb_candidates if len(mb_candidates) <= SPEEDBOAT_CAP \
        else rng.sample(mb_candidates, SPEEDBOAT_CAP)
    for stem, box in sampled:
        per_image.setdefault(stem, []).append(("speedboat", *box))
    print(f"motorboat -> speedboat after cap: {len(sampled)} (cap={SPEEDBOAT_CAP})")

    bucket_counts = Counter()
    for boxes in per_image.values():
        for bucket, *_ in boxes:
            bucket_counts[bucket] += 1
    print(f"images with >=1 mapped instance: {len(per_image)}")
    print(f"mapped instances (post-cap): {sum(bucket_counts.values())}")

    if args.check:
        print("\n--check: nothing written")
        return

    # KFGOD's own train split stays our train as-is (stratified per-class by the original
    # authors, no reason to reshuffle). KFGOD's val (their held-out set) gets split 50/50
    # into our val/test, since their real test split isn't downloadable.
    val_stems = sorted(s for s in per_image if stem_to_raw_split[s] == "val")
    rng.shuffle(val_stems)
    half = len(val_stems) // 2
    out_split_of = {s: "train" for s in per_image if stem_to_raw_split[s] == "train"}
    out_split_of.update({s: "val" for s in val_stems[:half]})
    out_split_of.update({s: "test" for s in val_stems[half:]})

    import shutil
    for split in ("train", "val", "test"):
        if (OUT / split).exists():
            shutil.rmtree(OUT / split)
            print(f"cleared previous {split}/")
        (OUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUT / split / "labels").mkdir(parents=True, exist_ok=True)

    per_split = defaultdict(Counter)
    images_per_split = Counter()
    for stem, boxes in per_image.items():
        raw_split, out_split = stem_to_raw_split[stem], out_split_of[stem]
        src_img = SRC / raw_split / "images" / f"{stem}.png"
        if not src_img.exists():
            continue
        lines = []
        for bucket, cx, cy, w, h in boxes:
            lines.append(f"{CLASS_ID[bucket]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            per_split[out_split][bucket] += 1
        (OUT / out_split / "labels" / f"{stem}.txt").write_text("\n".join(lines) + "\n")
        link = OUT / out_split / "images" / f"{stem}.png"
        if not link.exists():
            link.symlink_to(src_img)  # symlink: images total ~5.7GB, don't duplicate
        images_per_split[out_split] += 1

    (OUT / "data.yaml").write_text(
        "# Generated by scripts/kfgod_to_yolo.py -- do not hand-edit, rerun instead.\n"
        "# Source: KFGOD (Lee, Hong, Seo & Oh 2025, KARI), KOMPSAT-3/3A satellite imagery,\n"
        "# CC BY-SA 4.0 (share-alike -- see GUIDELINES.md Findings before redistributing).\n"
        "# https://huggingface.co/datasets/ohhan777/kfgod\n"
        "train: train/images\nval: val/images\ntest: test/images\n\n"
        f"nc: {len(CLASSES)}\nnames: {CLASSES}\n"
    )

    print(f"\nwrote -> {OUT.relative_to(REPO)}")
    header = f"{'bucket':<16}" + "".join(f"{s:>8}" for s in ("train", "val", "test")) + f"{'total':>8}"
    print("\n" + header)
    for bucket in CLASSES:
        row = [per_split[s][bucket] for s in ("train", "val", "test")]
        print(f"{bucket:<16}" + "".join(f"{v:>8}" for v in row) + f"{sum(row):>8}")
    totals = [sum(per_split[s].values()) for s in ("train", "val", "test")]
    print(f"{'ALL':<16}" + "".join(f"{v:>8}" for v in totals) + f"{sum(totals):>8}")
    print(f"\nimages: " + ", ".join(f"{s}={images_per_split[s]}" for s in ("train", "val", "test")))


if __name__ == "__main__":
    main()

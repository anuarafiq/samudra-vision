"""Convert VHRShips (metaFileV8.json + _mergedData/) to YOLO format.

Source: datasets/kaggle-VHRShips/  (Google Earth satellite imagery, MIT, 6312 images)
Output: datasets/converted-vhrships-yolo/{train,val,test}/{images,labels}/ + data.yaml

Run:  uv run python scripts/vhrships_to_yolo.py
Check: uv run python scripts/vhrships_to_yolo.py --check   (verifies counts, writes nothing)

Why this script exists: metaFileV8.csv (the obvious MATLAB export) is corrupted for 29% of rows,
variable-length nested bbox arrays spill into neighbouring columns. metaFileV8.json is clean.
See TODO.md's VHRShips section for the full history.
"""

import argparse
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "datasets" / "kaggle-VHRShips"
OUT = REPO / "datasets" / "converted-vhrships-yolo"

# Canonical project taxonomy order, from GUIDELINES.md "Mandatory class taxonomy".
# speedboat gets 0 instances from VHRShips but keeps its slot so class IDs stay
# consistent with every other converted source when these get merged.
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

# VHRShips raw class name -> our bucket. Raw names keep the source's own spelling
# ("yatch", "passanger", "auxilary" are literal, not typos here).
# Anything absent is deliberately dropped, see TODO.md for the per-class rationale.
# Most notably smallBoat (944) is NOT speedboat: spot-checked crops were barges and
# rafted utility boats, not recreational craft.
MAP = {
    "container": "container_ship",
    "tanker": "tanker",
    "oilTanker": "tanker",
    "generalCargo": "cargo",
    "oreCarrier": "cargo",
    "bulkCarrier": "cargo",
    "coaster": "cargo",
    "ferry": "passenger_ferry",
    "roro": "passenger_ferry",
    "passanger": "passenger_ferry",
    "smallPassanger": "passenger_ferry",
    "yatch": "yacht",
    "fishing": "fishing_boat",
    "destroyer": "military",
    "patrolForce": "military",
    "frigate": "military",
    "cruiser": "military",
    "submarine": "military",
    "landing": "military",
    "aircraft": "military",
    "auxilary": "military",
}

# Verified 2026-07-30 against the GitHub README's stated total and a manual recount.
# If these ever stop matching, the JSON or the mapping changed, stop and investigate.
EXPECTED_TOTAL_PARSED = 11337
EXPECTED_BUCKETS = {
    "yacht": 1621,
    "cargo": 2450,
    "tanker": 1373,
    "military": 616,
    "passenger_ferry": 763,
    "container_ship": 580,
    "fishing_boat": 37,
    "speedboat": 0,
}


def boxes_of(record):
    """allBoundingBoxes is a flat [x,y,w,h] for one ship, or a list of them for several."""
    bb = record["allBoundingBoxes"]
    if not bb:
        return []
    return [bb] if not isinstance(bb[0], list) else bb


def labels_of(record):
    lb = record["allLabels"]
    return lb if isinstance(lb, list) else [lb]


def parse(records):
    """-> {imageName: [(bucket, x, y, w, h), ...]}, plus stats. Pixel coords, x/y top-left."""
    per_image, raw_counts, bucket_counts = {}, Counter(), Counter()
    total_parsed = 0
    for r in records:
        boxes, labels = boxes_of(r), labels_of(r)
        if len(boxes) != len(labels):
            sys.exit(f"label/bbox count mismatch on {r['imageName']}: {len(labels)} vs {len(boxes)}")
        total_parsed += len(boxes)
        kept = []
        for label, box in zip(labels, boxes):
            raw = label.rsplit("_", 1)[0]  # strip the trailing numeric id: "yatch_18" -> "yatch"
            raw_counts[raw] += 1
            bucket = MAP.get(raw)
            if bucket is None:
                continue  # unmapped class, drop this box but keep any mapped ones on the image
            bucket_counts[bucket] += 1
            kept.append((bucket, *box))
        if kept:
            per_image[r["imageName"]] = kept
    return per_image, raw_counts, bucket_counts, total_parsed


def to_yolo(box, iw, ih):
    """[x,y,w,h] pixels, x/y top-left (verified by cropping) -> normalised cx,cy,w,h, clamped."""
    x, y, w, h = box
    cx, cy = (x + w / 2) / iw, (y + h / 2) / ih
    nw, nh = w / iw, h / ih
    return tuple(min(max(v, 0.0), 1.0) for v in (cx, cy, nw, nh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify counts only, write nothing")
    ap.add_argument("--seed", type=int, default=1337)
    args = ap.parse_args()

    records = json.loads((SRC / "metaFileV8.json").read_text())
    per_image, raw_counts, bucket_counts, total_parsed = parse(records)

    print(f"records: {len(records)}   instances parsed: {total_parsed}")
    print(f"images with >=1 mapped instance: {len(per_image)}")
    print(f"mapped instances: {sum(bucket_counts.values())}   "
          f"dropped (unmapped classes): {total_parsed - sum(bucket_counts.values())}")

    assert total_parsed == EXPECTED_TOTAL_PARSED, \
        f"parsed {total_parsed}, expected {EXPECTED_TOTAL_PARSED}"
    for bucket, want in EXPECTED_BUCKETS.items():
        got = bucket_counts[bucket]
        assert got == want, f"{bucket}: got {got}, expected {want}"
    print("counts match the verified per-class table")

    if args.check:
        print("\n--check: nothing written")
        return

    # ponytail: plain random split per HANDOFF spec. Known ceiling: VHRShips filename
    # prefixes (BV, BK, ...) are harbour codes, so two images of the same port can land in
    # different splits and slightly inflate val/test. Group-split by prefix if that ever
    # looks like it's flattering the numbers.
    names = sorted(per_image)
    random.Random(args.seed).shuffle(names)
    n_train, n_val = int(len(names) * 0.8), int(len(names) * 0.1)
    splits = {
        "train": names[:n_train],
        "val": names[n_train:n_train + n_val],
        "test": names[n_train + n_val:],
    }

    # Clear previous output first. Without this, re-running with a different seed leaves the old
    # split's labels/symlinks in place and the same image ends up in two splits, which is silent
    # train/val leakage. Only ever touches directories this script generates.
    for split in splits:
        if (OUT / split).exists():
            shutil.rmtree(OUT / split)
            print(f"cleared previous {split}/")

    per_split = defaultdict(Counter)
    missing = 0
    for split, split_names in splits.items():
        (OUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUT / split / "labels").mkdir(parents=True, exist_ok=True)
        for name in split_names:
            src_img = SRC / "_mergedData" / name
            if not src_img.exists():
                missing += 1
                continue
            with Image.open(src_img) as im:
                iw, ih = im.size  # read per image, don't assume 1280x720
            lines = []
            for bucket, *box in per_image[name]:
                cx, cy, w, h = to_yolo(box, iw, ih)
                lines.append(f"{CLASS_ID[bucket]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
                per_split[split][bucket] += 1
            (OUT / split / "labels" / f"{Path(name).stem}.txt").write_text("\n".join(lines) + "\n")
            link = OUT / split / "images" / name
            if not link.exists():
                link.symlink_to(src_img)  # symlink: _mergedData is 2.3GB, don't duplicate it

    (OUT / "data.yaml").write_text(
        "# Generated by scripts/vhrships_to_yolo.py -- do not hand-edit, rerun instead.\n"
        "# Source: VHRShips (Kizilkaya, Alganci & Sertel 2022), Google Earth imagery, MIT.\n"
        "# https://github.com/radres333/VHRShips\n"
        "train: train/images\nval: val/images\ntest: test/images\n\n"
        f"nc: {len(CLASSES)}\nnames: {CLASSES}\n"
    )

    print(f"\nwrote -> {OUT.relative_to(REPO)}")
    if missing:
        print(f"warning: {missing} images listed in the JSON were not on disk, skipped")
    header = f"{'bucket':<16}" + "".join(f"{s:>8}" for s in splits) + f"{'total':>8}"
    print("\n" + header)
    for bucket in CLASSES:
        row = [per_split[s][bucket] for s in splits]
        print(f"{bucket:<16}" + "".join(f"{v:>8}" for v in row) + f"{sum(row):>8}")
    totals = [sum(per_split[s].values()) for s in splits]
    print(f"{'ALL':<16}" + "".join(f"{v:>8}" for v in totals) + f"{sum(totals):>8}")
    print(f"\nimages: " + ", ".join(f"{s}={len(v)}" for s, v in splits.items()))


if __name__ == "__main__":
    main()

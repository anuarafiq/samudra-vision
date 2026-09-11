"""Crop `military`-class boxes out of datasets/merged-yolo/'s train split, for the
second-stage local-vs-foreign warship classifier (TODO.md's "Military classification
approach" section; HANDOFF.md 2026-09-11 hands this off).

Two problems block just grabbing every foreign box:
- `kapal` and `marina2` sources are Malaysian/mixed-provenance -- crops from them would be
  mislabelled "foreign", so both are excluded by their `tag__` filename prefix (see
  scripts/merge_dataset.py's `link_pair`).
- ~1:157 raw imbalance against the 38 confirmed-local images in datasets/wikimedia-rmn/
  triage.csv (verdict == "rmn"). Training on the raw ratio drowns the local class, but 1:1
  leaves too few images for a CNN classifier to learn from. This targets 5:1 (decided
  2026-09-11: enough foreign diversity without discarding most of the local class's weight
  per batch), computed from the *actual* rmn count at runtime, not hardcoded.

Output: datasets/military-foreign-crops/
  all/          every eligible crop (12% padding around each YOLO box, clamped to the image)
  sampled/      a 5x-rmn-count random sample of all/, fixed seed -- what the classifier trains on
  manifest.csv  one row per crop in all/: crop file, source image, source tag, box

Run:   uv run python scripts/wikimedia_rmn_crop_foreign.py
Check: uv run python scripts/wikimedia_rmn_crop_foreign.py --check   (counts only, writes nothing)
"""

import argparse
import csv
import random
import shutil
from pathlib import Path

from PIL import Image

from merge_dataset import read_names

REPO = Path(__file__).resolve().parent.parent
DATASETS = REPO / "datasets"
MERGED = DATASETS / "merged-yolo"
OUT = DATASETS / "military-foreign-crops"
TRIAGE_CSV = DATASETS / "wikimedia-rmn" / "triage.csv"

EXCLUDE_PREFIXES = ("kapal__", "marina2__")
PADDING = 0.12
SAMPLE_RATIO = 5
SEED = 1337


def military_class_id():
    return str(read_names(MERGED).index("military"))


def crop_box(img, cx, cy, w, h):
    iw, ih = img.size
    x1, y1 = (cx - w / 2) * iw, (cy - h / 2) * ih
    x2, y2 = (cx + w / 2) * iw, (cy + h / 2) * ih
    pad_x, pad_y = (x2 - x1) * PADDING, (y2 - y1) * PADDING
    x1, y1 = max(0, x1 - pad_x), max(0, y1 - pad_y)
    x2, y2 = min(iw, x2 + pad_x), min(ih, y2 + pad_y)
    return img.crop((x1, y1, x2, y2))


def rmn_count():
    with TRIAGE_CSV.open() as f:
        return sum(1 for row in csv.DictReader(f) if row["verdict"] == "rmn")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="count only, write nothing")
    args = ap.parse_args()

    military_id = military_class_id()
    labels_dir, images_dir = MERGED / "train" / "labels", MERGED / "train" / "images"

    if not args.check:
        if OUT.exists():
            shutil.rmtree(OUT)
        (OUT / "all").mkdir(parents=True)

    rows = []
    for label_path in sorted(labels_dir.glob("*.txt")):
        stem = label_path.stem
        if stem.startswith(EXCLUDE_PREFIXES):
            continue
        boxes = [parts for ln in label_path.read_text().splitlines()
                 if (parts := ln.split()) and parts[0] == military_id]
        if not boxes:
            continue
        img_candidates = list(images_dir.glob(stem + ".*"))
        if not img_candidates:
            continue
        img_path = img_candidates[0]
        img = None if args.check else Image.open(img_path)
        for i, parts in enumerate(boxes):
            cx, cy, w, h = (float(v) for v in parts[1:5])
            crop_name = f"{stem}__{i}.jpg"
            rows.append({
                "crop_file": crop_name, "source_image": str(img_path.relative_to(REPO)),
                "source_tag": stem.split("__", 1)[0], "cx": cx, "cy": cy, "w": w, "h": h,
            })
            if not args.check:
                crop_box(img, cx, cy, w, h).convert("RGB").save(OUT / "all" / crop_name)

    print(f"eligible military crops: {len(rows)}")
    assert not any(r["source_tag"] in ("kapal", "marina2") for r in rows), \
        "excluded source leaked through -- prefix check is broken"

    if args.check:
        print("--check: nothing written")
        return

    with (OUT / "manifest.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    n_local = rmn_count()
    sample_n = min(len(rows), n_local * SAMPLE_RATIO)
    random.seed(SEED)
    sampled = random.sample(rows, sample_n)

    (OUT / "sampled").mkdir()
    for row in sampled:
        shutil.copy(OUT / "all" / row["crop_file"], OUT / "sampled" / row["crop_file"])

    print(f"local (rmn) count: {n_local}, sampled foreign: {sample_n} (ratio {SAMPLE_RATIO}:1)")
    assert len(rows) == len(list((OUT / "all").iterdir())), "manifest/all count mismatch"
    assert len(list((OUT / "sampled").iterdir())) == sample_n, "sampled folder count mismatch"


if __name__ == "__main__":
    main()

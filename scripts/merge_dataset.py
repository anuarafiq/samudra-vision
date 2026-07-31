"""Merge every remapped/converted source into one unified YOLO dataset.

Output: datasets/merged-yolo/{train,val,test}/{images,labels}/ + data.yaml

Run:   uv run python scripts/merge_dataset.py
Check: uv run python scripts/merge_dataset.py --check   (verifies counts, writes nothing)

Three kinds of source, three handling paths:

1. Pre-converted (`converted-vhrships-yolo`, `converted-kfgod-yolo`): already in the
   canonical 8-class order with their own train/val/test split decided by their own
   scripts. Passed through as-is, just re-symlinked (their images are themselves
   symlinks into `kaggle-VHRShips`/`huggingface-KFGOD`; re-symlinking to the *resolved*
   real path avoids a chain of two indirections).

2. Native Roboflow sources (16 of them, `NATIVE_SOURCES` below): each ships its own
   raw class list and its own train/valid/test split. Every raw class with an
   established mapping (per GUIDELINES.md's "Class remapping" section) is translated
   to a bucket; everything else is dropped silently, matching every other conversion
   script in this project. `valid` is renamed `val`; a source missing a split (e.g.
   `Seaships7000` has no `valid`, `Boats Detection` has no `valid`/`test`) simply
   contributes nothing to that split, it isn't an error.

3. `roboflow-Marina 2.yolov11`: a mixed-provenance aggregate, handled separately
   because its own `data.yaml` cannot be trusted at face value (see GUIDELINES.md's
   Marina 2 finding). Its numeric-filename family is frontal shore-CCTV redundant
   with `Seaships7000` and is dropped outright; `DJI_*`/`Screenshot from 2024-05-29
   */`IPgiBNOPCjQ-*` are genuinely aerial and kept whole; `twist_*` reuses the
   per-image verdicts already established in `marina2_twist_triage.py` rather than
   re-deriving them.

No source's own train/valid/test split is reshuffled — each source already made a
reasonable split decision (Roboflow's own, or the two `converted-*` scripts' own),
and reshuffling 18 sources under one global seed would be far more likely to
introduce a leakage bug than to fix one.

Every source is symlinked (`kaggle-VHRShips` alone is 2.3GB, KFGOD is 5.7GB), never
copied, and every output filename is prefixed with a short per-source tag to
guarantee uniqueness across sources whose original filenames could otherwise collide
(short numeric names, generic `image.jpg`, etc).
"""

import argparse
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import marina2_twist_triage as marina2_triage

REPO = Path(__file__).resolve().parent.parent
DATASETS = REPO / "datasets"
OUT = DATASETS / "merged-yolo"

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

# Already-converted sources: (folder name, short tag). Passed through as-is.
PRECONVERTED = [
    ("converted-vhrships-yolo", "vhrships"),
    ("converted-kfgod-yolo", "kfgod"),
]

# Native Roboflow sources: folder name -> (short tag, {raw class name: bucket}).
# Only raw classes with an established mapping are included; everything else is
# dropped deliberately (generic/ambiguous/out-of-taxonomy) per GUIDELINES.md's
# "Class remapping: definitive mapping" section, which documents the exclusion
# rationale per dataset (LNG/gas-carriers, tug/patrol/kayak/canoe variants, etc).
NATIVE_SOURCES = {
    "roboflow-VESSELimg.v4i.yolov11": ("vesselimg", {
        "Container": "container_ship", "Chemical": "tanker", "Passenger-RoRo": "passenger_ferry",
    }),
    "roboflow-Seaships7000.v1i.yolov11": ("seaships7000", {
        "container ship": "container_ship", "ore carrier": "cargo",
        "bulk cargo carrier": "cargo", "general cargo ship": "cargo",
        "passenger ship": "passenger_ferry", "fishing boat": "fishing_boat",
    }),
    "roboflow-Vessel.v2i.yolov11": ("vesselv2", {
        "Container": "container_ship", "tanker": "tanker", "Bulker": "cargo", "warship": "military",
    }),
    "roboflow-MyBoats.v2i.yolov11": ("myboats", {
        "Container ship": "container_ship", "Oil tanker": "tanker",
        "General cargo ship": "cargo", "Sand carrier": "cargo", "Bulk carrier": "cargo",
        "Coastal tourist passenger ship": "passenger_ferry", "Ro-ro ship": "passenger_ferry",
        "Luxury Cruise": "passenger_ferry", "Speed boat": "speedboat", "Fishing vessel": "fishing_boat",
    }),
    "roboflow-typesofships.v6i.yolov11": ("typesofships", {
        "container": "container_ship", "bulk_carrier": "cargo",
        "combat_vessel": "military", "yacht": "yacht",
    }),
    "roboflow-Tanker.v1i.yolov11": ("tankerv1", {
        "Container": "container_ship", "Tanker": "tanker", "Cargo": "cargo",
    }),
    "roboflow-ship detection.v2i.yolov11": ("shipdetectionv2", {
        "container ship": "container_ship", "tanker": "tanker", "cargo ship": "cargo",
        "passenger ship": "passenger_ferry", "speedboat": "speedboat",
        "fishing boat": "fishing_boat", "warship": "military",
    }),
    "roboflow-Ship2.v1i.yolov11": ("ship2", {
        "Cargo": "cargo", "Carrier": "cargo", "Cruise": "passenger_ferry",
        "Military": "military", "Tanker": "tanker",
    }),
    "roboflow-vessel.v1i.yolov11": ("vesselv1", {
        "Cargo": "cargo", "Carrier": "cargo", "Cruise": "passenger_ferry",
        "Tanker": "tanker", "Warship": "military",
    }),
    "roboflow-kapal-penumpang-done.v1i.yolov11": ("kapalpenumpang", {
        "kapal_penumpang": "passenger_ferry",
    }),
    "roboflow-Yacht Detection.v2-alphayacht1.0.yolov11": ("yachtdetection", {
        "yacht": "yacht", "ferry": "passenger_ferry",
    }),
    "roboflow-Sea Vessels Dataset.v2-sea_vessels_v2.yolov11": ("seavessels", {
        "Fishing Boat": "fishing_boat", "Merchant Ship": "cargo",
        "Military Ship": "military", "Submarine": "military", "Yacht": "yacht",
    }),
    "roboflow-Boats Detection.v15i.yolov11": ("boatsdetection", {
        "cargo": "cargo", "speed": "speedboat", "yacht": "yacht",
    }),
    "roboflow-Buoys and Boats.v3i.yolov11": ("buoysandboats", {
        "merchant_ship": "cargo", "fishing_boat": "fishing_boat",
        "yacht": "yacht", "cruise": "passenger_ferry",
    }),
    "roboflow-Warship.v4i.yolov11": ("warshipv4", {
        "warship": "military",
    }),
    "roboflow-kapal.v1i.yolov11": ("kapal", {
        "cargo": "cargo", "speedboat": "speedboat", "warships": "military",
        "tanker": "tanker", "nelayan": "fishing_boat",
    }),
}

# Verified 2026-07-30: hand-summed from GUIDELINES.md's definitive per-dataset mapping
# table, then cross-checked arithmetically -- NATIVE_SOURCES totals + VHRShips (7440) +
# KFGOD (9392) + Marina2's clean-aerial contribution (132) reproduce the sufficiency
# table's Total column exactly for all 8 buckets. If this stops matching, either a
# source changed on disk or a mapping table above has a typo -- investigate before
# trusting the merge.
EXPECTED_NATIVE_TOTALS = {
    "container_ship": 6862, "tanker": 2413, "cargo": 8791, "passenger_ferry": 6964,
    "yacht": 3027, "speedboat": 3466, "fishing_boat": 3482, "military": 5430,
}
EXPECTED_MARINA2_TOTALS = {"cargo": 4, "fishing_boat": 9, "military": 92, "speedboat": 27}

MARINA2_DIR = "roboflow-Marina 2.yolov11"
MARINA2_TAG = "marina2"
MARINA2_MAP = {
    "cargo ship": "cargo", "fishing boat": "fishing_boat", "military ship": "military",
    "passenger ship": "passenger_ferry", "speedboat": "speedboat",
}
# Genuinely aerial filename families, kept whole (see GUIDELINES.md's Marina 2 finding).
# The numeric family (bare 6-digit names) is frontal shore-CCTV redundant with
# Seaships7000 and isn't in this list -- it's dropped by omission.
MARINA2_CLEAN_AERIAL_PREFIXES = ("DJI_", "Screenshot from 2024-05-29", "IPgiBNOPCjQ-")


def read_names(source_dir):
    """Parse the `names:` list out of a Roboflow data.yaml without needing PyYAML."""
    text = (source_dir / "data.yaml").read_text()
    m = re.search(r"^names:\s*\[(.*)\]", text, re.M)
    return [n.strip().strip("'\"") for n in m.group(1).split(",")]


def find_splits(source_dir):
    """-> {our_split_name: split_dir}, e.g. {'train': .../train, 'val': .../valid}."""
    rename = {"train": "train", "valid": "val", "val": "val", "test": "test"}
    out = {}
    for child in source_dir.iterdir():
        if child.is_dir() and child.name in rename and (child / "labels").is_dir():
            out[rename[child.name]] = child
    return out


def link_pair(out_split, tag, stem, img_src, label_lines, write=True):
    # Drop zero-area boxes. `ultralytics` does *not* filter these (verified against
    # verify_image_label: it reports nc=0 and keeps the row), so a w=0/h=0 row would
    # reach training as a garbage regression target. Exactly one exists today --
    # vhrships__SA_751, inherited from VHRShips' own labels -- but the guard is here
    # rather than special-cased because all three source paths funnel through here.
    label_lines = [ln for ln in label_lines
                   if all(float(v) > 0 for v in ln.split()[3:5])]
    if not label_lines or not write:
        return
    out_name = f"{tag}__{stem}"
    (OUT / out_split / "labels" / f"{out_name}.txt").write_text("\n".join(label_lines) + "\n")
    link = OUT / out_split / "images" / f"{out_name}{img_src.suffix}"
    if not link.exists():
        link.symlink_to(img_src.resolve())


def process_native(folder_name, tag, class_map, bucket_counts, write=True):
    source_dir = DATASETS / folder_name
    names = read_names(source_dir)
    for our_split, split_dir in find_splits(source_dir).items():
        images_dir = split_dir / "images"
        for label_path in sorted((split_dir / "labels").glob("*.txt")):
            img_candidates = list(images_dir.glob(label_path.stem + ".*"))
            if not img_candidates:
                continue
            lines = []
            for line in label_path.read_text().splitlines():
                parts = line.split()
                if not parts:
                    continue
                raw = names[int(parts[0])]
                bucket = class_map.get(raw)
                if bucket is None:
                    continue
                lines.append(f"{CLASS_ID[bucket]} {' '.join(parts[1:5])}")
                bucket_counts[bucket] += 1
            link_pair(our_split, tag, label_path.stem, img_candidates[0], lines, write=write)


def process_marina2(bucket_counts, write=True):
    source_dir = DATASETS / MARINA2_DIR
    names = read_names(source_dir)
    for our_split, split_dir in find_splits(source_dir).items():
        images_dir = split_dir / "images"
        for label_path in sorted((split_dir / "labels").glob("*.txt")):
            stem = label_path.stem
            keep = stem.startswith(MARINA2_CLEAN_AERIAL_PREFIXES)
            if stem.startswith("twist_"):
                prefix = stem.split("_")[0] + "_" + stem.split("_")[1] + "_"
                keep = prefix not in marina2_triage.DROP_PREFIXES
            if not keep:
                continue
            img_candidates = list(images_dir.glob(stem + ".*"))
            if not img_candidates:
                continue
            lines = []
            for line in label_path.read_text().splitlines():
                parts = line.split()
                if not parts:
                    continue
                raw = names[int(parts[0])]
                bucket = MARINA2_MAP.get(raw)
                if bucket is None:
                    continue
                lines.append(f"{CLASS_ID[bucket]} {' '.join(parts[1:5])}")
                bucket_counts[bucket] += 1
            link_pair(our_split, MARINA2_TAG, stem, img_candidates[0], lines, write=write)


def process_preconverted(folder_name, tag, bucket_counts):
    source_dir = DATASETS / folder_name
    for split in ("train", "val", "test"):
        images_dir, labels_dir = source_dir / split / "images", source_dir / split / "labels"
        if not labels_dir.is_dir():
            continue
        for label_path in sorted(labels_dir.glob("*.txt")):
            img_candidates = list(images_dir.glob(label_path.stem + ".*"))
            if not img_candidates:
                continue
            lines = label_path.read_text().splitlines()
            for line in lines:
                bucket_counts[CLASSES[int(line.split()[0])]] += 1
            link_pair(split, tag, label_path.stem, img_candidates[0], lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify counts only, write nothing")
    args = ap.parse_args()

    native_counts = Counter()
    for folder_name, (tag, class_map) in NATIVE_SOURCES.items():
        process_native(folder_name, tag, class_map, native_counts, write=False)

    print("native-source bucket totals:")
    for bucket, want in EXPECTED_NATIVE_TOTALS.items():
        got = native_counts[bucket]
        print(f"  {bucket:<16} {got:>6}  (expected {want})")
        assert got == want, f"{bucket}: got {got}, expected {want} -- a source or mapping drifted"

    marina2_counts = Counter()
    process_marina2(marina2_counts, write=False)
    print("\nMarina 2 clean-aerial bucket totals:")
    for bucket, want in EXPECTED_MARINA2_TOTALS.items():
        got = marina2_counts[bucket]
        print(f"  {bucket:<16} {got:>6}  (expected {want})")
        assert got == want, f"Marina2 {bucket}: got {got}, expected {want}"

    if args.check:
        print("\n--check: nothing written")
        return

    for split in ("train", "val", "test"):
        if (OUT / split).exists():
            shutil.rmtree(OUT / split)
        (OUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUT / split / "labels").mkdir(parents=True, exist_ok=True)

    # Re-run for real now that --check's dry totals are verified (write=True this
    # time actually links files; running twice keeps the script simple rather than
    # caching the first pass's per-source counts for reuse here).
    all_counts = Counter()
    for folder_name, tag in PRECONVERTED:
        process_preconverted(folder_name, tag, all_counts)
    for folder_name, (tag, class_map) in NATIVE_SOURCES.items():
        process_native(folder_name, tag, class_map, all_counts)
    process_marina2(all_counts)

    (OUT / "data.yaml").write_text(
        "# Generated by scripts/merge_dataset.py -- do not hand-edit, rerun instead.\n"
        "# Sources and licenses: see GUIDELINES.md's Dataset inventory.\n"
        "train: train/images\nval: val/images\ntest: test/images\n\n"
        f"nc: {len(CLASSES)}\nnames: {CLASSES}\n"
    )

    images_per_split = {
        s: len(list((OUT / s / "images").iterdir())) for s in ("train", "val", "test")
    }
    per_split = defaultdict(Counter)
    for split in ("train", "val", "test"):
        for label_path in (OUT / split / "labels").glob("*.txt"):
            for line in label_path.read_text().splitlines():
                per_split[split][CLASSES[int(line.split()[0])]] += 1

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

"""Compute a {(source_folder, stem): forced_split} override map correcting confirmed
train/val/test leakage in merge_dataset.py's inputs, and expose `resolve_split()` for
merge_dataset.py to call when assigning each image's output split.

Two distinct leak types found by scripts/check_split_leakage.py collapse into one union-find fix:

1. Within-source video-frame leakage: several Roboflow exports encode a continuous recording as
   sequential/timestamped filenames (`img_cameras_<timestamp>_<n>` for VESSELimg, `frame_<n>` for
   Yacht Detection, bare digit counters for Seaships7000/Warship/etc.) and were split PER FRAME
   rather than per recording, so consecutive frames land across all three splits.

2. Cross-source duplicate photos: several "different" Roboflow projects were built from the same
   underlying photos. Confirmed visually: `roboflow-MyBoats.v2i`'s frame `000141` and
   `roboflow-Seaships7000.v1i`'s frame `000141` are the same CCTV capture (`2017-01-04 10:02:47`
   burned into both). `roboflow-vessel.v1i`'s `709508` (train) is the same cruise-ship stock photo
   as `roboflow-Ship2.v1i`'s `709508` (test). Their filenames coincide because both scraped the
   same source pool, not because either one internally duplicates a frame.

Both boil down to "these images are the same underlying content, so they must land in the same
split." Adjacent-frame-number edges (within one source's own numbering) handle (1); exact-stem
edges across different sources handle (2). Union-find over both together gives the actual groups
of images that must move together; each group is then assigned whichever split already holds the
most of its members (ties broken train > val > test -- moving a duplicate INTO train never
inflates an eval metric, so that's the safe direction to err in on a tie).

Mechanism (1) is NOT applied blindly to every sequential-looking prefix check_split_leakage.py
flags -- it only fires for the allowlist in WITHIN_SOURCE_VIDEO_PREFIXES below, each entry
confirmed by opening actual images. Two flagged-but-unverified cases turned out to be false
positives when checked: `converted-vhrships-yolo`'s `PE_002`/`PE_003`/etc. are per-instance
catalog numbers for unrelated individual ships (one even carries a distinct `PE_003` placemark
label, Google-Earth-screenshot style), and `Sea Vessels Dataset.v2`'s `yacht_4`/`yacht_5`/etc. are
the same -- `yacht_4` is a 4-panel mosaic of unrelated yachts, `yacht_5` a single
FleetMon-watermarked megayacht photo, nothing in common. Forcing either into one split would have
merged unrelated ships for no reason. Everything not on the allowlist gets mechanism (2) only
(cross-source exact duplicates), which needs no such allowlist -- an exact full-filename match
between two independently-built Roboflow projects is strong evidence on its own (confirmed 2/2
checked: `MyBoats`/`Seaships7000`'s `000141`, `vessel.v1i`/`Ship2.v1i`'s `709508`).

Deliberately NOT touched: `roboflow-Marina 2.yolov11` (hand-triaged separately in a prior session,
see marina2_twist_triage.py and TODO.md's "Dataset split sanity check" entry -- its 21-frame leak
is accepted and documented rather than fixed, now that the sources here turned out far larger).

Run standalone to print what would move: uv run python scripts/split_overrides.py
"""

import re
from collections import defaultdict

RF_SUFFIX_RE = re.compile(r"^(.*)_(?:jpg|jpeg|png|bmp)\.rf\.[0-9a-f]{8,}$", re.I)
TRAILING_NUM_RE = re.compile(r"^(.*?)(\d+)$")
GAP = 10
SPLIT_RANK = {"train": 2, "val": 1, "test": 0}  # tie-break: prefer higher rank

# Sources/prefixes confirmed (by opening actual images, see module docstring) to be one
# continuous recording sliced per-frame -- only these get mechanism (1)'s adjacency treatment.
WITHIN_SOURCE_VIDEO_PREFIXES = {
    "roboflow-VESSELimg.v4i.yolov11": lambda p: p.startswith("img_cameras_"),
    "roboflow-Seaships7000.v1i.yolov11": lambda p: p == "",
    "roboflow-Yacht Detection.v2-alphayacht1.0.yolov11": lambda p: p == "frame_",
    # exclude its bare-numeric bucket: that's the shared stock-photo pool with vessel.v1i /
    # Ship2.v1i / Warship.v4i, mechanism (2)'s territory, not a video of its own
    "roboflow-kapal-penumpang-done.v1i.yolov11": lambda p: p != "",
    "roboflow-Buoys and Boats.v3i.yolov11": lambda p: p in ("buoy_b_2_", "youtube-"),
}


def original_stem(stem_with_rf_suffix):
    """Strip Roboflow's own `_<ext>.rf.<hash>` suffix from an extension-stripped stem, e.g.
    label_path.stem or Path(image_name).stem. A no-op for sources that never had one
    (VHRShips/KFGOD's own plain names)."""
    m = RF_SUFFIX_RE.match(stem_with_rf_suffix)
    return m.group(1) if m else stem_with_rf_suffix


def _split_prefix_number(stem):
    m = TRAILING_NUM_RE.match(stem)
    if not m:
        return stem, None
    prefix, digits = m.groups()
    return prefix, int(digits)


class _UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def _build():
    # imported lazily -- merge_dataset imports this module, so a top-level import here would
    # be circular
    import merge_dataset as merge

    sources = [name for name, _tag in merge.PRECONVERTED] + list(merge.NATIVE_SOURCES)
    node_split = {}  # (source, stem) -> its current split
    by_source_prefix = defaultdict(list)  # (source, prefix) -> [(number, stem)]
    by_stem_across_sources = defaultdict(set)  # stem -> {source, ...}

    for source in sources:
        for split, split_dir in merge.find_splits(merge.DATASETS / source).items():
            images_dir = split_dir / "images"
            if not images_dir.is_dir():
                continue
            for img_path in images_dir.iterdir():
                stem = original_stem(img_path.stem)
                node_split[(source, stem)] = split
                by_stem_across_sources[stem].add(source)
                prefix, number = _split_prefix_number(stem)
                if number is not None:
                    by_source_prefix[(source, prefix)].append((number, stem))

    uf = _UnionFind()
    for node in node_split:
        uf.find(node)

    for (source, prefix), entries in by_source_prefix.items():
        allow = WITHIN_SOURCE_VIDEO_PREFIXES.get(source)
        if allow is None or not allow(prefix):
            continue
        entries.sort()
        for (n1, stem1), (n2, stem2) in zip(entries, entries[1:]):
            if n2 - n1 <= GAP:
                uf.union((source, stem1), (source, stem2))

    for stem, sources_here in by_stem_across_sources.items():
        if len(sources_here) > 1:
            sources_here = sorted(sources_here)
            first = (sources_here[0], stem)
            for source in sources_here[1:]:
                uf.union(first, (source, stem))

    return node_split, uf


def compute_overrides():
    node_split, uf = _build()
    groups = defaultdict(list)
    for node in node_split:
        groups[uf.find(node)].append(node)

    overrides = {}
    for members in groups.values():
        if len({node_split[m] for m in members}) < 2:
            continue  # already all one split, nothing to fix
        counts = defaultdict(int)
        for m in members:
            counts[node_split[m]] += 1
        target = max(counts, key=lambda s: (counts[s], SPLIT_RANK[s]))
        for m in members:
            if node_split[m] != target:
                overrides[m] = target
    return overrides


_OVERRIDES = None


def resolve_split(source_folder, raw_stem, current_split):
    """raw_stem: label_path.stem / an image path's .stem -- extension already stripped, Roboflow
    rf-suffix still present. Returns current_split unchanged unless this image belongs to a
    confirmed cross-split leak group, in which case returns the group's forced split."""
    global _OVERRIDES
    if _OVERRIDES is None:
        _OVERRIDES = compute_overrides()
    return _OVERRIDES.get((source_folder, original_stem(raw_stem)), current_split)


if __name__ == "__main__":
    overrides = compute_overrides()
    by_source = defaultdict(list)
    for (source, stem), target in overrides.items():
        by_source[source].append((stem, target))

    total = 0
    for source, moves in sorted(by_source.items(), key=lambda kv: -len(kv[1])):
        print(f"{source}: {len(moves)} images reassigned")
        total += len(moves)
    print(f"\n{total} images total moved to close cross-split leaks across {len(by_source)} source(s)")

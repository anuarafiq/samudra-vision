"""Detect video-frame leakage across train/val/test splits for every source
`merge_dataset.py` pulls in (except `Marina 2`, already hand-triaged in a prior session -- see
TODO.md's "Dataset split sanity check" entry).

Roboflow gives every exported image a unique per-image hash suffix, so filenames never
literally collide across splits (already verified by merge_dataset.py's own run: "0 stems
shared across splits"). But many sources embed the *original* filename before that hash, and
that original name often records a video/camera identity: a timestamp, a camera tag, or a
sequential frame counter. Frames from the same recording landing in different splits is leakage
even though the exported filenames never collide.

Method: strip Roboflow's `_<ext>.rf.<hash>` suffix to recover the original stem, split each stem
into (prefix, trailing frame number), then within each (source, prefix) group sort by number and
flag adjacent entries that land in different splits within a small gap -- that's the signature of
one continuous recording sliced per-frame into more than one split. A large gap between same-prefix
numbers in different splits is far more likely coincidence (e.g. two unrelated stock photos that
happen to share a numeric ID range) than real frame adjacency, so it's not flagged.

This is a detector only, writes nothing. Flagged sources still need a manual look (open the
actual images) before deciding a fix -- same triage-then-verify order already used for Marina 2
and `wikimedia-rmn`. See scripts/merge_dataset.py's module docstring for why fixes, if any, must
stay scoped to the specific source found leaking rather than a global reshuffle.

Run: uv run python scripts/check_split_leakage.py [--gap N]
"""

import argparse
import re
from collections import defaultdict

import merge_dataset as merge

RF_SUFFIX_RE = re.compile(r"^(.*)_(?:jpg|jpeg|png|bmp)\.rf\.[0-9a-f]{8,}$", re.I)
TRAILING_NUM_RE = re.compile(r"^(.*?)(\d+)$")

SOURCES = [name for name, _tag in merge.PRECONVERTED] + list(merge.NATIVE_SOURCES)


def recover_stem(filename):
    stem = filename.rsplit(".", 1)[0]
    m = RF_SUFFIX_RE.match(stem)
    return m.group(1) if m else stem


def split_prefix_number(stem):
    m = TRAILING_NUM_RE.match(stem)
    if not m:
        return stem, None
    prefix, digits = m.groups()
    return prefix, int(digits)


def collect_entries(source_dir):
    """-> {prefix: [(number, split, stem), ...]}, number=None entries dropped (no adjacency signal)."""
    groups = defaultdict(list)
    for split, split_dir in merge.find_splits(source_dir).items():
        images_dir = split_dir / "images"
        if not images_dir.is_dir():
            continue
        for img_path in images_dir.iterdir():
            stem = recover_stem(img_path.name)
            prefix, number = split_prefix_number(stem)
            if number is not None:
                groups[prefix].append((number, split, stem))
    return groups


def find_leaks(groups, gap):
    """-> [(prefix, n1, split1, n2, split2), ...] for adjacent same-prefix entries within `gap`
    that fall in different splits."""
    leaks = []
    for prefix, entries in groups.items():
        entries.sort()
        for (n1, s1, _), (n2, s2, _) in zip(entries, entries[1:]):
            if s1 != s2 and n2 - n1 <= gap:
                leaks.append((prefix, n1, s1, n2, s2))
    return leaks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=int, default=10,
                     help="max numeric gap between same-prefix, cross-split frames to flag (default 10)")
    args = ap.parse_args()

    results = []
    for folder_name in SOURCES:
        groups = collect_entries(merge.DATASETS / folder_name)
        leaks = find_leaks(groups, args.gap)
        if not leaks:
            continue
        touched = {(p, n) for p, n, *_ in leaks} | {(p, n2) for p, _, _, n2, _ in leaks}
        results.append((folder_name, leaks, touched))

    results.sort(key=lambda r: -len(r[2]))

    if not results:
        print(f"no cross-split adjacency found within gap={args.gap} in any source")
        return

    for folder_name, leaks, touched in results:
        print(f"\n=== {folder_name} -- {len(touched)} frames touching a cross-split gap<={args.gap} ===")
        by_prefix = defaultdict(list)
        for p, n1, s1, n2, s2 in leaks:
            by_prefix[p].append((n1, s1, n2, s2))
        for prefix, pairs in sorted(by_prefix.items(), key=lambda kv: -len(kv[1]))[:5]:
            label = prefix if prefix else "(no prefix -- whole source shares one frame counter)"
            print(f"  {label}")
            for n1, s1, n2, s2 in pairs[:8]:
                print(f"    {n1:>8} [{s1:<5}] <-> {n2:>8} [{s2:<5}]  gap={n2 - n1}")
            if len(pairs) > 8:
                print(f"    ... and {len(pairs) - 8} more pairs under this prefix")
        if len(by_prefix) > 5:
            print(f"  ... and {len(by_prefix) - 5} more prefixes flagged in this source")

    print(f"\n{len(results)} source(s) flagged, ranked worst-first above. "
          "Confirm by opening actual images before deciding a fix -- this is a heuristic, not proof.")


if __name__ == "__main__":
    main()

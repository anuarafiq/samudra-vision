"""Per-image aerial/frontal/synthetic triage of Marina 2's `twist_*` filename family.

Marina 2 (datasets/roboflow-Marina 2.yolov11/) is a mixed-provenance aggregate: its labels come
from several unrelated source groups bundled under one data.yaml, see the finding in
GUIDELINES.md ("roboflow-Marina 2 is a mixed-provenance aggregate"). Every group except `twist_*`
was resolved outright (numeric family = frontal CCTV, DJI_/Screenshot/IPgiBNOPCjQ = clean aerial).
`twist_*` needed per-image human judgement: all 38 images were opened and classified 2026-07-30.

This isn't a conversion script (Marina 2 isn't merged into the unified taxonomy yet, so there's
nothing to write) -- it's the durable record of that judgement call, since datasets/ is gitignored
and would otherwise lose it. When the unified merge script gets written, import DROP_PREFIXES from
here to exclude the bad `twist_*` images instead of re-triaging.

Run: uv run python scripts/marina2_twist_triage.py   -- recomputes and prints the verified counts.
"""

import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "datasets" / "roboflow-Marina 2.yolov11"
CLASS_NAMES = {"0": "cargo", "1": "fishing_boat", "2": "military", "3": "passenger", "4": "speedboat", "5": "swimmer"}

# Filename prefix -> reason dropped. Everything else under twist_* is genuine aerial content
# (drone/aircraft shots: carrier strike groups, container terminals from above, top-down small
# craft) and should be counted as aerial. These six are not, despite the `military`/`cargo`/
# `speedboat` label on the box.
DROP_PREFIXES = {
    "twist_23_": "sea-level horizon shot (large sky, ships in silhouette) -- not aerial",
    "twist_28_": "CGI render of a frigate, not a photograph",
    "twist_58_": "Venice canal shot from a building balcony -- elevated shore, not aerial",
    "twist_67_": 'riverbank phone photo, watermarked "SHOT ON OPPO" -- elevated shore, not aerial',
    "twist_238_": "hillside scenic overlook, foliage in foreground -- elevated shore, not aerial",
    "twist_33_": "sea-level horizon shot, likely from another vessel -- not aerial",
}

# Verified 2026-07-30 by running this script against the downloaded dataset. If these stop
# matching, either the dataset changed or DROP_PREFIXES did -- investigate before trusting output.
EXPECTED_IMAGE_COUNT = 38
EXPECTED_KEPT = {"speedboat": 3, "military": 92, "cargo": 4, "fishing_boat": 1}
EXPECTED_DROPPED = {"military": 7, "speedboat": 12, "cargo": 1}


def main():
    label_files = sorted((SRC).glob("*/labels/twist_*.txt"))
    kept, dropped = Counter(), Counter()
    for f in label_files:
        prefix = re.match(r"(twist_\d+_)", f.name).group(1)
        bucket = dropped if prefix in DROP_PREFIXES else kept
        for line in f.read_text().splitlines():
            if line.strip():
                bucket[CLASS_NAMES[line.split()[0]]] += 1

    print(f"{len(label_files)} twist_ images, {len(DROP_PREFIXES)} dropped, "
          f"{len(label_files) - len(DROP_PREFIXES)} kept as aerial")
    print("kept (aerial):   ", dict(kept))
    print("dropped (not aerial):", dict(dropped))

    assert len(label_files) == EXPECTED_IMAGE_COUNT, len(label_files)
    assert dict(kept) == EXPECTED_KEPT, dict(kept)
    assert dict(dropped) == EXPECTED_DROPPED, dict(dropped)
    print("\nmatches verified counts")


if __name__ == "__main__":
    main()

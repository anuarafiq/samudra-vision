# Samudra Vision

Maritime vessel detection/classification for SEDIC 2026 Visual Track, Phase 1. Read
[GUIDELINES.md](GUIDELINES.md) first, it has the full competition brief, mandatory class
taxonomy, dataset inventory with per-class instance counts, and known open problems (local vs.
foreign military, validation strategy). Read [TODO.md](TODO.md) for the task board and who owns
what across the 4 team roles.

## Stack

- Python 3.13, managed with `uv` (`uv sync`, `uv add`, `uv run`), not pip/poetry/conda directly
- `ultralytics` (YOLOv11), matches the format every sourced dataset is already in
- `opencv-python`, for video clip inference

## Working with `datasets/`

- Gitignored, lives on disk only, don't try to commit anything under it
- **Flat layout, one folder per dataset** (restructured 2026-07-30, was previously split into
  `frontal-view/` + `aerial-view/` — that split was dropped because it couldn't express
  mixed-provenance sources like `Marina 2`, and because camera angle is a per-class property
  already tracked authoritatively in [GUIDELINES.md](GUIDELINES.md#dataset-inventory)'s `View`
  column, not a property of a whole folder)
- Two kinds of folder, distinguished by name prefix:
  - `converted-*` — **generated** by a script in `scripts/`. Safe to delete and regenerate, never
    hand-edit. Written in the canonical class order (see below). Images inside are **absolute
    symlinks** into the source folder, so moving or renaming a source breaks them — re-run that
    source's conversion script afterwards rather than repairing links by hand.
  - everything else (`roboflow-*`, `kaggle-*`, `huggingface-*`, `smd-*`, `inesctec-*`) — raw
    source material as downloaded, prefixed by where it came from. Expensive to re-acquire, don't
    hand-edit, don't rename (the conversion scripts hardcode these paths)
- **Canonical class order, fixed, match it rather than inventing a new one**: `container_ship,
  tanker, cargo, passenger_ferry, yacht, speedboat, fishing_boat, military`. Both existing
  `converted-*` datasets already use it.
- Before assuming a dataset's class list, image count, or license, check
  [GUIDELINES.md](GUIDELINES.md#dataset-inventory), several sources here turned out mislabeled,
  broken, or duplicates of ones already present, re-verify rather than trust a folder name
- **A Roboflow project's live overview page (class list, download count) does not necessarily
  match what's in the frozen downloadable version.** Hit repeatedly (`korean_marine_object`,
  `ships9000`, `kapal-penumpang-done`, `SentinelBlue`): the page shows N classes, the actual
  `data.yaml`/labels in the export are single-class or otherwise different. Always check the
  downloaded `data.yaml` and label files directly, never trust the Roboflow page alone. The other
  recurring traps are consolidated in
  [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan) — read that before sourcing
  anything new, along with its ruled-out list so already-dead datasets don't get re-checked
- The unified merged dataset now exists: `datasets/merged-yolo/` (generated 2026-07-30 by
  [scripts/merge_dataset.py](scripts/merge_dataset.py), `nc: 8`, 34,863 images / 57,398 boxes,
  symlink-based so not portable — see [TRAINING.md](TRAINING.md) for the transfer + train flow)
- Large binaries (weights, videos, `runs/`) stay gitignored, never committed

## Repo layout

No `src/` layout or model configs yet. Training is not run in this repo — it's handed to a
teammate on CUDA hardware; [TRAINING.md](TRAINING.md) is the handoff and
[scripts/colab_baseline.py](scripts/colab_baseline.py) is the runnable baseline (Colab cells +
CLI). `scripts/` holds the dataset conversion/merge/triage tooling; each script's docstring says
what it does and when to re-run it. Propose a proper structure when training moves in-repo.

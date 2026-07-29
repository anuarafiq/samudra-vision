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
- Existing per-source folders (`frontal-view/roboflow-*`, `aerial-view/*`, `smd-*`) are source
  material, don't restructure or rename them; add merged/processed/converted data under a new
  top-level dir instead
- Before assuming a dataset's class list, image count, or license, check
  [GUIDELINES.md](GUIDELINES.md#dataset-inventory), several sources here turned out mislabeled,
  broken, or duplicates of ones already present, re-verify rather than trust a folder name
- **A Roboflow project's live overview page (class list, download count) does not necessarily
  match what's in the frozen downloadable version.** Hit three times so far
  (`korean_marine_object`, `ships9000`, `kapal-penumpang-done`): the page shows N classes, the
  actual `data.yaml`/labels in the export are single-class or otherwise different. Always check
  the downloaded `data.yaml` and label files directly, never trust the Roboflow page alone
- No unified merged dataset or class-remapping script exists yet, that's an open TODO item, not
  something already decided
- Large binaries (weights, videos, `runs/`) stay gitignored, never committed

## Repo layout

No `src/` layout, training code, or model configs exist yet. Don't assume a structure is already
decided, propose one when the first training script actually gets written.

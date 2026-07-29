# Project Guidelines: Samudra Vision (SEDIC 2026 Visual Track)

Source of truth: [references/SEDIC2026-track2.pdf](references/SEDIC2026-track2.pdf). This file
distills it plus tracks project-specific decisions, so it can be read instead of the PDF.

## Mission

"Project Guardian": Advanced Maritime Domain Awareness (MDA). Build an object detection
model for multi-angle vessel classification: **frontal-view** and **aerial/satellite-view**.

## Mandatory class taxonomy

| Group | Classes |
|---|---|
| Civilian | Container Ship, Tanker, Cargo, Passenger Ferry |
| Small Craft | Yacht, Speedboat, Fishing Boat |
| Military (mandatory) | Military vessel (generic) |
| Military, competitive advantage | Local (Malaysian) vs. Foreign military |

Recall > 90% is required specifically on **military and threat-based classes**.

None of the sourced datasets already label Malaysian-vs-foreign military. That distinction
has to come from a downstream step (e.g. hull markings/flag/pennant number recognition, or a
second-stage classifier on crops), not from the base detector's class list. Treat this as an
open problem, not solved by relabeling existing data.

## Phase 1 submission package (online, all mandatory for Top 10)

- Model source code (standard open-source libraries)
- Detection log & results run on the provided "Qualifier Video Clip"
- Recall > 90% on military/threat classes
- Technical Brief PDF: dataset used, model architecture, military-classification logic
- Video demo, max 5 min, via YouTube

## Phase 2 (Top 10 only, "The Wireless Village")

- Display poster of the AI pipeline/data/accuracy
- Live demo station running the model in real time
- GUI is optional but a scored competitive advantage
- Jury presentation + live stress test on hidden verification images/video on the spot
  -> the pipeline needs to run standalone at a booth with no internet dependency assumed.

## Dataset inventory

`datasets/` is gitignored (19GB+), lives on disk only. Not all classes below map cleanly to
the mandatory taxonomy; a class-remapping step is needed before merging for training.

**Frontal-view** (`datasets/frontal-view/`)
- `roboflow-Warship.v4i.yolov11` - 1 class: warship
- `roboflow-vessel.v1i.yolov11` - 5 classes: Cargo, Carrier, Cruise, Tanker, Warship
- `roboflow-Military Ship Detection.v2i.yolov11` - 1 class: ship
- `roboflow-Seaships7000.v1i.yolov11` - 6 classes: bulk cargo carrier, container ship, fishing boat, general cargo ship, ore carrier, passenger ship
- `roboflow-ship detection.v2i.yolov11` - 11 classes: canoe, cargo ship, container ship, engineering ship, fishing boat, kayak, passenger ship, sailboat, speedboat, tanker, warship
- `singapore-maritime` - raw VIS/NIR captures (onshore + onboard), not pre-labeled YOLO

**Aerial/satellite-view** (`datasets/aerial-view/`)
- `roboflow-MASATI.v1i.yolov11` - 6 classes: coast_multi, multi, multi_224, ok, ship, water
- `roboflow-maritime.v3i.yolov11` - 4 classes: Boat, Person drowning, Person in water, Person out of water (SAR-flavored, not vessel-type)
- `kaggle-MASATI-V2` - raw MASATI source (1 class: ship)
- `kaggle-SeaDronesSee` - drone imagery, separate `images/`/`annotations/`
- `kaggle-satellite` - `shipsnet` classification chips + scenes, not detection-format

Every YOLO-format folder has its own `data.yaml` (train/val/test paths, `nc`, `names`) plus
Roboflow's `README.roboflow.txt` / `README.dataset.txt` with license + source URL.

## Stack

- Python 3.13, managed with `uv` (`uv sync`, `uv add`, `uv run`)
- `ultralytics` (YOLOv11) - matches the format all Roboflow exports are already in
- `opencv-python` - video clip inference for the Qualifier/Live Stress Test deliverables

## Repo conventions

- No training code, configs, or model folders exist yet, don't assume a `src/` layout is
  already decided, propose one when the first training script is actually written.
- `datasets/` and `references/*.pdf` are source material, don't restructure them; add new
  processed/merged data under a new top-level dir instead of mutating these in place.
- Large binaries (weights, videos, `runs/`) stay gitignored, never committed.

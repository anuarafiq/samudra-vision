# TODO: Samudra Vision (SEDIC 2026 Visual Track)

Task board for the 4-person team. Background/context lives in [GUIDELINES.md](GUIDELINES.md),
this file is just the task list. Check items off as they land.

## Military classification approach (reference)

Decision from planning: how to tell **Malaysian vs. foreign military** vessels apart (the
competitive-advantage bonus, see [GUIDELINES.md](GUIDELINES.md#mandatory-class-taxonomy)).

**Ship-class silhouette recognition (recommended approach).** The Royal Malaysian Navy's combat
fleet is small and well-documented, roughly 15 hull types: Kedah-class OPVs, Lekiu-class
frigates, Kasturi-class corvettes, the new Maharaja Lela-class LCS, Handalan/Perdana-class fast
attack craft. Each has a distinct superstructure shape. Collect reference photos per class
(Wikipedia Commons and Malaysian MinDef press photos have these publicly), label them "local",
pool a broad set of foreign navy vessels as "foreign", then train a second-stage classifier
that runs only on the crops the primary detector already tags as "military". This works whether
or not text or flags are legible, and it's genuinely how naval analysts do ID in practice.

Tradeoff: needs a roughly broadside/frontal view to read the silhouette, gets harder from
directly overhead (aerial view) or at a steep angle. Optional add-on: hull number/pennant OCR
as a confidence booster when text happens to be legible, not a replacement for the silhouette
classifier.

This spans two roles: **Member A** sources/labels the reference photos, **Member B** trains the
second-stage classifier on the crops.

**Possible starting point for "local" reference images**: [SKN601DEMO](https://universe.roboflow.com/apokhalidz82-eirqe/skn601demo-ohslz)
(1,906 images) and its smaller sibling SKN601UAV (280 images), both CC BY 4.0, drone/UAV-view.
Found while searching for tanker data, unrelated to that task but worth keeping. Their class
lists use maritime-enforcement vocabulary specific to Malaysia (`FCB90` = the Malaysian Maritime
Enforcement Agency's Fast Combat Boat class, `MPCSS` = a specific RMN support ship class,
`Sampan`, `Coast Guard - Police`), which aren't used anywhere outside Malaysia. Any
`Warship`/`Patrol Vessel` image in this set is very likely a genuine Malaysian asset, not
independently confirmed, but a plausible source of pre-labeled "local" reference photos instead
of hand-collecting them from scratch.

## Validation strategy (reference)

Decision from planning: the Recall > 90% requirement is graded against the organizer's
**Qualifier Video Clip**, not against Roboflow's held-out val/test splits, those are a different
population (different camera, distance, compression, angle) and doing well on one says nothing
about the other. The clip isn't released yet (checked [references/](references/), only the
track brief PDF is there), so don't wait idle:

1. **Build the frame-extraction + labeling tooling now**, not after the clip drops. A small
   script (`ffmpeg`/`opencv` frame sampling + a labeling pass) ready to run the moment it's
   released means zero lost time, and the same tool gets reused for Phase 2's live "Hidden
   Verification" stress test.
2. **Build a temporary proxy validation set in the meantime.** Pull a handful of real-world
   maritime videos that plausibly resemble what a qualifier clip could be, harbor/coastal CCTV
   footage, drone shots, ship-spotting YouTube channels, covering both frontal and aerial views
   since both are mandatory. Hand-label a small slice of frames from those. Won't match the real
   clip exactly, but it surfaces domain-shift problems (compression artifacts, camera angle,
   distance-to-target) months earlier than waiting and finding out cold.
3. **Treat Roboflow's val/test splits as a floor, not the number to report.** Keep tracking them
   for iteration speed, don't let "95% recall on Roboflow's split" stand in for the real
   benchmark internally.
4. **When the real clip lands, immediately re-run** the same extraction + labeling process on it
   and re-check recall before locking the submission.

This is primarily **Member A** (extraction tooling, proxy set, labeling) with **Member C**
consuming the tool to run official inference once the real clip lands.

---

## Member A: Data Lead & Dataset Engineering

- [ ] Consider pulling in **[Sailboat detector](https://universe.roboflow.com/learning-299jh/sailboat-detector)**
      (by Learning, 8,888 images, CC BY 4.0, likely a fork of the academic ABOships dataset).
      11 clean classes: `boat, sailboat, ferry, cargoship, cruiseship, militaryship, miscboat,
      miscellaneous, motorboat, passengership, seamark`. No `yacht` class (not why it was found),
      but would meaningfully boost the military/cargo/passenger_ferry buckets if needed later
- [x] ~~Fix `roboflow-korean_marine_object.v1i.yolov11` class export~~, confirmed via COCO
      re-export it's single-class by design (not a bug), see
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan). Use only as generic
      vessel-localization data, not a source of type labels
- [x] ~~Source more `tanker` data, the last mandatory class below the ~800-1000 floor~~ solved
      2026-07-29 after six sourcing attempts: `roboflow-Tanker.v1i`, `roboflow-VESSELimg.v4i`,
      `roboflow-Vessel.v2i` downloaded and folded in, +1924 instances (475 -> 2399). Every
      mandatory class now clears the floor. Full record (dead-end Roboflow slugs, per-dataset
      breakdown, untried leads) in
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan).
- [ ] Build the class-remapping table/script: map every raw dataset's classes into the
      mandatory taxonomy (`container_ship`, `tanker`, `cargo`, `passenger_ferry`, `yacht`,
      `speedboat`, `fishing_boat`, `military`)
- [ ] Decide handling for ambiguous/unmapped classes: `Carrier`, `ore carrier`, `Merchant Ship`,
      `Patrol Boat`, `Sails Boat`, `Tugboat`, `canoe`, `kayak`, `sailboat`, `engineering ship`,
      `Datasense@CRAS`'s `small boat`/`uncategorized` (drop, bucket into small-craft, or
      hand-review each)
- [ ] Decide what to do with generic/unusable sources: `kaggle-satellite` (classification-only,
      no boxes), `kaggle-MASATI-V2` (non-commercial license only), the SAR-oriented aerial sets
      (`roboflow-maritime.v3i`, `kaggle-SeaDronesSee`, people/jetski/buoy labels, not ship types)
- [ ] Write the frame-extraction + `.mat`-to-YOLO conversion script for Singapore Maritime
      Dataset (`smd-VIS_Onboard`, `smd-VIS_Onshore`, `smd-NIR`), currently raw video + MATLAB
      ground truth, unusable as-is
- [ ] Merge all remapped/converted sources into one unified YOLO dataset (single `data.yaml`,
      consistent train/val/test folders)
- [ ] Dataset split sanity check: make sure frames extracted from the same source video don't
      end up split across train and val (data leakage)
- [x] ~~Augmentation/oversampling pass for the thin classes (`tanker`, `yacht`)~~ no longer
      needed, both solved by sourcing dedicated datasets instead, every mandatory class now
      clears the ~800-1000 floor, see
      [GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-updated-2026-07-29-after-yacht-sourcing)
- [ ] Source and label reference photos for the local-vs-foreign military classifier (see
      "Military classification approach" above): RMN ship classes tagged "local", a broad
      foreign-navy set tagged "foreign". Check whether SKN601DEMO (above) is usable as a
      starting point before hand-collecting everything from scratch
- [ ] Build the frame-extraction + labeling tool (see "Validation strategy" above) before the
      Qualifier Video Clip is even released, so it's ready to run the moment it drops
- [ ] Source a handful of real-world proxy videos (harbor/coastal CCTV, drone footage,
      ship-spotting channels, both frontal and aerial) and hand-label a slice as a temporary
      validation set to catch domain-shift issues early
- [ ] Once the Qualifier Video Clip is released: extract representative frames from it and
      hand-label a validation slice in the mandatory taxonomy (this is the real recall
      benchmark, not the Roboflow splits, see
      [GUIDELINES.md](GUIDELINES.md#phase-1-submission-package-online-all-mandatory-for-top-10))
- [ ] Keep [GUIDELINES.md](GUIDELINES.md) dataset inventory updated as sources change
- [ ] Collect license/attribution info per dataset for the Technical Brief (feed to Member D)

## Member B: Model Lead & Training Pipeline

- [ ] Confirm base model: YOLOv11 (already matches every sourced dataset's export format,
      installed via `ultralytics`), decide single unified model vs. separate frontal-view /
      aerial-view models
- [ ] Set up training environment parity between Colab and local RTX 4050 (CUDA version,
      `ultralytics` version pinned in `pyproject.toml`)
- [ ] Baseline training run on Member A's merged dataset, sanity-check per-class metrics
- [ ] Hyperparameter tuning: image size, batch size, LR schedule, epoch count, augmentation
      config (mosaic, flip, rotation, brightness/weather jitter for maritime haze/glare)
- [ ] Class-imbalance handling in training config: class weights or oversampling for
      `tanker`/`yacht`
- [ ] Recall-specific tuning for military/threat classes: confidence threshold tuned for
      recall over precision on the `military` class specifically, hard-negative mining to cut
      false negatives, since Phase 1 requires Recall > 90% on this class
- [ ] Train the second-stage local-vs-foreign classifier on Member A's cropped reference photos
      (small CNN or fine-tuned classifier head on the military-class crops)
- [ ] Evaluate per-class precision/recall/mAP on held-out data, iterate until military recall
      clears 90%
- [ ] Benchmark inference speed (needed for the Phase 2 real-time live demo requirement),
      export to ONNX/TensorRT if the live booth machine needs the speedup
- [ ] Keep a lightweight run log (config + metrics per experiment, plain markdown/CSV is
      enough, no need for a full experiment-tracking platform)
- [ ] Once the Qualifier Video Clip is available: threshold-tune specifically against it to
      confirm the 90% recall requirement is actually met on real footage, not just on val split

## Member C: GUI Developer & Test Runner

- [ ] Pick GUI framework (Streamlit or PyQt), weigh against Phase 2's "no internet dependency"
      requirement, both can run fully local/offline, pick based on team's UI comfort and
      whether a browser-based or native-window demo suits the booth better
- [ ] Build video ingestion: file/clip upload (for the Qualifier Video Clip) + live camera feed
      (for the Phase 2 real-time demo)
- [ ] Render bounding boxes, class labels, and confidence scores overlaid on video frames
- [ ] Build a live stats panel: running counts per class, a distinct highlighted alert for
      military detections (the scored differentiator) and local-vs-foreign tags once Member B's
      second-stage classifier is ready
- [ ] Generate the structured detection log (CSV/JSON: timestamp, class, bbox, confidence per
      frame), this is a mandatory Phase 1 deliverable
- [ ] Track recall on Member A's temporary proxy validation set as the working number, don't
      treat Roboflow's split recall as the real benchmark (see "Validation strategy" above)
- [ ] Run the finished model against the actual Qualifier Video Clip once released, produce the
      official detection log + results file for submission, re-check recall against it before
      locking the submission
- [ ] Stress-test the GUI: corrupted frames, resolution changes, long-running video, make sure
      nothing crashes mid-demo in front of the jury
- [ ] Package a standalone run path for the booth (no internet dependency): PyInstaller build or
      a documented one-command `uv run` script, tested on the actual demo machine beforehand
- [ ] Rehearse the Phase 2 live demo flow end-to-end at least once on the target hardware

## Member D: Video Producer & Technical Report Author

- [ ] Draft the Technical Brief PDF: datasets used (pull from
      [GUIDELINES.md](GUIDELINES.md#dataset-inventory)), model architecture (from Member B),
      military-classification logic (the silhouette approach above), final metrics/results
- [ ] Architecture diagrams: full pipeline (input -> detector -> military crop -> local/foreign
      classifier -> output), and the class taxonomy diagram
- [ ] Licensing/citations section for every dataset used (CC BY 4.0 attributions, SeaShips,
      Singapore Maritime Dataset, MASATI, etc.), pull the list Member A collected
- [ ] Write the 5-minute video script: problem statement, pipeline walkthrough, live detection
      demo (civilian, small craft, generic military, local-vs-foreign highlight), results
- [ ] Record screen capture of the GUI running on the Qualifier Video Clip, plus any live camera
      footage needed
- [ ] Record and edit voiceover/narration
- [ ] Edit final cut to under 5 minutes, add captions/branding
- [ ] Publish to YouTube per submission rules, confirm the link is accessible
- [ ] Design the Phase 2 poster (pipeline diagram, dataset stats, accuracy numbers)
- [ ] Prep jury presentation talking points and likely Q&A for the live stress test defense
- [ ] Final Phase 1 submission checklist: source code repo link, detection log, Technical Brief
      PDF, video link, all present before the deadline

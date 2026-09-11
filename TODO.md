# TODO: Samudra Vision (SEDIC 2026 Visual Track)

Task board for the 4-person team. Background/context lives in [GUIDELINES.md](GUIDELINES.md),
this file is just the task list. Check items off as they land.

## RESOLVED: merge all sources into one unified YOLO dataset (closed 2026-07-30)

`datasets/merged-yolo/` exists and is verified. **Member B's baseline training run is unblocked**:
point it at `datasets/merged-yolo/data.yaml`, `nc: 8`, canonical order `container_ship, tanker,
cargo, passenger_ferry, yacht, speedboat, fishing_boat, military`.

Built by [scripts/merge_dataset.py](scripts/merge_dataset.py) from 2 pre-converted sources
(pass-through) + 16 native Roboflow sources (per-source class remap) + `Marina 2`'s clean-aerial
subset. No source's own train/val/test split was reshuffled. Rerunnable and safe to delete.

**Note (2026-09-11): the per-split counts below are the original 2026-07-30 numbers, now
superseded.** The Member A "Dataset split sanity check" item further down found real cross-split
leakage in several sources and `merge_dataset.py` now corrects it via
[scripts/split_overrides.py](scripts/split_overrides.py) — "no source's own split was reshuffled"
above is no longer quite true, see that entry for what changed and why. Class totals (this table's
`total` column) are unaffected; only the train/val/test columns shifted. Current numbers: train
31,211 img / 50,472 inst, val 2,247 img / 3,924 inst, test 1,405 img / 3,002 inst.

**Final counts — all 8 buckets matched their predicted totals exactly, no drift (2026-07-30,
split columns since corrected, see note above):**

| bucket | train | val | test | total |
|---|---|---|---|---|
| container_ship | 6175 | 1274 | 945 | 8,394 |
| tanker | 3315 | 449 | 234 | 3,998 |
| cargo | 8998 | 640 | 1607 | 11,245 |
| passenger_ferry | 7358 | 1403 | 839 | 9,600 |
| yacht | 3573 | 560 | 515 | 4,648 |
| speedboat | 3259 | 713 | 721 | 4,693 |
| fishing_boat | 6995 | 505 | 797 | 8,297 |
| military | 5645 | 524 | 355 | 6,524 |
| **ALL** | **45318** | **6068** | **6013** | **57,399** |

Images: train 27,428 / val 3,802 / test 3,633 (34,863 total).

**Verified, in this order:** `--check` assertions passed on all 12 expected subtotals → real run
matched the table above → 0 broken symlinks → image/label pairing exactly 1:1 in all three splits
→ all 34,863 symlinks resolve to real files (absolute, no chains through the `converted-*`
intermediates) → **0 stems shared across splits, so no filename-collision leakage** → `ultralytics`
scanned all three splits with **0 corrupt, 0 backgrounds** → crops opened per class across every
contributing source, and the remapping looked right in each.

**Bug found and fixed during this task:** `--check` was not actually dry. `link_pair()` wrote
label files unconditionally, and it ran *before* the output directories were created (the `mkdir`
sat after `--check`'s early return), so the very first `--check` invocation crashed with
`FileNotFoundError` instead of verifying anything. `link_pair`/`process_native`/`process_marina2`
now take `write=False` for the counting pass. Counting was already independent of the writes, so
the totals the assertions check are unaffected.

**Two data-quality notes this merge surfaced but deliberately did not act on** (both are "what's
in the sources", not "how they were combined"):

- `roboflow-Boats Detection.v15i.yolov11` (cargo 504, speedboat 348, yacht 276 — 1,128 instances,
  ~2% of the dataset) has Roboflow **preprocessing baked into the export**: `Grayscale (CRT
  phosphor)` + resize-to-416 stretch, plus 3 flip-augmented copies per source image. Its crops are
  grayscale and visibly unlike every other source, and its 1,128 images come from only **194
  unique source images**. It contributes to `train` only, so this is not a leakage risk — but it
  is a domain-mismatch and redundancy question worth a decision before the final training run
  (ultralytics does flip augmentation itself anyway).
- 15 images of 34,863 carry exact-duplicate boxes (pre-existing artifacts in `vhrships`,
  `seavessels`, `vesselv1`). `ultralytics` silently dedupes these at load; no action needed.

**One thing this task did not touch, don't assume it's covered**: `speedboat`'s quality caveat
(1,200 of 1,266 aerial instances are a capped subsample of KFGOD's `motorboat`, not a confirmed
1:1 recreational-speedboat mapping — see the RESOLVED section below) carries through into the
merged dataset unchanged. This task was about correctly *combining* already-decided sources, not
re-litigating what's in them.


## RESOLVED: aerial-view data sourcing (closed 2026-07-30)

A 2026-07-29 recount split every mandatory class's instance count by frontal vs. aerial view
instead of pooling them, and found **5 of 8 classes had essentially zero aerial-view instances**.
That gap is now closed: **all 8 classes clear the ~800-1000 aerial-instance floor.** Full per-class
numbers live in
[GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split).

What closed it, in order of contribution:

| Source | Aerial instances | Script |
|---|---|---|
| `KFGOD` (KOMPSAT satellite, KARI) | 9,392 | [scripts/kfgod_to_yolo.py](scripts/kfgod_to_yolo.py) |
| `VHRShips` (Google Earth) | 7,440 | [scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py) |
| `VESSELimg.v4i` (Valencia Port drone) | 7,545 | already YOLO, no conversion needed |
| `Marina 2` (triaged aerial subset) | 132 | [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py) |
| `kapal.v1i` (Google Earth + FPV drone) | 139 | already YOLO, no conversion needed |

**Two caveats carried forward, both flagged for whoever writes the Technical Brief:**

1. **`speedboat`'s aerial coverage rests on a judgment call.** 1,200 of its 1,266 aerial instances
   are a *capped random subsample* of KFGOD's `motorboat` class (34,574 raw), not a clean 1:1
   mapping — `motorboat` at 0.55-0.7m resolution is a catch-all for small motor-powered craft, not
   confirmed recreational-speedboat-specific. Capped deliberately so one KOMPSAT-only class
   wouldn't dwarf every other aerial class. If aerial `speedboat` behaves oddly once training
   starts, revisit the mapping before assuming it's a model problem. Reasoning is in
   `scripts/kfgod_to_yolo.py`'s module docstring.
2. **Three sources have license tags that don't survive scrutiny**: `kapal.v1i` ("Public Domain"
   but contains Google Earth screenshots), `Marina 2` ("CC BY 4.0" but contains watermarked forum
   scrapes, YouTube frames and a CGI render), and `KFGOD` (genuinely CC BY-SA 4.0 from the rights
   holder, but share-alike, so derivatives inherit the terms). Don't cite any of the three
   unqualified. Details in
   [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan).

**Don't re-search this.** Nine sourcing passes across Roboflow Universe, HuggingFace, Kaggle,
Zenodo, arXiv and a curated GitHub directory of ~25 satellite-ship datasets are consolidated into
the ruled-out list in [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan) — grouped by
failure mode (non-commercial license at source, single generic class, SAR/rescue, frontal-on-
inspection, redundant re-export), along with the standing traps that caused most of the wasted
effort and the handful of still-open leads. Check that list before opening any new candidate.

**The structural finding worth keeping**: large commercial and military vessels are well
represented in aerial/satellite ship-type datasets; small recreational and fishing craft are
mostly not, because a few pixels at satellite resolution rarely justifies dedicated labeling. The
sources that actually worked (`VESSELimg.v4i`, `VHRShips`, `KFGOD`, `kapal.v1i`) were all
purpose-built for vessel-*type* labeling. Generic "is there a ship" aerial datasets contributed
nothing across all nine passes, without exception — filter for purpose-built type labeling up
front rather than opening every promising-sounding result.

## Military classification approach (reference)

Decision from planning: how to tell **Malaysian vs. foreign military** vessels apart (the
competitive-advantage bonus, see [GUIDELINES.md](GUIDELINES.md#mandatory-class-taxonomy)).

> **PARKED 2026-07-30.** Not abandoned, deprioritised. The trainable "local" set bottoms out
> at **~40-45 images** against ~5,975 foreign (see the triage result below), which is too thin
> for a dependable second stage, and the approach also needs broadside views while much of our
> `military` data is aerial. This stage is a **scored bonus, not a Phase 1 gate** — the gate is
> >90% military recall, which rides entirely on the primary detector. Everything below stays
> accurate and the data stays on disk; resume by widening sources (MinDef press photos) rather
> than by reprocessing the existing 220. Revisit once the baseline's military recall is known.

**DECIDED 2026-07-30: binary local-vs-foreign, not per-hull-class.** A second-stage classifier
runs only on crops the primary detector already tagged `military`, and outputs two labels.
The earlier plan was per-hull-class silhouette ID (~15 RMN types, each learned separately);
that was dropped once the data was actually counted — Wikimedia Commons holds only ~230 RMN
photos total, and five of the ten hull-class categories have **under 10 images each**
(`gagah_training` has 1, `keris_lms` has 4). Per-class is not trainable at that volume.
Binary also matches what the competition actually asks for; per-class ID was our
implementation choice, never a requirement.

The two halves are asymmetric in a way that works in our favour:

- **"local"** — `datasets/wikimedia-rmn/`, 220 images, collected 2026-07-30 by
  [scripts/wikimedia_rmn.py](scripts/wikimedia_rmn.py). Kept in per-hull-class folders even
  though training pools them, so the split can be revisited if the set ever grows.
- **"foreign"** — **needs no sourcing.** The merged dataset already carries 6,524 `military`
  boxes (5,975 of them >1% of frame area, so croppable) from `warshipv4`, `seavessels`,
  `vhrships`, `shipdetectionv2`, `kfgod`, `vesselv1`/`v2`, `ship2`, `typesofships`. Those are
  overwhelmingly foreign navies. Crop them from `merged-yolo` rather than downloading anything.

Two open problems on this, both now solved 2026-09-11:

1. **Class imbalance ~1:157** (38 confirmed local vs 5,975 croppable foreign, worse than the
   ~1:27 the pre-triage 220-image guess implied). **Solved**: subsample foreign to 5:1 against
   the actual `rmn` count rather than training on the raw ratio — 190 foreign crops sampled,
   fixed seed for reproducibility.
2. **Possible Malaysian contamination in the "foreign" pool.** `kapal` (18 military boxes) is
   Indonesian/Malaysian-sourced and `marina2` (92) is mixed-provenance. **Solved**: both
   excluded by their `tag__` filename prefix before cropping or sampling.

Done by [scripts/wikimedia_rmn_crop_foreign.py](scripts/wikimedia_rmn_crop_foreign.py) ->
`datasets/military-foreign-crops/{all,sampled,manifest.csv}` (5,783 eligible crops as of
2026-09-11's split-leakage fix moving images into `train`, was 5,557 before; still 190 sampled,
12% padding around each YOLO box — regenerate by re-running the script if `merged-yolo` changes
again). Ready for Member B: foreign =
`datasets/military-foreign-crops/sampled/`, local = the 38 `rmn`-verdict rows in
`datasets/wikimedia-rmn/triage.csv`.

Tradeoff that survives the change: this still needs a roughly broadside view, and gets harder
from directly overhead. A large share of our `military` instances are aerial (`vhrships` 616,
`kfgod` 386, `marina2` 92), so if the Qualifier Video Clip is aerial-heavy the second stage
weakens exactly where it's needed. Optional add-on: hull number/pennant OCR as a confidence
booster when text is legible, never a replacement.

This spans two roles: **Member A** sources/labels the reference photos, **Member B** trains the
second-stage classifier on the crops.

**~~Possible starting point for "local" reference images: SKN601DEMO~~ — RULED OUT 2026-07-30,
verified against the actual export, don't re-check.** The earlier note guessed it was "very
likely genuine Malaysian assets" from its class vocabulary. It downloaded and it is not usable:

- **It's a person-detection dataset, not a vessel one.** `Person` (13,110) + `People` (4,710) +
  `sar` (697) are **96.4%** of its 19,215 instances. All 22 vessel classes together are 3.6%.
  SKN601 reads like a course code; this is a student SAR/man-overboard demo.
- **`Warship` has 11 instances across 4 unique source images.** Collapsing Roboflow
  augmentation, the whole military-ish set (`Warship`, `FAC`, `FCB90`, `MPCSS`, `Patrol Vessel`,
  `Coast Guard - Police`) is **179 unique source images**, not the 1,906 the page advertised.
- **The imagery is wrong even where it exists.** Opening real crops: `FAC` and `Patrol Vessel`
  are **thermal/IR** greyscale of one vessel shot repeatedly; `FCB90` mixes real photos with
  **3D CAD renders** on plain backgrounds (watermarked); `MPCSS` is one heavily-artefacted
  upscaled aerial; `Warship`/`Coast Guard - Police` are colour-filtered/tinted stills.
- **They are not reliably Malaysian.** One `FCB90` render carries a **Russian flag**, which
  directly falsifies the "vocabulary implies Malaysian asset" assumption the lead rested on.
- Also worth knowing if anyone reopens it: labels are **mixed format** — 18,851 five-token
  bboxes plus ~364 polygon-segmentation lines (up to 1,201 tokens), so any converter must
  handle both. Declared `nc: 25`, and all 25 classes do have instances.

**Collect from Wikimedia Commons instead.** It's organised *by hull class*, which is the label
the silhouette approach actually needs, each photo names the real vessel so "local" is
verifiable rather than inferred, and the RMN combat fleet is a small closed set (~15 classes ×
20-50 photos ≈ 300-750 images). Start at
[Category:Kedah class offshore patrol vessels](https://commons.wikimedia.org/wiki/Category:Kedah_class_offshore_patrol_vessels)
and the [RMN fleet list](https://en.wikipedia.org/wiki/Royal_Malaysian_Navy).

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

- [ ] Low priority, only if more frontal volume is ever wanted: the `Sailboat detector` lead in
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan)'s open-leads list (camera angle
      unverified). Every bucket it would touch is already past floor
- [x] ~~Fix `roboflow-korean_marine_object.v1i.yolov11` class export~~, confirmed via COCO
      re-export it's single-class by design (not a bug), see
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan). Use only as generic
      vessel-localization data, not a source of type labels
- [x] ~~Source more `tanker` data, the last mandatory class below the ~800-1000 floor~~ solved
      2026-07-29 after six sourcing attempts: `roboflow-Tanker.v1i`, `roboflow-VESSELimg.v4i`,
      `roboflow-Vessel.v2i` downloaded and folded in, +1924 instances (475 -> 2399 pooled).
      Full record (dead-end Roboflow slugs, per-dataset breakdown, untried leads) in
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan). (This fixed the *pooled*
      number only; tanker's aerial gap was closed separately, see the resolved section above.)
- [x] ~~Build the class-remapping table + decide handling for ambiguous/unmapped classes
      (`Carrier`, `ore carrier`, `Merchant Ship`, `Patrol Boat`, `Sails Boat`, `Tugboat`,
      `canoe`, `kayak`, `sailboat`, `engineering ship`, `Datasense@CRAS`'s
      `small boat`/`uncategorized`, etc.)~~ definitive mapping written 2026-07-29, recounted
      directly from label files (not carried over from old prose, which had drifted), see
      [GUIDELINES.md](GUIDELINES.md#class-remapping-definitive-mapping-recounted-2026-07-29).
      Still open: turning the table into an actual merge script (see below), and the one
      explicitly-flagged undecided call (`LNG`/`gas carriers` -> `tanker` or not)
- [x] ~~Decide what to do with `kaggle-satellite` and `roboflow-maritime.v3i`~~ both deleted
      2026-07-30 along with `korean_marine_object`, `Military Ship Detection` and `MASATI` — five
      zero-contribution sources, ~4.3GB reclaimed, each verified against its own `data.yaml`
      immediately before removal. Full list and reasons in
      [GUIDELINES.md](GUIDELINES.md#dataset-inventory)
- [x] ~~Source aerial-view data for the 5 zero-coverage classes~~ **solved 2026-07-30, all 8
      classes now clear the aerial floor — see the resolved section at the top of this file** for
      what closed it and the two caveats carried forward
- [x] ~~Hand-triage `roboflow-Marina 2.yolov11`'s `twist_*` filename family image by image~~ done
      2026-07-30, all 38 images opened; per-image verdicts in
      [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py), net counts in
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan)
- [x] ~~Decide where `roboflow-Marina 2.yolov11` should live on disk~~ moot as of the 2026-07-30
      restructure: `datasets/` is now flat, one folder per dataset, and camera angle is a column in
      [GUIDELINES.md](GUIDELINES.md#dataset-inventory) rather than a directory — so a
      genuinely-mixed source no longer needs to pretend to be one or the other
- [x] ~~Write the frame-extraction + `.mat`-to-YOLO conversion script for Singapore Maritime
      Dataset~~ **don't build this — closed 2026-07-30 after reading the actual `.mat` ground
      truth.** SMD is a detection/*tracking* benchmark, not a classification one: it annotates
      where vessels are, not what type. Full `ObjectType` histogram over all 67 `ObjectGT/*.mat`
      (264,250 boxes): `Vessel/ship` 185,719 (a generic catch-all — **70%, maps to nothing in our
      taxonomy**), `Other` 42,936, `Boat` 14,237, `Buoy` 4,407, `Kayak` 3,798, `Sail boat` 3,067,
      `Flying bird/plane` 499, and only `Ferry` 5,125 + `Speed boat` 4,462 are mappable — **3.6%**.
      Worse, those 9,587 mappable boxes come from just **18 videos** as tracked objects across
      consecutive frames (`MVI_1524_NIR` alone is 1,496 `Speed boat` boxes = one or two craft
      followed across ~1,500 near-identical frames), and 10 of the 18 are NIR. Restricted to
      visible light it's ~2,728 boxes from 8 videos, for `passenger_ferry`/`speedboat` — two
      classes already well past floor. Same generic-single-class trap that got
      `korean_marine_object`/`MASATI`/`Military Ship Detection` deleted, just in a MATLAB coat.
      **If SMD imagery is ever wanted, the path is `Datasense@CRAS`'s 914 `MVI_####_VIS_frame###`
      annotations** (INESC TEC re-annotated SMD footage with real ship types where SMD says only
      `Vessel/ship`), not SMD's own ground truth. The 5.4GB is the largest deletable block on disk
- [x] ~~Merge all remapped/converted sources into one unified YOLO dataset~~ **done 2026-07-30**,
      [scripts/merge_dataset.py](scripts/merge_dataset.py) → `datasets/merged-yolo/data.yaml`,
      `nc: 8` in canonical order. 34,863 images (27428/3802/3633), 57,399 instances, all 8 buckets
      matched their expected totals exactly. Verified: 0 broken symlinks, 0 corrupt images under
      `ultralytics`, 0 stems shared across splits (no leakage), crops opened per class per source.
      `inesctec-Datasense@CRAS` stays excluded as the ~87%-duplicate finding requires
- [x] ~~Dataset split sanity check: make sure frames extracted from the same source video don't
      end up split across train and val~~ **done 2026-09-11.** Bigger than expected: on top of
      within-source video-frame leakage (a prior session found `Marina 2`'s 21-frame `DJI_*`
      leak), this pass found **cross-source duplicate photos** — several "different" Roboflow
      projects were built from the same underlying stock/CCTV photos, so the identical image
      could land in train via one project and test via another. Confirmed visually before fixing
      anything: `MyBoats.v2i`'s frame `000141` and `Seaships7000.v1i`'s `000141` are the same CCTV
      capture (`2017-01-04 10:02:47` burned into both); `vessel.v1i`'s `709508` (train) is the same
      cruise-ship stock photo as `Ship2.v1i`'s `709508` (test).

      Two flagged-but-unverified candidates turned out to be **false positives** and were
      deliberately left untouched: `converted-vhrships-yolo`'s `PE_002`/`PE_003`/etc. are
      per-instance catalog numbers for unrelated individual ships (not video frames), and
      `Sea Vessels Dataset.v2`'s `yacht_4`/`yacht_5`/etc. are the same — a 4-panel mosaic next to
      an unrelated single megayacht photo. Numeric-adjacency alone isn't proof; every fix below
      was confirmed by opening actual images first.

      Detector: [scripts/check_split_leakage.py](scripts/check_split_leakage.py) (writes nothing,
      flags candidates by filename adjacency/duplication for manual confirmation). Fix:
      [scripts/split_overrides.py](scripts/split_overrides.py), consulted by
      `scripts/merge_dataset.py`'s `process_native`/`process_preconverted` — union-find over (a)
      confirmed within-source video sessions (`VESSELimg`, `Seaships7000`, `Yacht Detection`,
      `kapal-penumpang-done`'s timestamped frames, `Buoys and Boats`' `buoy_b_2_`/`youtube-`
      frames) and (b) exact-filename duplicates across different sources, then forces each
      resulting group into whichever split already holds most of its members (ties favour train,
      since moving a duplicate into train can't inflate an eval metric). 4,427 of 34,862 images
      reassigned. Total instances/classes unchanged (`--check`'s 12 `EXPECTED_*` assertions still
      pass exactly), only the split distribution shifted:

      | split | before | after |
      |---|---|---|
      | train | 27,428 img / 45,318 inst | 31,211 img / 50,472 inst |
      | val | 3,802 img / 6,068 inst | 2,247 img / 3,924 inst |
      | test | 3,633 img / 6,013 inst | 1,405 img / 3,002 inst |

      **val/test shrank by ~45%** (9,701 → 5,329 combined instances) — real held-out data was
      never as large as it looked, a lot of it was near-duplicates of train. Re-verified after
      the fix: 0 broken symlinks, exact 1:1 image/label pairing, 0 stems shared across splits,
      and the specific confirmed-leaking groups spot-checked to now land in one split (e.g. all
      696 frames of `VESSELimg`'s `2023-06-27-14-31-00` session are now in `train`; the `709508`
      quadruplet across `vessel.v1i`/`Ship2.v1i`/`kapal-penumpang-done` is now all in `train`).

      **`Marina 2`'s 21-frame leak: decided (b), accepted and documented, not fixed.** Left out of
      `split_overrides.py` on purpose — at 21 frames it's two orders of magnitude smaller than
      what this pass actually found and fixed (4,427 images), not worth the special-case code.

      **Not exhaustively checked**: sources whose own numeric filenames showed adjacency
      (`Warship.v4i`, `typesofships.v6i`, `kapal.v1i`, `ship detection.v2i`, `Tanker.v1i`,
      `Ship2.v1i`/`vessel.v1i`/`MyBoats.v2i`'s own-internal sequences) were deliberately **not**
      given the within-source video-session treatment — no independent confirmation they're
      continuous recordings rather than per-instance catalogs (that's exactly how VHRShips and Sea
      Vessels turned out to be false leads). They still benefit from the cross-source
      duplicate-detection half of the fix wherever they share an exact filename with another
      source, just not from adjacency-based grouping of their own numbering. If per-class metrics
      on these specific classes look off later, this is the first place to re-check.
- [x] ~~Augmentation/oversampling pass for the thin *pooled* classes (`tanker`, `yacht`)~~ no
      longer needed, both solved by sourcing dedicated datasets instead
- [x] ~~Source reference photos for the "local" half of the military classifier~~ **done
      2026-07-30**: `datasets/wikimedia-rmn/`, 220 images via
      [scripts/wikimedia_rmn.py](scripts/wikimedia_rmn.py), all licence-verified with
      per-image attribution in `credits.csv` (87 Public domain, 53 CC0, rest CC BY/BY-SA).
      0 exact duplicates, 0 undecodable. "Foreign" needs no sourcing — crop from
      `merged-yolo`'s existing 6,524 `military` boxes
- [x] ~~Triage `wikimedia-rmn` — it is NOT usable as-is~~ **filename-driven pass done
      2026-07-30, visual pass done 2026-09-11.** Reviewed all 80 `lekiu_frigate` and
      all 58 `patrol` images 2026-07-30. **A Commons category means "this photo is associated
      with X", not "this photo shows X"** — the same class of trap as the Roboflow
      page-vs-download mismatch, and it bites hard here:
      - `lekiu_frigate` is contaminated with **foreign warships**, including several **US
        aircraft carriers** (the RMN operates none) and Sydney-harbour shots from multinational
        exercises. Photos taken *from* a Lekiu during an exercise get filed under Lekiu. These
        are not merely useless, they are **wrong-label poison** for a local/foreign classifier.
      - Also present in `lekiu_frigate`: ~6 empty-sea/horizon frames with no vessel, 2 building
        interiors, several weapon/turret close-ups with no hull silhouette.
      - `patrol` is ~80% ceremony and open-day material of a single vessel (crowds, bunting,
        crew lined on deck) plus ~12 **bridge-interior** shots (control panels, steering
        wheels). Roughly 8-10 of 58 show a usable hull.
      - The `patrol` vessel reads **"KM Banggi"** — `KM` is Malaysian Maritime Enforcement
        Agency, not `KD` (Kapal Diraja, the RMN prefix). So most of that folder is **coast
        guard, not navy**. Decide explicitly whether MMEA counts as "local"; the primary
        detector's `military` class was trained on grey-hull warships and may never route a
        white MMEA hull to stage 2 at all.
      **Triaged 2026-07-30** by [scripts/wikimedia_rmn_triage.py](scripts/wikimedia_rmn_triage.py)
      -> `datasets/wikimedia-rmn/triage.csv`. Classification is **filename-driven, not
      eyeball-driven**: the Commons page title names the ship or the event (`USS_`, `JS_`,
      `HMNZS_`, `RIMPAC`, `RAN-IFR`), which is reproducible, whereas judging nationality from
      a 175px thumbnail is guesswork -- a Kasturi and a foreign corvette look alike at that
      size, and a hand-indexed contact-sheet pass misaligned labels to cells often enough to
      be untrustworthy. Result:

      | verdict | n | |
      |---|---|---|
      | `rmn` | 51 | trainable "local" **upper bound** |
      | `detail` | 9 | RMN but weapon/radar/boarding close-ups, no hull silhouette |
      | `foreign` | 90 | **41% of the download** — other navies + multinational exercises |
      | `mmea` | 55 | Malaysian coast guard, excluded by the RMN-only decision |
      | `unknown` | 15 | no nationality signal in the title |

      **51 is an upper bound, not a final count** — it still contains distant/occluded hulls
      and at least one museum scale-model shot that only a careful per-image visual pass will
      catch.

      **Visual pass done 2026-09-11** by
      [scripts/wikimedia_rmn_visual_triage.py](scripts/wikimedia_rmn_visual_triage.py), all 51
      `rmn` images opened at full resolution (not the 175px contact sheet). 13 rejected: the
      predicted museum scale-model (a display-case photo, not a real vessel), a misfiled/
      duplicate image, a busy multi-ship formation with 3 unidentified vessels, a hull under
      construction in red primer, a hull mostly hidden by ceremonial smoke, two Scorpene photos
      with no RMN markings at all (generic hull, also operated by India/Chile/Brazil, shot
      during French sea trials), and 5 equipment/interior close-ups (radar, torpedo tubes,
      bridge) that the filename regex missed and are now folded into `detail`. Final:

      | verdict | n | |
      |---|---|---|
      | `rmn` | **38** | confirmed trainable "local" set |
      | `detail` | 14 | RMN but weapon/radar/bridge/boarding close-ups, no hull silhouette |
      | `rmn_reject` | 8 | RMN but museum model / misfiled / formation-contaminated / under
        construction / smoke-occluded / no visible national markings |
      | `foreign` | 90 | other navies + multinational exercises |
      | `mmea` | 55 | Malaysian coast guard, excluded by the RMN-only decision |
      | `unknown` | 15 | no nationality signal in the title |

      38 lands a bit under the ~40-45 pre-look guess. Worth flagging for whoever trains the
      classifier: 38 "local" against ~5,975 croppable "foreign" `military` boxes already in
      `merged-yolo` is roughly **1:157** before any subsampling, worse than the ~1:27 the
      220-image pre-triage set implied.
- [x] ~~Write the crop-extraction step for the "foreign" half~~ **done 2026-09-11**: see the
      "Military classification approach" section above for the resolved ratio/contamination
      decisions and output paths. Handed off to Member B
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
      `ultralytics` version pinned in `pyproject.toml`). **Transfer bundle STALE as of
      2026-09-11**: `~/samudra-merged-yolo.tar` (4.41GB, 27428/3802/3633) was built before the
      "Dataset split sanity check" fix below moved 4,427 images between splits (val/test shrank
      ~45%). If training already started from that tar, its val/test numbers are inflated by
      cross-split duplicates — re-tar `datasets/merged-yolo/` (now 31211/2247/1405) and re-check
      any metrics already recorded. `merged-yolo` is symlinks into per-source folders and is
      **not portable as-is** — materialise with `tar -chf` (the `-h` dereferences) or `rsync -aL`
- [ ] Baseline training run on Member A's merged dataset, sanity-check per-class metrics.
      **Unblocked as of 2026-07-30**: `datasets/merged-yolo/data.yaml`, `nc: 8`, 34,863 images /
      57,398 instances, verified (see the RESOLVED merge section at the top of this file for the
      per-class table and the two open data-quality notes). Run it on **CUDA, not the Mac** —
      use [scripts/colab_baseline.py](scripts/colab_baseline.py), which carries the Colab cells
- [ ] ~~Don't train on the Mac~~ **measured 2026-07-31, all at imgsz=640, 27,428 train images:**

      | config | mem | throughput | per epoch |
      |---|---|---|---|
      | `yolo11n` batch 8 workers 2 MPS | 2.36GB | 2.5 it/s | ~23 min |
      | `yolo11s` batch 8 workers 2 MPS | 4.32GB | 1.0 it/s | ~57 min |
      | `yolo11s` batch 16 **workers 8** MPS | swaps | ~0.0015 it/s | **~310 h** |

      That last row is a real trap and cost a wasted 28-minute run: **16GB of unified memory
      is shared between CPU and the MPS backend**, so 8 dataloader workers each buffering
      640px batches push the machine into swap and throughput collapses to ~11 min *per
      batch*. On CUDA the worker count is far less dangerous (GPU memory is separate), so
      `workers=8 batch=16` is correct there and wrong here. Also: launch long runs
      **detached** (`nohup`/`setsid`) — a run started as a child of an editor/agent shell dies
      when that process restarts, which is how the first attempt was lost
- [ ] Hyperparameter tuning: image size, batch size, LR schedule, epoch count, augmentation
      config (mosaic, flip, rotation, brightness/weather jitter for maritime haze/glare)
- [ ] Class-imbalance handling in training config: class weights or oversampling. Note the
      imbalance is now per-view, not pooled — check the frontal/aerial split in
      [GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split)
      rather than the totals (e.g. `container_ship` is aerial-heavy, `speedboat`/`yacht` are
      frontal-heavy), and decide this alongside the single-model-vs-two-models call above
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

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

`datasets/` is gitignored, lives on disk only. Reviewed 2026-07-29, re-checked 2026-07-29 after
adding yacht sources (labels/metadata only, no image or video content opened). Instance counts
= bounding boxes, not images.

**Frontal-view** (`datasets/frontal-view/`)

| Dataset | Images (train/val/test) | Classes (instances) | License |
|---|---|---|---|
| `roboflow-Warship.v4i.yolov11` | 2814/150/40 | warship (3435) | CC BY 4.0 |
| `roboflow-vessel.v1i.yolov11` | 1318/249/125 | Cargo (336), Carrier (356), Cruise (685), Tanker (350), Warship (347) | CC BY 4.0 |
| `roboflow-Military Ship Detection.v2i.yolov11` | 1807/602/602 | ship (3713) | CC BY 4.0 |
| `roboflow-Seaships7000.v1i.yolov11` | 5584/-/1395 | bulk cargo carrier (1941), container ship (901), fishing boat (2187), general cargo ship (1501), ore carrier (2195), passenger ship (473) | CC BY 4.0 |
| `roboflow-ship detection.v2i.yolov11` | 2249/750/749 | canoe (2545), sailboat (2203), speedboat (3070), passenger ship (1073), fishing boat (527), cargo ship (244), kayak (332), warship (404), engineering ship (91), container ship (22), tanker (10) | CC BY 4.0 |
| `roboflow-Sea Vessels Dataset.v2-sea_vessels_v2.yolov11` | 530/139/67 | Fishing Boat (346), Merchant Ship (366), **Military Ship (383)**, Patrol Boat (382), Sails Boat (419), **Submarine (315)**, Tugboat (46), **Yacht (361)** | CC BY 4.0 |
| `roboflow-Boats Detection.v15i.yolov11` | 1128/0/0 (no val/test split) | cargo (504), speed (348), **yacht (276)** | CC BY 4.0 |
| `roboflow-korean_marine_object.v1i.yolov11` | 5754/0/0 | **broken: `nc: 1, names: ['-']`, all 17,525 boxes collapsed to one placeholder class** | CC BY 4.0 |
| `roboflow-Ship2.v1i.yolov11` | 348/99/51 | Cargo (100), Carrier (100), Cruise (177), Military (104), **Tanker (101)** | CC BY 4.0 |
| `Datasense@CRAS` (INESC TEC, DOI [10.25747/96kp-5033](https://doi.org/10.25747/96kp-5033)) | 6511/1628/905 | bulk carrier (2199), ore carrier (3510), **container ship (6742)**, cruise ship (278), **ferry boat (1113)**, sailboat (921), fishing boat (2227), small boat (3142), uncategorized (1038) | CC BY-SA |
| `roboflow-MyBoats.v2i.yolov11` | 634/170/84 | Bulk carrier (11), Coastal tourist passenger ship (59), Container ship (114), Fishing vessel (253), General cargo ship (303), LNG (16), Luxury Cruise (9), **Oil tanker (14)**, Patrol boat (38), Ro-ro ship (15), Rubber boat (17), Sailing boat (28), Sand carrier (115), Speed boat (9), Tug (31), Wooden boat (22) | CC BY 4.0 |
| `roboflow-Buoys and Boats.v3i.yolov11` | 7299/323/161 | buoy (10565), boat (3616), bridge (268), merchant_ship (245), fishing_boat (159), barge (146), beacon (94), ship (64), person (9), **cruise (3)**, **yacht (3)** | CC BY 4.0 |
| `roboflow-typesofships.v6i.yolov11` | 520/145/85 | buoy (173), sailing_vessel (109), bulk_carrier (108), patrol_vessel (134), kayak (152), tug (64), anchor_handling_tug_supply (63), container (74), **combat_vessel (48)**, **yacht (90)** | CC BY 4.0 |
| `roboflow-Yacht Detection.v2-alphayacht1.0.yolov11` | 1497/321/321 | **yacht (2297)**, motorship (394), small boat (243), jet ski (162), sailboat (45), ferry (14) | CC BY 4.0 |
| `roboflow-kapal-penumpang-done.v1i.yolov11` | 1766/421/22 | **single-class by design (see below): kapal_penumpang / passenger ship (2753)** | Public Domain |
| `roboflow-Tanker.v1i.yolov11` | 1173/146/0 | Boat (637), Cargo (52), CoastGuard (4), Container (42), **Tanker (1326)**, Tug (142) | CC BY 4.0 |
| `roboflow-Vessel.v2i.yolov11` | 1491/149/84 | Bulker (256), Container (174), Sail (372), gas carriers (209), **tanker (291)**, tug (16), warship (376) | CC BY 4.0 |
| `smd-VIS_Onboard`, `smd-VIS_Onshore`, `smd-NIR` (Singapore Maritime Dataset) | n/a | raw `.avi` + MATLAB `.mat` ground truth, not annotated for YOLO (see below) | not specified |

**Aerial/satellite-view** (`datasets/aerial-view/`)

| Dataset | Images (train/val/test) | Classes (instances) | License |
|---|---|---|---|
| `roboflow-MASATI.v1i.yolov11` | 2797/936/250 | ship (3486), multi (929), coast_multi (573), ok (195), multi_224 (184), water (25) | CC BY 4.0 |
| `roboflow-maritime.v3i.yolov11` | 2195/29/- | Person in water (6517), Person out of water (1129), Boat (923), Person drowning (356) | CC BY 4.0 |
| `kaggle-satellite` | 4000 chips (1000 ship / 3000 no-ship) + 8 full scenes | classification only, no boxes | not bundled, check Kaggle page |
| `roboflow-VESSELimg.v4i.yolov11` (drone footage, Eurecat Robotics, Valencia Port, H2020 PASSport project) | 4262/1222/608 | Buoy (573), **Chemical (307)**, Container (5535), Passenger-RoRo (1703), Pilot (397), Tugboat (4364) | CC BY 4.0 |

### Findings that change the plan

- **`roboflow-korean_marine_object.v1i.yolov11` is single-class by design, not a broken export.**
  Confirmed by re-downloading as COCO JSON: the frozen v1 export (generated 2023-09-07) genuinely
  only has one leaf category, literally named `-`, under a `ship` supercategory. The 10-class
  list (cargo ship, fishing boat, yacht, Korean harbor-infrastructure terms, etc.) shown on the
  live Roboflow project page reflects the project's current state, not what this particular
  frozen version contains. Usable only as generic vessel-localization data (no type info), same
  tier as `roboflow-Military Ship Detection`'s single `ship` class.
- **Military detection improved past silhouette-only.** `Sea Vessels Dataset` adds a genuinely
  distinct `Military Ship` (383) and `Submarine` (315) label, on top of the generic `warship`
  silhouette class everywhere else. Still nothing distinguishes Malaysian vs. foreign, that
  remains a from-scratch problem (see taxonomy section above).
- **Yacht gap solved.** `Sea Vessels Dataset` (361) + `Boats Detection.v15i` (276) = 637.
  `Buoys and Boats` looked promising on the Roboflow overview page (2935 images, includes a
  `yacht` class) but only contributed 3 instances out of 15172 total boxes, it's overwhelmingly
  a `buoy` (10565) / generic `boat` (3616) navigation-marker dataset, not a vessel-type one.
  `typesofships` did better, +90 (also adds `combat_vessel`, 48, to the military bucket). The
  real fix was `Yacht Detection` (Dinos Workspace), a dataset purpose-built for exactly this
  rather than yacht-as-a-minor-class in a big ship taxonomy: +2297, taking the bucket to 3027,
  comfortably past the ~800-1000 floor.
- **Severe class imbalance in `roboflow-ship detection.v2i`**: tanker (10 boxes) and container
  ship (22 boxes) are too sparse to train on alone, lean on Seaships7000 for those classes instead.
- **Tanker sourcing has hit diminishing returns.** Four attempts so far: `Ship2` (+101, 360 ->
  461), `MyBoats` (+14, -> 475), MVDD13 (a confirmed dead end, see its GitHub issues), and a
  further round of Roboflow searches (Gemi Sınıflandırma, ships-by-yao, georeferencing_data,
  several oil-tanker-named projects) that turned up only duplicates of the already-ruled-out
  50-class ShipRSImageNet family or unrelated "oil" hits (spills, cooking oil, tank trucks). A
  fifth attempt, `kapal-penumpang-done` (2209 images, same Cargo/Carrier/Cruise/Military/Tanker
  taxonomy as `Ship2` but 4.4x bigger, looked like the best lead yet) hit the exact same trap as
  `korean_marine_object` and `ships9000` before it: the frozen downloadable version is
  single-class (`kapal_penumpang`, all 2753 boxes), not the 6 classes the live Roboflow project
  page shows. Zero tanker gain from it (it did add 2753 to passenger_ferry instead, see below).
  Tanker is still the only mandatory class below the comfort floor after five attempts. Generic
  multi-class Roboflow search is no longer productive for this class; next step is likely a
  dedicated tanker-specific source or manual curation rather than another broad ship dataset.
- **Tanker gap solved (2026-07-29), six attempts total.** Two Roboflow projects looked promising
  but turned out to be raw-upload-only, same "0 dataset versions" trap as `ships9000`:
  `gdut-fbja3/vessel-wqp7q` (4,841 images, has Oil Tanker) and `-i1wmc/vessel-yhmsk` (6,092
  images, has Chemical=chemical tanker), neither downloaded. But `-i1wmc`'s sibling
  `b-rubi/vesselimg` has the *same 6,092-image pool already packaged into a downloadable
  version* (drone footage, Eurecat Robotics, Valencia Port, H2020 PASSport project) and two more
  targeted single-purpose datasets panned out: `hungcheck-siodu/tanker-3s16r` (537 base images)
  and `1-ty2nq/vessel-5aqsj` (632 images, filenames confirm real tanker ships, e.g.
  `Scorpio-Tankers-Inc`). All three downloaded and verified directly against `data.yaml` +
  labels (not the live page): **Tanker (1326, `roboflow-Tanker.v1i`) + Chemical (307,
  `roboflow-VESSELimg.v4i`, visually confirmed as tanker-hulled vessels not container ships) +
  tanker (291, `roboflow-Vessel.v2i`) = 1924 new instances**, taking the bucket from 475 to
  **2399**, comfortably past the ~800-1000 floor. Confirms the same pattern as yacht: a
  dedicated tanker-only or tanker-heavy dataset succeeds where tanker-as-a-minor-class in a
  broad ship taxonomy kept failing. HuggingFace and Zenodo were never checked specifically
  during the search (only Kaggle was, which turned up the "Game of Deep Learning" ship dataset,
  1,217 tanker images, but whole-image classification not bounding boxes, not a direct fix but
  worth keeping in mind for a second-stage classifier later) — not urgent now that the floor is
  cleared, but a place to look first if more tanker volume/diversity is wanted for augmentation.
- **Container_ship gap solved.** `Datasense@CRAS` adds 6742 container ship instances (923 ->
  7665), by far the single largest class it has. Also adds a genuine `ferry boat` label (1113),
  the first source that isn't just proxying passenger_ferry via "cruise"/"passenger ship". No
  class-name file was bundled with the download, the 9-class mapping (`bulk carrier`,
  `ore carrier`, `container ship`, `cruise ship`, `ferry boat`, `sailboat`, `fishing boat`,
  `small boat`, `uncategorized`, in that ID order) was determined empirically on 2026-07-29 by
  cropping and visually inspecting sample boxes per class ID, not from official docs (none could
  be found, including the associated conference paper). Written into this dataset's `data.yaml`.
  Tanker (475, unrelated to this fix) is now the only remaining "collect more" gap.
- **`roboflow-maritime.v3i` is SAR/rescue-oriented, not vessel-typed**: labels
  people-in-water/jetski/buoy, not ship types. Useful only for generic small-craft localization
  in aerial view, not for the civilian/military taxonomy.
- **Disk cleanup (2026-07-29): dropped two aerial-view datasets, 26GB -> 14GB, zero loss to any
  mandatory class.** `kaggle-SeaDronesSee` (9.3GB) had the same SAR/rescue problem as
  `roboflow-maritime.v3i` above but contributed nothing to the sufficiency table either way, and
  at a third of the entire `datasets/` footprint was the single biggest non-contributor.
  `kaggle-MASATI-V2` (3.3GB) was also removed: its license ("non-profit research/educational"
  only, not CC) would have blocked it from a competition submission regardless of relevance, so
  it carried legal risk with no offsetting value. Deleted from disk, not just unused, if either
  is needed again they'd need to be re-downloaded from Kaggle.
- **`kaggle-satellite` is image-classification, not detection**: 80x80px chips labeled
  ship/no-ship (no bounding boxes), plus 8 large scenes meant for sliding-window search. Can't
  be merged into YOLO training directly, best used as a classifier or hard-negative source.
- **Singapore Maritime Dataset is unprocessed but fully extracted** (`smd-VIS_Onboard`,
  `smd-VIS_Onshore`, `smd-NIR`): raw `.avi` videos + MATLAB `.mat` ground truth in `TrackGT/`,
  `ObjectGT/`, `HorizonGT/`, no images/labels, no `data.yaml`. Needs a frame-extraction +
  `.mat`-to-YOLO conversion script before any of it is trainable.

Every YOLO-format Roboflow folder has its own `data.yaml` (train/val/test paths, `nc`, `names`)
plus `README.roboflow.txt` / `README.dataset.txt` with license + source URL. `Datasense@CRAS` is
not a Roboflow export (no bundled `data.yaml` or license file), the `data.yaml` in that folder
was written by hand here, source/license/DOI documented inside it.

### Class remapping needed before merging

None of the raw class sets match the mandatory taxonomy verbatim. Before combining datasets for
training, map source classes into: `container_ship`, `tanker`, `cargo`, `passenger_ferry`
(civilian); `yacht`, `speedboat`, `fishing_boat` (small craft); `military` (generic, then a
separate local/foreign step). Generic/ambiguous classes (`ship`, `boat`, `multi`, `ok`, `water`,
`canoe`, `kayak`, `sailboat`, `patrol boat`, `sails boat`, `tugboat`) don't map 1:1 and need
either a decision to drop, bucket into small-craft, or hand-review.

## Data sufficiency (checked 2026-07-29, updated 2026-07-29 after yacht + container_ship + tanker sourcing)

Rule of thumb for fine-tuning a pretrained YOLO to a reliable recall number: ~800-1000 train
instances and ~150-200 validation instances per class. Below that, recall on that class is
noisy regardless of how good the model looks.

Current instance counts after mapping raw classes into the mandatory taxonomy:

| Bucket | Instances | Status |
|---|---|---|
| container_ship | 7853 | fixed (was 923), now the best-covered class |
| yacht | 3027 | fixed (was 0), `Yacht Detection` alone contributed 2297 |
| military (warship + Military Ship + Submarine + Ship2's Military + typesofships' combat_vessel) | 5036 | good, genuinely distinct military labels, not just silhouette "warship" |
| cargo | 5293 (+2651 ambiguous "carrier"/"ore carrier", +366 + 245 "Merchant Ship", +5709 Datasense@CRAS bulk/ore carrier, +108 typesofships' bulk_carrier) | good |
| speedboat | 3427 | good |
| fishing_boat | 3472 (+2227 Datasense@CRAS, +253 MyBoats, +159 Buoys and Boats) | good |
| passenger_ferry | 5246 (+1113 genuine "ferry boat", +278 + 3 "cruise ship", +14 Yacht Detection's ferry, +2753 kapal-penumpang-done, rest still proxied via "cruise"/"passenger ship") | good |
| tanker | 2399 | fixed (was 475), `roboflow-Tanker.v1i` alone contributed 1326 |
| local vs. foreign military | 0 | still unsolved, doesn't exist in any off-the-shelf dataset |

Tanker took six targeted sourcing attempts (`Ship2` +101, `MyBoats` +14, MVDD13 a dead end, a
round of Roboflow searches that found nothing new, `kapal-penumpang-done` which turned out
single-class, then finally `roboflow-Tanker.v1i` + `roboflow-VESSELimg.v4i` + `roboflow-Vessel.v2i`
which together added 1924, see findings above). Same pattern as yacht: multi-class datasets with
tanker as a minor category gave diminishing returns until a dedicated tanker-only or
tanker-heavy dataset (`Tanker` by Hungcheck, mirroring `Yacht Detection`'s role for the yacht
gap) solved it in one shot.

Every mandatory class now clears the ~800-1000 floor. Only "local vs. foreign military" remains
unsolved, and that's a labeling/classifier problem, not a volume problem (see "Military
classification approach" in [TODO.md](TODO.md)).

Verdict: **sufficient to start training** the civilian/small-craft/generic-military detector.
Two things still block a Top-10-competitive submission regardless of dataset volume:

- **Local vs. foreign military** doesn't exist in any public detection dataset. Build it by
  hand from reference photos (RMN/APMM public releases for "local", foreign navy press photos
  for "foreign"), and treat it as a second-stage classifier on cropped military detections, not
  a class in the primary detector.
- **Validation must match the actual test domain.** Recall > 90% is measured against the
  Qualifier Video Clip, not Roboflow's held-out split. Once that clip is available, pull frames
  from it and hand-label a slice as the real validation set.

Stack and repo conventions live in [CLAUDE.md](CLAUDE.md).

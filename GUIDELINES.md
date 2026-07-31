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

`datasets/` is gitignored, lives on disk only. **Flat layout, one folder per dataset** — the old
`frontal-view/` + `aerial-view/` split was dropped 2026-07-30 (it couldn't express
mixed-provenance sources, and camera angle is a per-class property, so it's the `View` column
below instead of a directory). Folder-name prefixes carry the meaning now: `converted-*` is
script-generated and safe to regenerate, everything else is raw source material named for where it
came from. See [CLAUDE.md](CLAUDE.md#working-with-datasets) for the conventions.

Instance counts = bounding boxes, not images. `View` is where a dataset's *usable* instances come
from, verified by opening real sample images, not inferred from the class list — several sources
with aerial-sounding class lists turned out shore-level on inspection.

**`merged-yolo` is the training dataset.** Everything below it in this table is an input to it,
listed so each source's contribution stays traceable, not something to point a training run at
directly. (It's script-generated and freely regenerable like the `converted-*` folders, but keeps
the bare `merged-yolo` name because it's the one path downstream code and teammates reference.)

| Dataset | View | Images (train/val/test) | Classes (instances) | License |
|---|---|---|---|---|
| `merged-yolo` (**generated** by [scripts/merge_dataset.py](scripts/merge_dataset.py) from the 2 `converted-*` sources + 16 native Roboflow sources + `Marina 2`'s clean-aerial subset; canonical 8-class order, absolute symlinks, per-source filename tags) | mixed | 27428/3802/3633 (34863 total, 0 corrupt) | container_ship (8394), tanker (3998), cargo (11245), passenger_ferry (9600), yacht (4648), speedboat (4693), fishing_boat (8297), military (6524) — **57399 instances**, verified 2026-07-30 | inherits the most restrictive input license: **CC BY-SA 4.0** (via `converted-kfgod-yolo`) |
| `converted-kfgod-yolo` (**generated** from `huggingface-KFGOD` by [scripts/kfgod_to_yolo.py](scripts/kfgod_to_yolo.py); KOMPSAT-3/3A satellite, 0.55-0.7m GSD) | aerial | 697/41/42 | **fishing_boat (4769)**, **speedboat (1200, capped subsample of `motorboat`, see script docstring)**, **military (386, from `warship`)**, container_ship (952, bonus), tanker (212, bonus), passenger_ferry (1873, bonus) — 9392 mapped, cargo/yacht not mappable from this source | CC BY-SA 4.0 (**share-alike, see the license caveat in Findings**) |
| `converted-vhrships-yolo` (**generated** from `kaggle-VHRShips` by [scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py); Google Earth, 500m eye altitude) | aerial | 3500/437/439 | container_ship (580), **tanker (1373)**, **cargo (2450)**, passenger_ferry (763), **yacht (1621)**, speedboat (0), fishing_boat (37), **military (616)** — 7440 mapped of 11337 total | MIT |
| `roboflow-VESSELimg.v4i.yolov11` (drone footage, Eurecat Robotics, Valencia Port, H2020 PASSport project) | aerial | 4262/1222/608 | Buoy (573), **Chemical (307)**, Container (5535), Passenger-RoRo (1703), Pilot (397), Tugboat (4364) | CC BY 4.0 |
| `roboflow-kapal.v1i.yolov11` (Google Earth screenshots + real FPV drone footage w/ flight telemetry HUD, Indonesian labels) | aerial | 33/9/6 | cargo (58), speedboat (39), **warships (18)**, tanker (14), kapal/generic-ship (14), nelayan/fishing (10), cole cole (8, unidentified, excluded), tongkang/barge (5), tugbuoat (4), tallships (1) | Public Domain per uploader, **but see license caveat in Findings** |
| `roboflow-Marina 2.yolov11` | **mixed** | 747/178/74 | **raw counts are NOT the usable counts — fully triaged 2026-07-30, see Findings and [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py)**: of 1,744 raw instances only 132 are verified clean aerial (military +92, speedboat +27, fishing_boat +9, cargo +4); the rest is frontal shore-CCTV (cargo 400, passenger 208, redundant with `Seaships7000`), out-of-taxonomy swimmer (984), or confirmed-not-aerial | CC BY 4.0 (**but see license caveat in Findings**) |
| `inesctec-Datasense@CRAS` (INESC TEC, DOI [10.25747/96kp-5033](https://doi.org/10.25747/96kp-5033)) | frontal | 6511/1628/905 | bulk carrier (2199), ore carrier (3510), **container ship (6742)**, cruise ship (278), **ferry boat (1113)**, sailboat (921), fishing boat (2227), small boat (3142), uncategorized (1038) | CC BY-SA |
| `roboflow-Seaships7000.v1i.yolov11` | frontal | 5584/-/1395 | bulk cargo carrier (1941), container ship (901), fishing boat (2187), general cargo ship (1501), ore carrier (2195), passenger ship (473) | CC BY 4.0 |
| `roboflow-ship detection.v2i.yolov11` | frontal | 2249/750/749 | canoe (2545), sailboat (2203), speedboat (3070), passenger ship (1073), fishing boat (527), cargo ship (244), kayak (332), warship (404), engineering ship (91), container ship (22), tanker (10) | CC BY 4.0 |
| `roboflow-Warship.v4i.yolov11` | frontal | 2814/150/40 | warship (3435) | CC BY 4.0 |
| `roboflow-Yacht Detection.v2-alphayacht1.0.yolov11` | frontal | 1497/321/321 | **yacht (2297)**, motorship (394), small boat (243), jet ski (162), sailboat (45), ferry (14) | CC BY 4.0 |
| `roboflow-Tanker.v1i.yolov11` | frontal | 1173/146/0 | Boat (637), Cargo (52), CoastGuard (4), Container (42), **Tanker (1326)**, Tug (142) | CC BY 4.0 |
| `roboflow-kapal-penumpang-done.v1i.yolov11` | frontal | 1766/421/22 | **single-class by design (see Findings): kapal_penumpang / passenger ship (2753)** | Public Domain |
| `roboflow-Vessel.v2i.yolov11` | frontal | 1491/149/84 | Bulker (256), Container (174), Sail (372), gas carriers (209), **tanker (291)**, tug (16), warship (376) | CC BY 4.0 |
| `roboflow-vessel.v1i.yolov11` | frontal | 1318/249/125 | Cargo (336), Carrier (356), Cruise (685), Tanker (350), Warship (347) | CC BY 4.0 |
| `roboflow-Buoys and Boats.v3i.yolov11` | frontal | 7299/323/161 | buoy (10565), boat (3616), bridge (268), merchant_ship (245), fishing_boat (159), barge (146), beacon (94), ship (64), person (9), **cruise (3)**, **yacht (3)** | CC BY 4.0 |
| `roboflow-MyBoats.v2i.yolov11` | frontal | 634/170/84 | Bulk carrier (11), Coastal tourist passenger ship (59), Container ship (114), Fishing vessel (253), General cargo ship (303), LNG (16), Luxury Cruise (9), **Oil tanker (14)**, Patrol boat (38), Ro-ro ship (15), Rubber boat (17), Sailing boat (28), Sand carrier (115), Speed boat (9), Tug (31), Wooden boat (22) | CC BY 4.0 |
| `roboflow-Sea Vessels Dataset.v2-sea_vessels_v2.yolov11` | frontal | 530/139/67 | Fishing Boat (346), Merchant Ship (366), **Military Ship (383)**, Patrol Boat (382), Sails Boat (419), **Submarine (315)**, Tugboat (46), **Yacht (361)** | CC BY 4.0 |
| `roboflow-typesofships.v6i.yolov11` | frontal | 520/145/85 | buoy (173), sailing_vessel (109), bulk_carrier (108), patrol_vessel (134), kayak (152), tug (64), anchor_handling_tug_supply (63), container (74), **combat_vessel (48)**, **yacht (90)** | CC BY 4.0 |
| `roboflow-Boats Detection.v15i.yolov11` | frontal | 1128/0/0 (no val/test split) | cargo (504), speed (348), **yacht (276)** | CC BY 4.0 |
| `roboflow-Ship2.v1i.yolov11` | frontal | 348/99/51 | Cargo (100), Carrier (100), Cruise (177), Military (104), **Tanker (101)** | CC BY 4.0 |

**Second-stage classifier data** (not part of the 8-class detection merge, feeds the
local-vs-foreign military stage — see [TODO.md](TODO.md)'s Military classification approach):

| Dataset | View | Images | Contents | License |
|---|---|---|---|---|
| `wikimedia-rmn` (**generated** by [scripts/wikimedia_rmn.py](scripts/wikimedia_rmn.py) from Wikimedia Commons, 2026-07-30) | frontal/broadside | 220 (per-hull-class folders) | The **"local"** half: RMN vessels — `lekiu_frigate` 80, `patrol` 58, `kasturi_corvette` 28, `kedah_opv` 23, `scorpene_submarine` 8, `laksamana_corvette`/`auxiliary`/`other_rmn` 6 each, `amphibious` 3, `keris_lms`/`gagah_training` 1 each. **Not yet triaged** — contains crew/ceremony shots and some non-RMN white hulls | mixed, **per-image attribution in `credits.csv`** (87 Public domain, 53 CC0, 37 CC BY-SA 3.0, 27 CC BY-SA 4.0, rest CC BY). 3 files skipped as non-free |

The **"foreign"** half needs no separate source: crop the 6,524 `military` boxes already in
`merged-yolo`. Feed `credits.csv` to Member D for the Technical Brief's licensing section.

**On disk but deliberately contributing nothing** (kept for a stated future purpose, not merged
into any bucket — see Findings for why each was rejected):

| Dataset | Why it's still here |
|---|---|
| `kaggle-VHRShips` | Raw source for `converted-vhrships-yolo`; its `_mergedData/` is the symlink target, so it can't be deleted while that conversion exists |
| `huggingface-KFGOD` | Raw source for `converted-kfgod-yolo`, same symlink constraint |
| `smd-VIS_Onboard`, `smd-VIS_Onshore`, `smd-NIR` (Singapore Maritime Dataset, 5.4GB) | Raw `.avi` + MATLAB `.mat` ground truth, no YOLO labels — **and the conversion is not worth writing, closed 2026-07-30 after reading the `.mat` files** (see Findings). 70% of its 264,250 boxes are the generic `ObjectType` `Vessel/ship`; only 3.6% (`Ferry`, `Speed boat`) maps to our taxonomy, from 18 videos of temporally-redundant tracked frames, for two classes already past floor. Largest deletable block on disk |
| `roboflow-IR boats.yolov11` | Confirmed shore-mounted thermal, frontal. Kept only as a thermal/night-vision robustness option for later; every class it covers is already past floor |
| `roboflow-Simulator 2.v3i.yolov11` | Confirmed frontal merged aggregate (stock photos, harbour CCTV, naval PR). Kept as documented frontal volume; not merged because it risks near-duplicate content with `SeaShips`-derived data already on disk |
| `roboflow-SKN601DEMO.v1i.yolov11` (234MB) | Sourced as a candidate "local" (Malaysian) military reference set; **ruled out 2026-07-30, see the finding in [TODO.md](TODO.md)'s Military classification section**. It's 96.4% `Person`/`People`/`sar` — a student SAR demo, not a vessel dataset. `Warship` = 11 instances over 4 unique source images; the whole military-ish set is 179 unique images after collapsing augmentation. Imagery is thermal/IR, 3D CAD renders, and colour-filtered stills, and one `FCB90` render flies a **Russian flag**, so the "Malaysian vocabulary implies Malaysian asset" premise is false. Labels are mixed bbox + polygon-segmentation. Deletable |

**Deleted 2026-07-30, don't re-download** (contributed zero instances to any mandatory bucket;
verified against their own `data.yaml`/contents immediately before removal, ~4.3GB reclaimed):
`roboflow-korean_marine_object.v1i` (3.3GB, `nc: 1, names: ['-']` — single placeholder class by
design, 17,525 generic boxes), `kaggle-satellite` (442MB, classification chips only, zero label
files), `roboflow-Military Ship Detection.v2i` (278MB, `nc: 1, names: ['ship']`),
`roboflow-MASATI.v1i` (195MB, generic `ship`/`multi`/`water` scene classes),
`roboflow-maritime.v3i` (50MB, SAR/rescue `Person in water`/`drowning` labels, no ship types).
Earlier deletions for the same reason: `kaggle-SeaDronesSee` (9.3GB) and `kaggle-MASATI-V2` (3.3GB,
also non-commercial-licensed), both 2026-07-29.


### Findings that change the plan

**Standing traps** (hit repeatedly across every sourcing session, check for these before trusting
any new candidate):

- A Roboflow project's live overview page (class list, image count) does not necessarily match
  the frozen downloadable version. Always check the actual downloaded `data.yaml` and label
  files directly, never trust the page. Hit repeatedly: `korean_marine_object`, `ships9000`,
  `kapal-penumpang-done`, `SentinelBlue`.
- Some Roboflow projects show real images but have "0 dataset versions" — raw uploads never
  packaged into a downloadable split (hit with `gdut-fbja3/vessel-wqp7q`, `-i1wmc/vessel-yhmsk`,
  `holi-atkgu/ir-boats` before forking it, `roniabusayeed/vessel-detection-3-final`). Not usable
  without forking + generating a version yourself.
- A project's displayed license (MIT/Apache/CC BY/Public Domain) reflects whatever the
  *uploader* typed in, not necessarily the license of the underlying imagery, especially for
  re-uploads of known academic benchmarks or Google Earth screenshots. Hit repeatedly: xView and
  ShipRSImageNet forks tagged permissively despite the source being non-commercial-only;
  `kapal.v1i` and `Marina 2`'s Google Earth content tagged Public Domain/CC BY despite Google's
  imagery not being either. Check the original paper/dataset page's license, not just a mirror's
  badge, whenever a project looks like a re-upload or contains screenshot-sourced imagery.
- A promising class list is not evidence of camera angle. Confirmed wrong repeatedly (`Simulator
  2`, `IR boats`, `ARG-NCTU/spscd_plus_buoy_yolo`, `singapore-maritime`, and more below) — every
  aerial candidate needs 3-5 real sample images opened before it's trusted, not just its
  `data.yaml`.
- Check license before investing time. `kaggle-MASATI-V2`'s "non-profit research/educational
  only" license got it deleted after already being on disk, wasted effort.

**Ruled out for aerial-view vessel-type sourcing, don't re-check** (grouped by why they failed;
all confirmed via the dataset's own license page/data.yaml/sample images, not a mirror's claims):

- *Academic benchmarks with real per-type taxonomies, blocked by non-commercial licensing at the
  source* — the imagery rights holder restricts commercial use regardless of what license tag a
  re-uploader (Roboflow/Kaggle/HuggingFace mirror) attaches: **xView** (DIUx/NGA, CC BY-NC-SA
  4.0, incl. `HichTala/xview` on HF), **FAIR1M** (Gaofen/ISPRS, CC BY-NC-SA 3.0), **ShipRSImageNet**
  (GitHub, "academic purposes only" — signature class names `Arleigh Burke DD`/`Atago DD`/
  `Ticonderoga`, re-uploaded as `HiResShipDetection`/`ShipRSImageNet_V1`/`Marine Vessels
  Detection`/`ShipRSI`/`viviwang/MARINER` on HF — MARINER additionally is a 1,000-image test-only
  split, no train data, don't chase any project with this class signature), **DOTA**/**DOTA v2**
  (CC BY-NC, and only a single generic `ship` class regardless), **AFO** (CC BY-NC-SA 3.0), and
  the Sentinel-2-based **recreational-boat-tracking Zenodo release**
  (`10.5281/zenodo.10046341`)/its HF model twin (`mayrajeo/marine-vessel-detection-yolov8`) — this
  one also fails on resolution (10m/px, too coarse for vessel type) independent of licensing.
- *Genuinely aerial but single generic class or classification-only, no vessel-type breakdown*:
  `NWPU VHR-10`, `FGSD` (43 classes but only 5,634 instances total, thinner than useful), `FGSCR-42`
  (no license stated, Baidu-Pan-gated), `siddharthkumarsah/ships-in-aerial-images` (CC BY-SA 4.0
  but single-class), `kaggle-satellite`/`apollo2506/satellite-imagery-of-ships` (classification
  chips, no boxes), `myworkspace-t26e4/maritime-object-detection-v1`, the "Aerial Maritime"
  tutorial dataset and its ~10 re-uploads, `DefendIntelligence/vessel-detection-labeled-patches`
  (Sentinel-2, same 10m/px problem).
- *SAR or rescue-oriented, not vessel-typed*: `roboflow-maritime.v3i`, `kaggle-SeaDronesSee` (incl.
  its v2 host at `cloud.cs.uni-tuebingen.de`), `SentinelBlue`, `xView3-SAR` (wrong modality
  entirely — radar backscatter, not camera imagery, rules out the whole SAR fishing-detection
  research area for this project).
- *Confirmed frontal/shore-level on actual image inspection despite a promising class list*:
  `Simulator 2` (merged aggregate: stock photos, harbor CCTV, naval PR shots), `IR boats` (shore
  thermal camera), `ARG-NCTU/spscd_plus_buoy_yolo` (Split, Croatia harbor webcam),
  `maritime-cumkb/singapore-maritime` (the academic Singapore Maritime Dataset, onshore/onboard
  camera), `tom-mirowski-kiwmj/updated_classes`, `university-of-naples-federico-ii-f7xio/infrarosso2`
  (fixed IR camera), `roniabusayeed/vessel-detection-3-final`, `hanchong/real-infrared-maritime-
  vessel-dataset` (near-duplicate of `IR boats`), the `seaobjects`/`mcship`/`ship-data01` family,
  `ADRS_Ship_Detection`, `whutboat/boatds`, `ABOships` (onboard waterbus camera), `MASS-LSVD`
  (onboard mast camera), DLUVA's "Ship Vessel Identification" family (same as `Sea Vessels
  Dataset` already on disk).
- *Redundant re-exports of a dataset already on disk*: `datnguyentien204/Seaship7000` and
  `roboflow-Sea Ships.v3-resized_640_2_classes` (both re-exports of `Seaships7000`, the latter
  downloaded, confirmed, and deleted).
- *Wrong domain entirely*: `zhuchi76/Boat_dataset` (mostly synthetic/CGI renders for ASV-robotics
  obstacle detection, not vessel-type classification; no license stated).
- *No usable annotations yet*: `AMP2026` (semantic labels are stated future work in the paper).

**Not ruled out, still open leads if more aerial volume is ever needed**:
- **`Marship-OBB9`/YOLO-UAVShip** (Li et al. 2025, real DJI drone footage, has `fishing boat`/
  `cargo`/`tanker`/`container ship` categories) — available on request only, email pending to
  corresponding author Chao Yuan (Aerospace Information Research Institute, Chinese Academy of
  Sciences), ask about redistribution terms explicitly if it comes through.
- **Seagull dataset** (VisLab, Instituto Superior Técnico Lisbon, fixed-wing UAV, has `cargo
  ships`/`patrol boats`) — available on request only, email the VisLab team via their site.
- **`zenodo.org/records/16588542`** ("Roboflow Maritime & Aerial Objects," 44-class compilation of
  existing Roboflow Universe projects, CC BY 4.0, single 16.7GB `.7z`) — deprioritized, not
  conclusively ruled out. By construction it's a repackaging of Roboflow Universe projects (the
  exact surface already swept above), so likely low marginal value, and would need the same
  per-family provenance triage `Marina 2` required, at ~17x the size. If ever pursued, extract
  `AGGREGATED_README.md` first and diff its 44 source URLs against the ruled-out list above before
  touching the imagery.
- **Sailboat detector** (`learning-299jh/sailboat-detector`, 8,888 images, CC BY 4.0, likely an
  `ABOships` fork, 11 classes incl. `militaryship`/`cargoship`/`passengership`/`motorboat`, no
  `yacht`) — not checked for camera angle yet, would boost military/cargo/passenger_ferry if
  needed later, not currently a priority since those buckets are cleared.

**Per-dataset findings for what's actually on disk:**

- **`roboflow-korean_marine_object.v1i.yolov11` was single-class by design, not a broken export**
  (deleted from disk 2026-07-30, kept here as the record of why).
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
- **Tanker gap solved (2026-07-29) after six sourcing attempts.** Final contributors: **Tanker
  (1326, `roboflow-Tanker.v1i`) + Chemical (307, `roboflow-VESSELimg.v4i`, visually confirmed as
  tanker-hulled, not container ships) + tanker (291, `roboflow-Vessel.v2i`) = 1924 instances**,
  taking the bucket from 475 to 2399. The five failed attempts before it (`Ship2` +101, `MyBoats`
  +14, MVDD13 dead end, a broad Roboflow sweep that only resurfaced the ShipRSImageNet family or
  unrelated "oil" hits, and `kapal-penumpang-done` which hit the frozen-version-is-single-class
  trap) establish the pattern that also held for yacht: **a dedicated tanker-heavy dataset
  succeeded where tanker-as-a-minor-class in a broad ship taxonomy kept failing.** If more tanker
  volume/diversity is ever wanted for augmentation, HuggingFace/Zenodo were never swept for this
  class specifically, and Kaggle's "Game of Deep Learning" ship dataset (1,217 tanker images,
  whole-image classification not boxes) could feed a second-stage classifier.
- **Container_ship gap solved.** `Datasense@CRAS` adds 6742 container ship instances (923 ->
  7665), by far the single largest class it has. Also adds a genuine `ferry boat` label (1113),
  the first source that isn't just proxying passenger_ferry via "cruise"/"passenger ship". No
  class-name file was bundled with the download, the 9-class mapping (`bulk carrier`,
  `ore carrier`, `container ship`, `cruise ship`, `ferry boat`, `sailboat`, `fishing boat`,
  `small boat`, `uncategorized`, in that ID order) was determined empirically on 2026-07-29 by
  cropping and visually inspecting sample boxes per class ID, not from official docs (none could
  be found, including the associated conference paper). Written into this dataset's `data.yaml`.
  Tanker (475, unrelated to this fix) is now the only remaining "collect more" gap.
- **Aggregate sufficiency numbers were hiding a severe frontal/aerial imbalance (found
  2026-07-29, since resolved).** The old sufficiency table pooled both views into one instance
  count per class, which made every mandatory class look "good" while **5 of 8 actually had zero
  aerial-view instances** (cargo, yacht, speedboat, fishing_boat, military), with every aerial
  mandatory-class instance on disk coming from a single dataset (`VESSELimg.v4i`). The lesson
  outlasts the gap, which is why the sufficiency table below stays split by view permanently:
  **the ~800-1000 floor has to be applied per class *per view*, not to pooled counts** — a model
  can look fully trained on paper and never have seen a whole class from directly overhead. The
  mission statement requires both frontal and aerial/satellite classification, and Phase 2's
  hidden stress test could use either angle. (Closed 2026-07-30 by the VHRShips + KFGOD
  conversions; `container_ship` remains skewed the opposite way, aerial-heavy with the weakest
  frontal count of any class, still above floor.)
- **`roboflow-kapal.v1i.yolov11` is the second aerial source ever found to contribute
  mandatory-class instances** (after `VESSELimg.v4i`), and the first for `cargo`/`speedboat`/
  `military`/`fishing_boat`, all of which were at exactly zero before it. Confirmed aerial by
  opening samples: a mix of Google Earth satellite screenshots and real FPV drone footage (flight
  telemetry HUD visible). 171 instances, 139 mapped. Tiny, but real. **License caveat**: tagged
  "Public Domain" by the uploader, but part of it is literally Google Earth screenshots, which
  Google's imagery is not — don't cite that tag unqualified in the Technical Brief.
- **`Simulator 2` and `IR boats` are on disk but deliberately unintegrated.** Both were downloaded
  chasing aerial coverage and confirmed frontal (see the ruled-out list above); both are kept as
  documented frontal volume / thermal-robustness options rather than deleted, but neither feeds
  any bucket — every class they cover is already past the frontal floor, and `Simulator 2` is an
  unvetted merged aggregate whose near-duplicate risk against `SeaShips`-derived data on disk
  isn't worth taking for volume that isn't needed.
- **Disk cleanup (2026-07-29): dropped two aerial-view datasets, 26GB -> 14GB, zero loss to any
  mandatory class.** `kaggle-SeaDronesSee` (9.3GB, SAR/rescue, biggest non-contributor on disk)
  and `kaggle-MASATI-V2` (3.3GB, "non-profit research/educational only" license — legal risk with
  no offsetting value). Both deleted from disk, not just unused; re-download from Kaggle if ever
  needed.
- **`roboflow-Marina 2` is a mixed-provenance aggregate: its raw per-class counts are NOT usable,
  they must be split by source-filename family (triaged 2026-07-30, see
  [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py) for the per-image verdicts).**
  Its 1,744 instances come from at least five unrelated sources under one 6-class `data.yaml`,
  landing in different view buckets. Verified by grouping labels by filename prefix and opening
  real images from each: the `0XXXXX` numeric family (cargo 400, passenger 208) is Chinese harbour
  shore-CCTV, **frontal and almost certainly redundant with `Seaships7000`** already on disk;
  `DJI_*`, `Screenshot from 2024-05-29 *` and `IPgiBNOPCjQ-*` are genuinely aerial and clean; and
  the `twist_*` family needed per-image triage (32 of 38 images genuine aerial, 6 dropped: 2
  sea-level, 2 elevated-shore, 1 hillside overlook, 1 CGI render). **Net verified aerial
  contribution: speedboat +27, fishing_boat +9, military +92, cargo +4**, folded into the
  sufficiency table below. **License caveat**: tagged CC BY 4.0, but the content demonstrably
  includes third-party-watermarked forum scrapes, YouTube frames and a synthetic render, so that
  tag can't be cited unqualified in the Technical Brief. This is the clearest case of why this
  project opens sample images rather than trusting `data.yaml` — the raw counts alone would have
  claimed ~99 aerial military and 39 aerial speedboat instances, and both are wrong.
- **`kaggle-satellite` was image-classification, not detection** (deleted 2026-07-30): 80x80px
  chips labeled ship/no-ship with zero label files, plus 8 large scenes for sliding-window search.
  Never usable for YOLO training directly; the speculative "could be a classifier/hard-negative
  source" case didn't justify 442MB once every class was past floor.
- **Singapore Maritime Dataset is unprocessed, and should stay that way (closed 2026-07-30).**
  `smd-VIS_Onboard`/`smd-VIS_Onshore`/`smd-NIR` are raw `.avi` + MATLAB `.mat` ground truth in
  `TrackGT/`, `ObjectGT/`, `HorizonGT/` — no images, no labels, no `data.yaml`. An earlier note
  called for a frame-extraction + `.mat`-to-YOLO script; **don't write it.** Parsing all 67
  `ObjectGT/*.mat` (`structXML`, fields `ObjectType`/`BB`/`Motion`/`Distance`) gives 264,250
  boxes with this `ObjectType` histogram: `Vessel/ship` 185,719, `Other` 42,936, `Boat` 14,237,
  `Ferry` 5,125, `Speed boat` 4,462, `Buoy` 4,407, `Kayak` 3,798, `Sail boat` 3,067, `Flying
  bird/plane` 499. **SMD annotates vessel *location*, not vessel *type*** — it's a detection and
  tracking benchmark, so 70% of it is the generic `Vessel/ship` catch-all and only `Ferry` +
  `Speed boat` (9,587 boxes, **3.6%**) map to our taxonomy at all. Those come from just 18 videos
  as tracked objects across consecutive frames — `MVI_1524_NIR` contributes 1,496 `Speed boat`
  boxes, which is one or two craft followed across ~1,500 near-identical frames, not 1,496
  vessels — and 10 of the 18 are NIR (a different imaging modality). Visible-light only, it's
  ~2,728 boxes from 8 videos, for `passenger_ferry` and `speedboat`, both already well past
  floor. This is the same generic-label trap that got `korean_marine_object`, `MASATI`, and
  `Military Ship Detection` deleted. **If SMD imagery is ever wanted, take `Datasense@CRAS`'s 914
  `MVI_####_VIS_frame###` images instead** — INESC TEC re-annotated SMD footage with real ship
  types where SMD itself says only `Vessel/ship` — which folds into option (a) in the
  `Datasense@CRAS` finding below rather than being a separate conversion job.
- **`inesctec-Datasense@CRAS` is ~87% a re-annotation of data already on disk, and is deliberately
  excluded from the merge (proven 2026-07-30).** Its own counts are real and correct (21,170
  instances over 9 classes, recounted from its 9,044 label files, matching the inventory above),
  and an earlier finding credited it with "solving" container_ship. **But it is not in the
  definitive mapping, and that is correct, not an oversight** — the reason simply was never
  written down until now. Breaking its filenames down by family: **7,000 are pure-numeric SeaShips
  names, and 6,979 of those are the exact same image stems as `roboflow-Seaships7000.v1i` already
  on disk**; a further 914 are `MVI_####_VIS_frame###`, i.e. Singapore Maritime Dataset frames
  (also already on disk as `smd-*`); only 103 `rosbag_leixoes_*` (INESC TEC's own Porto de Leixões
  recordings) plus ~1,027 others are genuinely new imagery. Merging it alongside `Seaships7000`
  would double-count the same physical images under two different label sets and leak them across
  the train/val boundary. Its labels are *denser* than SeaShips' (21,170 vs 9,198 instances on
  broadly the same images, e.g. container ship 6742 vs 901), so it is a legitimate alternative
  annotation of that imagery — but not an addition to it. Excluded because every mandatory class
  already clears its floor without it, so there is no benefit to offset the duplication risk. If
  more frontal volume is ever wanted, the honest options are (a) take only its ~1,130
  non-duplicate images, or (b) swap it in *instead of* `Seaships7000`, never both — and note its
  9 class names were determined empirically by eyeballing crops, not from documentation (its own
  `data.yaml` says so), which is a quality caveat for option (b).
- **`KFGOD` closed the last aerial gaps, and is the best-provenanced source in the project
  (2026-07-30).** KOMPSAT-3/3A satellite imagery (0.55-0.7m GSD) published by **KARI**, the actual
  satellite operator, via [Lee et al., *Remote Sensing* 2025](https://doi.org/10.3390/rs17223774)
  and Korea's national research data platform (DataON, `doi.org/10.22711/idr/1101`). Unlike every
  other academic satellite benchmark checked, the license (CC BY-SA 4.0) comes from the rights
  holder itself, not a third party redistributing restricted imagery. Raw data on disk at
  `datasets/huggingface-KFGOD/` (5.7GB, PNG + YOLO-OBB only, verified byte-exact
  against the source manifest); converted by
  [scripts/kfgod_to_yolo.py](scripts/kfgod_to_yolo.py). **License caveat**: CC BY-SA is
  share-alike, so any redistributed derivative (converted dataset, arguably the trained model)
  inherits those terms — flag this in the Technical Brief's licensing section rather than citing
  it as unconditionally permissive. **Mapping caveat**: `speedboat` comes from a capped random
  subsample of KFGOD's `motorboat` class, a deliberate judgment call rather than a clean 1:1
  mapping — see the sufficiency table below and the script's module docstring.

Every YOLO-format Roboflow folder has its own `data.yaml` (train/val/test paths, `nc`, `names`)
plus `README.roboflow.txt` / `README.dataset.txt` with license + source URL. `Datasense@CRAS` is
not a Roboflow export (no bundled `data.yaml` or license file), the `data.yaml` in that folder
was written by hand here, source/license/DOI documented inside it.

### Class remapping: definitive mapping (recounted 2026-07-29)

None of the raw class sets match the mandatory taxonomy verbatim. Earlier versions of this doc
described the remapping in prose only, and it drifted: the cargo bucket's own breakdown text
didn't even sum to its stated total (9079 vs. the 5293 once shown here). The table below is a
full recount straight from every dataset's `data.yaml` + label files (not carried over from
old notes), so it's now the single source of truth for which raw class goes where. It also
splits every number by `frontal-view`/`aerial-view`, see
[Data sufficiency](#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split) for
why that split matters.

**Three sources' mappings now live in code, not in this table.** `VHRShips` (34 raw classes -> 7
buckets) is mapped by the `MAP` dict in
[scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py); `KFGOD` (33 raw classes -> 6 buckets,
including the capped `motorboat` -> `speedboat` subsample) by
[scripts/kfgod_to_yolo.py](scripts/kfgod_to_yolo.py); `Marina 2`'s aerial subset by
[scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py). Each script documents its own
deliberate exclusions. `converted-vhrships-yolo/` and `converted-kfgod-yolo/` are already written
in the canonical taxonomy order, so they need no remapping at merge time — and that order is the
one the unified merge script must match:
`container_ship, tanker, cargo, passenger_ferry, yacht, speedboat, fishing_boat, military`.
`Marina 2` deliberately has **no** entry below because its raw counts are not usable per-bucket
without the source-family split described in the findings above.

**Mapped classes, grouped by mandatory bucket** (dataset :: raw class = instances [view]):

- **container_ship**: `VESSELimg.v4i` :: Container = 5535 [aerial] · `Seaships7000.v1i` ::
  container ship = 901 [frontal] · `Vessel.v2i` :: Container = 174 [frontal] · `MyBoats.v2i` ::
  Container ship = 114 [frontal] · `typesofships.v6i` :: container = 74 [frontal] · `Tanker.v1i`
  :: Container = 42 [frontal] · `ship detection.v2i` :: container ship = 22 [frontal]
- **tanker**: `Tanker.v1i` :: Tanker = 1326 [frontal] · `vessel.v1i` :: Tanker = 350 [frontal] ·
  `VESSELimg.v4i` :: Chemical = 307 [aerial] · `Vessel.v2i` :: tanker = 291 [frontal] · `Ship2.v1i`
  :: Tanker = 101 [frontal] · `MyBoats.v2i` :: Oil tanker = 14 [frontal] · `kapal.v1i` :: tanker =
  14 [aerial] · `ship detection.v2i` :: tanker = 10 [frontal]
- **cargo**: `Seaships7000.v1i` :: ore carrier = 2195, bulk cargo carrier = 1941, general cargo
  ship = 1501 [all frontal] · `Boats Detection.v15i` :: cargo = 504 [frontal] · `Sea Vessels
  Dataset` :: Merchant Ship = 366 [frontal] · `vessel.v1i` :: Carrier = 356, Cargo = 336
  [frontal] · `MyBoats.v2i` :: General cargo ship = 303, Sand carrier = 115, Bulk carrier = 11
  [frontal] · `Vessel.v2i` :: Bulker = 256 [frontal] · `Buoys and Boats` :: merchant_ship = 245
  [frontal] · `ship detection.v2i` :: cargo ship = 244 [frontal] · `typesofships.v6i` ::
  bulk_carrier = 108 [frontal] · `Ship2.v1i` :: Cargo = 100, Carrier = 100 [frontal] ·
  `Tanker.v1i` :: Cargo = 52 [frontal] · `kapal.v1i` :: cargo = 58 [aerial]
- **passenger_ferry**: `kapal-penumpang-done` :: kapal_penumpang = 2753 [frontal] ·
  `VESSELimg.v4i` :: Passenger-RoRo = 1703 [aerial] · `ship detection.v2i` :: passenger ship =
  1073 [frontal] · `vessel.v1i` :: Cruise = 685 [frontal] · `Seaships7000.v1i` :: passenger ship
  = 473 [frontal] · `Ship2.v1i` :: Cruise = 177 [frontal] · `MyBoats.v2i` :: Coastal tourist
  passenger ship = 59, Ro-ro ship = 15, Luxury Cruise = 9 [frontal] · `Yacht Detection` :: ferry
  = 14 [frontal] · `Buoys and Boats` :: cruise = 3 [frontal]
- **yacht**: `Yacht Detection` :: yacht = 2297 [frontal] · `Sea Vessels Dataset` :: Yacht = 361
  [frontal] · `Boats Detection.v15i` :: yacht = 276 [frontal] · `typesofships.v6i` :: yacht = 90
  [frontal] · `Buoys and Boats` :: yacht = 3 [frontal]
- **speedboat**: `ship detection.v2i` :: speedboat = 3070 [frontal] · `Boats Detection.v15i` ::
  speed = 348 [frontal] · `MyBoats.v2i` :: Speed boat = 9 [frontal] · `kapal.v1i` :: speedboat =
  39 [aerial]
- **fishing_boat**: `Seaships7000.v1i` :: fishing boat = 2187 [frontal] · `ship detection.v2i`
  :: fishing boat = 527 [frontal] · `Sea Vessels Dataset` :: Fishing Boat = 346 [frontal] ·
  `MyBoats.v2i` :: Fishing vessel = 253 [frontal] · `Buoys and Boats` :: fishing_boat = 159
  [frontal] · `kapal.v1i` :: nelayan = 10 [aerial]
- **military**: `Warship.v4i` :: warship = 3435 [frontal] · `ship detection.v2i` :: warship =
  404 [frontal] · `Sea Vessels Dataset` :: Military Ship = 383 [frontal] · `Vessel.v2i` ::
  warship = 376 [frontal] · `vessel.v1i` :: Warship = 347 [frontal] · `Sea Vessels Dataset` ::
  Submarine = 315 [frontal] · `Ship2.v1i` :: Military = 104 [frontal] · `typesofships.v6i` ::
  combat_vessel = 48 [frontal] · `kapal.v1i` :: warships = 18 [aerial]

**The per-dataset lists above cover frontal-view sources plus the two small aerial ones
(`VESSELimg.v4i`, `kapal.v1i`).** The three largest aerial contributors are mapped in code
instead, as noted at the top of this section: `converted-vhrships-yolo` (7,440 instances),
`converted-kfgod-yolo` (9,392), and `Marina 2`'s triaged aerial subset (132). Their per-class
numbers are in the dataset inventory table and the sufficiency table; the aerial column of the
sufficiency table is the sum of all five aerial sources, not just the two itemised here.

**Excluded classes (generic, ambiguous, or outside the taxonomy)** — deliberately left
unmapped, not an oversight, decision still open per dataset:

- Generic/no-type-info (excluded everywhere): `roboflow-Military Ship Detection.v2i`'s `ship`
  (3713), `roboflow-korean_marine_object.v1i`'s `-` (17525, broken export), `roboflow-MASATI.v1i`'s
  entire class list (`ship`, `multi`, `coast_multi`, `ok`, `multi_224`, `water`, 5392 total),
  `Buoys and Boats`' `boat`/`ship`/`buoy`/`bridge`/`barge`/`beacon`/`person` (14762 total)
- SAR/rescue, not vessel-typed (excluded): `roboflow-maritime.v3i`'s `Person in water`/`Person
  out of water`/`Boat`/`Person drowning` (8925 total, aerial)
- Small-craft/support types not in the 8-class taxonomy (undecided, could bucket into
  small-craft later): `sailboat`/`canoe`/`kayak` variants across several datasets, `Patrol
  Boat`/`patrol_vessel`, `Tugboat`/`tug`, `jet ski`, `motorship`, `small boat`, `Rubber boat`,
  `Wooden boat`, `Sailing boat`, `CoastGuard`, `Pilot` (aerial, `VESSELimg.v4i`), `Buoy`/`buoy`
  (not a vessel), `LNG`/`gas carriers` (arguably tanker-adjacent, deliberately left out pending
  a decision, see below), `anchor_handling_tug_supply`, `Sail`
- `Datasense@CRAS`'s `sailboat`/`small boat`/`uncategorized` (unchanged from earlier finding)

**Open decision, not yet made**: whether `LNG` (`MyBoats.v2i`, 16 instances, frontal) and `gas
carriers` (`Vessel.v2i`, 209 instances, frontal) should map to `tanker` alongside `Chemical`
(already mapped, since a chemical/gas/LNG carrier is a specialized tanker subtype). Left
excluded here for consistency with how `gas carriers` was treated in earlier notes. Note both
are frontal-view, so including them would pad tanker's already-strong frontal count, not touch
the aerial gap, and LNG/gas carrier hulls look visually distinct from oil/chemical tankers so
may deserve their own class rather than being folded in silently.

## Data sufficiency (checked 2026-07-29, recounted with frontal/aerial split)

Rule of thumb for fine-tuning a pretrained YOLO to a reliable recall number: ~800-1000 train
instances and ~150-200 validation instances per class. Below that, recall on that class is
noisy regardless of how good the model looks.

Instance counts below are a direct recount from every dataset's label files (not carried over
from prior sessions' prose), split by view, using the definitive mapping above. This supersedes
all earlier versions of this table, some of which (cargo, military, container_ship,
passenger_ferry) had drifted from an inconsistent, undocumented set of ambiguous-class
decisions, see the note at the top of the class-remapping section.

| Bucket | Frontal | Aerial | Total | Status |
|---|---|---|---|---|
| container_ship | 1327 | 7067 | 8394 | good total, but weakest **frontal** count of any class |
| tanker | 2092 | 1906 | 3998 | **aerial floor CLEARED 2026-07-30** by the VHRShips conversion |
| cargo | 8733 | 2512 | 11245 | **aerial floor CLEARED 2026-07-30** by the VHRShips conversion |
| passenger_ferry | 5261 | 4339 | 9600 | good in both views independently |
| yacht | 3027 | 1621 | 4648 | **aerial floor CLEARED 2026-07-30**, went from literal zero to comfortably over floor in one step |
| speedboat | 3427 | 1266 | 4693 | **aerial floor CLEARED 2026-07-30** by the KFGOD conversion, was the thinnest class at 66 |
| fishing_boat | 3472 | 4825 | 8297 | **aerial floor CLEARED 2026-07-30** by the KFGOD conversion, went from ~15x under floor to well over it |
| military | 5412 | 1112 | 6524 | **aerial floor CLEARED 2026-07-30** by the KFGOD conversion, was 726 (close but short) |
| local vs. foreign military | 0 | 0 | 0 | still unsolved, doesn't exist in any off-the-shelf dataset |

**Update 2026-07-30 (VHRShips converted): the aerial gap is now mostly closed.** Converting
VHRShips to YOLO ([scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py)) added 7,440 aerial
instances in one step and cleared the floor outright for `yacht` (0 -> 1621, the class that had
been at literal zero across three sourcing sessions), `cargo` and `tanker` (321 -> 1694).
**Update 2026-07-30, `Marina 2` fully triaged** (see the finding above and
[scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py)) added a further military
+92, speedboat +3, fishing_boat +1, cargo +4 of genuinely aerial, hand-verified content on top of
that. `military` now sits at 726 (was 18 at the start of the day), close to the floor but not
over it.

**Update 2026-07-30 (KFGOD converted): the aerial gap for the last two classes is now closed.**
`KFGOD` (KOMPSAT satellite imagery, KARI, see the dataset inventory below) was downloaded and
converted ([scripts/kfgod_to_yolo.py](scripts/kfgod_to_yolo.py)), adding 9,392 aerial instances:
`fishing_boat` +4,769 (56 -> 4,825, from ~15x under floor to comfortably over), `military` +386
(726 -> 1,112, clearing the floor it had been ~75-275 short of), and `speedboat` +1,200 (66 ->
1,266, clearing the floor it had been thinnest and ~13x under). The `speedboat` contribution is a
**capped random subsample** of KFGOD's `motorboat` class (raw total 34,574 in the downloadable
train+val split alone) rather than a straight map — `motorboat` is KOMPSAT's catch-all label for
small motor-powered craft, not confirmed recreational-speedboat-specific, and taking all 34,574
would have let one KOMPSAT-only source dwarf every other aerial class in the merged dataset. See
the KFGOD finding above and `scripts/kfgod_to_yolo.py`'s module docstring for the full
reasoning and the user decision behind the cap. **Every mandatory class now clears the ~800-1000
aerial floor** — the first time that's been true since the frontal/aerial split was discovered.

Every pooled total clears the ~800-1000 floor, which is why earlier passes over this table (in
both this doc and TODO.md) called the class taxonomy fully solved, that reasoning was hiding the
per-view problem above — **as of the KFGOD conversion, every class now clears the floor in both
views independently too**, so the trap that motivated this whole recount no longer applies, but
the per-view table stays here rather than getting collapsed back into a pooled-only view, exactly
because collapsing it once already hid a real problem. See the finding above ("Aggregate
sufficiency numbers were hiding a severe frontal/aerial imbalance") for what drove this and why
it matters for this project's mission specifically (frontal **and** aerial/satellite
classification is a stated requirement, not a nice-to-have).

Tanker's *pooled* fix took six targeted sourcing attempts (`Ship2` +101, `MyBoats` +14, MVDD13 a
dead end, a round of Roboflow searches that found nothing new, `kapal-penumpang-done` which
turned out single-class, then finally `roboflow-Tanker.v1i` + `roboflow-VESSELimg.v4i` +
`roboflow-Vessel.v2i` which together added 1924, see findings above). Same pattern as yacht:
multi-class datasets with tanker as a minor category gave diminishing returns until a dedicated
tanker-heavy dataset solved the pooled number in one shot. That fix did not touch the aerial
gap though, only `VESSELimg.v4i` (aerial) contributed, and only 307 instances.

"Local vs. foreign military" remains unsolved for a different reason, it's a labeling/classifier
problem, not a volume problem (see "Military classification approach" in [TODO.md](TODO.md)).

Verdict: **sufficient to start training both a frontal-view and an aerial-view detector for all
8 classes**, as of the KFGOD conversion. This is volume sufficiency only, not a substitute for
actually training and validating against the real qualifier clip — see the remaining blockers
below. Two things block a Top-10-competitive submission regardless of further volume growth:

- **`speedboat`'s aerial volume leans on a single source and a judgment call.** 1,200 of its
  1,266 aerial instances come from one dataset (KFGOD) via a capped subsample of a `motorboat`
  class that isn't confirmed recreational-speedboat-specific (see the KFGOD update above). If
  training results show `speedboat` behaving oddly on aerial input, revisit that mapping decision
  before assuming it's a model problem.

- **Local vs. foreign military** doesn't exist in any public detection dataset. Build it by
  hand from reference photos (RMN/APMM public releases for "local", foreign navy press photos
  for "foreign"), and treat it as a second-stage classifier on cropped military detections, not
  a class in the primary detector.
- **Validation must match the actual test domain.** Recall > 90% is measured against the
  Qualifier Video Clip, not Roboflow's held-out split. Once that clip is available, pull frames
  from it and hand-label a slice as the real validation set.

Stack and repo conventions live in [CLAUDE.md](CLAUDE.md).

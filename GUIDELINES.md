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
| `converted-vhrships-yolo` (**converted 2026-07-30** from `kaggle-VHRShips` by [scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py), aerial) | 3500/437/439 | container_ship (580), **tanker (1373)**, **cargo (2450)**, passenger_ferry (763), **yacht (1621)**, speedboat (0), fishing_boat (37), **military (616)** — 7440 mapped of 11337 total | MIT |
| `roboflow-Marina 2.yolov11` | 747/178/74 | **mixed-provenance, fully triaged 2026-07-30, see finding below and [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py) — raw counts are NOT the usable counts**: of 1,744 raw instances, only 100 are verified clean aerial (cargo +4, fishing_boat +1, military +92, speedboat +3); the rest is frontal shore-CCTV (cargo 400, passenger 208, redundant with `Seaships7000`), out-of-taxonomy swimmer (984), or confirmed-not-aerial (military 7, speedboat 12, cargo 1) | CC BY 4.0 (**but see license caveat below**) |
| `smd-VIS_Onboard`, `smd-VIS_Onshore`, `smd-NIR` (Singapore Maritime Dataset) | n/a | raw `.avi` + MATLAB `.mat` ground truth, not annotated for YOLO (see below) | not specified |
| `roboflow-Simulator 2.v3i.yolov11` (misleading project name, confirmed a merged aggregate of stock photos/harbor CCTV/naval PR shots, not synthetic, see below) | 15642/4332/1725 | bulk carrier (4565), warship (3919), sailing_ship (3703), fishing boat (3455), container ship (3065), speedboat (3110), cargo ship (3050), canoe (3286), cruise ship (1535), passenger ship (1199), coaster (328), RORO (316), aircraft carrier (726), Oil Tanker (122), Others (20), submarine (10) | CC BY 4.0 |
| `roboflow-IR boats.yolov11` (shore-mounted thermal/IR camera, horizon-level) | 7941/322/135 | motorboat (9175), sailboat (5870), canoe (4532), warship (2547), bulk carrier (1939), liner (1433), yacht (325), container ship (692), unknown_boat (60), tall_buoy (19), boat (19), tugboat (7), fishing_trawler (7), fishing_boat (5), ship (2) | CC BY 4.0 |

**Aerial/satellite-view** (`datasets/aerial-view/`)

| Dataset | Images (train/val/test) | Classes (instances) | License |
|---|---|---|---|
| `roboflow-MASATI.v1i.yolov11` | 2797/936/250 | ship (3486), multi (929), coast_multi (573), ok (195), multi_224 (184), water (25) | CC BY 4.0 |
| `roboflow-maritime.v3i.yolov11` | 2195/29/- | Person in water (6517), Person out of water (1129), Boat (923), Person drowning (356) | CC BY 4.0 |
| `kaggle-satellite` | 4000 chips (1000 ship / 3000 no-ship) + 8 full scenes | classification only, no boxes | not bundled, check Kaggle page |
| `roboflow-VESSELimg.v4i.yolov11` (drone footage, Eurecat Robotics, Valencia Port, H2020 PASSport project) | 4262/1222/608 | Buoy (573), **Chemical (307)**, Container (5535), Passenger-RoRo (1703), Pilot (397), Tugboat (4364) | CC BY 4.0 |
| `roboflow-kapal.v1i.yolov11` (mix of Google Earth satellite screenshots + real FPV drone footage w/ flight telemetry HUD, Indonesian labels) | 33/9/6 | cargo (58), speedboat (39), **warships (18)**, tanker (14), kapal/generic-ship (14), nelayan/fishing (10), cole cole (8, unidentified, excluded), tongkang/barge (5), tugbuoat (4), tallships (1) | Public Domain per uploader, but caveat below |

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
- **Aggregate sufficiency numbers were hiding a severe frontal/aerial imbalance (found
  2026-07-29).** The old sufficiency table pooled both views into one instance count per class,
  which made every mandatory class look "good." Splitting by view (see the definitive mapping
  above) shows **5 of 8 mandatory classes have zero aerial-view instances**: cargo, yacht,
  speedboat, fishing_boat, military. Every aerial-view mandatory-class instance in the entire
  `datasets/` folder, across all sourcing sessions, comes from exactly one dataset
  (`VESSELimg.v4i`, and only 3 of its 6 classes). `container_ship` is skewed the opposite way
  (81% aerial, only 1327 frontal instances, the weakest frontal count of any class). Of the two
  non-zero-aerial classes, `passenger_ferry`'s aerial count (1703) actually clears the ~800-1000
  floor on its own, only `tanker` is genuinely thin in aerial specifically (307, well under
  floor, despite 2399 total). This isn't a volume problem the ~800-1000 floor rule catches
  when applied to pooled counts, it needs applying per class-per-view instead: a model can look
  fully trained on paper and still have never seen a cargo ship, yacht, speedboat, fishing boat,
  or military vessel from directly overhead. Given
  the mission statement explicitly requires both **frontal-view and aerial/satellite-view**
  classification, and Phase 2's hidden stress test could include either angle, this is now a
  real risk to flag in the Technical Brief at minimum, and ideally source against: aerial-view
  data for the 5 zero-coverage classes is the next highest-value sourcing target, higher
  priority than further frontal-view volume for any class.
- **`roboflow-maritime.v3i` is SAR/rescue-oriented, not vessel-typed**: labels
  people-in-water/jetski/buoy, not ship types. Useful only for generic small-craft localization
  in aerial view, not for the civilian/military taxonomy.
- **The major fine-grained aerial/satellite ship-type benchmarks are all non-commercially
  licensed (checked 2026-07-29).** Went looking for datasets in `VESSELimg.v4i`'s mold (drone
  footage, purpose-built vessel-type labels) to fix the 5-zero-aerial-class gap below. Three
  well-known academic benchmarks have exactly the per-type taxonomy needed: **xView** (DIUx/NGA,
  `maritime vessel` parent class with motorboat/sailboat/tugboat/barge/fishing vessel/ferry/
  yacht/container ship/oil tanker children), **FAIR1M** (Gaofen Challenge, ship category split
  into liquid cargo ship/dry cargo ship/fishing vessel/cruise ship/tugboat/engineering vessel/
  motorboat/warship), and **ShipRSImageNet** (50 fine-grained categories incl. cargo/container
  ship/oil tanker/fishing vessel/ferry/yacht plus ~15 named warship hull classes). All three
  turned out CC BY-NC-SA (xView 4.0, FAIR1M 3.0) or explicit "academic purposes only, commercial
  use prohibited" (ShipRSImageNet's GitHub README), confirmed against each dataset's own
  terms/license page, not just a Roboflow mirror's badge. This retroactively explains why an
  earlier session's tanker-search notes called the ShipRSImageNet family "already ruled out"
  without stating why. All three are re-uploaded on Roboflow Universe under many different
  project names (`HiResShipDetection`, `Devided xView Dataset`, `ShipRSImageNet_V1`, `Marine
  Vessels Detection`, etc.) tagged MIT/Apache/CC BY 4.0 by whoever re-uploaded them, but a
  re-uploader can't relicense someone else's copyrighted satellite imagery, the source terms
  still govern. Full write-up and the newly-checked DOTA/NWPU VHR-10 (confirmed generic
  single-`ship`-class only, same tier as MASATI) in
  [TODO.md](TODO.md#handoff-source-aerial-view-data-for-5-zero-coverage-classes-active-task).
  Net effect: `VESSELimg.v4i` is still the only large, freely-licensed, per-type aerial dataset
  found across two full sourcing sessions. The one live lead, `Marship-OBB9`/`YOLO-UAVShip`
  (Li et al. 2025, real DJI drone footage, fishing boat/cargo/bulk carrier/tanker/container ship/
  passenger ship categories), requires emailing the corresponding author for access, not a public
  download, see the TODO.md handoff for contact details and status.
- **Three Roboflow candidates downloaded and verified 2026-07-30; class lists lied, actual pixel
  content is what mattered.** Following up on the marginal candidates flagged in the previous
  session (`kapal`, `IR boats`, and the then-unchecked `Simulator 2`), all three were downloaded
  and spot-checked by opening actual sample images, not just reading `data.yaml`, same standard
  as always. Result: **`kapal` is genuinely aerial, the other two are not**, despite `Simulator
  2`'s class list looking like the best aerial match found all session:
  - **`roboflow-kapal.v1i.yolov11` confirmed aerial** — sample images are a mix of Google Earth
    satellite screenshots (watermarked) and real FPV drone footage (flight telemetry HUD visible:
    altitude, GPS, ground speed). Recounted directly from label files: 171 instances across 10
    classes, of which 139 map to the mandatory taxonomy — cargo (58), speedboat (39), warships
    (18, -> `military`), tanker (14), nelayan/fishing (10, -> `fishing_boat`) — the rest
    (kapal/generic-ship, cole cole [unidentified], tongkang/barge, tugbuoat, tallships) are
    generic or outside the taxonomy, excluded same as elsewhere. Tiny relative to the ~800-1000
    floor, but it's the **second dataset ever found** (after `VESSELimg.v4i`) to contribute real
    aerial instances to `cargo`/`speedboat`/`military`/`fishing_boat`/`tanker`, and the first for
    `military`/`speedboat`/`fishing_boat`/`cargo` specifically, all four were sitting at exactly
    zero. **License caveat**: the uploader tagged it "Public Domain," but a chunk of the images
    are literally Google Earth screenshots, and Google's satellite imagery isn't public domain
    regardless of what a re-uploader claims, same mislabeling pattern hit repeatedly this project
    (see the NC-license finding above). Given the dataset's small size the exposure is minor, but
    don't cite "Public Domain" at face value in the Technical Brief without flagging this.
  - **`roboflow-Simulator 2.v3i.yolov11` confirmed NOT aerial**, despite having the best-matching
    class list found all session (16 classes incl. warship, speedboat, fishing boat, bulk
    carrier, cargo ship, aircraft carrier, submarine — 32,409 instances, 21.7k images). The
    "Simulator" project name turned out to be a red herring, it's not synthetic/game-rendered.
    It's a large merged aggregate of stock photography (a Venice gondola tourist photo showed up
    in the sample), harbor PTZ/CCTV cameras with on-screen timestamp overlays (same elevated
    shore-camera style as `SeaShips7000`, already classified frontal in this project), and naval
    PR photography (mostly shot from dock-level or another vessel, e.g. a cruise ship in port).
    One sampled image (two warships, sea-level horizon barely below center) looked like it might
    be a helicopter shot, but that's inconsistent and not something to rely on. Left on disk in
    `frontal-view/` as documented volume, not integrated into any bucket, `military`/`speedboat`/
    `fishing_boat`/`cargo`/`tanker` are all already well past floor in frontal, so this adds
    nothing the sufficiency table needs, and merging in an unvetted aggregate risks near-duplicate
    content with sources already on disk (e.g. more `SeaShips`-style images).
  - **`roboflow-IR boats.yolov11` confirmed NOT aerial** — sample thermal images show a
    sea-level horizon near the bottom third of frame, camera mounted near water height (shore or
    low tower), not overhead. Good class list (yacht 325, container ship 692, bulk carrier 1939,
    warship 2547, 26,632 instances total, CC BY 4.0, and now has 3 real dataset versions after
    being forked to escape the "0 versions" trap noted previously) but same conclusion: frontal,
    not needed right now since every class it covers is already sufficient in frontal view. Kept
    on disk as a documented option for thermal/night-vision robustness work later, not integrated.
  - **Lesson for the rest of this handoff**: a promising class list is not evidence of camera
    angle. Every remaining Roboflow candidate needs the same treatment, open 3-5 actual sample
    images and look at them, before spending any more time on `data.yaml` alone.
- **Disk cleanup (2026-07-29): dropped two aerial-view datasets, 26GB -> 14GB, zero loss to any
  mandatory class.** `kaggle-SeaDronesSee` (9.3GB) had the same SAR/rescue problem as
  `roboflow-maritime.v3i` above but contributed nothing to the sufficiency table either way, and
  at a third of the entire `datasets/` footprint was the single biggest non-contributor.
  `kaggle-MASATI-V2` (3.3GB) was also removed: its license ("non-profit research/educational"
  only, not CC) would have blocked it from a competition submission regardless of relevance, so
  it carried legal risk with no offsetting value. Deleted from disk, not just unused, if either
  is needed again they'd need to be re-downloaded from Kaggle.
- **`roboflow-Marina 2` is a mixed-provenance aggregate: its per-class counts must be split by
  source-filename family before use (checked 2026-07-30).** The dataset's 1,744 instances come from
  at least five unrelated sources bundled under one 6-class `data.yaml`, and they land in different
  view buckets. Verified by grouping labels by filename prefix and opening real images from each
  group: the `0XXXXX` numeric family (cargo 400, passenger 208) is Chinese harbour shore-CCTV with
  burned-in timestamp/camera-ID overlays and the same numbering convention as
  `Seaships7000.v1i` already on disk, i.e. **frontal and almost certainly redundant with SeaShips**;
  `DJI_*` (speedboat 21), `Screenshot from 2024-05-29 *` (fishing_boat 8) and `IPgiBNOPCjQ-*`
  (speedboat 3) are **genuinely aerial and clean** (true top-down drone / aerial video frames);
  and the `twist_*` family (military 99, speedboat 15, cargo 5, fishing_boat 1) needed per-image
  triage. **Update 2026-07-30, triage complete**: all 38 `twist_*` images opened and classified
  individually, see [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py) for the
  per-image verdict and reasons. 32 of 38 are genuine aerial content (carrier strike groups and
  container terminals shot from aircraft/drone, small craft from directly above); 6 are not and
  were dropped: 2 sea-level/horizon shots (from another vessel, not aerial), 2 elevated-shore
  shots (a Venice canal from a building balcony; a riverbank phone photo watermarked "SHOT ON
  OPPO"), 1 hillside scenic overlook, and 1 **CGI render** of a frigate. Net clean aerial
  instances from `twist_*`: military +92, speedboat +3, cargo +4, fishing_boat +1 (dropped:
  military 7, speedboat 12, cargo 1). Combined with the other clean families, `Marina 2`'s total
  verified aerial contribution is speedboat +27, fishing_boat +9, military +92, cargo +4, all
  folded into the sufficiency table below. **License caveat**: tagged CC BY 4.0 by the uploader,
  but the content
  demonstrably includes third-party-watermarked forum scrapes, YouTube video frames, and synthetic
  renders, so that tag can't be cited unqualified in the Technical Brief — same mislabeling pattern
  as `kapal`'s Google Earth screenshots. This is the clearest case yet of why this project opens
  sample images instead of trusting `data.yaml`: the raw counts alone would have suggested ~99
  aerial military and 39 aerial speedboat instances, and both numbers are wrong.
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

### Class remapping: definitive mapping (recounted 2026-07-29)

None of the raw class sets match the mandatory taxonomy verbatim. Earlier versions of this doc
described the remapping in prose only, and it drifted: the cargo bucket's own breakdown text
didn't even sum to its stated total (9079 vs. the 5293 once shown here). The table below is a
full recount straight from every dataset's `data.yaml` + label files (not carried over from
old notes), so it's now the single source of truth for which raw class goes where. It also
splits every number by `frontal-view`/`aerial-view`, see
[Data sufficiency](#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split) for
why that split matters.

**Two sources' mappings now live in code, not in this table.** `VHRShips` is mapped by the `MAP`
dict in [scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py) (34 raw classes -> 7 buckets,
with the deliberate exclusions documented in that file and in
[TODO.md](TODO.md)'s VHRShips section), and its output `converted-vhrships-yolo/` is already
written in the canonical taxonomy order, so it needs no remapping at merge time. When the unified
merge script gets written, that script's class order is the one to match:
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

Aerial-view contributions now come from two datasets: `VESSELimg.v4i` (Container, Chemical,
Passenger-RoRo — the bulk of the volume) and, as of 2026-07-30, `kapal.v1i` in small amounts
(cargo, speedboat, tanker, fishing_boat, military — the first non-zero aerial evidence for four
of those five). No other aerial source on disk contributes a mandatory-class instance, see the
verification finding above for what got checked and ruled out this round (`Simulator 2`,
`IR boats`, both confirmed frontal despite promising class lists).

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
| container_ship | 1327 | 6115 | 7442 | good total, but weakest **frontal** count of any class |
| tanker | 2092 | 1694 | 3786 | **aerial floor CLEARED 2026-07-30** by the VHRShips conversion |
| cargo | 8733 | 2512 | 11245 | **aerial floor CLEARED 2026-07-30** by the VHRShips conversion |
| passenger_ferry | 5261 | 2466 | 7727 | good in both views independently |
| yacht | 3027 | 1621 | 4648 | **aerial floor CLEARED 2026-07-30**, went from literal zero to comfortably over floor in one step |
| speedboat | 3427 | 66 | 3493 | good total, aerial **thinnest class now, ~13x under floor** |
| fishing_boat | 3472 | 56 | 3528 | good total, aerial **still ~15x under floor** |
| military | 5412 | 726 | 6138 | good total, aerial **close to floor, ~75-275 short** depending on how strict the target is read |
| local vs. foreign military | 0 | 0 | 0 | still unsolved, doesn't exist in any off-the-shelf dataset |

**Update 2026-07-30 (VHRShips converted): the aerial gap is now mostly closed.** Converting
VHRShips to YOLO ([scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py)) added 7,440 aerial
instances in one step and cleared the floor outright for `yacht` (0 -> 1621, the class that had
been at literal zero across three sourcing sessions), `cargo` and `tanker` (321 -> 1694).
**Update 2026-07-30, `Marina 2` fully triaged** (see the finding above and
[scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py)) added a further military
+92, speedboat +3, fishing_boat +1, cargo +4 of genuinely aerial, hand-verified content on top of
that. `military` now sits at 726 (was 18 at the start of the day), close to the floor but not
over it. **Two classes remain clearly open in aerial view**: `speedboat` (66, thinnest, VHRShips
had nothing mappable to it and `Marina 2` only added a handful) and `fishing_boat` (56, VHRShips's
own `fishing` class is only 37 instances). Both need new sourcing, not more triage of what's
already on disk, everything usable in the currently-downloaded sources has now been counted.

Every pooled total clears the ~800-1000 floor, which is why earlier passes over this table (in
both this doc and TODO.md) called the class taxonomy fully solved, that reasoning was hiding the
per-view problem above and the same trap is worth avoiding again now that most of it is fixed:
`speedboat` and `fishing_boat` are still genuinely unfit for aerial input.
`yacht` remains at literal zero aerial instances, no dataset found yet contributes any. `tanker`'s
aerial count (321) is still well under floor even though its pooled total looks fine. Only
`passenger_ferry` and `container_ship` have real coverage in both views independently. See the
finding above ("Aggregate sufficiency numbers were hiding a severe frontal/aerial imbalance")
for what's driving this and why it matters for this project's mission specifically (frontal
**and** aerial/satellite classification is a stated requirement, not a nice-to-have).

Tanker's *pooled* fix took six targeted sourcing attempts (`Ship2` +101, `MyBoats` +14, MVDD13 a
dead end, a round of Roboflow searches that found nothing new, `kapal-penumpang-done` which
turned out single-class, then finally `roboflow-Tanker.v1i` + `roboflow-VESSELimg.v4i` +
`roboflow-Vessel.v2i` which together added 1924, see findings above). Same pattern as yacht:
multi-class datasets with tanker as a minor category gave diminishing returns until a dedicated
tanker-heavy dataset solved the pooled number in one shot. That fix did not touch the aerial
gap though, only `VESSELimg.v4i` (aerial) contributed, and only 307 instances.

"Local vs. foreign military" remains unsolved for a different reason, it's a labeling/classifier
problem, not a volume problem (see "Military classification approach" in [TODO.md](TODO.md)).

Verdict: **sufficient to start training a frontal-view detector, and now also an aerial-view
detector for 5 of 8 classes** (container_ship, tanker, cargo, passenger_ferry, yacht). `military`
is close but not quite there. Not yet sufficient to trust it on aerial input for `speedboat` or
`fishing_boat` specifically, those two are the remaining sourcing target, and every
already-downloaded source has now been triaged for them, further gains need new data. Three things block a
Top-10-competitive submission regardless of further pooled-volume growth:

- **Aerial-view coverage for cargo, yacht, speedboat, fishing_boat, military (and to a lesser
  extent tanker).** Whether this gets fixed by sourcing more aerial-specific datasets, or
  accepted as a documented model limitation in the Technical Brief, is a decision the team needs
  to make, not something to discover after Phase 2's hidden stress test.

- **Local vs. foreign military** doesn't exist in any public detection dataset. Build it by
  hand from reference photos (RMN/APMM public releases for "local", foreign navy press photos
  for "foreign"), and treat it as a second-stage classifier on cropped military detections, not
  a class in the primary detector.
- **Validation must match the actual test domain.** Recall > 90% is measured against the
  Qualifier Video Clip, not Roboflow's held-out split. Once that clip is available, pull frames
  from it and hand-label a slice as the real validation set.

Stack and repo conventions live in [CLAUDE.md](CLAUDE.md).

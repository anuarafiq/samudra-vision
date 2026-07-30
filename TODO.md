# TODO: Samudra Vision (SEDIC 2026 Visual Track)

Task board for the 4-person team. Background/context lives in [GUIDELINES.md](GUIDELINES.md),
this file is just the task list. Check items off as they land.

## HANDOFF: source aerial-view data for 5 zero-coverage classes (active task)

Current state: a 2026-07-29 recount split every mandatory class's instance count by
frontal-view vs. aerial-view (not just pooled), see
[GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split)
for the full table and
[GUIDELINES.md](GUIDELINES.md#class-remapping-definitive-mapping-recounted-2026-07-29) for the
exact per-dataset mapping. Result: **`cargo`, `yacht`, `speedboat`, `fishing_boat`, and
`military` have essentially zero aerial-view instances** across all sourced datasets. `tanker`
has some (originally 307) but is well under floor. `container_ship` (5535) and `passenger_ferry`
(1703) are fine in aerial already, don't need more. This matters because the mission statement
explicitly requires **both frontal-view and aerial/satellite-view** classification, and Phase
2's hidden verification stress test could use either angle.

**Update 2026-07-30 (start of day)**: a tiny dataset (`kapal.v1i`, see below) landed the
first-ever non-zero aerial evidence for `cargo` (+58), `speedboat` (+39), `military` (+18), and
`fishing_boat` (+10), and added +14 to `tanker`. Small, but real and verified.

**Update 2026-07-30 (final state for the day) — READ THIS FIRST**: `VHRShips` has now been
**converted and integrated** ([scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py) ->
`datasets/converted-vhrships-yolo/`, 7,440 aerial instances), and `Marina 2` was downloaded and
**fully triaged**, including the `twist_*` family
([scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py)). Current **actual** aerial
counts, everything already downloaded is now accounted for:

| Bucket | Aerial | Status |
|---|---|---|
| `cargo` | 2512 | floor cleared |
| `tanker` | 1694 | floor cleared |
| `yacht` | 1621 | floor cleared (was literal zero) |
| `military` | 726 | close, ~75-275 short depending on how strict the floor is read |
| `speedboat` | 66 | **still critically thin, thinnest class** |
| `fishing_boat` | 56 | **still critically thin** |

So the original framing of this handoff — "5 classes with essentially zero aerial coverage" — is
now down to **2 open classes, both severe**: `speedboat` and `fishing_boat`. Six passes of
searching suggest this is a genuine data-scarcity issue rather than something more searching
fixes (see the conclusion further down). `military` no longer has a bounded already-available
task left to run against it, both VHRShips and Marina 2 have been fully mined, closing the
remaining gap needs new sourcing like the other two.

Don't treat the remaining classes as solved, and don't let the cleared pooled totals hide
them — that exact mistake is what this handoff was created to correct in the first place.

**Target, per class, not a ratio**: ~800-1000 aerial-view instances is the floor (same rule of
thumb used everywhere else in this project). Don't chase matching frontal's volume, frontal
classes have 3000-8700+ instances each, that's not the bar, ~800-1000 aerial instances per class
is. Rough total ask: ~5000 new aerial instances across the 5 thin/zero classes plus tanker's
remaining gap, not 25,000+.

**Already ruled out for this, don't re-check:**
1. `roboflow-MASATI.v1i.yolov11` (aerial, still in `datasets/`) — generic `ship`/`multi`/`water`
   classes, no vessel-type info at all, contributes 0 to any bucket
2. `roboflow-maritime.v3i.yolov11` (aerial, still in `datasets/`) — SAR/rescue labels
   (person-in-water, jetski, drowning), not ship types
3. `kaggle-satellite` (aerial, still in `datasets/`) — image classification only, no bounding
   boxes, can't be used for detection training as-is
4. `kaggle-MASATI-V2` and `kaggle-SeaDronesSee` — already deleted from disk (2026-07-29), see
   [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan). Former had a
   non-commercial-only license (blocks competition use regardless of relevance), latter was
   SAR/rescue like `maritime.v3i` and was the single largest non-contributing dataset on disk
   (9.3GB). Don't re-download either.
5. **xView** (DIUx/NGA, 60 classes incl. a `maritime vessel` parent with 9 vessel-type children:
   motorboat, sailboat, tugboat, barge, fishing vessel, ferry, yacht, container ship, oil
   tanker) — exactly the taxonomy we want, but confirmed via the official
   [xviewdataset.org/terms.html](https://xviewdataset.org/terms.html) it's **CC BY-NC-SA 4.0**,
   non-commercial, same category of blocker that got `kaggle-MASATI-V2` deleted. Several Roboflow
   re-uploads exist (`sbr-wlxsx/devided-xview-dataset`, 10k images) tagged "CC BY 4.0" on the
   page, but that's the uploader mislabeling someone else's copyrighted satellite imagery, not a
   real relicense, the source terms still govern. Don't chase further xView forks on Roboflow.
6. **FAIR1M** (Gaofen Challenge / ISPRS, ship category has 9 sub-types: liquid cargo ship, dry
   cargo ship, fishing vessel, cruise ship, tugboat, engineering vessel, motorboat, warship,
   other-ship) — also exactly the taxonomy we want, also blocked: **CC BY-NC-SA 3.0**,
   "academic purpose only" per the official license text. Roboflow mirrors exist
   (`project-7sgmz/fair1m-train`) but are tiny (56 images) and inherit the same restriction
   regardless of what license tag the mirror shows.
7. **ShipRSImageNet** ([zzndream/ShipRSImageNet](https://github.com/zzndream/ShipRSImageNet) on
   GitHub, 50 fine-grained categories incl. Cargo, Container Ship, Oil Tanker, Fishing Vessel,
   Ferry, Motorboat, Yacht, plus ~15 warship hull-class types like Arleigh Burke DD/Ticonderoga) —
   this is almost certainly why an earlier session's notes called this family "already ruled
   out" without saying why (see the tanker findings in
   [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan)): the GitHub README states
   images "can be used for academic purposes only, but any commercial use is prohibited."
   Same trap as xView: it's re-uploaded under 10+ different names on Roboflow
   (`HiResShipDetection`, `ShipRSImageNet_V1`, `Marine Vessels Detection`, `ShipRSI`, etc, all
   the same satellite-derived class list) tagged MIT/Apache/unspecified by different uploaders,
   none of which overrides the source license. Don't chase any Roboflow project with the
   `AOE`/`Arleigh Burke DD`/`Atago DD` class signature, it's this dataset.
8. **DOTA** and **NWPU VHR-10** — checked, both confirmed to only have a single generic `ship`
   class (no cargo/tanker/yacht/military breakdown), same tier as MASATI. NWPU VHR-10 is also
   tiny for ships specifically (302 instances total). Not worth downloading for this task
   regardless of license. **Correction (2026-07-30, checked HuggingFace mirrors)**: an earlier
   version of this note called DOTA "permissively licensed" without actually checking, that was
   wrong — `isaaccorley/dota` on HF states DOTA is **CC-BY-NC-4.0, "academic purposes only, any
   commercial use is prohibited."** Doesn't change the verdict (single generic `ship` class makes
   it useless for this task either way), but don't repeat the "DOTA is CC-licensed" claim
   elsewhere, it isn't. NWPU VHR-10's license (CC BY 4.0) was independently confirmed earlier and
   still stands.
9. **xView on HuggingFace, checked 2026-07-30**: `HichTala/xview` is a public, ungated parquet
   mirror (20,881 train images, full 60-class taxonomy confirmed directly from its
   `dataset_info` metadata, including all 9 maritime vessel classes: Motorboat, Sailboat,
   Tugboat, Barge, Fishing Vessel, Ferry, **Yacht**, Container Ship, Oil Tanker). This removes
   the friction of registering at the DIUx portal, the data is one `load_dataset()` call away.
   **Doesn't change the verdict**: the imagery is still NGA/DigitalGlobe satellite data under
   the CC BY-NC-SA 4.0 terms set at xviewdataset.org, an unlicensed/untagged HF re-upload doesn't
   relicense it, same principle as every other mirror checked this project. Two other HF mirrors
   were also checked: `Honaker/xview_dataset` returned 401 (gated, respects the original
   registration requirement), `CDAO/xview-subset-classification` is gone (404, dataset removed
   or renamed since the web search that surfaced it). Bottom line: easier to *get* than before,
   still blocked to *use*, per this project's established non-commercial-license policy.

**Pattern worth remembering**: every major fine-grained aerial/satellite ship-*type* benchmark
found so far (xView, FAIR1M, ShipRSImageNet, and now confirmed DOTA too even though DOTA's `ship`
class isn't fine-grained) is non-commercially licensed at the source, and that doesn't change no
matter which mirror (Roboflow, Kaggle, HuggingFace) you find it on. `VESSELimg.v4i` remains the
only large, freely-licensed, per-type aerial dataset found across three full sourcing sessions
now. This isn't proof none exists, but it explains why broad search keeps surfacing the same
handful of academic benchmarks under different names and why they keep being dead ends.

**What actually worked, use as the template**: `roboflow-VESSELimg.v4i.yolov11`, the only
dataset currently providing any aerial-view mandatory-class coverage at all. It's drone
footage of a real port (Eurecat Robotics, Valencia Port, Spain, EU H2020 PASSport project),
purpose-built to label individual vessel types from an elevated angle, not a generic
ship-detection or SAR dataset with "boat" as an afterthought class. The lesson from both this
and the tanker search: a dataset purpose-built for vessel-type classification from the air beats
a big generic aerial dataset with vessel-type as a minor/absent category, every time. Look for
more datasets in this mold: drone/UAV port surveillance, harbor traffic monitoring, marina
overhead footage (good for yacht/speedboat), fishing fleet aerial surveys, naval base drone
footage (for military, mind operational-security-sensitive sources).

**SOLVED AND CONVERTED (2026-07-30): `VHRShips`.**
[Kızılkaya, Alganci & Sertel, ISPRS Int. J. Geo-Info. 2022](https://doi.org/10.3390/ijgi11080445),
GitHub: [radres333/VHRShips](https://github.com/radres333/VHRShips). Google Earth satellite
imagery, 500m eye altitude, MIT license, genuinely aerial (confirmed by opening real sample
images, not just reading the label list, multiple times over). **The data extraction is fully
solved and verified. The YOLO conversion script has not been written yet** — that's the actual
next action, see below.

**What's on disk right now**: `datasets/kaggle-VHRShips/` — 6,312 images in `_mergedData/`
(matches the paper's total exactly), plus `metaFileV8.mat` (original), `metaFileV8.csv`
(**broken, see below, do not use**), and `metaFileV8.json` (**clean, use this one**). Two other
copies (`github-VHRShips`, `roboflow-vhrships4.v4i.yolov11`) were downloaded, found fully
redundant (same images, worse or subset labels — `vhrships4`'s Roboflow export from the paper's
own institution collapsed everything to `nc: 1, names: ['ship']`, same trap as
`korean_marine_object`), and **deleted**. Don't re-download them.

**Extraction history, both attempts, so no one repeats the failed one:**
1. First try: `writetable(metaFileV8, 'metaFileV8.csv')` in MATLAB, then parse with Python. This
   **produced a corrupted file** — 1,823 of 6,312 rows (29%) had a different column count than
   the header. Root cause: some `metaFileV8` columns hold variable-length nested arrays (one
   cell = a matrix of N ships × 4 bbox coords), and `writetable` doesn't safely flatten those to
   CSV, it spills extra unquoted values into the row, shifting every later column. A naive
   column-index parse of this CSV silently produces wrong class-instance counts, this happened
   once already, catch it if it happens again: check `len(row) == len(header)` for every row
   before trusting anything.
2. Second try, worked cleanly:
   ```matlab
   load('metaFileV8.mat');
   fid = fopen('metaFileV8.json', 'w');
   fprintf(fid, '%s', jsonencode(metaFileV8));
   fclose(fid);
   ```
   `metaFileV8.json` is a JSON array of 6,312 objects, each with `imageName`, `allBoundingBoxes`,
   `allLabels` (both lists, index-paired — `allLabels[i]` describes the box at
   `allBoundingBoxes[i]`), plus one redundant per-class field per class (e.g. `yatch_18: [x,y,w,h]`
   or `[]`) that can be ignored, `allLabels`+`allBoundingBoxes` alone is sufficient and simpler.
   **Verified correct**: total instances parsed = 11,337, exact match to the GitHub README's
   stated total, zero label/bbox count mismatches across all 6,312 records. `allBoundingBoxes` is
   `[x, y, w, h]` (a flat 4-list) for a single ship, or a list of `[x, y, w, h]` lists for
   multiple ships in one image, handle both shapes.

**Real per-class instance counts, extracted and verified** (note: raw VHRShips class names have
typos/British-vs-project-spelling in the original MATLAB code, e.g. `yatch` not `yacht`,
`passanger` not `passenger`, `auxilary` not `auxiliary` — these are literal, not typos on my
part, keep them when referencing the source):

| Our bucket | VHRShips raw classes | Instances |
|---|---|---|
| `yacht` | yatch | **1,621** |
| `cargo` | generalCargo+oreCarrier+bulkCarrier+coaster | **2,450** |
| `tanker` | tanker+oilTanker | **1,373** |
| `military` | destroyer+patrolForce+frigate+cruiser+submarine+landing+aircraft+auxilary | **616** |
| `fishing_boat` | fishing | 37 (thin even here) |
| `speedboat` | — nothing safely mappable | 0 |
| container_ship (bonus) | container | 580 |
| passenger_ferry (bonus) | ferry+roro+passanger+smallPassanger | 763 |

Excluded/not mapped (ambiguous, out of taxonomy, or visually disqualified, consistent with
existing project precedent elsewhere): `smallBoat` (944 instances — **visually spot-checked, do
NOT map to speedboat**, crops showed a barge/work-vessel and rafted utility boats, not
recreational speedboats, this was tempting because of its size but the pixels don't support it),
`tug`, `bargePontoon`, `undefined`, `dredgerReclamation`, `dredging`, `serviceCraft`, `offshore`,
`floatingDock`, `coastGuard` (paramilitary, not military, same exclusion as `VESSELimg`'s
`CoastGuard` class elsewhere), `drill`, `lpg` (tanker-adjacent, same "open decision, not yet
made" status as the existing LNG/gas-carrier question in
[GUIDELINES.md](GUIDELINES.md#class-remapping-definitive-mapping-recounted-2026-07-29)), `other`.

Visual spot-checks done on `yatch` (2 samples: a small sailboat and a fast powerboat throwing
wake, both legitimately within a broad "recreational craft" reading of yacht) and `auxilary`
(1 sample: a real gray naval support vessel). All checked out.

**Net effect if converted**: closes `yacht`, `cargo`, `tanker` outright (all comfortably past the
~800-1000 floor once added to existing aerial counts). Gets `military` most of the way there
(~634 total after adding kapal's 18) but not fully. Barely moves `fishing_boat` (~47 total).
Does nothing for `speedboat` (stays at kapal's 39).

**DONE 2026-07-30 — conversion built, run, and verified. See
[scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py).** Output is
`datasets/converted-vhrships-yolo/` (3500/437/439 images, 7,440 mapped instances of 11,337 total,
`nc: 8` in the canonical taxonomy order from [GUIDELINES.md](GUIDELINES.md#mandatory-class-taxonomy)).
Realized per-class: container_ship 580, tanker 1373, cargo 2450, passenger_ferry 763, yacht 1621,
speedboat 0, fishing_boat 37, military 616 — exactly matching the projected table above, so the
"known-but-not-yet-realized upside" is now actual. Aerial floors **cleared** for `yacht`, `cargo`
and `tanker`; `military` at 634 total is close but under; `speedboat`/`fishing_boat` still open.
Verification done: the script has a `--check` mode that asserts total-parsed (11,337) and all eight
per-bucket counts and exits nonzero if the JSON or mapping ever drifts; one crop per class was cut
from the *written* YOLO labels and opened (naval vessel, container ship with visible containers,
tanker with deck manifold, yacht, fishing boat — all correctly and tightly framed); image/label
pairing is exact in all three splits with zero broken symlinks and zero empty label files; and
`ultralytics.data.utils.check_det_dataset` loads the `data.yaml` cleanly.
Implementation notes worth knowing: raw JSON labels carry a numeric suffix (`yatch_18`, not
`yatch`) which the mapping strips; bbox `[x,y,w,h]` was confirmed **top-left origin** (not centre)
by cropping and eyeballing a bulk carrier before trusting it; images are symlinked rather than
copied since `_mergedData` is 2.3GB; the split is a plain seeded random 80/10/10 per the spec below,
with the known ceiling that VHRShips filename prefixes (`BV`, `BK`, `SA`...) are harbour codes so
same-port images can straddle splits — group-split by prefix if val/test ever look flattering.

**Original spec, kept for reference**: write the JSON → YOLO conversion script. Straightforward
now that the data is clean: for each of the 6,312 records, zip `allLabels` with `allBoundingBoxes`
(normalizing the flat-vs-nested shape), map each raw class name through the table above (skip
unmapped classes silently, an image can have both a mapped and unmapped ship, only label the
mapped one), convert `[x,y,w,h]` pixel coords to YOLO-normalized `class_id x_center y_center w h`
(image dimensions are 720×1280 or similar per-image, read actual dimensions from each image file
rather than assuming, some may have been resized), write one `.txt` label file per image that has
at least one mapped instance, do a train/val/test split (VHRShips's own paper split isn't
recoverable from what's on disk anymore, `testList.mat`'s split assignment was in the now-deleted
`github-VHRShips`, just do a fresh random 80/10/10 split, fixed seed). Per
[CLAUDE.md](CLAUDE.md#working-with-datasets), output goes in a **new top-level directory**
(something like `datasets/converted-vhrships-yolo/`), not nested inside `aerial-view/` or
`frontal-view/` and not restructuring `kaggle-VHRShips/` itself. After conversion, spot-check a
handful of the generated crops against their assigned YOLO label the same way every other
dataset in this project gets verified, then fold the real numbers into
[GUIDELINES.md](GUIDELINES.md)'s dataset inventory, class-remapping table, and sufficiency table.
(The user deferred this twice while more sourcing was tried, then greenlit it on 2026-07-30 once
the search had clearly hit diminishing returns. All of the above is now implemented; every
requirement in this spec was met, including reading per-image dimensions rather than assuming
1280×720 — they all turned out to be 1280×720 in practice, but the script doesn't rely on it.)

**Standing traps, already bit us multiple times this project, see
[CLAUDE.md](CLAUDE.md#working-with-datasets):**
- A Roboflow project's live overview page (class list, image count) does not necessarily match
  the frozen downloadable version. Always check the actual downloaded `data.yaml` and label
  files directly, never trust the page. Hit 3x so far on unrelated datasets
  (`korean_marine_object`, `ships9000`, `kapal-penumpang-done`).
- Some Roboflow projects show real images but have "0 dataset versions", raw uploads never
  packaged into a downloadable split (hit with `gdut-fbja3/vessel-wqp7q` and
  `-i1wmc/vessel-yhmsk` during the tanker search, and `holi-atkgu/ir-boats` during this search).
  Not usable without forking + generating a version yourself on Roboflow.
- A Roboflow project's displayed license (MIT/Apache/CC BY/Public Domain) reflects whatever the
  *uploader* typed in, not necessarily the license of the underlying imagery, especially for
  re-uploads of known academic benchmarks. Hit repeatedly this search: xView and ShipRSImageNet
  forks tagged permissively on Roboflow despite the source datasets being non-commercial-only.
  Check the original paper/dataset page's license, not just the Roboflow mirror's badge, whenever
  a Roboflow project looks like a re-upload of a named academic dataset rather than an original
  collection.
- Check license before investing time in any candidate. `kaggle-MASATI-V2`'s "non-profit
  research/educational only" license got it deleted after already being on disk, wasted effort.

**Session update (2026-07-29, second pass): DOTA/xView/NWPU VHR-10/FAIR1M now checked (see ruled
out list above), HuggingFace/Zenodo now checked, wider Roboflow class-combo search done. No new
dataset added to disk this pass, nothing found cleared both the "real aerial vessel-type data"
bar and the "actually downloadable now" bar, but one strong lead needs a manual follow-up:**

- **Try this first: email the Marship-OBB9 authors.** [YOLO-UAVShip: An Effective Method and
  Dataset for Multi-View Ship Detection in UAV Images](https://www.mdpi.com/2072-4292/17/17/3119)
  (Li et al., *Remote Sensing* 2025, published 2025-09-08) is exactly the template we're looking
  for: real DJI M3E / DJI Mini 4 Pro drone
  footage shot at 40-400m altitude over real high-traffic maritime zones, purpose-built for
  UAV ship-*type* detection (not SAR, not generic). 11,268 images, 18,632 instances, 9
  categories: **fishing boat, general cargo vessel, bulk carrier, tug, passenger ships, coast
  guard ship, oil tanker, container ships, other ships**. That's a direct hit on `fishing_boat`,
  `cargo` (general cargo + bulk carrier), and `tanker` (oil tanker), our three thinnest aerial
  buckets after `military`/`yacht`/`speedboat`. Per-category instance counts are in the paper's
  Table 2 but didn't extract as text (it's a rendered table/figure), check that once we have the
  PDF. **The catch**: no public download link, the paper's Data Availability Statement says
  "available from the corresponding author upon reasonable request." Corresponding author is
  Chao Yuan, Aerospace Information Research Institute, Chinese Academy of Sciences. Worth an
  email (mention academic/student-competition use), but don't count on a response before any
  internal deadline, and license/redistribution terms for competition use aren't stated, ask
  about that explicitly. Doesn't help `yacht`, `speedboat`, or `military` even if it comes
  through, those still need a separate source.
- Roboflow class-combo search (`class:yacht`, `class:speedboat`, plus "drone"/"aerial ship"
  phrase searches) done this pass. Found a few small/marginal candidates.
  **Update 2026-07-30: `kapal`, `IR boats`, and `Simulator 2` downloaded and verified by opening
  actual sample images**, not just reading `data.yaml` — same standard as everywhere else in this
  project, and it mattered: two of the three had misleadingly good class lists.
  - **`indra-pratama/kapal-v4ern` ("kapal") confirmed genuinely aerial** — real mix of Google
    Earth satellite screenshots and FPV drone footage (flight telemetry HUD visible). Recounted
    from labels: 171 instances, 139 map to the taxonomy — cargo +58, speedboat +39, warships
    (->`military`) +18, tanker +14, nelayan (->`fishing_boat`) +10. Small, but it's the first
    non-zero aerial evidence ever found for `cargo`/`speedboat`/`military`/`fishing_boat`. Now
    living in `datasets/aerial-view/`, folded into
    [GUIDELINES.md](GUIDELINES.md#class-remapping-definitive-mapping-recounted-2026-07-29)'s
    mapping and the sufficiency table. **License caveat**: tagged "Public Domain" by the
    uploader, but part of it is literally Google Earth screenshots, and Google's satellite
    imagery isn't public domain regardless of what a re-uploader claims — flag this before citing
    the license in the Technical Brief, same mislabeling pattern as xView/ShipRSImageNet.
  - **`holi-atkgu/ir-boats` ("IR boats") confirmed NOT aerial** — forked and a version generated
    (workspace now shows `anuar-afiq`, so the "0 dataset versions" trap is cleared, all 8,398
    images downloadable), but sample thermal images show a sea-level horizon near the bottom of
    frame, camera mounted near water height. Frontal, not aerial, despite the good class list
    (yacht 325, container ship 692, warship 2547, 26,632 instances total). Moved to
    `datasets/frontal-view/`, not integrated into any bucket, all its classes are already
    sufficient in frontal view. Kept on disk as a documented option for thermal/night-vision
    robustness work later, nothing more.
  - **`simulator-flvry/simulator-2` ("Simulator 2") confirmed NOT aerial** — had the best-looking
    class list of anything found this session (16 classes: warship, speedboat, fishing boat,
    bulk carrier, cargo ship, aircraft carrier, submarine, 32,409 instances, 21,699 images, CC BY
    4.0), and it's real photos not a rendered game despite the name (that suspicion was wrong).
    But it's a merged aggregate: sample images included a Venice gondola stock photo, harbor
    PTZ/CCTV cameras with on-screen timestamps (same elevated-shore-camera style as
    `SeaShips7000`, already classified frontal in this project), and naval PR photos shot from
    dock-level or another ship. Moved to `datasets/frontal-view/`, not integrated, every class it
    covers is already well past the frontal floor, and merging an unvetted aggregate risks
    near-duplicate content with sources already on disk.
  - `whutboat/boatds` ("BoatDS", CC BY 4.0, 2,273 images, 3 real dataset versions, classes
    incl. `cargo ship`/`fishing boat`/`speedboat`/`tanker`/`warship`) — not downloaded, but
    preview thumbnails on the Roboflow page show close-up frontal/surface-level shots (boat hull
    side-on), same conclusion expected as `IR boats`/`Simulator 2`. Skip for this task.
  - "Marina 2" (by tetianas, 1.05k images) — still not checked, deprioritized after `Simulator 2`
    (which had a near-identical profile: great class list, turned out frontal) came back
    negative. Only worth a look if the leads above dry up.
  - **Lesson that held up under an actual test**: a promising class list is not evidence of
    camera angle, confirmed twice more this pass. Any further Roboflow candidate needs someone to
    open 3-5 real sample images before it's trusted, `data.yaml` alone isn't enough.
- **`universe.roboflow.com/search?q=aerial+maritime` checked 2026-07-30, don't re-run.** Surfaces
  two families, both dead ends (verified via preview thumbnails, not just class lists):
  - The well-known **"Aerial Maritime" tutorial dataset** (Jacob Solawetz, ~2020, MIT) and its
    ~10 re-uploads (UC Merced, DEMM, George Brown College, yolov5/yolov8 forks, etc.) — genuinely
    aerial drone footage, but generic `boat`/`car`/`dock`/`jetski`/`lift` only, no vessel-type
    breakdown. Same tier as MASATI.
  - The **"seaobjects" / "mcship" / "ship-data01" family**, new this session, looked promising
    (large, CC BY 4.0, civilian/warship-type classes): `seaobjects-2rxjz/8_final_corrected3`
    (18,664 images, `civilianship`/`warship`/`fishing boat`/`passenger-vessel`/`tug boat`/`rig`),
    `maritime-cumkb/mcship` (7,881 images, `civilianship`/`warship` only), `admobnattapong-rt/
    ship-data01` (4,603 images, `civilianship`/`warship1`/`warship2`/`fishing ship`/`cruise`/
    `container`/`tug boat`, re-uploaded again as "maritime" by School and "holder" by Zane).
    Preview thumbnails on all three show water-level/dockside shots (a warship and container
    ship viewed from a pier, a cruise ship shot from a promenade railing) — frontal, same style
    as `mcship`'s sibling `Mcship_database_lite_v1`. `ship-data01` additionally looks like a
    low-provenance scraped mix (personal/candid photos of people on a boat turned up in the
    preview grid alongside ship shots), skip that one on data-quality grounds even if it were
    aerial. None of this family is worth downloading for this task.
- Military-specific OSINT drone/satellite footage of warships: not searched this pass, still
  open. `Marship-OBB9` above has a `coast guard ship` class which is adjacent but not the same
  as `military` (paramilitary/civilian law enforcement vessel, not a naval combatant), doesn't
  solve this bucket even if the email request comes through.
- HuggingFace/Zenodo checked this pass, nothing usable found: `ABOships` (Zenodo, referenced by
  the Member A checklist's "Sailboat detector" item below) confirmed **shore/onboard-camera
  footage from a moving waterbus, not aerial**, CC BY 4.0 — fine for frontal volume, doesn't
  touch this handoff. Zenodo's "Aerial Vessels Detection Dataset" (Cyprus UAV coastal survey) and
  "MOBDrone" are real drone footage but both generic `person`/`ship`/`boat` only, same tier as
  MASATI, no vessel-type breakdown.

**Session update (2026-07-30, third pass): targeted search specifically for `fishing_boat` and
`speedboat` in aerial view, since those are the two buckets VHRShips barely touches. Conclusion:
likely a genuine structural data-scarcity problem, not a search-effort gap, see below.**

- **IUU (illegal/unreported/unregulated) fishing detection datasets checked** — this looked like
  the most promising angle (fisheries-monitoring is an active satellite-imagery research area
  specifically about finding fishing vessels from above). `xView3-SAR` is the main public one.
  **Wrong modality**: it's Synthetic Aperture Radar, not optical/camera imagery — SAR looks
  nothing like camera footage (grayscale radar backscatter, not RGB), can't be used to train a
  detector that has to work on the qualifier video clip's camera footage. This rules out the
  entire SAR-based fishing-detection research area for this project, not just this one dataset.
- **Marina/recreational-boat-specific search**: nothing new beyond datasets already ruled out
  (`Aerial Maritime` family, `Aerial Vessels Detection Dataset`, `MOBDrone`), all generic
  `person`/`boat`/`ship` only.
- **`FGSD`** (Google Earth, 43 classes, warship/carrier/submarine/civil-ship hierarchy) — checked,
  only 5,634 instances across 43 classes (2,612 images), thinner per-class than VHRShips even
  before mapping. Same research lineage as `ShipRSImageNet` (small Google-Earth-sourced academic
  benchmark, warship-hull-type-heavy). Not checked for license, but given every dataset in this
  lineage found so far has been NC-restricted, and the per-class volume is worse than what we
  already have, not worth the download.
- **`FGSCR-42`** (Google Earth + DOTA/HRSC2016/NWPU VHR-10 sourced, 9,320 images, 42 categories)
  — checked the GitHub repo directly, **no class list and no license statement anywhere in the
  README**, that absence is itself a caution flag per this project's established rule (check
  license before investing time). Download is gated behind Baidu Pan (password-protected Chinese
  cloud storage). Not pursued further given the missing license and access friction.
- **Curated satellite-ship-dataset directory checked**: [jasonmanesis/Satellite-Imagery-Datasets-Containing-Ships](https://github.com/jasonmanesis/Satellite-Imagery-Datasets-Containing-Ships)
  on GitHub lists ~25 datasets. Cross-checked against everything already known: most are SAR
  (wrong modality, e.g. `SSDD`, `OpenSARShip`, `SRSDD-v1.0`, `HRSID`) or generic single-`ship`-class
  optical (`HRSC2016`, `DOTA`, `Airbus Ship Detection`, `DIOR`). Nothing new survived this cross-
  check beyond `FGSD`/`FGSCR-42` above, both already ruled out.
- **Seagull dataset** ([VisLab, Instituto Superior Técnico, Lisbon](https://vislab.isr.tecnico.ulisboa.pt/seagull-dataset/))
  — genuinely aerial (fixed-wing UAV flying over the sea), 7 object types including **cargo
  ships and patrol boats** as distinct categories. Real lead, but same access model as
  `Marship-OBB9`: **available upon request only**, no public download, email the VisLab team via
  their site if pursuing. Doesn't include `fishing_boat`/`speedboat`/`yacht` even if it comes
  through, would only help `military`/`cargo` further.
- **`MASS-LSVD`** (Dalian Maritime University, 64,263 image pairs, "first-view" dataset) —
  checked, confirmed **NOT aerial**: it's footage from a camera mounted on the mast of a real
  training/research ship (`Xinhongzhuan`), i.e. onboard/first-person camera, not overhead. Same
  category as `ABOships`, frontal-volume only, doesn't touch this handoff.
- **`datnguyentien204/Seaship7000` on HuggingFace, checked 2026-07-30** — just a raw
  `SeaShips(7000).zip` re-upload, no README, no license, no class list on the HF page. This is
  almost certainly the same well-known 2018 Shao et al. shore-CCTV dataset already on disk as
  `frontal-view/roboflow-Seaships7000.v1i.yolov11` (6 real classes, CC BY 4.0, already YOLO
  format). Skipped without downloading, redundant and frontal by strong prior + naming match,
  not worth 1.23GB to confirm what's already extremely well-established in the literature.
- **`roboflow-Sea Ships.v3-resized_640_2_classes.yolov11` downloaded, checked, deleted
  2026-07-30** — workspace `maritime-cumkb` (same org as `mcship`, already ruled out). `data.yaml`
  was `nc: 2, names: ['boat', 'ship']`, generic. Opened an actual image: confirmed shore-based PTZ
  harbor camera (visible timestamp overlay, camera ID text), same filename numbering convention
  (`000001`, `000003`...) as `Seaships7000.v1i.yolov11` already on disk, i.e. the same underlying
  SeaShips source video, just re-exported with only 2 generic classes instead of the existing
  6-class version already on disk. Strictly redundant and worse. Deleted (353M reclaimed).

**Session update (2026-07-30, fourth pass): checked 4 specific candidates (3 Kaggle + DOTA v2).
All four are dead ends — three are re-confirmations of already-documented dead ends found under a
different name/mirror, one is new but hits the same generic-class problem.**

- **`apollo2506/satellite-imagery-of-ships`** — confirmed this is the same dataset already on
  disk and ruled out as `kaggle-satellite` (4000 80x80px chips, 1000 ship/3000 no-ship, plus 8
  full scenes; classification only, no bounding boxes, see
  [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan)). No new information. Don't
  re-download.
- **`louisaberdeen/masati-v2`** — confirmed via the official source
  ([iuii.ua.es/datasets/masati](https://www.iuii.ua.es/datasets/masati/)) this is the same
  underlying data already downloaded and deleted from disk as `kaggle-MASATI-V2`. License is
  literally "shared only for non-profit research or educational purposes" (blocks competition
  use, same reason it was deleted before), and the 7 classes (land, coast, sea, ship, multi,
  coast-ship, detail) are scene-level, not vessel-type — would contribute 0 to any bucket even if
  the license weren't a blocker. Don't re-download.
- **`siddharthkumarsah/ships-in-aerial-images`** — new candidate, not previously checked. 26,900
  images, YOLO format, **CC BY-SA 4.0** (genuinely permissive, unlike the two above). But
  single-class (`ship` only — the dataset's own description says "curated to include images of
  only one class"), same tier as `roboflow-MASATI.v1i` and DOTA, no vessel-type breakdown at all.
  Confirmed via the live Kaggle page (data card + description), not just a mirror's blurb.
  Doesn't help any of the 5 target classes regardless of the good license. Not worth downloading
  for this task.
- **DOTA v2** ([docs.ultralytics.com/datasets/obb/dota-v2](https://docs.ultralytics.com/datasets/obb/dota-v2/))
  — re-confirms the existing DOTA entry in the ruled-out list above (#8): still CC BY-NC
  (academic-only per the official DOTA site), still a single generic `ship` category, v2's only
  addition over v1 is two unrelated categories (`airport`, `helipad`). Nothing changed by
  checking the v2-specific docs page, same verdict as before.

**Pattern held again**: every dataset that surfaces on a general "ships in aerial/satellite
imagery" search and isn't purpose-built for vessel-*type* classification turns out to be
single-class or scene-classification-only, no exception found yet across four sourcing sessions.
The three sources that actually contributed vessel-type buckets so far (`VESSELimg.v4i`,
`kapal.v1i`, `VHRShips`) were all purpose-built for exactly that, not generic "is there a ship"
datasets. Any further search should filter for that up front rather than opening every
generic-sounding "ships in satellite imagery" result.

**Session update (2026-07-30, fifth pass): open-ended re-search specifically for
`fishing_boat`/`speedboat`, per explicit user instruction to keep looking after the fourth pass
came up empty. Checked ~10 more candidates across Kaggle, arXiv/Zenodo, and a fresh Roboflow
`class:speedboat`/`class:"fishing boat"` sweep (300+ listings scanned). Still empty — every new
lead fails the same two ways already established, no third failure mode found.**

- **`SentinelBlue` (Kaggle, Rupankar Majumdar)** — new, UAV-based, but confirmed Search & Rescue
  category like `SeaDronesSee`/`maritime.v3i`: classes are person/boat/jetski/buoy/
  emergency_appliance (the page says 5 classes; the actual bundled `data.yaml` says `nc: 3,
  names: [person, vessel, emergency_appliance]` — yet another live-page-vs-downloadable-export
  mismatch, filed under the standing trap). `vessel`/`boat` generic either way. Skip.
- **`AFO` (Aerial dataset of floating objects, Gąsienica-Józkowy et al.)** — genuinely aerial UAV
  footage, 6 classes incl. `sailboat`/`kayak`, but **CC BY-NC-SA 3.0** (non-commercial, same
  blocker tier as xView/FAIR1M/MASATI-V2) and no fishing_boat/speedboat-specific class anyway.
  Skip on both grounds.
- **`AMP2026`** (arXiv, marine robotics multi-platform tracking/mapping dataset) — real aerial+surface+
  underwater synchronized data, but the paper itself says semantic annotations are future work,
  i.e. no class labels exist yet to train on. Not usable now.
- **AeroSTREAM / "Aerial Maritime Vessel Detection and Identification" (arXiv 2507.07153)** and
  **the recreational-boat-tracking ScienceDirect paper** — checked for a released dataset behind
  either paper, found none (the latter's actual Zenodo release, `10.5281/zenodo.10046341`, turned
  out to be Sentinel-2 satellite imagery, single generic `boat` class, 10m/px resolution — vessels
  are only a few pixels wide at that resolution, too coarse for type classification regardless of
  class count. Its companion HF model repo, `mayrajeo/marine-vessel-detection-yolov8`, confirmed
  same source data, same single-class limitation).
- **Roboflow `class:speedboat` and `class:"fishing boat"` searches redone fresh** (250-300+
  results each) — the overwhelming majority are re-exports of the same handful of underlying
  datasets already known (SeaShips7000's 6-class combo appears under 15+ different
  workspace/project names; the `sailboat/canoe/cargo ship/.../warship` 11-class combo, source
  unclear but repeats identically across a dozen projects, is worth naming as a pattern but wasn't
  individually re-verified). Two specific checks worth recording:
  - **DLUVA's "Ship Vessel Identification" family** (incl. `..._2_SD_ImagePrompt` variants,
    "Sea Vessels Dataset" by Yehonatan Engel) — confirmed this is the exact same dataset already
    on disk as `roboflow-Sea Vessels Dataset.v2-sea_vessels_v2.yolov11`
    ([GUIDELINES.md](GUIDELINES.md#dataset-inventory) line 58), same 8 classes, same per-class
    counts, already classified **frontal**. No new information; the "_SD_ImagePrompt" variants
    weren't independently opened since the base dataset is already a known quantity.
  - **`ADRS_Ship_Detection` (Mario López, 168 images, CC BY 4.0)** — genuinely novel class list
    (`Patera`, `narco-boat` — Spanish coast-guard/interdiction vocabulary, not seen elsewhere in
    this search), opened the actual preview image: a shore-level ship-spotting photo of a "CMA
    CGM" container ship, same frontal style as everything else in this family. Confirmed frontal,
    skip.
  - **Marina 2 (tetianas)** — not opened this pass (site navigation to the specific project kept
    404ing). **Now downloaded and fully verified in the sixth pass below — partial win, see
    there.**

**Pattern now confirmed across five separate sourcing sessions, no exceptions found**: every
aerial/satellite dataset with real fishing_boat or speedboat coverage either (a) doesn't exist
publicly, (b) is NC-licensed, or (c) turns out frontal/shore-level on inspection despite a
promising class list. The two access-request leads (`Marship-OBB9`, `Seagull`) and the untested
`Marina 2` are the only remaining unexplored threads; everything else in reach of open search has
now been checked at least once.

**Session update (2026-07-30, sixth pass): `Marina 2` downloaded and verified (partial win, first
clean aerial `speedboat`/`fishing_boat` data beyond `kapal`), plus 3 user-supplied links checked.**

- **`roboflow-Marina 2.yolov11` — DOWNLOADED, VERIFIED, PARTIAL WIN.** Now on disk (999 images,
  1,744 instances, CC BY 4.0, forked into workspace `anuar-afiq` so the version is generated and
  stable). `data.yaml` is `nc: 6, names: ['cargo ship','fishing boat','military ship','passenger
  ship','speedboat','swimmer']`. Raw recount from label files: cargo 405, fishing_boat 9,
  military 99, passenger 208, speedboat 39, swimmer 984.
  **Critically, this is a mixed-provenance aggregate and the raw counts are NOT usable as-is.**
  Broke the labels down by source-filename family and opened real images from each:
  | Filename family | Instances | Verdict (opened actual images) |
  |---|---|---|
  | `0XXXXX` numeric | cargo 400, passenger 208 | **Frontal, redundant.** Chinese harbour shore-CCTV with burned-in timestamp + camera ID, same style and numbering as `Seaships7000.v1i` already on disk. Almost certainly the same SeaShips source. Contributes nothing. |
  | `DJI_*` | speedboat 21 | **Genuinely aerial**, clean. True top-down DJI drone shots over a lakeside marina. |
  | `Screenshot from 2024-05-29 *` | fishing_boat 8 | **Genuinely aerial**, clean. Top-down drone footage of a longboat (YouTube player chrome visible in-frame, title "Amazing Drone shot of Boat on lake HD"). |
  | `IPgiBNOPCjQ-*` | speedboat 3 | **Genuinely aerial**, clean. Aerial video frames of a speedboat on open sea (filename is a YouTube video ID). |
  | `twist_*` | military 99, speedboat 15, cargo 5, fishing_boat 1 | **MIXED, do not bulk-trust.** 6 samples opened: 3 real aerial (2 carrier-strike-group photos from aircraft, 1 motorboat from above), 2 elevated-shore-not-aerial (a Venice canal shot from a building balcony; a phone photo from a riverbank watermarked "SHOT ON OPPO"), and **1 CGI render** of a frigate (flat lighting, no crew, artificial water — synthetic, not a photo). One aerial sample was watermarked "uploaded @ DefenceTalk.com", i.e. scraped from a forum. Low-provenance scrape, same data-quality profile that got `ship-data01` skipped earlier. |
  | swimmer families | swimmer 984 | Out of taxonomy, ignore. |
  **Net clean, verified aerial gain: `speedboat` +24, `fishing_boat` +8.** Modest, but it's the
  first aerial data for either class from a source other than `kapal.v1i`, and it roughly doubles
  aerial `speedboat` (39 -> 63) and `fishing_boat` (10 -> 18). The `twist_` family's ~99 aerial-ish
  `military` instances are a **potential** further +50ish but need per-image hand triage first
  (drop the elevated-shore and CGI ones); not counted anywhere until that's done. Folded the clean
  numbers into [GUIDELINES.md](GUIDELINES.md)'s inventory and sufficiency table; the `twist_`
  triage is left as an open sub-task.
  **License caveat for the Technical Brief**: tagged CC BY 4.0, but the actual content includes
  scraped forum images with third-party watermarks, YouTube video frames, and a CGI render. Same
  mislabeling pattern as `kapal`'s Google Earth screenshots — do not cite "CC BY 4.0" for this one
  without qualification.
- **`cloud.cs.uni-tuebingen.de/.../ZZxX65FGnQ8zjBP`** — this is the official University of Tübingen
  host for **SeaDronesSee Object Detection v2**, i.e. a newer version of a dataset already ruled
  out *and already deleted from disk* (see ruled-out item 4 above). Confirmed v2's classes are
  still SAR-oriented and vessel-generic: `swimmer`, `boat`, `jetski`, `life_saving_appliances`,
  `buoy` (14,227 images, 5-260m altitude). Genuinely aerial, but a single generic `boat` class with
  no vessel-type breakdown — same tier as MASATI. **Don't re-download**, the v1 deletion decision
  applies unchanged to v2.
- **`zenodo.org/records/10892012`** — **wrong link, not a maritime dataset at all.** This record is
  "ToneTwist AFx Dataset - External: Marshall JVM410H - Channel: OD1" by Miklánek: a 2.8GB *audio*
  dataset of guitar-amplifier recordings, CC BY-NC 4.0. Presumably a paste error. If there was a
  specific Zenodo maritime record intended here, the correct DOI/ID still needs to be supplied.
- **`zenodo.org/records/16588542`** — "Roboflow Maritime & Aerial Objects Dataset (44 Classes:
  Boats, Drones, Driftwood) – Integrated Edition v1.0" (Wu, ZHENG-ZHE; published 2025-07-30;
  CC BY 4.0). **Not downloaded, deprioritized, but not conclusively ruled out.** It is explicitly
  *"a compilation [that] repackages 44 publicly available datasets from Roboflow Universe without
  modifying their content"* — i.e. by construction it contains no new imagery, only Roboflow
  Universe projects, which is exactly the surface six passes of this handoff have already swept.
  Two concrete problems: (1) it's a single **16.7GB `.7z`** with the per-source
  `AGGREGATED_README.md` (the only place the 44 titles/authors/licenses are listed) *inside* the
  archive, so there is no way to see what's in it without committing the full download — the
  Zenodo landing page lists neither the 44 class names nor the 44 source projects; (2) as an
  unvetted merged aggregate it carries the same near-duplicate risk that got `Simulator 2`
  rejected, and would need the same per-family provenance triage that `Marina 2` just required,
  at ~17x the size. Worth a download only if a session has the disk headroom and appetite to
  triage it; if so, the first action is extracting `AGGREGATED_README.md` alone and diffing its 44
  source URLs against this project's already-checked list before touching the imagery.

**Conclusion on `fishing_boat`/`speedboat` specifically**: after this session's full search
(Roboflow Universe across many query angles, HuggingFace, Zenodo, Kaggle, a curated GitHub
directory of ~25 satellite-ship datasets, and the major academic fine-grained benchmarks), large
commercial and military vessels are well represented in aerial/satellite ship-type datasets;
small recreational and fishing craft are not, they're either absent, generic-`boat`-only, or
present in single digits (VHRShips's own `fishing` class: 37 instances out of 11,337 total,
despite the dataset otherwise being rich and well-labeled). This looks like a genuine
structural gap in the available data, plausibly because small vessels are a few pixels at typical
satellite/high-altitude resolution and rarely justify dedicated labeling effort, rather than a
search-effort failure. Two access-request leads remain open (`Marship-OBB9` — has `fishing boat`;
`Seagull` — has neither `fishing_boat` nor `speedboat` specifically) but both require an email and
neither is a sure thing. If both come up empty, per the fallback below, documenting this as a
known model limitation in the Technical Brief is the honest path, not further open-ended search.

**How to record progress**: same convention as every other dataset in this project — download,
verify the class list against the actual `data.yaml` + label files (not the live page), spot
check a sample image or two if a class name is ambiguous (e.g. is "Chemical" really a tanker,
not a lab hazard icon — this was checked for `VESSELimg` already, don't re-check that one).
Update [GUIDELINES.md](GUIDELINES.md)'s dataset inventory table, the class-remapping mapping
section, the findings list, and the sufficiency table. Update this file's Member A checklist.
If sourcing keeps failing after a real attempt, the fallback is documenting the aerial gap as a
known model limitation in the Technical Brief, not silently shipping it undocumented, that's an
acceptable outcome, going quiet about it is not.

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
      `roboflow-Vessel.v2i` downloaded and folded in, +1924 instances (475 -> 2399 pooled).
      Full record (dead-end Roboflow slugs, per-dataset breakdown, untried leads) in
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan). Note: this fixed the
      *pooled* number only, see the frontal/aerial split item below, tanker's aerial count
      (307) is still thin.
- [x] ~~Build the class-remapping table + decide handling for ambiguous/unmapped classes
      (`Carrier`, `ore carrier`, `Merchant Ship`, `Patrol Boat`, `Sails Boat`, `Tugboat`,
      `canoe`, `kayak`, `sailboat`, `engineering ship`, `Datasense@CRAS`'s
      `small boat`/`uncategorized`, etc.)~~ definitive mapping written 2026-07-29, recounted
      directly from label files (not carried over from old prose, which had drifted), see
      [GUIDELINES.md](GUIDELINES.md#class-remapping-definitive-mapping-recounted-2026-07-29).
      Still open: turning the table into an actual merge script (see below), and the one
      explicitly-flagged undecided call (`LNG`/`gas carriers` -> `tanker` or not)
- [ ] Decide what to do with `kaggle-satellite` (classification-only, no boxes) and
      `roboflow-maritime.v3i` (SAR-oriented, people/jetski labels not ship types) — both still
      on disk, neither contributes to the mandatory taxonomy. (`kaggle-MASATI-V2` and
      `kaggle-SeaDronesSee`, the two other generic/unusable sources, were already deleted, see
      [GUIDELINES.md](GUIDELINES.md#findings-that-change-the-plan))
- [ ] Source aerial-view data for `speedboat`/`fishing_boat` — **see the HANDOFF section at
      the top of this file**, active task. `VHRShips` (converted) and `Marina 2` (fully triaged,
      including `twist_*`) cleared `yacht`/`cargo`/`tanker` and got `military` close; those two
      classes are the only ones left, at 66 and 56 aerial instances respectively. Everything
      currently on disk has been mined, this now genuinely needs new sourcing, not more triage of
      existing downloads. One lead (`Marship-OBB9`) waiting on an author email reply.
- [x] ~~Hand-triage `roboflow-Marina 2.yolov11`'s `twist_*` filename family image by image~~ done
      2026-07-30, see [scripts/marina2_twist_triage.py](scripts/marina2_twist_triage.py) for the
      per-image verdict. All 38 images opened, not just the earlier 6-image sample: 32 were
      genuine aerial (much better than the sample's ~50% suggested), 6 were not (2 sea-level/
      near-water shots, 2 elevated-shore, 1 hillside overlook, 1 CGI render). Net clean gain:
      military +92, speedboat +3, fishing_boat +1, cargo +4. Aerial `military` now 726
      (was 18 at the start of 2026-07-30). Folded into
      [GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split).
- [ ] Decide where `roboflow-Marina 2.yolov11` should live on disk: it's currently at `datasets/`
      top level rather than under `aerial-view/` or `frontal-view/`, which is defensible since
      it's genuinely both (that's the whole reason it needed triage), but it's the only source
      folder not sorted into a view directory. Minor, not blocking anything.
- [ ] Write the frame-extraction + `.mat`-to-YOLO conversion script for Singapore Maritime
      Dataset (`smd-VIS_Onboard`, `smd-VIS_Onshore`, `smd-NIR`), currently raw video + MATLAB
      ground truth, unusable as-is
- [ ] Merge all remapped/converted sources into one unified YOLO dataset (single `data.yaml`,
      consistent train/val/test folders). **Canonical class order is now fixed** by
      [scripts/vhrships_to_yolo.py](scripts/vhrships_to_yolo.py), match it rather than inventing a
      new one: `container_ship, tanker, cargo, passenger_ferry, yacht, speedboat, fishing_boat,
      military`. `converted-vhrships-yolo/` is already in that order and can be merged as-is;
      that script is also the working template for the remaining per-source conversions (symlink
      images instead of copying, assert known-good counts, verify crops before trusting output)
- [ ] Dataset split sanity check: make sure frames extracted from the same source video don't
      end up split across train and val (data leakage)
- [x] ~~Augmentation/oversampling pass for the thin *pooled* classes (`tanker`, `yacht`)~~ no
      longer needed, both solved by sourcing dedicated datasets instead. Pooled counts aren't
      the whole story though, see the aerial-view sourcing item above, see
      [GUIDELINES.md](GUIDELINES.md#data-sufficiency-checked-2026-07-29-recounted-with-frontalaerial-split)
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

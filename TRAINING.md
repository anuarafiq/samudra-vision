# Training handoff

Everything needed to train the detector without reading the rest of the repo. If you want
the full picture: [GUIDELINES.md](GUIDELINES.md) has the competition brief and the dataset
inventory, [TODO.md](TODO.md) has the task board.

## What you're getting

`samudra-merged-yolo.tar`, 4.41GB. If it arrived split into parts (FAT32 caps files at
4GB), reassemble first:

```bash
cat samudra-merged-yolo.tar.part.* > samudra-merged-yolo.tar
```

Unpack anywhere:

```bash
tar -xf samudra-merged-yolo.tar -C /wherever/
```

You get a standard YOLO layout. `data.yaml` uses relative paths, so it works from wherever
you unpack it.

`samudra-merged-yolo.tar` is the only thing training needs. If you also received
`output.z01`-`output.z08` / `output.zip`, that's the full raw `datasets/` folder (all ~19
source datasets plus intermediates, ~29GB), included on request. It's not needed to run
the commands below, only for re-deriving the merge or auditing a source dataset directly.

```
merged-yolo/
├── data.yaml          nc: 8
├── train/  images/ 27,428   labels/ 27,428
├── val/    images/  3,802   labels/  3,802
└── test/   images/  3,633   labels/  3,633
```

**34,863 images, 57,398 boxes.** Class order is fixed, don't change it:

```
container_ship, tanker, cargo, passenger_ferry, yacht, speedboat, fishing_boat, military
```

| class | train | val | test | total |
|---|---|---|---|---|
| container_ship | 6,175 | 1,274 | 945 | 8,394 |
| tanker | 3,315 | 449 | 234 | 3,998 |
| cargo | 8,998 | 640 | 1,607 | 11,245 |
| passenger_ferry | 7,357 | 1,403 | 839 | 9,599 |
| yacht | 3,573 | 560 | 515 | 4,648 |
| speedboat | 3,259 | 713 | 721 | 4,693 |
| fishing_boat | 6,995 | 505 | 797 | 8,297 |
| military | 5,645 | 524 | 355 | 6,524 |

`ultralytics` silently drops 15 exact-duplicate box rows at load, so it will report 57,383.
That's expected, not a bug.

## The one number that matters

**Military recall must exceed 0.90.** It's a hard pass/fail gate for Phase 1, not a target.
Everything else is diagnostic. Report per-class precision/recall/mAP, but lead with military
recall.

## Commands

```bash
pip install ultralytics
```

```bash
yolo detect train data=/path/to/merged-yolo/data.yaml model=yolo11s.pt \
  epochs=100 imgsz=640 batch=8 workers=8 device=0 patience=15 \
  project=runs name=baseline
```

**`batch=8` is deliberate.** The RTX 4050 is a laptop GPU with **6GB VRAM**, and `yolo11s`
at 640px with `batch=16` will probably OOM. If it runs fine, raise it. Watch `nvidia-smi`
during the first epoch to see the headroom. If it OOMs, drop to `batch=4` before reducing
`imgsz`, since shrinking images hurts small and distant vessels most, and those are the
hard cases.

AMP is on by default on CUDA and roughly halves memory. Leave it on.

Then get the per-class table:

```bash
yolo detect val data=/path/to/merged-yolo/data.yaml model=runs/baseline/weights/best.pt
```

[scripts/colab_baseline.py](scripts/colab_baseline.py) does the same thing and prints the
military-recall verdict directly. It also carries Colab cells if you'd rather use a free T4.

## Things that will confuse you if nobody warns you

**Per-class val proportions are uneven, from 5.7% to 15.2%.** `cargo` has 640 val instances
out of 11,245 total; `passenger_ferry` has 1,403. `fishing_boat` has only 505. Low val mAP
on `cargo` or `fishing_boat` early on is more likely thin validation sampling than a real
model problem. Don't chase it.

This is deliberate. Each source dataset's own train/val/test split was preserved rather than
reshuffled, because ~19 sources reshuffled under one seed risks leaking near-duplicate images
across the split boundary. **Please don't re-split the data.** If it genuinely needs fixing,
it has to be a source-grouped stratified split, never a naive global shuffle.

**`warshipv4` is 44.8% byte-identical duplicates** and supplies 60% of military images. All
of it sits in `train`, so val/test metrics are unaffected and there's no leakage. It acts as
roughly 2× oversampling of `military`. Leave it alone for the baseline. If military recall
comes in comfortably above 0.90, deduping it is a reasonable follow-up experiment; if recall
is marginal, that oversampling may be helping.

**~2% of training images are grayscale with CRT-style preprocessing** (from a source tagged
`boatsdetection`), train-only. Possibly harmless, possibly mild noise. Worth an A/B later,
not worth acting on now.

**`speedboat` includes a capped subsample of a `motorboat` class** from another source. A
known quality caveat carried over deliberately.

## What to send back

1. `results.csv` and the final per-class table
2. **Military recall**, called out explicitly
3. The confusion matrix. We specifically want to know what `military` gets confused with
4. Inference speed (ms/image, and which GPU), since Phase 2 needs a live real time demo
5. Your exact config, so the run can be reproduced

## Don'ts

- Don't re-split or reshuffle (leakage, see above)
- Don't change the class order or `nc`
- Don't hand-edit anything under the dataset folder; it's generated by
  [scripts/merge_dataset.py](scripts/merge_dataset.py) and gets regenerated
- Don't commit weights, `runs/`, or the dataset; all gitignored already

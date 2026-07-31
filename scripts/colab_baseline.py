"""Baseline training, sized for a Colab T4 / local RTX 4050 rather than this repo's Mac.

Paste the cells below into Colab, or run this file directly on any CUDA box that already
has the dataset unpacked:

    uv run python scripts/colab_baseline.py --data /path/to/merged-yolo/data.yaml

Why not train on the Mac: measured 2026-07-31 on an M-series/16GB machine, `yolo11s` at
640px needs ~57 min/epoch on MPS (batch 8, workers 2), so 30 epochs is ~28h. The same run
on a T4 is roughly 2-4h. Numbers for the record, all at imgsz=640:

    yolo11n  batch 8  workers 2  MPS   2.36GB  2.5 it/s   ~23 min/epoch
    yolo11s  batch 8  workers 2  MPS   4.32GB  1.0 it/s   ~57 min/epoch
    yolo11s  batch16  workers 8  MPS   THRASHES -- ~11 min per *batch*, ~310h/epoch

That last row is the trap: 16GB of unified memory is shared between CPU and the MPS
backend, and 8 dataloader workers each buffering 640px batches pushes it into swap.
On CUDA the worker count is far less dangerous because GPU memory is separate --
`workers=8, batch=16` is fine on a T4, and that is what this script defaults to.

The dataset is symlinks into per-source folders, so it is NOT portable as-is. Materialise
before transferring, which is what the tar in the Colab cell below assumes:

    tar -chf merged-yolo.tar -C datasets merged-yolo     # -h dereferences symlinks

------------------------------------------------------------------------------------
COLAB CELLS
------------------------------------------------------------------------------------
# 1. GPU check -- if this says None, Runtime > Change runtime type > T4 GPU
!nvidia-smi

# 2. Mount Drive and unpack (upload merged-yolo.tar to Drive once, reuse every session)
from google.colab import drive; drive.mount('/content/drive')
!tar -xf "/content/drive/MyDrive/samudra-merged-yolo.tar" -C /content/
!ls /content/merged-yolo

# 3. Install
!pip -q install ultralytics

# 4. Train
!yolo detect train data=/content/merged-yolo/data.yaml model=yolo11s.pt \
    epochs=30 imgsz=640 batch=16 workers=8 device=0 patience=10 \
    project=/content/drive/MyDrive/samudra-runs name=baseline exist_ok=True

# 5. Per-class table (also written to results.csv by the run itself)
from ultralytics import YOLO
m = YOLO('/content/drive/MyDrive/samudra-runs/baseline/weights/best.pt')
m.val(data='/content/merged-yolo/data.yaml', split='val')
------------------------------------------------------------------------------------

Write `project=` to Drive as above. A Colab runtime can be reclaimed at any time, and a
run that only exists on local disk dies with it -- the same way the first Mac attempt died
with its parent process.

What to read off the result: per-class precision/recall/mAP, and **`military` recall
specifically** -- >90% on military/threat classes is the hard Phase 1 gate (GUIDELINES.md,
"Phase 1 submission package"). Everything else is diagnostic.
"""

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to merged-yolo/data.yaml")
    ap.add_argument("--model", default="yolo11s.pt")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--imgsz", type=int, default=640)
    # CUDA defaults. On MPS drop to batch 8 / workers 2 or it will swap -- see docstring.
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--device", default="0")
    ap.add_argument("--project", default="runs")
    ap.add_argument("--name", default="baseline")
    args = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                workers=args.workers, device=args.device, patience=10,
                project=args.project, name=args.name, exist_ok=True)

    metrics = model.val(data=args.data, split="val")

    names = model.names
    print(f"\n{'class':<18}{'P':>8}{'R':>8}{'mAP50':>9}{'mAP50-95':>10}")
    for i, c in enumerate(metrics.box.ap_class_index):
        p, r, ap50, ap = metrics.box.class_result(i)
        print(f"{names[c]:<18}{p:>8.3f}{r:>8.3f}{ap50:>9.3f}{ap:>10.3f}")

    # The one number that decides Phase 1 eligibility.
    mil = [i for i, c in enumerate(metrics.box.ap_class_index) if names[c] == "military"]
    if mil:
        recall = metrics.box.class_result(mil[0])[1]
        gate = "PASS" if recall > 0.90 else "BELOW GATE"
        print(f"\nmilitary recall = {recall:.3f}  ->  {gate} (Phase 1 requires >0.90)")


if __name__ == "__main__":
    main()

# Samudra Vision

Maritime object detection for **SEDIC 2026 Visual Track, Phase 1** (see [references/SEDIC2026-track2.pdf](references/SEDIC2026-track2.pdf)).

Detects and classifies vessels across frontal and aerial/satellite views, with mandatory
identification of military vessels and a bonus for distinguishing Malaysian vs. foreign
military assets.

See [GUIDELINES.md](GUIDELINES.md) for the full mission brief, class taxonomy, dataset
inventory, and open problems. See [TODO.md](TODO.md) for the team task board (Data, Model, GUI,
Report roles).

## Setup

```bash
uv sync
```

## Datasets

Not tracked in git (19GB+). Already downloaded under `datasets/frontal-view/` and
`datasets/aerial-view/`, see [GUIDELINES.md](GUIDELINES.md#dataset-inventory) for sources.

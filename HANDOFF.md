# Handoff - samudra-vision, dataset split sanity check - 2026-09-11 (CLOSED)

## Done
- **Dataset split sanity check, closed.** Found far more than the single Marina2 leak this task
  started with: cross-source duplicate photos (`MyBoats.v2i`/`Seaships7000.v1i` share exact CCTV
  frames, `vessel.v1i`/`Ship2.v1i`/`kapal-penumpang-done.v1i`/`Warship.v4i` share a stock-photo
  pool) on top of within-source video-frame leakage (`VESSELimg.v4i`, `Seaships7000.v1i`,
  `Yacht Detection.v2`, `Buoys and Boats.v3i`'s `buoy_b_2_`/`youtube-` frames). Two
  filename-pattern candidates checked and ruled out as false positives before touching anything:
  `converted-vhrships-yolo` and `Sea Vessels Dataset.v2` are per-instance catalog numbers, not
  video frames.
- Built [scripts/check_split_leakage.py](scripts/check_split_leakage.py) (detector, writes
  nothing) and [scripts/split_overrides.py](scripts/split_overrides.py) (the fix, a union-find
  over confirmed leak groups, consulted by `merge_dataset.py`). Re-ran the full merge: 4,427 of
  34,862 images moved between splits, all 12 `--check` class-total assertions still pass exactly,
  0 broken symlinks, exact 1:1 image/label pairing, 0 stems shared across splits post-fix, and
  specific confirmed-leaking groups spot-checked to now land in one split.
- **val/test shrank ~45%** (9,701 → 5,329 combined instances) — a lot of what looked like
  held-out data was near-duplicates of train. New counts: train 31,211 img / 50,472 inst, val
  2,247 img / 3,924 inst, test 1,405 img / 3,002 inst.
- `Marina 2`'s original 21-frame leak: decided (b), accepted and documented rather than
  special-cased in code — two orders of magnitude smaller than what this pass actually fixed.
- TODO.md and GUIDELINES.md updated with the full findings, the fix mechanism, and an explicit
  flag that **Member B's existing transfer bundle (`~/samudra-merged-yolo.tar`) is now stale** —
  it was built before this fix, so any training/metrics already run from it used the old,
  leakier split.
- All committed work is `git status`-clean of this session's changes except staging/committing
  itself, which is the user's call, not done here.

## Next (for whoever picks this up, none of it blocking)
1. Tell Member B directly (not just TODO.md) that the transfer bundle is stale and any run from
   it needs redoing from the regenerated `datasets/merged-yolo/`.
2. Not exhaustively checked: `Warship.v4i`, `typesofships.v6i`, `kapal.v1i`,
   `ship detection.v2i`, `Tanker.v1i`, and `Ship2.v1i`/`vessel.v1i`/`MyBoats.v2i`'s own-internal
   numeric sequences were deliberately NOT given the within-source video-session treatment (no
   independent confirmation they're continuous recordings rather than per-instance catalogs, and
   guessing wrong here is exactly what went wrong with VHRShips/Sea Vessels). If per-class
   metrics on these look off, this is the first place to look.
3. No other open item from this task. `datasets/` changes are gitignored by design (re-run
   `scripts/merge_dataset.py` to reproduce); only the three script/doc changes need committing,
   and only if the user asks for a commit.

## Remember
- `merge_dataset.py` no longer blindly trusts every source's own split — `split_overrides.py` now
  corrects specific, confirmed-leaking sources. It's still not a global reshuffle: unconfirmed
  sources are left as-is on purpose.
- `datasets/` is gitignored — check outputs stay local; the reusable scripts are the only
  artifacts that belong in git.

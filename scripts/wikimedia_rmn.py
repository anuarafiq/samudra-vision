"""Collect Royal Malaysian Navy reference photos from Wikimedia Commons.

Output: datasets/wikimedia-rmn/<hull_class>/*.jpg  +  datasets/wikimedia-rmn/credits.csv

Run:   uv run python scripts/wikimedia_rmn.py --list          (show what would be fetched)
       uv run python scripts/wikimedia_rmn.py                 (download)
       uv run python scripts/wikimedia_rmn.py --max-per-class 40

These are the "local" half of the local-vs-foreign military classifier (see TODO.md's
"Military classification approach"). Commons is used rather than a pre-built Roboflow set
because it's organised *by hull class* -- which is the label the silhouette approach needs --
and every file names its actual vessel, so "local" is verifiable instead of inferred.
SKN601DEMO was the alternative and was ruled out (see GUIDELINES.md).

Three things this handles that a manual download wouldn't:

1. **Per-file licensing.** Commons is not uniformly free. Each file carries its own licence,
   author and source, and the Technical Brief needs a citations section. Every download writes
   a `credits.csv` row; files whose licence isn't recognised as free are skipped, not fetched.
2. **Category recursion.** Photos live in per-ship categories nested 3-4 deep under the class
   category (`Lekiu class frigate` -> `30 Lekiu (ship, 1999)` -> files), not in the class
   category itself.
3. **Thumbnails, not originals.** Commons originals are frequently 20MP+. We ask for a
   1280px-wide render, which is plenty for training crops and ~50x smaller.

No API key is needed, but Wikimedia blocks generic user agents -- hence USER_AGENT below.
Be polite: this is a shared free service, so requests are serialised with a small delay.
"""

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "datasets" / "wikimedia-rmn"
API = "https://commons.wikimedia.org/w/api.php"

# Wikimedia requires a descriptive UA with contact info; generic ones get 403'd.
USER_AGENT = (
    "SamudraVision-SEDIC2026/0.1 (academic competition dataset; "
    "contact: anuarafiq2407@gmail.com)"
)

# RMN hull classes -> Commons category. Deliberately per-class rather than one blanket
# "Naval ships of Malaysia" walk, because the hull class *is* the training label.
CLASSES = {
    "kedah_opv": "Category:Kedah class offshore patrol vessels",
    "lekiu_frigate": "Category:Lekiu class frigate",
    "kasturi_corvette": "Category:Kasturi-class corvettes",
    "laksamana_corvette": "Category:Laksamana class corvette",
    "keris_lms": "Category:Keris class littoral mission ships",
    "gagah_training": "Category:Gagah Samudera class training ships",
    "scorpene_submarine": "Category:Submarines of Malaysia",
    "auxiliary": "Category:Auxiliary ships of Malaysia",
    "amphibious": "Category:Amphibious assault ships of Malaysia",
    "patrol": "Category:Patrol vessels of Malaysia",
    # Catch-all, listed last so the named-class folders claim their files first (see the
    # dedup in main()). Picks up RMN hulls that aren't filed under any class category.
    "other_rmn": "Category:Naval ships of Malaysia",
}

# Substrings marking a licence as free enough to redistribute with attribution.
# Anything not matching is skipped rather than guessed at -- the Brief has to state
# licences accurately, and a wrong claim is worse than a missing image.
FREE = ("cc0", "cc by", "cc-by", "public domain", "pd-", "gfdl", "attribution")
NONFREE = ("non-free", "fair use", "noncommercial", "non-commercial", "nc-", "nd-")

IMG_EXT = (".jpg", ".jpeg", ".png")


def fetch(url, tries=5):
    """GET with backoff. Commons returns 429 readily; a flat delay isn't enough because
    the limit is a moving window, so back off progressively and let it recover."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            time.sleep(2 ** attempt * 2)   # 2, 4, 8, 16s
    raise RuntimeError("unreachable")


def api(**params):
    params.setdefault("format", "json")
    params.setdefault("action", "query")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def members(cat, kind):
    """All category members of `kind` ('file' or 'subcat'), following continuations."""
    out, cont = [], None
    while True:
        kw = dict(list="categorymembers", cmtitle=cat, cmtype=kind, cmlimit=500)
        if cont:
            kw["cmcontinue"] = cont
        r = api(**kw)
        out += [m["title"] for m in r["query"]["categorymembers"]]
        cont = r.get("continue", {}).get("cmcontinue")
        if not cont:
            return out


def collect_files(root_cat, depth=4):
    """Files under a category, recursing into per-ship subcategories."""
    seen, files = set(), []
    def walk(cat, d):
        if cat in seen or d > depth:
            return
        seen.add(cat)
        files.extend(f for f in members(cat, "file") if f.lower().endswith(IMG_EXT))
        for sub in members(cat, "subcat"):
            walk(sub, d + 1)
    walk(root_cat, 0)
    return sorted(set(files))


def file_info(titles, width=1280):
    """-> {title: {url, licence, author, descriptionurl}} for up to 50 titles per call."""
    info = {}
    for i in range(0, len(titles), 50):
        r = api(titles="|".join(titles[i:i + 50]), prop="imageinfo",
                iiprop="url|extmetadata", iiurlwidth=width)
        for page in r.get("query", {}).get("pages", {}).values():
            ii = (page.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            meta = ii.get("extmetadata", {})
            def m(k):
                return re.sub(r"<[^>]+>", "", str(meta.get(k, {}).get("value", ""))).strip()
            info[page["title"]] = {
                "url": ii.get("thumburl") or ii.get("url", ""),
                "licence": m("LicenseShortName") or m("UsageTerms"),
                "author": m("Artist"),
                "page": ii.get("descriptionurl", ""),
            }
    return info


def is_free(licence):
    low = licence.lower()
    if any(b in low for b in NONFREE):
        return False
    return any(g in low for g in FREE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="show counts only, download nothing")
    ap.add_argument("--max-per-class", type=int, default=60)
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between downloads")
    args = ap.parse_args()

    # Categories overlap (a hull sits in its class category *and* the catch-all), so a file
    # is assigned to the first class that claims it. Without this the same photo would be
    # downloaded into two folders and count twice in the pooled "local" set.
    rows, plan, claimed = [], {}, set()
    for label, cat in CLASSES.items():
        titles = [t for t in collect_files(cat) if t not in claimed]
        claimed.update(titles)
        plan[label] = (cat, titles)
        print(f"{label:<22}{len(titles):>5} files  ({cat[9:]})")
    total = sum(len(t) for _, t in plan.values())
    print(f"{'TOTAL':<22}{total:>5} unique files across {len(plan)} categories")

    if args.list:
        print("\n--list: nothing downloaded")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    kept = skipped = 0
    for label, (cat, titles) in plan.items():
        d = OUT / label
        d.mkdir(exist_ok=True)
        info = file_info(titles)
        n = 0
        for title in titles:
            if n >= args.max_per_class:
                break
            meta = info.get(title)
            if not meta or not meta["url"]:
                continue
            if not is_free(meta["licence"]):
                skipped += 1
                continue
            name = re.sub(r"[^A-Za-z0-9._-]", "_", title[5:])
            dest = d / name
            if not dest.exists():
                try:
                    dest.write_bytes(fetch(meta["url"]))
                except Exception as e:
                    print(f"  !! {title[5:60]}: {e}")
                    continue
                time.sleep(args.delay)
            rows.append({"file": f"{label}/{name}", "hull_class": label,
                         "licence": meta["licence"], "author": meta["author"],
                         "source": meta["page"]})
            kept += 1
            n += 1
        print(f"  {label:<22}{n:>4} kept")

    with (OUT / "credits.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "hull_class", "licence", "author", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {kept} images + credits.csv -> {OUT.relative_to(REPO)}")
    print(f"skipped {skipped} files with unrecognised/non-free licences")


if __name__ == "__main__":
    main()

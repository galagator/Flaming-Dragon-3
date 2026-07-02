#!/usr/bin/env python3
"""Re-crop generated face references from fd3-actor-mapping.json.

Preserves manual uploads named *_manual_* and only deletes regenerated numeric crops
like Tony01.jpg / Erb_Dean03.jpg before writing fresh crops.
"""
import json
import os
import re
import sys
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
MAPPING_PATH = BASE / "fd3-actor-mapping.json"
PHOTOS_DIR = BASE
OUT_DIR = ROOT / "character-references"
OUT_DIR.mkdir(exist_ok=True)

PREFIX = {
    "Galen / Ji-lan": "Galen-Ji-lan",
    "Tony": "Tony",
    "Yake-oh": "Yake-oh",
    "Erb Dean": "Erb_Dean",
    "MAMA": "MAMA",
    "Trubble": "Trubble",
    "Slarth": "Slarth",
    "Zoh-baggo": "Zoh-baggo",
    "TK-Maxx": "TK-Maxx",
    "Jasmine": "Jasmine",
}

def prefix_for(char: str) -> str:
    return PREFIX.get(char, re.sub(r"[^A-Za-z0-9_-]+", "_", char.strip()))

def remove_generated_crops() -> int:
    removed = 0
    for prefix in PREFIX.values():
        for path in OUT_DIR.glob(f"{prefix}[0-9][0-9].jpg"):
            path.unlink()
            removed += 1
    return removed

def main() -> int:
    with MAPPING_PATH.open() as f:
        mapping = json.load(f)

    removed = remove_generated_crops()
    counters = {}
    total = 0
    expected = 0
    missing_photos = []
    skipped = 0

    for photo_key, markers in sorted(mapping.items()):
        photo_path = PHOTOS_DIR / f"{photo_key}.jpg"
        usable_markers = [m for m in markers if str(m.get("char", "")).strip() != "Not in film"]
        expected += len(usable_markers)
        if not photo_path.exists():
            if usable_markers:
                missing_photos.append(str(photo_path.name))
            continue

        try:
            with Image.open(photo_path) as img:
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                elif img.mode == "L":
                    img = img.convert("RGB")
                w, h = img.size

                for marker in usable_markers:
                    char = str(marker["char"]).strip()
                    prefix = prefix_for(char)
                    counters[char] = counters.get(char, 0) + 1
                    idx = counters[char]

                    cx = int(float(marker["x"]) / 100.0 * w)
                    cy = int(float(marker["y"]) / 100.0 * h)
                    crop_size = max(120, int(min(w, h) * 0.28))
                    crop_w, crop_h = crop_size, int(crop_size * 1.33)

                    x1 = max(0, cx - crop_w // 2)
                    y1 = max(0, cy - crop_h // 2)
                    x2, y2 = min(w, x1 + crop_w), min(h, y1 + crop_h)
                    if x2 - x1 < crop_w:
                        x1 = max(0, x2 - crop_w)
                    if y2 - y1 < crop_h:
                        y1 = max(0, y2 - crop_h)

                    crop = img.crop((x1, y1, x2, y2))
                    crop.save(OUT_DIR / f"{prefix}{idx:02d}.jpg", "JPEG", quality=92)
                    total += 1
        except Exception as exc:
            skipped += len(usable_markers)
            print(f"WARN failed {photo_path.name}: {exc}", file=sys.stderr)

    if missing_photos:
        print(f"WARN missing photos: {', '.join(missing_photos)}", file=sys.stderr)

    print(f"REMOVED={removed}")
    print(f"EXPECTED={expected}")
    print(f"SKIPPED={skipped}")
    print(f"TOTAL={total}")
    return 0 if total else 1

if __name__ == "__main__":
    raise SystemExit(main())

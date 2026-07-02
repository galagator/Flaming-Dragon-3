#!/usr/bin/env python3
"""
After the user tags footage faces in the tagger UI, this script reads
fd3-footage-tags.json, finds the face crop files, and copies them into
character-references/<Prefix>##.jpg using the per-character counter so
existing references are not overwritten.

Run from project root:
  /home/galagator/.hermes/venvs/fd3-frames/bin/python3 actor-photos-raw/copy_tagged_faces.py
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAGS = ROOT / "actor-photos-raw" / "fd3-footage-tags.json"
REF_DIR = ROOT / "character-references"

# Same map as server.js: refPrefix()
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

SKIP = {"Not in film", ""}


def next_index(prefix: str) -> int:
    """Return the next available NN for <prefix>NN.jpg (existing files)."""
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)(?:_manual.*)?\.(?:jpg|jpeg|png)$", re.IGNORECASE)
    max_n = 0
    for f in REF_DIR.iterdir():
        m = pattern.match(f.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def main() -> int:
    if not TAGS.exists():
        print(f"ERROR: {TAGS} not found — run the footage face tagger first.")
        return 1
    REF_DIR.mkdir(parents=True, exist_ok=True)

    tags = json.loads(TAGS.read_text())
    counts: dict[str, int] = {}
    next_idx: dict[str, int] = {c: next_index(p) for c, p in PREFIX.items()}
    written: list[str] = []
    skipped: list[str] = []

    for face_id, char in tags.items():
        char = (char or "").strip()
        if char in SKIP:
            skipped.append(f"{face_id} ({char or 'empty'})")
            continue
        prefix = PREFIX.get(char)
        if not prefix:
            print(f"  unknown char {char!r} on {face_id} — skipping")
            continue
        # face_id is "Scene_3/0" → crop path is scene-extract/faces/Scene_3/face_00000.png
        scene, num = face_id.split("/")
        crop = ROOT / "scene-extract" / "faces" / scene / f"face_{int(num):05d}.png"
        if not crop.exists():
            print(f"  missing crop: {crop}")
            continue
        idx = next_idx[char]
        next_idx[char] = idx + 1
        dest_name = f"{prefix}{idx:02d}.jpg"
        dest = REF_DIR / dest_name
        # Convert PNG → JPG; opencv not required if Pillow available
        try:
            from PIL import Image
            Image.open(crop).convert("RGB").save(dest, "JPEG", quality=92)
        except ImportError:
            # fallback: copy bytes if extension was jpg; for png we still need pillow
            print("  ERROR: Pillow required for PNG→JPG conversion")
            return 2
        counts[char] = counts.get(char, 0) + 1
        written.append(f"{dest_name} ← {face_id}")

    print(f"Wrote {len(written)} new references to {REF_DIR}/")
    for char, n in sorted(counts.items()):
        print(f"  {char:20s} +{n}  (now {next_idx[char] - 1} total)")
    print()
    print(f"Skipped {len(skipped)} 'Not in film'/empty tags")
    if written:
        print()
        print("Sample writes:")
        for line in written[:8]:
            print(f"  {line}")
        if len(written) > 8:
            print(f"  ... and {len(written) - 8} more")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

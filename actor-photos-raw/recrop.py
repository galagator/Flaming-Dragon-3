#!/usr/bin/env python3
"""Re-crop all face references from the mapping JSON."""
import json, os
from PIL import Image

base = os.path.dirname(os.path.abspath(__file__))
mapping_path = os.path.join(base, "fd3-actor-mapping.json")
photos_dir = base
out_dir = os.path.join(os.path.dirname(base), "character-references")
os.makedirs(out_dir, exist_ok=True)

with open(mapping_path) as f:
    mapping = json.load(f)

counters = {}
total = 0

for photo_key, markers in sorted(mapping.items()):
    photo_file = f"{photo_key}.jpg"
    photo_path = os.path.join(photos_dir, photo_file)
    if not os.path.exists(photo_path):
        continue

    img = Image.open(photo_path)
    if img.mode in ('P', 'RGBA'):
        img = img.convert('RGB')
    w, h = img.size

    for m in markers:
        char = m["char"]
        slug = char.replace(" / ", "-").replace(" ", "_").replace("/", "_")
        counters[char] = counters.get(char, 0) + 1
        idx = counters[char]

        cx = int(m["x"] / 100.0 * w)
        cy = int(m["y"] / 100.0 * h)
        crop_size = max(120, int(min(w, h) * 0.28))
        crop_w, crop_h = crop_size, int(crop_size * 1.33)

        x1 = max(0, cx - crop_w // 2)
        y1 = max(0, cy - crop_h // 2)
        x2, y2 = min(w, x1 + crop_w), min(h, y1 + crop_h)
        if x2 - x1 < crop_w: x1 = max(0, x2 - crop_w)
        if y2 - y1 < crop_h: y1 = max(0, y2 - crop_h)

        crop = img.crop((x1, y1, x2, y2))
        out_path = os.path.join(out_dir, f"{slug}{idx:02d}.jpg")
        crop.save(out_path, "JPEG", quality=92)
        total += 1

print(f"{total} crops")

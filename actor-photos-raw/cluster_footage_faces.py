#!/usr/bin/env python3
"""
Cluster the footage face crops by perceptual similarity.

Output: scene-extract/face_clusters.json
  {
    "clusters": [
      {
        "id": 0,
        "size": 12,
        "rep": "scene-extract/faces/Scene_3/face_00000.png",
        "members": ["scene-extract/faces/Scene_3/face_00000.png", ...]
      },
      ...
    ]
  }

This gives the tagger UI a "you tagged one, here are N visually similar
ones" affordance so the user can batch-tag common-looking faces (Tony's
glasses + white shirt, MAMA's floral blouse, Trubble's t-shirt + tats).
"""
from __future__ import annotations

import json
from pathlib import Path
import imagehash
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FACES_DIR = ROOT / "scene-extract" / "faces"
OUT = ROOT / "scene-extract" / "face_clusters.json"
HASH_SIZE = 12
SAME_FACE_DIST = 22  # perceptual hash distance for "same person" across angles/lighting
NEAR_FACE_DIST = 28  # unused; placeholder for future expansion


def main() -> int:
    crops = sorted(p for p in FACES_DIR.rglob("*.png") if p.is_file())
    print(f"Hashing {len(crops)} face crops…")
    hashes: dict[str, imagehash.ImageHash] = {}
    for p in crops:
        rel = str(p.relative_to(ROOT))
        try:
            hashes[rel] = imagehash.phash(Image.open(p), hash_size=HASH_SIZE)
        except Exception as e:
            print(f"  skip {rel}: {e}")
    print(f"  {len(hashes)} hashed")

    # Single-linkage clustering: a face joins a cluster if within SAME_FACE_DIST
    # of ANY existing member's hash.
    parent: dict[str, str] = {k: k for k in hashes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb

    keys = list(hashes)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if abs(hashes[a] - hashes[b]) < SAME_FACE_DIST:
                union(a, b)

    clusters: dict[str, list[str]] = {}
    for k in keys:
        clusters.setdefault(find(k), []).append(k)
    clusters = {i: v for i, v in enumerate(sorted(clusters.values(), key=len, reverse=True))}
    cluster_list = []
    for cid, members in clusters.items():
        # Pick representative: first face (lowest face_id) for stable UX
        members_sorted = sorted(members)
        cluster_list.append({
            "id": cid,
            "size": len(members),
            "rep": members_sorted[0],
            "members": members_sorted,
        })

    with open(OUT, "w") as f:
        json.dump({"clusters": cluster_list, "count": len(crops)}, f, indent=2)
    print(f"Wrote {OUT} with {len(cluster_list)} clusters "
          f"(largest={cluster_list[0]['size']}, smallest={cluster_list[-1]['size']})")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

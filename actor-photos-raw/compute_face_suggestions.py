#!/usr/bin/env python3
"""
Compute per-face character suggestions for the footage face crops.

Uses Frigate's bundled arcface.onnx (proper aspect-preserving preprocessing,
BGR input, /127.5 - 1 normalization). Each face crop is embedded, then
compared against existing character-references/<Char>NN.jpg embeddings.

Output: scene-extract/face_suggestions.json
  { "Scene_3/0": { "best_char": "MAMA", "best_score": 0.61,
                   "ranked": [["MAMA", 0.61], ["Tony", 0.58], ...] }, ... }

The tagger UI shows "Suggested: <char>" as a label on each untagged face.

This is a HINT, not authoritative. Arcface discrimination on Frigate's
quantized model is noisy (0.6-0.9 range, low dynamic range). But the rank
order is usually right: the highest-scoring reference for a Tony face is
typically a Tony reference, even if all scores are clustered.

Run from project root:
  /home/galagator/.hermes/venvs/fd3-frames/bin/python3 \
    /mnt/d/Projects/FD3/actor-photos-raw/compute_face_suggestions.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parent.parent
ARC = Path("/home/galagator/frigate-config/facedet/arcface.onnx")
ARC = Path("/home/galagator/hermes/frigate/config/model_cache/facedet/arcface.onnx")
ARC_INPUT = 112

PREFIX = {
    "Galen / Ji-lan": "Galen-Ji-lan", "Tony": "Tony", "Yake-oh": "Yake-oh",
    "Erb Dean": "Erb_Dean", "MAMA": "MAMA", "Trubble": "Trubble",
    "Slarth": "Slarth", "Zoh-baggo": "Zoh-baggo", "TK-Maxx": "TK-Maxx", "Jasmine": "Jasmine",
}
REF_DIR = ROOT / "character-references"
FOOTAGE = ROOT / "scene-extract" / "faces"
OUT = ROOT / "scene-extract" / "face_suggestions.json"


def embed_arcface(arc_sess, img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    if w != ARC_INPUT or h != ARC_INPUT:
        if w > h:
            new_h = int((h / w) * ARC_INPUT // 4 * 4)
            img = cv2.resize(img, (ARC_INPUT, new_h))
        else:
            new_w = int((w / h) * ARC_INPUT // 4 * 4)
            img = cv2.resize(img, (new_w, ARC_INPUT))
    h, w = img.shape[:2]
    canvas = np.zeros((ARC_INPUT, ARC_INPUT, 3), dtype=np.float32)
    x0, y0 = (ARC_INPUT - w) // 2, (ARC_INPUT - h) // 2
    canvas[y0:y0 + h, x0:x0 + w] = img.astype(np.float32)
    canvas = (canvas / 127.5) - 1.0
    canvas = canvas.transpose(2, 0, 1)[None]
    e = arc_sess.run(None, {"data": canvas})[0][0]
    e = e / (np.linalg.norm(e) + 1e-9)
    return e


def main() -> int:
    print("Loading arcface…")
    arc = ort.InferenceSession(str(ARC), providers=["CPUExecutionProvider"])

    print("Embedding character-references/…")
    ref_embs: list[tuple[str, np.ndarray, str]] = []  # (char, emb, file)
    for char, prefix in PREFIX.items():
        for f in sorted(REF_DIR.glob(f"{prefix}*.jpg")):
            if "_manual" in f.name: continue
            img = cv2.imread(str(f))
            if img is None: continue
            ref_embs.append((char, embed_arcface(arc, img), str(f.relative_to(ROOT))))
    print(f"  → {len(ref_embs)} reference embeddings")
    ref_arr = np.array([e for _, e, _ in ref_embs], dtype=np.float32)
    ref_arr = ref_arr / (np.linalg.norm(ref_arr, axis=1, keepdims=True) + 1e-9)

    print("Embedding footage face crops…")
    suggestions: dict[str, dict] = {}
    crop_paths = sorted(FOOTAGE.rglob("face_*.png"))
    for i, p in enumerate(crop_paths):
        rel = p.relative_to(ROOT)
        # rel is scene-extract/faces/Scene_3/face_00000.png
        # key is Scene_3/0
        parts = rel.parts
        scene = parts[2]
        face_id = int(parts[3].replace("face_", "").replace(".png", ""))
        key = f"{scene}/{face_id}"
        img = cv2.imread(str(p))
        if img is None: continue
        e = embed_arcface(arc, img)
        sims = ref_arr @ e
        order = np.argsort(-sims)  # desc
        # rank by char (best per char)
        per_char: dict[str, float] = {}
        for idx in order:
            c = ref_embs[idx][0]
            if c not in per_char:
                per_char[c] = float(sims[idx])
        ranked = sorted(per_char.items(), key=lambda kv: -kv[1])
        best_char, best_score = ranked[0]
        suggestions[key] = {
            "best_char": best_char,
            "best_score": round(best_score, 4),
            "ranked": [[c, round(s, 4)] for c, s in ranked[:5]],
        }
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(crop_paths)} scored")

    OUT.write_text(json.dumps({"suggestions": suggestions, "count": len(suggestions)}, indent=2))
    print(f"Wrote {OUT}")
    print()
    # quick sample
    sample_keys = list(suggestions.keys())[:8]
    for k in sample_keys:
        s = suggestions[k]
        ranked = ", ".join(f"{c}={sc:.2f}" for c, sc in s["ranked"][:3])
        print(f"  {k:18s} best={s['best_char']:12s} ({s['best_score']:.3f})  [{ranked}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

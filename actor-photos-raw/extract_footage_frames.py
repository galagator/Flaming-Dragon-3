#!/usr/bin/env python3
"""
Extract frames from the FD3 shot footage for character reference building.

Pipeline (per scene):
  1. ffmpeg → frames at 0.5 fps (every 2 seconds) at full source resolution
  2. Perceptual dedup (dHash, 8px, threshold 8) — drop near-duplicates
  3. YuNet face detection → annotate faces in a debug copy + write
     a manifest of which frames have faces (and how many)

Output layout (under the project root):
  scene-extract/
    raw/<scene>          ffmpeg-extracted frames (frame_00001.jpg ...)
    raw/<scene>_dedup    deduped subset
    debug/<scene>        frames with face boxes drawn
    faces/<scene>        individual face crops (face_00000.png ...)
    manifests/<scene>.json  { frame, faces: [{face_id, box, score}] }

Run from project root:
  /home/galagator/.hermes/venvs/fd3-frames/bin/python3 actor-photos-raw/extract_footage_frames.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SCENES_DIR = ROOT / "scenes"
OUT_DIR = ROOT / "scene-extract"
RAW_DIR = OUT_DIR / "raw"
DEBUG_DIR = OUT_DIR / "debug"
FACES_DIR = OUT_DIR / "faces"
MANIFEST_DIR = OUT_DIR / "manifests"
MODEL_PATH = Path("/tmp/face_detection_yunet.onnx")
MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"

FPS_INTERVAL = 0.5
DHASH_THRESHOLD = 8
FACE_PADDING = 1.25  # 1:1 crop, half-side = face_diag * FACE_PADDING
FACE_MIN_CONF = 0.5

SCENES = [
    ("Scene_1", "Scene 1.mp4"),
    ("Scene_2", "Scene 2.mp4"),
    ("Scene_3", "Scene 3.mp4"),
    ("Scene_4", "Scene 4.mp4"),
    ("Scene_5", "Scene 5.mp4"),
    ("Scene_6", "Scene 6.mp4"),
]


def ensure_model() -> None:
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 100_000:
        return
    print(f"  fetching YuNet model → {MODEL_PATH}")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    if MODEL_PATH.stat().st_size < 100_000:
        raise RuntimeError(f"YuNet model fetch failed (size={MODEL_PATH.stat().st_size})")


def run_ffmpeg(scene_key: str, mp4_path: Path) -> int:
    target = RAW_DIR / scene_key
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.jpg"):
        old.unlink()
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(mp4_path),
        "-vf", f"fps={FPS_INTERVAL}",
        "-q:v", "2",
        str(target / "frame_%05d.jpg"),
    ]
    print(f"  ffmpeg {scene_key}: ", end="", flush=True)
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc != 0:
        print(f"FAILED (rc={rc})")
        return 0
    count = sum(1 for _ in target.glob("*.jpg"))
    print(f"{count} frames")
    return count


def perceptual_dedup(scene_key: str) -> int:
    src = RAW_DIR / scene_key
    keep_dir = RAW_DIR / f"{scene_key}_dedup"
    keep_dir.mkdir(parents=True, exist_ok=True)
    for old in keep_dir.glob("*.jpg"):
        old.unlink()
    seen: list[imagehash.ImageHash] = []
    kept = 0
    for img_path in sorted(src.glob("*.jpg")):
        h = imagehash.dhash(Image.open(img_path), hash_size=8)
        if any(abs(h - s) < DHASH_THRESHOLD for s in seen):
            continue
        seen.append(h)
        shutil.copy2(img_path, keep_dir / img_path.name)
        kept += 1
    return kept


def detect_faces(detector, scene_key: str) -> list[dict]:
    src = RAW_DIR / f"{scene_key}_dedup"
    debug = DEBUG_DIR / scene_key
    faces = FACES_DIR / scene_key
    manifest = MANIFEST_DIR / f"{scene_key}.json"
    debug.mkdir(parents=True, exist_ok=True)
    faces.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    for old in debug.glob("*.jpg"):
        old.unlink()
    for old in faces.glob("*.png"):
        old.unlink()
    if manifest.exists():
        manifest.unlink()

    manifest_entries: list[dict] = []
    face_records: list[dict] = []
    face_id = 0

    for img_path in sorted(src.glob("*.jpg")):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w = img.shape[:2]
        detector.setInputSize((w, h))
        _, detections = detector.detect(img)
        if detections is None or len(detections) == 0:
            continue

        # Draw debug boxes
        dbg = img.copy()
        frame_faces: list[dict] = []
        for det in detections:
            # YuNet returns [x, y, w, h, ...landmarks..., score]
            x, y, bw, bh = int(det[0]), int(det[1]), int(det[2]), int(det[3])
            score = float(det[14])
            cx, cy = x + bw / 2, y + bh / 2
            side = max(bw, bh) * 2 * FACE_PADDING
            half = side / 2
            x0 = max(0, int(cx - half))
            y0 = max(0, int(cy - half))
            x1 = min(w, int(cx + half))
            y1 = min(h, int(cy + half))
            face_crop = img[y0:y1, x0:x1]
            if face_crop.size == 0:
                continue
            face_crop = cv2.resize(face_crop, (512, 512), interpolation=cv2.INTER_LANCZOS4)
            face_path = faces / f"face_{face_id:05d}.png"
            cv2.imwrite(str(face_path), face_crop)

            frame_faces.append({
                "face_id": face_id,
                "box": [x, y, bw, bh],
                "score": round(score, 3),
                "crop": str(face_path.relative_to(ROOT)),
            })
            face_records.append({
                "source_frame": img_path.name,
                "scene": scene_key,
                "face_id": face_id,
                "box": [x, y, bw, bh],
                "score": score,
                "crop": str(face_path.relative_to(ROOT)),
            })
            cv2.rectangle(dbg, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
            label = f"#{face_id} {score:.2f}"
            cv2.putText(dbg, label, (x, max(0, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            face_id += 1

        cv2.imwrite(str(debug / img_path.name), dbg)
        manifest_entries.append({
            "frame": img_path.name,
            "faces": [
                {"face_id": f["face_id"], "box": f["box"], "score": f["score"]}
                for f in frame_faces
            ],
        })

    with open(manifest, "w") as f:
        json.dump({"scene": scene_key, "frames": manifest_entries}, f, indent=2)
    with open(MANIFEST_DIR / f"{scene_key}_faces.json", "w") as f:
        json.dump(face_records, f, indent=2)
    return face_records


def main() -> int:
    print("FD3 frame extraction (ffmpeg → dHash dedup → YuNet faces)")
    print(f"  scenes → {SCENES_DIR}")
    print(f"  output → {OUT_DIR}")
    if not SCENES_DIR.exists():
        print(f"ERROR: scenes/ not found at {SCENES_DIR}")
        return 1

    ensure_model()
    detector = cv2.FaceDetectorYN.create(
        str(MODEL_PATH), "", (320, 320),
        score_threshold=FACE_MIN_CONF, nms_threshold=0.3,
    )

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    for scene_key, fname in SCENES:
        mp4 = SCENES_DIR / fname
        if not mp4.exists():
            print(f"  SKIP {scene_key}: {mp4} not found")
            continue
        extracted = run_ffmpeg(scene_key, mp4)
        kept = perceptual_dedup(scene_key)
        print(f"  dedup {scene_key}: {kept} kept")
        faces = detect_faces(detector, scene_key)
        print(f"  faces {scene_key}: {len(faces)} detected")
        summary.append({"scene": scene_key, "extracted": extracted, "kept": kept, "faces": len(faces)})

    with open(OUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print()
    print("Done.")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

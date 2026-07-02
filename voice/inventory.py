#!/usr/bin/env python3
"""Inventory all extracted chunks. Per-scene totals + duration histograms.

Speaker diarization is not available (pyannote requires HF token +
model access), so per-character breakdowns are NOT computed here.
This script just reports what's in voice/chunks/.

Run voice/diarize-chunks.py after providing an HF token to get
per-character assignments.
"""
import os
import wave
import contextlib
import json
import collections
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHUNKS = ROOT / "voice" / "chunks"
OUT = ROOT / "voice" / "notes" / "inventory.json"

by_scene = collections.defaultdict(list)
total_dur = 0.0
total_chunks = 0
total_short = 0
total_long = 0
for wav in sorted(CHUNKS.glob("*.wav")):
    name = wav.name
    # filename: <scene>_<idx>_<start>_<end>.wav
    parts = name[:-4].rsplit("_", 3)
    # rsplit('_', 3) → [scene, idx, start, end]
    # But scene names contain underscores (GKD_Commercial_1, Scene_1, etc.)
    # so we need a smarter split
    # Format: <scene>_<idx>_<start>_<end>
    # First two underscores separate idx, last two are start and end
    # e.g. "GKD_Commercial_1_001_0.00_3.00" → scene=GKD_Commercial_1, idx=001, start=0.00, end=3.00
    if len(parts) == 4:
        scene, idx, start, end = parts
    else:
        # fallback: take first 2 as scene
        scene = parts[0]
        idx = parts[1]
        start = parts[2] if len(parts) > 2 else "?"
        end = parts[3] if len(parts) > 3 else "?"
    with contextlib.closing(wave.open(str(wav), 'rb')) as w:
        nframes = w.getnframes()
        rate = w.getframerate()
        dur = nframes / rate
    by_scene[scene].append({"file": name, "start": start, "end": end, "duration": round(dur, 2)})
    total_dur += dur
    total_chunks += 1
    if dur < 2.0:
        total_short += 1
    if dur > 5.0:
        total_long += 1

# Build summary
summary = {
    "total_chunks": total_chunks,
    "total_duration_seconds": round(total_dur, 1),
    "total_duration_minutes": round(total_dur / 60, 2),
    "chunks_under_2s": total_short,
    "chunks_over_5s": total_long,
    "by_scene": {}
}
for scene, items in sorted(by_scene.items()):
    durs = [i["duration"] for i in items]
    summary["by_scene"][scene] = {
        "chunk_count": len(items),
        "total_duration_seconds": round(sum(durs), 1),
        "min_chunk_seconds": round(min(durs), 2) if durs else 0,
        "max_chunk_seconds": round(max(durs), 2) if durs else 0,
        "mean_chunk_seconds": round(sum(durs) / len(durs), 2) if durs else 0,
    }

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))

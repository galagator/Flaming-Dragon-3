#!/usr/bin/env python3
"""Speaker diarization on the FD3 audio.

For each scene's raw audio, run pyannote/speaker-diarization-3.1 to
produce per-speaker timeline segments. Then map each pre-extracted
chunk (voice/chunks/<scene>_<idx>_<start>_<end>.wav) to the speaker
who dominates that time range.

Writes voice/notes/diarization.json with per-chunk speaker assignments
and per-character clean-speech totals.
"""
import json
import os
import time
import torch
import contextlib
import wave
from pathlib import Path

from huggingface_hub import HfApi
from pyannote.audio import Pipeline

ROOT = Path(__file__).parent.parent
RAW = ROOT / "voice" / "raw"
CHUNKS = ROOT / "voice" / "chunks"
OUT = ROOT / "voice" / "notes" / "diarization.json"

# Auth: prefer HF_TOKEN env, fall back to cached login
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN env var not set; export HF_TOKEN=... before running")

print("Loading pyannote pipeline...")
t0 = time.time()
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=HF_TOKEN,
)
# Move to GPU if available
if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))
    print(f"  -> using CUDA ({torch.cuda.get_device_name(0)})")
else:
    print("  -> using CPU (no CUDA available)")
print(f"  loaded in {time.time() - t0:.1f}s")


def diarize_scene(wav_path: Path):
    """Run pyannote on a single scene. Returns a list of (start, end, speaker_label) tuples."""
    print(f"Diarizing {wav_path.name}...")
    t0 = time.time()
    output = pipeline(str(wav_path))
    # pyannote 4.x returns a DiarizeOutput; the actual diarization is in .speaker_diarization
    diarization = getattr(output, "speaker_diarization", output)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append((turn.start, turn.end, speaker))
    print(f"  -> {len(segments)} segments, {time.time() - t0:.1f}s")
    return segments


def dominant_speaker(chunk_start: float, chunk_end: float, segments):
    """Return the speaker with the most time overlap in the [chunk_start, chunk_end] range."""
    overlap = {}
    for s_start, s_end, speaker in segments:
        ov = max(0.0, min(chunk_end, s_end) - max(chunk_start, s_start))
        if ov > 0:
            overlap[speaker] = overlap.get(speaker, 0.0) + ov
    if not overlap:
        return None, 0.0
    # Use a sorted list rather than max() with a callable key — avoids
    # pyright typing complaints and is more deterministic
    items = sorted(overlap.items(), key=lambda kv: kv[1], reverse=True)
    return items[0][0], items[0][1]


# Parse chunk filenames: <scene>_<idx>_<start>_<end>.wav
def parse_chunk_name(name: str):
    base = name[:-4]  # strip .wav
    # rsplit '_' max 3 → [scene_with_underscores, idx, start, end]
    # But scene names have underscores (e.g. GKD_Commercial_1)
    # We know the index is always 3 digits, start and end are floats
    # So split on the last 3 underscores from the right
    parts = base.rsplit("_", 3)
    if len(parts) != 4:
        return None, None, None, None, None
    scene, idx, start, end = parts
    try:
        return scene, idx, float(start), float(end), base
    except ValueError:
        return None, None, None, None, None


# Per-scene diarization cache (run once per scene)
diar_cache = {}

# Walk all chunks
results = {"chunks": [], "per_speaker_clean_seconds": {}, "per_scene_diarization": {}}

# Build list of (chunk_path, scene, start, end)
chunk_records = []
for wav in sorted(CHUNKS.glob("*.wav")):
    scene, idx, start, end, base = parse_chunk_name(wav.name)
    if scene is None:
        print(f"  skip unparseable: {wav.name}")
        continue
    chunk_records.append({"file": wav.name, "scene": scene, "start": start, "end": end, "base": base})

# Dedupe scenes
scenes = sorted(set(c["scene"] for c in chunk_records))
print(f"\nFound {len(scenes)} scenes: {scenes}")

# Run diarization per scene
for scene in scenes:
    raw = RAW / f"{scene}.wav"
    if not raw.exists():
        print(f"  WARN: no raw wav for {scene}")
        continue
    segments = diarize_scene(raw)
    diar_cache[scene] = segments
    # Save raw diarization
    results["per_scene_diarization"][scene] = [
        {"start": round(s, 3), "end": round(e, 3), "speaker": sp}
        for s, e, sp in segments
    ]

# Map each chunk
print("\nMapping chunks to speakers...")
for rec in chunk_records:
    scene = rec["scene"]
    if scene not in diar_cache:
        rec["speaker"] = None
        rec["overlap_seconds"] = 0.0
        rec["chunk_duration"] = round(rec["end"] - rec["start"], 2)
        results["chunks"].append(rec)
        continue
    speaker, overlap = dominant_speaker(rec["start"], rec["end"], diar_cache[scene])
    rec["speaker"] = speaker
    rec["overlap_seconds"] = round(overlap, 2)
    rec["chunk_duration"] = round(rec["end"] - rec["start"], 2)
    results["chunks"].append(rec)

# Per-speaker clean-seconds totals (sum of chunk durations where this speaker dominates)
per_speaker = {}
for rec in results["chunks"]:
    sp = rec.get("speaker")
    if sp is None:
        continue
    per_speaker[sp] = per_speaker.get(sp, 0.0) + rec["chunk_duration"]

# Per-scene per-speaker
per_scene_speaker = {}
for rec in results["chunks"]:
    sp = rec.get("speaker")
    if sp is None:
        continue
    sc = rec["scene"]
    per_scene_speaker.setdefault(sc, {}).setdefault(sp, 0.0)
    per_scene_speaker[sc][sp] += rec["chunk_duration"]

results["per_speaker_clean_seconds"] = {sp: round(s, 1) for sp, s in sorted(per_speaker.items())}
results["per_scene_per_speaker_seconds"] = {
    sc: {sp: round(s, 1) for sp, s in sorted(d.items())}
    for sc, d in per_scene_speaker.items()
}

OUT.write_text(json.dumps(results, indent=2))
print(f"\nDONE — wrote {OUT}")
print(f"\nPer-speaker clean seconds totals:")
for sp, s in sorted(per_speaker.items(), key=lambda x: -x[1]):
    print(f"  {sp}: {s:.1f}s")
print(f"\nPer-scene breakdown:")
for sc in sorted(per_scene_speaker):
    print(f"  {sc}:")
    for sp, s in sorted(per_scene_speaker[sc].items(), key=lambda x: -x[1]):
        print(f"    {sp}: {s:.1f}s")

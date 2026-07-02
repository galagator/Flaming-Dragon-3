#!/usr/bin/env python3
"""Organize assigned voice chunks into per-character folders for
ElevenLabs Instant Voice Cloning upload.

For each character with assigned audio:
1. Create voice/by_character/<Name>/
2. Copy or symlink the assigned chunks
3. Concatenate them into a single .wav for easy upload
4. Write a manifest with per-chunk timing + durations

Output:
  voice/by_character/
    Tony/
      Tony_combined.wav            # all chunks concatenated
      chunks/                       # individual chunks
        GKD_Commercial_1_001_0.00_3.00.wav
        ...
      manifest.json                # per-chunk metadata
      summary.txt                   # human-readable summary
    Ji-lan/
    ...
"""
import json
import os
import shutil
import subprocess
import wave
import contextlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHUNKS = ROOT / "voice" / "chunks"
BY_CHAR = ROOT / "voice" / "by_character"
ASSIGNMENTS = ROOT / "voice" / "notes" / "voice_assignments.json"
DIAR = ROOT / "voice" / "notes" / "diarization.json"

if BY_CHAR.exists():
    shutil.rmtree(BY_CHAR)
BY_CHAR.mkdir(parents=True)

# Load assignments
assignments = json.loads(ASSIGNMENTS.read_text())
# Load per-chunk metadata (for scene/duration/cluster)
diar = json.loads(DIAR.read_text())
chunk_meta = {c["file"]: c for c in diar["chunks"]}

# Group by character (excluding Reject)
by_char = {}
for fname, character in assignments.items():
    if character == "Reject":
        continue
    by_char.setdefault(character, []).append(fname)

# Sort each character's chunks by scene then start time for natural playback
def sort_key(fname):
    m = chunk_meta.get(fname, {})
    return (m.get("scene", ""), m.get("start", 0.0))

for character in sorted(by_char):
    char_dir = BY_CHAR / character
    char_dir.mkdir(parents=True)
    chunks_subdir = char_dir / "chunks"
    chunks_subdir.mkdir()

    files = sorted(by_char[character], key=sort_key)

    # Copy individual chunks
    for fname in files:
        src = CHUNKS / fname
        if src.exists():
            shutil.copy2(src, chunks_subdir / fname)

    # Concatenate chunks into one combined wav for easy upload.
    # ffmpeg concat demuxer handles variable-framerate wav fine.
    concat_list = char_dir / "concat_list.txt"
    with concat_list.open("w") as f:
        for fname in files:
            f.write(f"file '{chunks_subdir / fname}'\n")

    combined = char_dir / f"{character.replace(' ', '_')}_combined.wav"
    # Get sample rate from first file
    first_wav = chunks_subdir / files[0]
    with contextlib.closing(wave.open(str(first_wav), 'rb')) as w:
        rate = w.getframerate()
        channels = w.getnchannels()

    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-ar", str(rate), "-ac", str(channels),
        "-acodec", "pcm_s16le",
        str(combined),
    ], check=True)

    # Combined duration
    with contextlib.closing(wave.open(str(combined), 'rb')) as w:
        nframes = w.getnframes()
        rate = w.getframerate()
        combined_dur = nframes / rate

    # Also build a "clean" version that excludes chunks > 10s (typically
    # multi-speaker scenes with music/SFX — bad input for voice cloning)
    clean_files = [f for f in files if chunk_meta.get(f, {}).get("chunk_duration", 0) <= 10]
    clean_concat = char_dir / "concat_list_clean.txt"
    with clean_concat.open("w") as f:
        for fname in clean_files:
            f.write(f"file '{chunks_subdir / fname}'\n")
    clean_combined = None
    if clean_files:
        clean_combined = char_dir / f"{character.replace(' ', '_')}_clean_combined.wav"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(clean_concat),
            "-ar", str(rate), "-ac", str(channels),
            "-acodec", "pcm_s16le",
            str(clean_combined),
        ], check=True)
        with contextlib.closing(wave.open(str(clean_combined), 'rb')) as w:
            clean_dur = w.getnframes() / w.getframerate()
    else:
        clean_dur = 0

    # Per-chunk manifest
    manifest = {
        "character": character,
        "chunk_count": len(files),
        "combined_duration_seconds": round(combined_dur, 2),
        "combined_file": f"{character.replace(' ', '_')}_combined.wav",
        "clean_combined_file": f"{character.replace(' ', '_')}_clean_combined.wav" if clean_files else None,
        "clean_duration_seconds": round(clean_dur, 2),
        "clean_chunk_count": len(clean_files),
        "sample_rate": rate,
        "channels": channels,
        "chunks": [
            {
                "file": fname,
                "scene": chunk_meta.get(fname, {}).get("scene"),
                "start": chunk_meta.get(fname, {}).get("start"),
                "end": chunk_meta.get(fname, {}).get("end"),
                "duration": round(chunk_meta.get(fname, {}).get("chunk_duration", 0), 2),
                "speaker_cluster": chunk_meta.get(fname, {}).get("speaker"),
            }
            for fname in files
        ],
    }
    (char_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # Human-readable summary
    lines = [
        f"=== {character} ===",
        f"  Chunks: {len(files)}",
        f"  Combined duration: {combined_dur:.1f}s ({combined_dur/60:.2f}m)",
        f"  Combined file: {combined.name}",
        f"  Clean (≤10s chunks only): {clean_dur:.1f}s ({len(clean_files)} chunks) → {clean_combined.name if clean_combined else 'N/A'}",
        f"  Sample rate: {rate} Hz, {channels} ch",
        "",
        "  Per-chunk:",
    ]
    for c in manifest["chunks"]:
        cluster = c["speaker_cluster"] or "?"
        lines.append(
            f"    {c['file']:<55} {c['duration']:>5.1f}s  [{c['scene']}, cluster={cluster}]"
        )
    (char_dir / "summary.txt").write_text("\n".join(lines) + "\n")

    print(f"  {character}: {len(files)} chunks, {combined_dur:.1f}s combined → {combined.relative_to(ROOT)}")

# Also: write a global manifest
global_manifest = {
    "characters": sorted(by_char.keys()),
    "rejected_chunks": sum(1 for v in assignments.values() if v == "Reject"),
    "total_chunks": len(assignments),
}
(BY_CHAR / "MANIFEST.json").write_text(json.dumps(global_manifest, indent=2))
print()
print(f"Done. Wrote {len(by_char)} character folders to {BY_CHAR.relative_to(ROOT)}/")
print(f"  {global_manifest['rejected_chunks']} rejected chunks (not copied)")

#!/usr/bin/env python3
"""Extract individual speech segments as separate WAV files.

Reads voice/notes/<scene>.segments.tsv, extracts each segment from
voice/raw/<scene>.wav, writes to voice/chunks/<scene>_<idx>_<start>_<end>.wav.

Skips zero-duration and tiny (<0.5s) segments.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
NOTES = ROOT / "voice" / "notes"
RAW = ROOT / "voice" / "raw"
CHUNKS = ROOT / "voice" / "chunks"
CHUNKS.mkdir(parents=True, exist_ok=True)

# nuke old chunks so renames are clean
for f in CHUNKS.glob("*.wav"):
    f.unlink()

total = 0
for tsv in sorted(NOTES.glob("*.segments.tsv")):
    scene = tsv.stem.replace(".segments", "")
    wav = RAW / f"{scene}.wav"
    if not wav.exists():
        print(f"SKIP {scene}: no raw wav")
        continue
    idx = 0
    for line in tsv.read_text().splitlines():
        if not line or line.startswith("#") or line.startswith("start"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            print(f"  bad line in {tsv.name}: {line!r}")
            continue
        try:
            start = float(parts[0])
            end = float(parts[1])
            dur = float(parts[2])
        except ValueError:
            print(f"  non-numeric line in {tsv.name}: {line!r}")
            continue
        if dur < 0.5:
            continue
        if start >= end:
            continue
        idx += 1
        out = CHUNKS / f"{scene}_{idx:03d}_{start:.2f}_{end:.2f}.wav"
        if out.exists():
            continue
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(wav),
            "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
            "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "1",
            str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ffmpeg failed for {out.name}: {r.stderr.strip()}")
            out.unlink(missing_ok=True)
            continue
    print(f"{scene}: {idx} chunks extracted")
    total += idx

print(f"DONE — {total} total chunks")
print(f"--- size ---")
import subprocess
r = subprocess.run(["du", "-sh", str(CHUNKS)], capture_output=True, text=True)
print(r.stdout.strip())

#!/usr/bin/env python3
"""GKD commercial has no detectable silence (continuous broadcast audio).

Instead of silence detection, split the full 30s clip into 3-second fixed
chunks. These are the Ji-lan voice source — the user said they have very
little source audio for Ji-lan, so every second matters.
"""
import subprocess
import wave
import contextlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW = ROOT / "voice" / "raw"
CHUNKS = ROOT / "voice" / "chunks"

wav = RAW / "GKD_Commercial_1.wav"
with contextlib.closing(wave.open(str(wav), 'rb')) as w:
    duration = w.getnframes() / w.getframerate()
    print(f"GKD_Commercial_1: {duration:.2f}s")

chunk_dur = 3.0
idx = 0
t = 0.0
while t < duration:
    end = min(t + chunk_dur, duration)
    if end - t < 1.0:
        break
    idx += 1
    out = CHUNKS / f"GKD_Commercial_1_{idx:03d}_{t:.2f}_{end:.2f}.wav"
    if out.exists():
        t = end
        continue
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(wav),
        "-ss", f"{t:.3f}", "-to", f"{end:.3f}",
        "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "1",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ffmpeg failed: {r.stderr.strip()}")
        out.unlink(missing_ok=True)
    t = end

print(f"-> {idx} fixed-duration chunks")

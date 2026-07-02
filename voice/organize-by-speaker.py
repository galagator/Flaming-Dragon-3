#!/usr/bin/env python3
"""Organize voice/chunks/ into per-speaker subfolders for easy listening.

Reads voice/notes/diarization.json and copies each chunk into
voice/by_speaker/SPEAKER_xx/ so you can browse by voice instead of
by scene.

Also writes voice/notes/speaker_inventory.json with per-speaker
file lists and per-chunk metadata.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHUNKS = ROOT / "voice" / "chunks"
BY_SPEAKER = ROOT / "voice" / "by_speaker"
DIAR = ROOT / "voice" / "notes" / "diarization.json"
OUT = ROOT / "voice" / "notes" / "speaker_inventory.json"

# Wipe and rebuild
if BY_SPEAKER.exists():
    shutil.rmtree(BY_SPEAKER)
BY_SPEAKER.mkdir(parents=True)

data = json.loads(DIAR.read_text())
chunks = data["chunks"]

# Group by speaker (UNASSIGNED for chunks where diarization found no overlap)
by_spk = {}
for c in chunks:
    sp = c.get("speaker") or "UNASSIGNED"
    by_spk.setdefault(sp, []).append(c)

# Write per-speaker folder
for sp, items in by_spk.items():
    sp_dir = BY_SPEAKER / sp
    sp_dir.mkdir(parents=True, exist_ok=True)
    for c in items:
        src = CHUNKS / c["file"]
        if src.exists():
            shutil.copy2(src, sp_dir / c["file"])

# Write inventory with helpful metadata
inventory = {
    sp: {
        "chunk_count": len(items),
        "total_seconds": sum(c.get("chunk_duration", 0) for c in items),
        "scenes": sorted(set(c["scene"] for c in items)),
        "files": [c["file"] for c in items],
    }
    for sp, items in by_spk.items()
}

OUT.write_text(json.dumps(inventory, indent=2))
print(f"Wrote {OUT}")
print(f"Created {len(by_spk)} speaker folders under {BY_SPEAKER}")
for sp in sorted(by_spk, key=lambda s: -len(by_spk[s])):
    n = len(by_spk[sp])
    s = sum(c.get("chunk_duration", 0) for c in by_spk[sp])
    print(f"  {sp}: {n} chunks, {s:.1f}s total")
print()
print("Quick listening guide:")
print("  - cd voice/by_speaker/SPEAKER_00")
print("  - play *.wav (or open them in your audio player of choice)")
print("  - SPEAKER_00 is the most prominent voice (135s across all scenes)")

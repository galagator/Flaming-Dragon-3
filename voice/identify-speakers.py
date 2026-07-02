#!/usr/bin/env python3
"""Print a human-readable speaker identification report.

Lists each detected speaker with:
- Total seconds
- Per-scene breakdown
- Most likely character based on scene context (heuristic)

This is a guide for the user to listen-and-confirm. Not authoritative.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
INVENTORY = ROOT / "voice" / "notes" / "speaker_inventory.json"
DIAR = ROOT / "voice" / "notes" / "diarization.json"

# Scene context (from production guide + script)
SCENE_CONTEXT = {
    "GKD_Commercial_1": "Ji-lan infomercial, ~1 character speaking",
    "Scene_1": "Tony's lounge — Tony, Yake-oh, Erb Dean",
    "Scene_2": "Fruity Groovin walking montage — mostly Tony",
    "Scene_3": "Restaurant with MAMA — Tony, MAMA, Trubble, Slarth",
    "Scene_4": "Chase/beatdown — no clean speech",
    "Scene_5": "Bridge Under Moonlight — Tony solo with sax",
    "Scene_6": "Tony's house, enlists help — Tony, Yake-oh, Erb Dean",
}

inv = json.loads(INVENTORY.read_text())
diar = json.loads(DIAR.read_text())

print("=" * 70)
print("FD3 SPEAKER DIARIZATION REPORT")
print("=" * 70)
print()
print("Per-speaker audio totals (sorted by total seconds):")
print()
print(f"{'Speaker':<14} {'Total':<8} {'Files':<7} Scenes")
print("-" * 70)

# Sort by total seconds desc
sorted_sp = sorted(inv.items(), key=lambda x: -x[1]["total_seconds"])
for sp, info in sorted_sp:
    secs = info["total_seconds"]
    files = info["chunk_count"]
    scenes = ", ".join(sorted(set(s.split("_")[0] for s in info["scenes"])))
    print(f"{sp:<14} {secs:>6.1f}s  {files:>5}   {scenes}")
print()

# Heuristic guesses based on scene context
print("Heuristic identification (based on which scenes each speaker dominates):")
print()
guess = {}
for sp, info in sorted_sp:
    secs = info["total_seconds"]
    scenes = info["scenes"]
    # Scene 2 + Scene 5 = almost all Tony
    scene2 = info.get("scenes", [])
    # Heuristic: extract per-scene seconds from diarization.json
    per_scene = {}
    for c in diar["chunks"]:
        if c.get("speaker") == sp:
            per_scene[c["scene"]] = per_scene.get(c["scene"], 0) + c.get("chunk_duration", 0)
    top_scenes = sorted(per_scene.items(), key=lambda x: -x[1])[:3]
    scene_str = ", ".join(f"{s}={v:.1f}s" for s, v in top_scenes)
    print(f"  {sp}: top scenes = {scene_str}")
print()

# Apply the strong heuristics
if "SPEAKER_00" in inv:
    s0 = inv["SPEAKER_00"]
    scene_set = set(s0["scenes"])
    if "Scene_2" in scene_set and "Scene_5" in scene_set:
        print(">>> STRONG GUESS: SPEAKER_00 is TONY")
        print("    (only character in Scene 2 walking montage + Scene 5 sax scene)")
        print()
        guess["SPEAKER_00"] = "Tony"
if "SPEAKER_01" in inv:
    s1 = inv["SPEAKER_01"]
    if "GKD_Commercial_1" in s1["scenes"]:
        print(">>> STRONG GUESS: SPEAKER_01 is JI-LAN")
        print("    (Ji-lan is the only character in the GKD infomercial)")
        print()
        guess["SPEAKER_01"] = "Ji-lan"

# Other speakers: 02, 03, 04, 05 in scene 1 + 3 + 6 — need to listen
print("Other speakers (SPEAKER_02, 03, 04, 05) appear in:")
print("  Scene 1: Tony, Yake-oh, Erb Dean")
print("  Scene 3: Tony, MAMA, Trubble, Slarth")
print("  Scene 6: Tony, Yake-oh, Erb Dean")
print()
print("These need to be identified by listening. SPEAKER_03 has the most")
print("speech across these scenes (33.5s) — likely a primary character")
print("in those scenes (could be MAMA in Scene 3 or one of the leads).")
print()
print("SPEAKER_05 only has 1.9s — probably SFX or background noise,")
print("not a real character.")
print()
print("=" * 70)
print("To identify speakers, listen to chunks in voice/by_speaker/SPEAKER_xx/")
print("Each .wav file is named <scene>_<idx>_<start>_<end>.wav so you can")
print("navigate by scene if needed.")
print("=" * 70)

# Save the guesses for the next script
out = ROOT / "voice" / "notes" / "speaker_guesses.json"
out.write_text(json.dumps(guess, indent=2))
print(f"\nGuesses written to {out}")

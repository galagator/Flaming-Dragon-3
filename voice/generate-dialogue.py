#!/usr/bin/env python3
"""Generate dialogue audio for FD3 characters using ElevenLabs voices.

Reads:
  - voice/notes/voice_ids.json  (per-character voice_id + settings)
  - character-references/dialogue_data.json  (per-character lines)

Usage:
  # All lines for one character
  python3 voice/generate-dialogue.py --character Tony
  python3 voice/generate-dialogue.py --character Erb\ Dean

  # All characters
  python3 voice/generate-dialogue.py --all

  # Specific scenes (filter by line index range)
  python3 voice/generate-dialogue.py --character Tony --start 0 --end 5

  # List characters and their voice status
  python3 voice/generate-dialogue.py --list

Output: voice/dialogue/<character>/<NN>_<slug>.mp3
        voice/dialogue/<character>_manifest.json
"""
import argparse
import json
import os
import re
import sys
import time
import requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY env var not set")

HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
VOICE_IDS_PATH = ROOT / "voice" / "notes" / "voice_ids.json"
DIALOGUE_PATH = ROOT / "character-references" / "dialogue_data.json"
OUT_DIR = ROOT / "voice" / "dialogue"


def slugify(text: str, max_len: int = 40) -> str:
    """Make a filesystem-safe slug from a line of dialogue."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:max_len] or "line"


def list_characters(voice_ids: dict, dialogue: dict):
    print("=== Character voice status ===\n")
    print(f"{'Character':<14} {'Voice':<14} {'Lines':<6} Source")
    print("-" * 70)
    all_chars = sorted(set(voice_ids.keys()) | set(dialogue.keys()))
    for ch in all_chars:
        v = voice_ids.get(ch)
        d = dialogue.get(ch, [])
        if v and isinstance(v, dict) and v.get("voice_id"):
            src = v.get("source", "?")
            vname = v.get("voice_name", "?")[:30]
            n_lines = len(d)
            print(f"{ch:<14} {vname:<14} {n_lines:<6} {src}")
        else:
            n_lines = len(d) if isinstance(d, list) else 0
            print(f"{ch:<14} {'(no voice)':<14} {n_lines:<6} —")


def get_voice_settings(voice_info: dict) -> dict:
    """Get the per-character voice settings, falling back to defaults."""
    defaults = voice_info.get("_default_voice_settings", {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "speed": 1.0,
        "use_speaker_boost": True,
        "model_id": "eleven_flash_v2_5",
    })
    settings = dict(defaults)
    char_settings = voice_info.get("voice_settings", {})
    settings.update(char_settings)
    return settings


def synthesize(voice_id: str, text: str, settings: dict) -> bytes | None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": settings.get("model_id", "eleven_flash_v2_5"),
        "voice_settings": {
            "stability": settings.get("stability", 0.5),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "speed": settings.get("speed", 1.0),
            "use_speaker_boost": settings.get("use_speaker_boost", True),
        },
    }
    r = requests.post(url, headers=HEADERS, json=body, timeout=60)
    if r.status_code == 200:
        return r.content
    print(f"    TTS failed: {r.status_code} {r.text[:200]}")
    return None


def generate_for_character(character: str, voice_ids: dict, dialogue: dict,
                           start: int | None = None, end: int | None = None,
                           force: bool = False) -> dict:
    if character not in voice_ids:
        print(f"  No voice_id for '{character}' — skipping")
        return {"skipped": True, "reason": "no voice_id"}
    if character not in dialogue:
        print(f"  No dialogue lines for '{character}' — skipping")
        return {"skipped": True, "reason": "no dialogue"}
    voice_info = voice_ids[character]
    if not isinstance(voice_info, dict) or "voice_id" not in voice_info:
        print(f"  voice_ids['{character}'] missing voice_id — skipping")
        return {"skipped": True, "reason": "invalid voice_id"}

    voice_id = voice_info["voice_id"]
    settings = get_voice_settings(voice_ids)
    lines = dialogue[character]
    if not isinstance(lines, list):
        print(f"  dialogue['{character}'] is not a list — skipping")
        return {"skipped": True, "reason": "invalid dialogue"}

    # Apply range
    if start is not None or end is not None:
        s = start or 0
        e = end if end is not None else len(lines)
        lines = lines[s:e]

    out_dir = OUT_DIR / character
    out_dir.mkdir(parents=True, exist_ok=True)

    # Clean action notes in asterisks? No, keep them — ElevenLabs handles them
    # Just strip if very long (>500 chars to avoid API issues)
    manifest = {"character": character, "voice_id": voice_id, "settings": settings, "lines": []}
    n_done, n_skip, n_fail = 0, 0, 0

    for i, line in enumerate(lines):
        slug = slugify(line)
        out_file = out_dir / f"{i:03d}_{slug}.mp3"
        manifest_entry = {"index": i, "text": line, "file": out_file.name}
        if out_file.exists() and not force:
            n_skip += 1
            manifest_entry["status"] = "skipped (exists)"
            manifest["lines"].append(manifest_entry)
            continue
        # Truncate if extremely long (defensive)
        text = line if len(line) <= 500 else line[:497] + "..."
        audio = synthesize(voice_id, text, settings)
        if audio:
            out_file.write_bytes(audio)
            n_done += 1
            manifest_entry["status"] = "generated"
        else:
            n_fail += 1
            manifest_entry["status"] = "failed"
        manifest["lines"].append(manifest_entry)
        time.sleep(0.3)  # politeness

    # Write manifest
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"  {character}: {n_done} generated, {n_skip} skipped, {n_fail} failed → {out_dir.relative_to(ROOT)}")
    return {"done": n_done, "skip": n_skip, "fail": n_fail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", "-c", help="Single character to generate")
    ap.add_argument("--all", action="store_true", help="Generate for all characters with both voice_id and dialogue")
    ap.add_argument("--start", type=int, help="Start index (inclusive) of dialogue lines for the character")
    ap.add_argument("--end", type=int, help="End index (exclusive) of dialogue lines for the character")
    ap.add_argument("--force", action="store_true", help="Re-generate even if output file exists")
    ap.add_argument("--list", action="store_true", help="List characters and their voice status, then exit")
    args = ap.parse_args()

    voice_ids = json.loads(VOICE_IDS_PATH.read_text())
    dialogue = json.loads(DIALOGUE_PATH.read_text())

    if args.list:
        list_characters(voice_ids, dialogue)
        return

    if args.all:
        all_chars = sorted(set(voice_ids.keys()) & set(dialogue.keys()))
        print(f"=== Generating for {len(all_chars)} characters ===\n")
        totals = {"done": 0, "skip": 0, "fail": 0}
        for ch in all_chars:
            if not isinstance(voice_ids.get(ch), dict) or "voice_id" not in voice_ids[ch]:
                continue
            r = generate_for_character(ch, voice_ids, dialogue, args.start, args.end, args.force)
            for k in totals:
                if k in r:
                    totals[k] += r[k]
        print(f"\n=== Totals: {totals} ===")
        return

    if args.character:
        generate_for_character(args.character, voice_ids, dialogue, args.start, args.end, args.force)
        return

    # No args: show help
    ap.print_help()
    print()
    list_characters(voice_ids, dialogue)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate extended test lines for each ElevenLabs library voice
candidate. Different emotional registers help evaluate fit.

Outputs more MP3s per candidate, organized by emotion tag.
"""
import json
import os
import time
import requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY env var not set")

HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

# More test lines per character, tagged by emotion
TEST_LINES = {
    "Jasmine": {
        "neutral_intro": "Hey Tony. I'm Jasmine. I was hoping I'd find you here.",
        "excited": "Yes! I knew you could do it! That's my Flaming Dragon!",
        "concerned": "Tony, are you okay? You look like you've been through a lot.",
        "flirty": "You know, I think we make a pretty good team. Maybe we should... celebrate?",
    },
    "Zoh-baggo": {
        "neutral_intro": "Heyyyy. And who do we have here?",
        "intimidating": "You think you can just walk in here? This is GKD territory.",
        "angry": "You're going to regret this, dough boy!",
        "hurt": "Oww! My heel! Tony, you bastard!",
    },
    "TK-Maxx": {
        "neutral_intro": "Alright, listen up. We've got a problem.",
        "threatening": "You're messing with the wrong people, pretty boy.",
        "fighting": "Come on then! Let's see what you've got!",
        "defeated": "Ugh... I... I tapped out. I tapped out, okay?",
    },
}

# Reuse the candidate lists from elevenlabs-candidates.py
CANDIDATE_VOICES = {}
synthesize = None
import importlib.util
_loader = importlib.util.spec_from_file_location(
    "_ec", str(ROOT / "voice" / "elevenlabs-candidates.py")
)
if _loader is not None:
    mod = importlib.util.module_from_spec(_loader)
    if _loader.loader is not None:
        _loader.loader.exec_module(mod)
        CANDIDATE_VOICES = mod.CANDIDATE_VOICES
        synthesize = mod.synthesize

for ch, lines_by_emotion in TEST_LINES.items():
    out_dir = ROOT / "voice" / "by_character" / ch / "elevenlabs_candidates"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        "character": ch, "description": "", "candidates": []
    }

    # Index existing samples by voice_id for quick lookup
    existing_by_vid = {c["voice_id"]: c for c in manifest.get("candidates", [])}

    print(f"\n=== {ch} ===")
    for vid, reason in CANDIDATE_VOICES[ch]:
        if vid not in existing_by_vid:
            print(f"  SKIP {vid} (not in initial manifest)")
            continue
        cand = existing_by_vid[vid]
        safe_name = cand["voice_name"].split(" - ")[0].replace(" ", "_") if " - " in cand["voice_name"] else cand["voice_name"][:8]

        # Generate each emotional test line
        cand.setdefault("extended_samples", [])
        for emotion, text in lines_by_emotion.items():
            out_file = out_dir / f"ext_{safe_name}_{vid[:8]}_{emotion}.mp3"
            if out_file.exists():
                print(f"  SKIP {safe_name}/{emotion} (exists)")
                continue
            print(f"  gen {safe_name}/{emotion}...")
            audio = synthesize(vid, text)
            if audio:
                out_file.write_bytes(audio)
                cand["extended_samples"].append({
                    "emotion": emotion,
                    "text": text,
                    "file": out_file.name,
                })
            time.sleep(0.3)
        manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  Updated {manifest_path}")

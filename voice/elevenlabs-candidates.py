#!/usr/bin/env python3
"""Pick ElevenLabs voices for the 3 unshot FD3 characters.

For each character, pick 3 candidate voices from the user's premade
library + shared community voices, generate a short test sample
with each, and write a manifest so the user can listen and pick.

Output: voice/by_character/<Name>/elevenlabs_candidates/
  candidate_<voice_id>.mp3    test sample
  manifest.json                 voice_id, name, description, audio file
"""
import json
import os
import requests
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY env var not set")

HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

# Character voice profiles — what we're looking for in each character
# Based on the production guide + script context
CHAR_PROFILES = {
    "Jasmine": {
        "description": "Tony's love interest. Young adult woman, late 20s to early 30s, vibrant red hair, party attire. Plays a love interest so should sound warm and engaging, not too aggressive.",
        "sample_text": "Hey Tony, I've been waiting for you. I heard what happened at the park. Are you okay?",
        "candidate_pools": ["female", "young", "american", "warm", "playful", "social_media"],
    },
    "Zoh-baggo": {
        "description": "Female goon, early 20s, business-casual office goon. Breaks a heel in a fight scene. Should sound confident, a bit sharp, ready for action.",
        "sample_text": "You think you can walk in here and just take what you want? Think again, pal. Let's go.",
        "candidate_pools": ["female", "young", "american", "confident", "narrative_story", "social_media"],
    },
    "TK-Maxx": {
        "description": "Male goon, fights Erb Dean, gets KO'd by Yake-oh. Should sound tough, aggressive, ready to throw down.",
        "sample_text": "What's the matter, pretty boy? You scared of a little fight? Come on then. Let's see what you've got.",
        "candidate_pools": ["male", "young", "american", "aggressive", "social_media", "narrative_story"],
    },
}

# Test voice IDs from the user's premade library (the 21 available)
# Curated based on character profiles
CANDIDATE_VOICES = {
    "Jasmine": [
        # Australian female voices for Tony's love interest (late 20s)
        ("jVaO0tjr2YWfUw1xLmB2", "Krystal - Young female, Australian accent (FREE)"),
        ("56bWURjYFHyYyVf490Dp", "Emma - Warm Australian voice, early 30s, sweet & engaging (FREE)"),
        ("DusxpIechtn2D8hID1Jy", "Tanya - Warm & confident Australian voice, business/mentoring (FREE)"),
    ],
    "Zoh-baggo": [
        # Australian female voices for tough young goon (early 20s)
        ("DusxpIechtn2D8hID1Jy", "Tanya - Warm & confident (Zoh-baggo has business-casual confidence)"),
        ("OluJZCsIVfyg64DC1NPq", "Kailey - Sales with sass, confident/upbeat (FREE)"),
        ("IwFADcBfc7Yo8KGhxTR5", "Zoe - Upbeat Aussie & British (young, soft — for the heel-breaking vulnerability)"),
    ],
    "TK-Maxx": [
        # Australian male voices for tough goon
        ("CbQryPGe1i0tLYfqq2b3", "Freddy Brown - Warm personable Aussie male, easygoing humor (FREE)"),
        ("Jp0fPKXUBLCdWE82ol3M", "Jett - Deep warm baritone, light Australian tint (FREE)"),
        ("q7VZEIc6Sfunon4tcOtk", "Simon - Mid-30s conversational Aussie male (FREE)"),
    ],
}

# Verify these IDs exist by fetching the user's voices
print("Fetching user's premade voices for reference...")
r = requests.get("https://api.elevenlabs.io/v1/voices", headers=HEADERS, timeout=30)
d = r.json()
available = {v["voice_id"]: v["name"] for v in d.get("voices", [])}
print(f"  {len(available)} voices in user's library")
# Note: shared/featured voices can be used directly via TTS API
# without adding them to the library first.

# Generate test samples
def synthesize(voice_id, text, model="eleven_flash_v2_5"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(url, headers=HEADERS, json=body, timeout=60)
    if r.status_code == 200:
        return r.content
    print(f"  TTS failed for {voice_id}: {r.status_code} {r.text[:200]}")
    return None


for ch, profile in CHAR_PROFILES.items():
    out_dir = ROOT / "voice" / "by_character" / ch / "elevenlabs_candidates"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "character": ch,
        "description": profile["description"],
        "sample_text": profile["sample_text"],
        "candidates": [],
    }

    print(f"\n=== {ch} ===")
    for vid, reason in CANDIDATE_VOICES[ch]:
        vname = vid  # we'll show the ID since shared voices have arbitrary names
        # If the voice is in the user's library, use its real name
        if vid in available:
            vname = available[vid]
        print(f"  generating sample with {vname} ({vid})...")
        audio = synthesize(vid, profile["sample_text"])
        if audio:
            safe_name = vname.split(" - ")[0].replace(" ", "_")
            out_file = out_dir / f"candidate_{safe_name}_{vid[:8]}.mp3"
            out_file.write_bytes(audio)
            manifest["candidates"].append({
                "voice_id": vid,
                "voice_name": vname,
                "why": reason,
                "sample_file": out_file.name,
                "sample_text": profile["sample_text"],
            })
            print(f"    -> {out_file.relative_to(ROOT)} ({len(audio)} bytes)")
        time.sleep(0.3)  # rate limit politeness

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"  manifest: {out_dir / 'manifest.json'}")

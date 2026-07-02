#!/usr/bin/env python3
"""Upload per-character clean audio to ElevenLabs as Instant Voice
Clones, then generate a test line with each new voice_id.

Output: voice/notes/voice_ids.json updated with cloned voice_ids
        voice/voice_clone_test/<Name>_test.mp3  test line per character

ElevenLabs Instant Voice Cloning needs ~25-30s of clean audio and
a single audio file per clone. We use the *_clean_combined.wav
files which exclude the long multi-speaker chunks that would poison
the clone.
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

HEADERS = {"xi-api-key": API_KEY}
VOICE_IDS_PATH = ROOT / "voice" / "notes" / "voice_ids.json"
BY_CHAR = ROOT / "voice" / "by_character"
TEST_DIR = ROOT / "voice" / "voice_clone_test"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Test line per character — distinctive so we can tell voices apart
TEST_LINES = {
    "Tony": "Wow GKD looks so powerful. But I'm not afraid — I'll defend myself with my sexy saxophone riffs.",
    "Yake-oh": "Man that's some corny shit. You really think a headband makes you a flaming dragon?",
    "Erb Dean": "He's just a sell out mon. I bet he can't even do a proper downward dog.",
    "MAMA": "Tony, I'm glad you're here. Since your father died it's been so hard to knead the dough.",
    "Ji-lan": "When I was young I came to this country with nothing but the headband on my head.",
    "Trubble": "Oh yes you will. We always get what we want, you know.",
    "Slarth": "We always get what we want. You can't stop us, Tony.",
}

# ElevenLabs Instant Voice Cloning minimum: 25s of clean audio
# Per docs, samples should be 1-5 minutes for best quality, but it
# accepts shorter. We'll try and see what happens.
#
# https://elevenlabs.io/docs/api-reference/voices/add


def list_my_voices():
    r = requests.get("https://api.elevenlabs.io/v1/voices", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("voices", [])


def find_existing_clone(character: str, voices) -> str | None:
    """Return voice_id if we've already cloned this character (by name)."""
    target = f"FD3-{character}"
    for v in voices:
        if v.get("name") == target and v.get("category") == "cloned":
            return v.get("voice_id")
    return None


def upload_voice_clone(character: str, audio_path: Path) -> str:
    """Upload audio as an Instant Voice Clone. Returns voice_id."""
    url = "https://api.elevenlabs.io/v1/voices/add"
    # ElevenLabs accepts multipart/form-data with the file + name
    name = f"FD3-{character}"
    with open(audio_path, "rb") as f:
        files = {"files": (audio_path.name, f, "audio/wav")}
        data = {
            "name": name,
            "description": f"FD3 character: {character}. Source: {audio_path.name}",
        }
        r = requests.post(url, headers=HEADERS, files=files, data=data, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"Upload failed for {character}: {r.status_code} {r.text[:500]}")
    d = r.json()
    return d.get("voice_id")


def synthesize(voice_id: str, text: str, model: str = "eleven_flash_v2_5") -> bytes | None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=body, timeout=60)
    if r.status_code == 200:
        return r.content
    print(f"    TTS failed: {r.status_code} {r.text[:200]}")
    return None


def main():
    # Load existing voice_ids
    voice_ids = json.loads(VOICE_IDS_PATH.read_text()) if VOICE_IDS_PATH.exists() else {}

    # List current voices to check for existing clones
    print("Fetching existing voices...")
    my_voices = list_my_voices()
    print(f"  {len(my_voices)} voices in your account")

    # Process each cloned character
    for character, test_line in TEST_LINES.items():
        clean_wav = BY_CHAR / character / f"{character.replace(' ', '_')}_clean_combined.wav"
        if not clean_wav.exists():
            print(f"\n=== {character}: SKIP (no clean wav at {clean_wav})")
            continue

        # Skip if already in voice_ids.json
        if voice_ids.get(character, {}).get("source") == "cloned":
            print(f"\n=== {character}: SKIP (already in voice_ids.json as cloned)")
            continue

        # Check if we already uploaded but didn't save
        existing = find_existing_clone(character, my_voices)
        if existing:
            print(f"\n=== {character}: found existing clone on ElevenLabs: {existing}")
            voice_ids[character] = {
                "source": "cloned",
                "voice_id": existing,
                "voice_name": f"FD3-{character}",
                "voice_url": "https://elevenlabs.io/voice-lab",
                "clean_combined_wav": str(clean_wav.relative_to(ROOT)),
                "notes": "Found existing clone from prior run",
            }
            VOICE_IDS_PATH.write_text(json.dumps(voice_ids, indent=2))
            continue

        print(f"\n=== {character}: uploading {clean_wav.name}...")
        try:
            voice_id = upload_voice_clone(character, clean_wav)
        except Exception as e:
            print(f"  UPLOAD FAILED: {e}")
            continue
        print(f"  voice_id: {voice_id}")
        voice_ids[character] = {
            "source": "cloned",
            "voice_id": voice_id,
            "voice_name": f"FD3-{character}",
            "voice_url": "https://elevenlabs.io/voice-lab",
            "clean_combined_wav": str(clean_wav.relative_to(ROOT)),
            "notes": "Instant Voice Clone from clean_combined.wav",
        }
        VOICE_IDS_PATH.write_text(json.dumps(voice_ids, indent=2))

        # Generate test line
        print(f"  generating test line...")
        audio = synthesize(voice_id, test_line)
        if audio:
            test_file = TEST_DIR / f"{character.replace(' ', '_')}_test.mp3"
            test_file.write_bytes(audio)
            print(f"  test line: {test_file.relative_to(ROOT)} ({len(audio)} bytes)")

        time.sleep(0.5)  # politeness

    print("\n=== Final voice_ids.json ===")
    print(json.dumps(voice_ids, indent=2))


if __name__ == "__main__":
    main()

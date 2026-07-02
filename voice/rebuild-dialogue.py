#!/usr/bin/env python3
"""Rebuild character-references/dialogue_data.json from FD3-Script.md.

The current dialogue_data.json was parsed from FD3-Script.html and is
broken — character keys are contaminated with markdown scene headers,
several characters (Zoh-baggo, TK-Maxx, Jasmine) are missing or
under-counted, and some keys hold entire scene blocks instead of
dialogue lines.

FD3-Script.md is the clean reformat by Galen — use it as the source
of truth.

Output: character-references/dialogue_data.json with keys = clean
character names, values = lists of dialogue lines (one per line).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT_MD = ROOT / "FD3-Script.md"
OUT = ROOT / "character-references" / "dialogue_data.json"

# Canonical character list (from production guide + script)
CHARACTERS = {
    "Tony", "Yake-oh", "Erb Dean", "MAMA", "Ji-lan", "Trubble", "Slarth",
    "Zoh-baggo", "TK-Maxx", "Jasmine",
    "Bruce Lee", "Jackie Chan", "Steven Seagal", "Bruce Lee hologram",
    "Flaming Dragon",
    "Announcer", "Woman 1", "Woman 2",
    "Written by", "Galen Graham & Jamie Rando",
}

# How to normalize names — case-insensitive match
def normalize(name: str) -> str:
    n = name.strip()
    # canonical case mapping
    upper_map = {
        "TONY": "Tony", "YAKE-OH": "Yake-oh", "ERB DEAN": "Erb Dean",
        "MAMA": "MAMA", "JI-LAN": "Ji-lan", "TRUBBLE": "Trubble", "SLARTH": "Slarth",
        "ZOH-BAGGO": "Zoh-baggo", "TK-MAXX": "TK-Maxx", "JASMINE": "Jasmine",
        "BRUCE LEE": "Bruce Lee", "JACKIE CHAN": "Jackie Chan", "STEVEN SEAGAL": "Steven Seagal",
        "FLAMING DRAGON": "Flaming Dragon",
        "ANNOUNCER": "Announcer", "WOMAN 1": "Woman 1", "WOMAN 2": "Woman 2",
        "WRITTEN BY": "Written by",
    }
    if n.upper() in upper_map:
        return upper_map[n.upper()]
    # fallback: title case
    return n.title()


# Read the script
text = SCRIPT_MD.read_text(encoding="utf-8")
lines = text.split("\n")

# Dialogue lines look like:
#   **CHARACTER:** line content
#   *CHARACTER:* line content (italic style)
#   **CHARACTER & CHARACTER:** line content
# Action lines (no colon) are skipped.

# We use a 2-pass parser:
# Pass 1: find every line that starts with **NAME:** or *NAME:*
# Pass 2: validate against the canonical character list

# Speaker pattern: **NAME:** or *NAME:* (possibly with & for shared)
# The script format is **NAME:** (colon is INSIDE the ** markers)
# e.g. **ZOH-BAGGO:** or *TONY:*
SPEAKER_RE = re.compile(r"^\*{1,2}([A-Za-z][A-Za-z0-9 &'\-]+):\*{0,2}\s*(.*)$")

dialogue = {}  # character -> list of lines

# Track state: only collect dialogue between scene blocks (not action)
# Actually, for FD3 all dialogue is fair game, so just collect everything.
in_metadata = True  # skip the header before the first scene header
for line in lines:
    line = line.rstrip()
    # Skip the title block — lines until the first '## ' scene header
    if in_metadata:
        if line.startswith("## "):
            in_metadata = False
        else:
            continue

    # Skip empty lines and pure scene headers
    if not line.strip():
        continue
    if line.startswith("## ") or line.startswith("# ") or line.startswith("### "):
        continue
    # Skip blockquote (action) lines that don't have a speaker
    if line.startswith(">") and ":" not in line:
        continue
    # Skip horizontal rules
    if line.strip() in ("---", "***", "==="):
        continue

    # Try to match a speaker
    m = SPEAKER_RE.match(line)
    if not m:
        continue

    speaker_raw, content = m.group(1), m.group(2).strip()
    speaker = normalize(speaker_raw)

    # Skip if speaker isn't a known character (probably a stray parse)
    if speaker not in CHARACTERS:
        continue

    # Skip empty content
    if not content:
        continue

    dialogue.setdefault(speaker, []).append(content)

# Sort the output: by canonical character order, with unknown at end
def sort_key(name):
    if name in CHARACTERS:
        return (0, list(CHARACTERS).index(name))
    return (1, name)


sorted_dialogue = {k: dialogue[k] for k in sorted(dialogue.keys(), key=sort_key)}

# Write
OUT.write_text(json.dumps(sorted_dialogue, indent=2, ensure_ascii=False))

# Print summary
print(f"Wrote {OUT}")
print()
print("Per-character dialogue counts:")
print()
for ch, lines in sorted_dialogue.items():
    print(f"  {ch:<20} {len(lines):>3} lines")
total = sum(len(v) for v in sorted_dialogue.values())
print(f"  {'TOTAL':<20} {total:>3} lines")
print()
print("Unshot characters (target for this fix):")
for ch in ["Zoh-baggo", "TK-Maxx", "Jasmine"]:
    n = len(sorted_dialogue.get(ch, []))
    print(f"  {ch}: {n} lines")

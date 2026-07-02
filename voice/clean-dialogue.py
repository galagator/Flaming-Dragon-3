#!/usr/bin/env python3
"""Clean stage directions out of dialogue_data.json.

The script format includes acting notes in *asterisks* and
(parentheses) that the TTS model shouldn't speak. Clean them up:

1. Strip *...* stage directions entirely (silent removal)
2. Strip parenthetical acting notes (but keep 'pause', 'beat' as
   SSML breaks)
3. Strip "to CHARACTER:" addressed-dialogue prefixes (kept separate
   for downstream tools)
4. Strip "CHARACTER:" prefixes that got mixed into lines
5. Detect ALL-CAPS lines as shouts and add SSML emphasis

The output is a new dialogue_data_clean.json with SSML tags, plus
a backup of the original.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
IN = ROOT / "character-references" / "dialogue_data.json"
OUT = ROOT / "character-references" / "dialogue_data.json"  # overwrite in place
BACKUP = ROOT / "character-references" / "dialogue_data.unclean.json"

# Stage direction patterns
ASTERISK_ACTION = re.compile(r'\*[^*]+\*')           # *action note*
PAREN_NOTE = re.compile(r'\((?:[^)]+)\)')              # (any note)
# "to CHARACTER:" addressed dialogue prefix
ADDRESSED = re.compile(r'^\s*to\s+[A-Za-z][A-Za-z0-9 &\'\-]+:\s*', re.IGNORECASE)
# "*(to MAMA)*" — the to-prefix is inside asterisks
ASTERISK_ADDRESSED = re.compile(r'\*\(to\s+[A-Za-z][A-Za-z0-9 &\'\-]+\)\*\s*', re.IGNORECASE)


def clean_line(line: str) -> str:
    # Strip asterisk-bracketed stage directions (including "to X" variants)
    line = ASTERISK_ADDRESSED.sub('', line)
    line = ASTERISK_ACTION.sub('', line)
    # Strip "(to MAMA)" addressed dialogue
    line = re.sub(r'\(to\s+[A-Za-z][A-Za-z0-9 &\'\-]+\)\s*', '', line, flags=re.IGNORECASE)
    # Strip leading "to MAMA:" or "to MAMA " (sometimes without parens)
    line = ADDRESSED.sub('', line)
    # Strip "(sassy head shake)", "(looks at X)", etc. — but PRESERVE timing cues
    # Timing cues: pause, beat, silence, long pause, dramatic pause
    def _paren_replace(m):
        inner = m.group(1).strip().lower()
        if inner in ("pause", "beat", "silence", "long pause", "dramatic pause", "short pause"):
            return '<break time="700ms"/>'
        if inner in ("quick pause",):
            return '<break time="300ms"/>'
        if inner in ("long silence",):
            return '<break time="1500ms"/>'
        return ''  # strip other parens
    line = re.sub(r'\(([^)]+)\)', _paren_replace, line)
    # Clean up whitespace
    line = re.sub(r'\s+', ' ', line).strip()
    # Strip leading "CHARACTER:" if it leaked in
    line = re.sub(r'^[A-Z][A-Z0-9\- &\'\.]{2,}:\s*', '', line)
    # SSML convert ALL-CAPS lines (just shouting) — wrap in <emphasis> not in caps
    if line.isupper() and len(line) > 3:
        line = '<emphasis level="strong">' + line.lower().capitalize() + '</emphasis>'
    return line


def main():
    d = json.loads(IN.read_text())
    # Backup
    BACKUP.write_text(json.dumps(d, indent=2, ensure_ascii=False))

    cleaned = {}
    for ch, lines in d.items():
        if not isinstance(lines, list):
            cleaned[ch] = lines
            continue
        new_lines = []
        for line in lines:
            if not isinstance(line, str):
                new_lines.append(line)
                continue
            cleaned_line = clean_line(line)
            if cleaned_line:  # skip empty
                new_lines.append(cleaned_line)
        cleaned[ch] = new_lines

    OUT.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False))

    # Show before/after for a few examples
    print(f"Original saved to: {BACKUP.relative_to(ROOT)}")
    print(f"Cleaned saved to:  {OUT.relative_to(ROOT)}")
    print()
    print("Sample diffs:")
    for ch in ['Zoh-baggo', 'Erb Dean', 'Tony', 'Trubble', 'Ji-lan']:
        if ch not in d:
            continue
        for i, (orig, new) in enumerate(zip(d[ch], cleaned[ch])):
            if orig != new and i < 3:
                print(f"  {ch} [{i}]:")
                print(f"    - {orig}")
                print(f"    + {new}")


if __name__ == "__main__":
    main()

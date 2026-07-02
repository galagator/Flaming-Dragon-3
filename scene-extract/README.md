# Footage Face Tagger

**Open:** http://localhost:6060/footage-face-tagger.html

Tag the 296 face crops extracted from the original shot scenes. Once tagged,
the assigned crops get copied into `../character-references/` as
`<Character>NN.jpg`, joining the existing Google-Photos-based references.

## Pipeline

```
scenes/*.mp4
  → ffmpeg 0.5 fps (this/extract_footage_frames.py)
  → dHash dedup
  → YuNet face detection (this/extract_footage_frames.py)
  → face crops 512x512 in scene-extract/faces/<scene>/face_NNNNN.png
  → THIS TAGGER → tagged with character name
  → next step: copy tagged crops into character-references/<Char>NN.jpg
```

## Running the extract

```bash
/home/galagator/.hermes/venvs/fd3-frames/bin/python3 \
  /mnt/d/Projects/FD3/actor-photos-raw/extract_footage_frames.py
```

Takes ~30s. Overwrites `scene-extract/` (gitignored — regenerable).

## Tagger UX

- 296 face tiles, 11 character chips (Tony, MAMA, Erb Dean, Trubble, Slarth, Yake-oh, Galen / Ji-lan, Jasmine, Zoh-baggo, TK-Maxx, "Not in film")
- Click a tile → popup with character picker
- Number keys 1-9 = quick-pick from the popup
- Right-click tile = clear current tag
- Filter chips show count per character; click to filter
- "Untagged only" toggle for cleanup passes
- Autosaves to `actor-photos-raw/fd3-footage-tags.json` on every change (600ms debounce)
- "Save Now" forces flush

## Per-scene expected counts (rough)

| Scene | Tony | MAMA | Erb Dean | Trubble | Slarth | Yake-oh | Notes |
|---|---|---|---|---|---|---|---|
| 1 | ~15 | – | ~10 | – | – | ~10 | lounge room |
| 2 | ~5 | – | – | ~10 | ~10 | – | walking montage |
| 3 | ~15 | ~15 | – | ~5 | ~10 | – | restaurant |
| 4 | ~20 | – | – | ~10 | ~10 | – | mall chase |
| 5 | ~20 | – | – | – | – | – | bridge / sax |
| 6 | ~15 | – | ~10 | – | – | ~15 | tony's house |

## After tagging

Once 5+ of each shot character is tagged, run the copy step (TODO) to
populate `character-references/`:

```bash
/home/galagator/.hermes/venvs/fd3-frames/bin/python3 \
  /mnt/d/Projects/FD3/actor-photos-raw/copy_tagged_faces.py
```

That script reads `fd3-footage-tags.json`, finds each face crop path,
and writes `<Prefix>##.jpg` into `character-references/` using the
existing per-character counter (so Tony12.jpg comes after Tony11.jpg).

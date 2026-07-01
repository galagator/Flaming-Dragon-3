# Flaming Dragon 3

**Flaming Dragon 3** is an unfinished comedy kung-fu short film revival project. Six scenes and the GKD commercial were already shot; the goal is to finish the missing scenes using an AI-assisted production workflow while preserving the look, cast, tone, and low-budget parody energy of the original footage.

## Repository Contents

| Path | Purpose |
|---|---|
| `FD3-Script.html` | Original Google Docs HTML export of the script. Kept as source/archive. |
| `FD3-Script.md` | Clean reformatted script with consistent character names. |
| `AI-PRODUCTION-GUIDE.md` | Current AI workflow notes: what's shot, what's missing, character descriptions, recommended pipeline. |
| `scenes/` | Shot video scenes and GKD commercial. Video files are tracked with Git LFS. |
| `scene-captures/` | Raw still frames extracted from the shot footage for review and analysis. |
| `character-references/` | Reserved for curated character reference images, e.g. `Tony01.jpg`, `Ji-Lan01.jpg`, `Jasmine01.jpg`. |
| `images/` | Existing image assets/reference art. |

## Shot Footage

Current shot material:

- `GKD Commercial(1).mp4` — 35.8s, 1080p
- `Scene 1.mp4` — Tony's Lounge Room
- `Scene 2.mp4` — Fruity Groovin
- `Scene 3.mp4` — The Goons Descend
- `Scene 4.mp4` — Chinatown Mall / chase / beatdown
- `Scene 5.mp4` — Bridge Under Moonlight / sax scene
- `Scene 6.mp4` — Tony's House

Total shot footage is roughly 10 minutes.

## Next Production Steps

1. Add curated character references into `character-references/`.
2. Add photos of actors intended for unshot characters: Zoh-baggo, TK-Maxx, Jasmine, etc.
3. Generate key art/storyboards for missing scenes.
4. Use FAL / gpt-image / ComfyUI-style workflows to produce video inserts.
5. Assemble generated scenes with the existing footage in an NLE.

## Git LFS

Video files are large and tracked with Git LFS. Before cloning/pulling footage:

```bash
git lfs install
git lfs pull
```

## Repo

GitHub: <https://github.com/galagator/Flaming-Dragon-3>

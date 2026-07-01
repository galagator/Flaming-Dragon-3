# AGENTS.md — Flaming Dragon 3

Guidance for AI/code agents working in this repo.

## Project Intent

This is a short-film restoration/completion repo, not a normal software project. Preserve the original shot material, script tone, and production context. The job is to help finish an unfinished comedy kung-fu short using AI-assisted character references, storyboards, video generation, audio, and edit planning.

## Directory Rules

- `scenes/` contains original shot video footage. Treat it as source material. Do not overwrite it.
- `scene-captures/` contains raw still frames extracted from the videos. These are analysis/capture assets, not curated character sheets.
- `character-references/` is reserved for curated character references named like `Tony01.jpg`, `Ji-Lan01.jpg`, `Jasmine01.jpg`, etc.
- `FD3-Script.html` is the original exported script. Preserve it.
- `FD3-Script.md` is the working clean script. Edit this for formatting/continuity passes.
- `AI-PRODUCTION-GUIDE.md` is the active workflow and production bible. Keep it updated when workflow decisions change.

## Git / Storage

- Video files must stay in Git LFS. `.gitattributes` tracks `*.mp4`, `*.mov`, and `*.mkv`.
- Before adding large media, check that it will be tracked by LFS:

```bash
git lfs track
git check-attr filter -- path/to/file.mp4
```

- Do not commit generated throwaway renders unless they are selected deliverables.

## Script Normalization

Use these canonical character names:

- Tony
- Yake-oh
- Erb Dean
- MAMA
- Ji-lan
- Trubble
- Slarth
- Zoh-baggo
- TK-Maxx
- Jasmine

Avoid reintroducing placeholders like `GOON1`, `GOON2`, `GOON3`, `GOON4`, or `THUG1` in the working script.

## AI Workflow Notes

- Prefer reference-based generation over text-only generation for any shot character.
- Tony appears across most missing scenes; every Tony generation should use real reference imagery.
- Keep the AI scenes visually compatible with the existing low-budget indie footage. Over-polished cinematic output will clash.
- For unshot characters, use the actor photos supplied by the user as source references.
- Scene-capture stills are useful for lighting, wardrobe, composition, and continuity.

## Verification

There is no canonical test suite. For repo changes, run targeted checks instead:

```bash
git status --short
git lfs ls-files
find scene-captures -maxdepth 1 -type f | wc -l
grep -R "GOON1\|GOON2\|GOON3\|GOON4\|THUG1" FD3-Script.md || true
```

If editing the script or production guide, verify the relevant names/paths changed as intended before committing.

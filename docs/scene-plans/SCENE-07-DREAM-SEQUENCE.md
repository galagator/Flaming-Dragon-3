# Scene 7 Construction Plan — Dream Sequence

> **For Hermes:** Use subagent-driven-development skill if executing this plan task-by-task.

**Goal:** Build Scene 7, the first AI-generated missing scene after the shot footage, as a short dream-recap sequence starring Tony.

**Architecture:** Keep this as a contained pipeline test: one generated bedroom setup, short dream inserts, recycled audio/visual callbacks from Scenes 1–6, and simple edit/composite work. Avoid glossy AI cinema; match the low-budget kung-fu comedy tone of the existing footage.

**Tech Stack:** FD3 repo assets, `server.js` dashboard on port 6060, `character-references/Tony*.jpg`, generated stills/video via available AI tools, final edit in NLE or scripted ffmpeg assembly.

---

## Status

- **Target scene:** `SCENE 7 — DREAM SEQUENCE`
- **Source:** `FD3-Script.md:236-243`
- **Characters:** Tony only
- **Estimated duration:** 25–45 seconds
- **Resolution target:** 720p unless the final edit standard changes
- **Purpose:** Bridge Scene 6 into Scene 8A by showing Tony processing the day’s humiliation, MAMA’s danger, and the call to train.

## Source Script Beat

Tony is in bed in PJs and an eye mask, tossing and turning. The dream recaps the key emotional/comedy beats from the day:

1. “Why bother with fighting” / pacifist Tony.
2. Friends ripping on him.
3. MAMA talking about how hard things are.
4. Goons calling him “doughboy”.
5. Goons threatening MAMA.
6. Final fork-off-table audio sting.

## Creative Direction

- **Look:** Low-budget indie comedy, not polished superhero trailer.
- **Dream language:** Warped flashes, cheap VHS smear, pasta/fork/saxophone/GKD contract imagery, overlaid faces, exaggerated zooms.
- **Tony continuity:** Use Tony face refs heavily. Glasses may be off while sleeping, but include hair/face consistency.
- **Bedroom:** Single bed, kids’ sheets, awkward grown-man-in-childhood-room vibe, PJs, eye mask.
- **Comedy rule:** It should feel stupid on purpose. Cheap, weird, memorable beats beat expensive-looking generic AI.

## Required Existing Assets

- `FD3-Script.md` — scene source.
- `AI-PRODUCTION-GUIDE.md` — overall pipeline notes.
- `character-references/Tony01.jpg` through `Tony11.jpg` — face refs.
- Existing edited footage/audio from Scenes 1–6 if available outside repo.
- Any raw scene audio/dialogue exports if available.

## New Assets To Create

- `generated/scene-07/frames/` — generated stills/keyframes.
- `generated/scene-07/video/` — generated video clips.
- `generated/scene-07/audio/` — extracted or generated dream audio.
- `generated/scene-07/edit/` — rough assembly exports.
- `generated/scene-07/prompts.md` — final prompts and generation notes.
- `generated/scene-07/shotlist.md` — final shot list and status.

Do not commit huge generated videos unless explicitly wanted. Commit prompts, shotlist, and small stills only if useful.

## Proposed Shot List

| Shot | Duration | Description | Source |
|------|----------|-------------|--------|
| 7.01 | 4s | Bedroom wide: Tony asleep in single bed, kids’ sheets, eye mask, moonlight. | AI generated |
| 7.02 | 3s | Close-up: Tony grimaces/tosses, bedsheets twisting like noodles. | AI generated |
| 7.03 | 3s | Dream flash: Yake-oh/Erb Dean mocking him, distorted audio. | Existing footage/audio or stylized still |
| 7.04 | 4s | Dream flash: MAMA kneading dough, talking hardship, restaurant lights flicker. | Existing footage/audio or stylized still |
| 7.05 | 4s | Dream flash: Trubble/Slarth loom huge, “doughboy” echo. | Existing footage/audio or stylized still |
| 7.06 | 4s | Tony in bed trapped under a giant pasta sheet/contract. | AI generated |
| 7.07 | 4s | GKD logo/contract/fork/saxophone spiral montage. | AI generated/composite |
| 7.08 | 3s | Fork audio sting: fork falls in dream void, Tony jolts awake. | AI generated + SFX |
| 7.09 | 3s | Tony sits bolt upright, terrified, hard cut to morning/Scene 8A. | AI generated |

Keep the first pass under 10 shots. If it drags, cut harder.

## Audio Plan

1. Prefer real audio snippets from the existing shot scenes.
2. If clean dialogue is not available, use muffled dream fragments rather than full regenerated dialogue.
3. Layer these sounds:
   - low bedroom room tone
   - exaggerated tossing/blanket rustle
   - dreamy whoosh/reverse cymbal transitions
   - pasta slap/stretch sounds
   - fork table/floor sting at the end
4. Avoid pristine narration. Dream fragments should be messy and comic.

## AI Generation Strategy

### Base Tony Bedroom Prompts

Use Tony face references and generate 2–3 keyframes first.

Prompt starter:

```text
Low-budget indie kung fu comedy film still, Tony, Asian man with dark hair and expressive face, sleeping in a small bedroom in pajamas and a silly eye mask, single bed with childish bedsheets, moonlight through blinds, awkward grown man in childhood bedroom, 720p camcorder movie look, slight grain, not glossy, comedic tone
```

Negative direction:

```text
no luxury bedroom, no cinematic superhero lighting, no perfect fashion model, no extra people, no clean commercial look, no text artifacts
```

### Dream Insert Prompt Motifs

Use these as separate keyframes or overlays:

```text
surreal dream montage, giant pasta noodles twisting around a kung fu contract, fork spinning through darkness, saxophone floating in the air, cheap VHS smear, low-budget comedy, red and green restaurant lighting
```

```text
Tony trapped under an oversized pasta sheet like a blanket, GKD contract papers swirling around him, absurd kung fu comedy dream, intentionally corny low-budget film still
```

### Consistency Rule

Any shot showing Tony’s face must use at least one `character-references/Tony*.jpg` image as reference. Do not generate Tony from text only.

## Implementation Tasks

### Task 1: Create Scene 7 workspace

**Objective:** Create a clean folder structure for all Scene 7 work.

**Files:**
- Create: `generated/scene-07/frames/.gitkeep`
- Create: `generated/scene-07/video/.gitkeep`
- Create: `generated/scene-07/audio/.gitkeep`
- Create: `generated/scene-07/edit/.gitkeep`
- Create: `generated/scene-07/prompts.md`
- Create: `generated/scene-07/shotlist.md`

**Commands:**

```bash
cd /mnt/d/Projects/FD3
mkdir -p generated/scene-07/{frames,video,audio,edit}
touch generated/scene-07/frames/.gitkeep generated/scene-07/video/.gitkeep generated/scene-07/audio/.gitkeep generated/scene-07/edit/.gitkeep
```

**Verify:**

```bash
cd /mnt/d/Projects/FD3
find generated/scene-07 -maxdepth 2 -type d | sort
```

Expected: folders for `audio`, `edit`, `frames`, and `video`.

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07
git commit -m "chore: scaffold Scene 7 workspace"
```

### Task 2: Build final Scene 7 shotlist

**Objective:** Convert the proposed shot list into a trackable production sheet.

**Files:**
- Create/modify: `generated/scene-07/shotlist.md`

**Content:**

```md
# Scene 7 Shotlist — Dream Sequence

| Shot | Status | Duration | Type | Description | Asset Path | Notes |
|------|--------|----------|------|-------------|------------|-------|
| 7.01 | TODO | 4s | AI video | Tony asleep in bedroom wide | generated/scene-07/video/scene7_01_bedroom_wide.mp4 | 720p |
| 7.02 | TODO | 3s | AI video | Tony tossing close-up | generated/scene-07/video/scene7_02_tossing_close.mp4 | Use Tony refs |
| 7.03 | TODO | 3s | Flashback | Friends mocking Tony | TBD | Use existing footage/audio if available |
| 7.04 | TODO | 4s | Flashback | MAMA hardship memory | TBD | Use existing footage/audio if available |
| 7.05 | TODO | 4s | Flashback | Goons doughboy threat | TBD | Use existing footage/audio if available |
| 7.06 | TODO | 4s | AI video | Tony trapped under pasta/contract | generated/scene-07/video/scene7_06_pasta_contract.mp4 | Dream gag |
| 7.07 | TODO | 4s | Composite | Fork/sax/GKD spiral | generated/scene-07/video/scene7_07_spiral.mp4 | Cheap VHS look |
| 7.08 | TODO | 3s | AI video/SFX | Fork sting, Tony jolts | generated/scene-07/video/scene7_08_fork_jolt.mp4 | Hard audio hit |
| 7.09 | TODO | 3s | AI video | Tony wakes upright | generated/scene-07/video/scene7_09_wakeup.mp4 | Cut to Scene 8A |
```

**Verify:**

```bash
cd /mnt/d/Projects/FD3
git diff -- generated/scene-07/shotlist.md
```

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/shotlist.md
git commit -m "docs: add Scene 7 shotlist"
```

### Task 3: Write reusable prompts

**Objective:** Save prompts so generation is repeatable.

**Files:**
- Create/modify: `generated/scene-07/prompts.md`

**Prompt blocks to include:**

```md
# Scene 7 Prompts

## Tony bedroom wide
Low-budget indie kung fu comedy film still, Tony, Asian man with dark hair and expressive face, sleeping in a small bedroom in pajamas and a silly eye mask, single bed with childish bedsheets, moonlight through blinds, awkward grown man in childhood bedroom, 720p camcorder movie look, slight grain, not glossy, comedic tone

## Tony tossing close-up
Low-budget indie kung fu comedy close-up, Tony asleep in pajamas and eye mask, grimacing and tossing in bed, kids bedsheets twisted like noodles, moonlit bedroom, cheap practical lighting, weird dream energy, 720p camcorder look

## Dream pasta contract gag
Tony trapped under an oversized pasta sheet like a blanket, GKD contract papers swirling around him, fork and saxophone floating in surreal dream space, absurd kung fu comedy, intentionally corny low-budget film still, VHS smear

## Negative prompt
luxury bedroom, glossy superhero lighting, extra people, text artifacts, fashion model, high-end commercial, perfect studio lighting
```

**Verify:**

```bash
cd /mnt/d/Projects/FD3
git diff -- generated/scene-07/prompts.md
```

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/prompts.md
git commit -m "docs: add Scene 7 generation prompts"
```

### Task 4: Generate 3 still keyframes

**Objective:** Validate Tony consistency before making video.

**Inputs:**
- `character-references/Tony01.jpg`
- `character-references/Tony02.jpg`
- `character-references/Tony03.jpg`
- `generated/scene-07/prompts.md`

**Outputs:**
- `generated/scene-07/frames/scene7_01_bedroom_wide.jpg`
- `generated/scene-07/frames/scene7_02_tossing_close.jpg`
- `generated/scene-07/frames/scene7_06_pasta_contract.jpg`

**Verification:**

Open the stills and check:

- Tony reads as the same person.
- Bedroom is low-budget, not glossy.
- No extra characters.
- No gibberish text.
- Comedy tone is intact.

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/frames/*.jpg generated/scene-07/prompts.md
git commit -m "art: add Scene 7 keyframes"
```

### Task 5: Extract or identify flashback audio/video beats

**Objective:** Find the real footage/audio snippets that make the dream feel connected to the shot material.

**Candidate beats:**

- Tony: “Hey guys why do you even bother with fighting…”
- Yake-oh/Erb Dean mocking Tony.
- MAMA hardship line from Scene 3.
- Trubble/Slarth “doughboy” threat.
- Fork thrown/falling audio sting.

**Files:**
- Create/modify: `generated/scene-07/audio/audio-notes.md`

**If source clips are available, export short WAV/MP4 snippets:**

```bash
cd /mnt/d/Projects/FD3
mkdir -p generated/scene-07/audio
```

Document exact source filenames and timestamps in `audio-notes.md`.

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/audio/audio-notes.md
git commit -m "docs: map Scene 7 dream audio beats"
```

### Task 6: Generate short AI video clips

**Objective:** Turn approved keyframes into short video shots.

**Outputs:**
- `generated/scene-07/video/scene7_01_bedroom_wide.mp4`
- `generated/scene-07/video/scene7_02_tossing_close.mp4`
- `generated/scene-07/video/scene7_06_pasta_contract.mp4`
- `generated/scene-07/video/scene7_08_fork_jolt.mp4`
- `generated/scene-07/video/scene7_09_wakeup.mp4`

**Rules:**

- Keep clips short: 3–4 seconds.
- Prefer subtle movement: tossing, breathing, blanket movement, eye-mask shift.
- Avoid long AI action shots; they drift.

**Verify:**

- Tony remains recognizable.
- No face melt.
- No random extra limbs.
- Movement is usable in a fast montage.

**Commit:**

Usually do **not** commit large MP4 files unless the repo is intended to store generated media. Instead commit notes:

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/shotlist.md generated/scene-07/prompts.md
git commit -m "docs: update Scene 7 generated clip notes"
```

### Task 7: Build rough edit

**Objective:** Assemble a first-pass Scene 7 sequence.

**Output:**
- `generated/scene-07/edit/scene7_rough_v1.mp4`

**Edit order:**

1. Tony asleep wide.
2. Tossing close-up.
3. Flashback smash cuts from Scenes 1–6.
4. Pasta/contract dream gag.
5. GKD/fork/sax spiral.
6. Fork audio sting.
7. Tony jolts awake.
8. Hard cut to Scene 8A setup.

**Style:**

- Fast cuts.
- Wavy dissolve/cheap VHS distortion.
- Audio echoes.
- Slightly too loud fork sting.

**Verify:**

Watch it without explaining it. It should communicate: Tony is anxious, MAMA is in danger, training is next.

### Task 8: Review and lock Scene 7

**Objective:** Decide whether Scene 7 is good enough to move on.

**Acceptance Criteria:**

- Runtime lands between 25 and 45 seconds.
- Tony is recognizable in generated shots.
- Scene connects emotionally/comically to Scenes 1–6.
- It ends cleanly into Scene 8A training.
- No distracting AI artifacts survive longer than a quick dream flash.
- Audio carries the recap even if visuals are surreal.

**Commit:**

```bash
cd /mnt/d/Projects/FD3
git add generated/scene-07/shotlist.md generated/scene-07/prompts.md docs/scene-plans/SCENE-07-DREAM-SEQUENCE.md
git commit -m "docs: lock Scene 7 construction notes"
```

## Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Tony face drift | Use Tony face refs for every Tony frame; keep generated shots short. |
| AI scene looks too polished | Add explicit low-budget/VHS/camcorder language; grade down in edit. |
| Dream montage becomes confusing | Anchor with real audio snippets from Scenes 1–6. |
| No clean source audio | Use muffled fragments and SFX instead of full regenerated lines. |
| Generated video artifacts | Hide with fast cuts, overlays, VHS smear, and dream logic. |
| Scene bloats | Cap at 8–10 shots and 45 seconds. |

## Immediate Next Action

Before generating video, create the Scene 7 workspace and write `generated/scene-07/prompts.md` + `generated/scene-07/shotlist.md`. Then generate only three still keyframes for review. Do not jump straight to full video generation.

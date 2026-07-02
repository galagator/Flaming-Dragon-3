# Flaming Dragon 3 — Production Analysis & AI Workflow Guide

*Generated from analysis of shot footage, script, and available tools*

---

## 1. WHAT'S SHOT (Completed)

| Scene | Duration | Content | Characters Visible |
|-------|----------|---------|-------------------|
| GKD Commercial | 35.8s, 1080p | Ji-lan's infomercial with disciples | Ji-lan, crowd |
| Scene 1 | 77.6s, 720p | Tony's Lounge Room | Tony, Yake-oh, Erb Dean |
| Scene 2 | 81.2s, 720p | Fruity Groovin (walking montage) | Tony, Trubble, Slarth |
| Scene 3 | 99.3s, 720p | The Goons Descend (restaurant) | Tony, MAMA, Trubble, Slarth |
| Scene 4 | 123.8s, 720p | Chinatown Mall (chase + beatdown) | Tony, Trubble, Slarth |
| Scene 5 | 104.2s, 720p | Bridge Under Moonlight (sax crying) | Tony |
| Scene 6 | 67.9s, 720p | Tony's House (bursts in, enlists help) | Tony, Yake-oh, Erb Dean |

**Total shot:** ~10 minutes

## 2. WHAT'S MISSING (Needs AI)

| Scene | Content | Key Challenge |
|-------|---------|---------------|
| Intro + Sitcom | Flaming Dragon origin text + TV show parody | Text overlay, short scene |
| Scene 7 | Dream Sequence (Tony in bed, recap) | Trippy visuals |
| Scene 8a | Park meditation training | Yake-oh + Tony (shot actors) |
| Scene 8b | GKD HQ — Ji-lan, MAMA held hostage | Ji-lan, Zoh-baggo, TK-Maxx (unshot) |
| Scene 8c | Park fight — Zoh-baggo + TK-Maxx | Fight choreography, new goons |
| Scene 8d | Office — Ji-lan watches, sends Trubble+Slarth | Ji-lan |
| Scene 8e | Escape from Trubble + Slarth | Pursuit |
| Scene 9 | Dirt Bowl party — Tony gets phone call | Crowd scene, Ji-lan voice |
| Scene 10 | Spirit Path — Bruce Lee, Jackie Chan, Segal | Celebrity likenesses |
| Scene 11 | Tony as Flaming Dragon, dirt bowl fight | Tony in costume, crowd |
| Scene 12 | Morning after with Jasmine | Jasmine (new character) |
| Scene 13 | Deaths Dam — final showdown | Full cast, action, sushi bomb |
| Scene 16 | Post-credits — Jasmine's baby | Newborn + kung fu baby |

**Total missing:** ~15-20 minutes

## 3. CHARACTER REFERENCE GUIDE (From Shot Footage)

### Shot Characters (extract frames for AI reference)

| Character | Description | Key Features |
|-----------|-------------|--------------|
| **Tony** | Asian male, glasses, dark hair in ponytail/bun | Black-rimmed glasses, white button-down shirt, business-casual, expressive |
| **Yake-oh** | Caucasian, blonde man bun, ear gauges | Large black ear tunnels, denim jacket, goatee, laid-back stoner vibe |
| **Erb Dean** | Caucasian, dreadlocks under beanie | Camo shirt, barefoot, Rastafarian/hippie style, comedic |
- **MAMA** | Latina woman, dark hair pulled back, gold stud earring | Red apron with white snowflake pattern, white shirt, frazzled |
| **Jasmine** | Caucasian, vibrant red hair, party attire | Red top with low scoop neckline, dark fitted trousers |
| **Zoh-baggo** | Caucasian, shoulder-length dark brown hair, denim jacket | Business-casual goon, breaks heel in fight scene |
| **Ji-lan** | Caucasian, shaved head, full reddish-brown beard | White shirt under black polo with "VO" logo, blue eyes, cult-leader infomercial vibe |
| **Trubble** | Short brown hair, light stubble | Full sleeve tattoo (left arm), black t-shirt with white text, brown work boots |
| **Slarth** | (Partially visible — dark clothing) | Wears dark jacket/hoodie, second goon |

### Characters NOT Shot (need AI generation)

| Character | Role | Notes |
|-----------|------|-------|
| **Zoh-baggo** | Female goon | Breaks heel in fight |
| **TK-Maxx** | Goon | Fights Erb Dean, KOd by Yake-oh |
| **Jasmine** | Tony's love interest | "White belt in Suq yo Wang" |
| **Bruce Lee** | Spirit guide | Celebrity — need likeness clearance |
| **Jackie Chan** | Spirit guide | Celebrity |
| **Steven Seagal** | Spirit guide | Celebrity — intentionally ridiculous |
| **Announcer** | Voiceover | Voice only or simple character |
| **Woman 1 & 2** | Sitcom actors | Quick throwaway scene |

## 4. AI WORKFLOW RECOMMENDATION

### Available Tools on This System

| Tool | What It Does | Key For FD3 |
|------|--------------|-------------|
| **FAL AI Key** (gpt-image-2 via `~/.hermes/.env`) | Image gen with reference-image editing | Character design, frame generation |
| **genmedia-cli** (`genmedia`) | FAL CLI — upload, run, download | Batch img2img, video model access |
| **ComfyUI skill** (scripts in `~/.hermes/skills/creative/comfyui/`) | Local/cloud Stable Diffusion + video workflows | Character consistency, img2video |
| **gpt-image skill** (scripts in `~/.hermes/skills/creative/gpt-image/`) | FAL gpt-image-2 endpoint | Quick character renders, edit endpoint |

### Recommended Pipeline

#### Phase 1: Build Character Reference Packs
```
[Shot footage] → Extract best frames of each character → Build character sheet
```

1. **Extract clean frames** of each actor from shot footage (already done — 32 frames in `scene-captures/`)
2. **Crop face/body** for each character → create curated reference sheets in `character-references/` (for example `Tony01.jpg`, `Ji-Lan01.jpg`)
3. **For unshot characters** (Zoh-baggo, Jasmine, TK-Maxx): take the user's photographs of the real people who were meant to play them → use as face references
4. **Test consistency** with gpt-image-2 edit endpoint: pass character reference + scene description

**Command pattern:**
```bash
# Upload character reference to FAL CDN
genmedia upload ./character-references/Tony_best_face.jpg

# Generate character in new scene using reference
python3 ~/.hermes/skills/creative/gpt-image/scripts/generate.py \
  -p "Tony, an Asian man with glasses, white button-down shirt, looking determined in a park, cinematic lighting, kung fu comedy" \
  -i https://fal.media/files/.../reference.jpg \
  --size landscape --quality medium
```

#### Phase 2: Key Art & Storyboarding
For the unshot scenes, generate keyframe images first:
- 8a: Park training (Tony + Yake-oh — use shot actor refs)
- 8b: GKD HQ interior (Ji-lan + MAMA hostage)
- 10: Spirit path (Bruce/Jackie/Segal holograms in sky)
- 13: Deaths Dam final showdown

#### Phase 3: Video Generation
Options for generating video from the storyboard frames:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **ComfyUI + AnimateDiff/Wan** | Local video gen with image conditioning | Full control, free (GPU) | Needs WSL GPU, setup time |
| **FAL AI video models** | `genmedia run fal-ai/...` | Fast, cloud GPU billed | Cost per video |
| **RunwayML / Pika** | Direct web tools | Polished results | External service |
| **Frame-by-frame with img2img** | Generate each frame from reference | Total character control | Tedious, 24fps × duration |

**Recommended for FD3:** Start with FAL AI video models for the new characters (Ji-lan scenes, Jasmine, Zoh-baggo), and ComfyUI local img2img for scenes that need to match the shot footage exactly.

#### Phase 4: Audio
- **Voice generation**: Use the user's own recordings, or AI voice cloning for unshot characters
- **Music**: Script mentions "Heal the World" parody, "Flaming Dragon" theme song, funky music, 80s party music
- **Sound effects**: Combat sounds, sushi bomb explosion, comedy stings

#### Phase 5: Editing & Assembly
- The shot scenes are already edited as individual clips
- Generated scenes slot between the existing footage
- Final edit in standard NLE (DaVinci Resolve, Premiere)

## 5. KEY CONSIDERATIONS

### Character Consistency
- **Most critical**: Tony appears in nearly every scene. Must maintain his face, glasses, white shirt across ALL generated frames.
- **Use the edit endpoint** (reference-based generation) for every Tony frame — never generate him from text alone.
- The `gpt-image` skill's edit endpoint (`-i` flag) is designed for exactly this — pass a real photo as reference.

### Celebrity Likenesses (Scene 10)
- Bruce Lee, Jackie Chan, Steven Seagal are copyrighted likenesses
- Options:
  1. **Stylized/anime versions** (safer legally, fits comedy tone)
  2. **Lookalike actors** (photograph them + reference generation)
  3. **AI caricature** with intentional over-exaggeration (parody protection)

### Tone & Style
- The script is a **comedy/kung fu parody** with absurdist humour
- Shot footage has a **low-budget indie film** look — don't make AI scenes look too polished
- Intentionally corny/cheesy aesthetic (GKD commercial parody, gay stereotypes for comedic effect)
- **Note**: The script leans heavily on gay stereotypes for Tony's character (walking fruitily, "in an extremely gay fashion", etc.). Review for modern sensitivity.

### What About Scene 16?
- Script jumps from Scene 13 to Scene 16 — Scene 14 & 15 are missing. This may be intentional (deleted scenes) or an error.

## 6. NEXT STEPS

1. ✅ GitHub repo created: `github.com/galagator/Flaming-Dragon-3`
2. ✅ Script reformatted for naming consistency
3. ✅ Character frames extracted from shot footage
4. 🔲 **User provides photographs** of real actors for Zoh-baggo, Jasmine, TK-Maxx
5. 🔲 Build character reference sheets for each actor
6. 🔲 Generate key art/storyboards for unshot scenes
7. 🔲 Produce video for unshot scenes via FAL/ComfyUI
8. 🔲 Source audio (voice, music, SFX)
9. 🔲 Final assembly and export

### 4a. Character Turnaround Workflow (`feat/character-sheets` branch)

For each shot character, generate a 4-pose full-body turnaround (front, back, left, right) on a clean white studio background. These are the canonical references for downstream scene generation.

**Inputs** (curated from `scene-captures/` and `character-references/`, one per character):
- `Tony` ← `character-references/Tony15.jpg` (glasses on, white shirt, calm)
- `Yake-oh` ← `character-references/Yake-oh10.jpg` (man-bun + ear gauge visible)
- `Erb Dean` ← `character-references/Erb_Dean14.jpg` (dreadlocks + beanie, no sunglasses)
- `MAMA` ← `character-references/MAMA22.jpg`
- `Ji-lan` ← `character-references/Galen-Ji-lan09.jpg` (eyes visible, bald + beard)
- `Trubble` ← `character-references/Trubble15.jpg` (eyes visible, no sunglasses)
- `Slarth` ← `character-references/Slarth09.jpg` (leather-jacket Slarth, red wall)

Stage curated inputs in `.hermes/turnaround-input/<Name>.jpg` for the script to consume.

**Generation** via FAL `gpt-image-2` edit endpoint:
```bash
python3 ~/.hermes/skills/creative/gpt-image/scripts/generate.py \
  -p "Keep the person's face, hair, build, and ethnicity exactly as in the reference image. Full-body shot of <character description>. He/she is standing in a natural relaxed pose — <pose> — on a clean white studio background with soft even lighting. Low-budget indie film aesthetic, sharp focus on the subject. The person must match the reference image precisely — same face, same hair, same build, same outfit details." \
  -i .hermes/turnaround-input/<Name>.jpg \
  --size portrait --quality medium \
  --format jpeg \
  -f character-turnarounds/<Name>-<pose>.jpg
```

**Convention note:** the "left" and "right" prompts use the viewer's perspective — "turned 90 degrees to the viewer's left" means the subject is facing screen-left with their right side toward the camera. FAL's interpretation may invert this in some generations; always vision-check the result. If a profile shows the wrong side, regenerate or re-label.

**Output** in `character-turnarounds/<Name>-<pose>.jpg` (medium quality, jpeg).

---

*Generated 2026-07-02 — AI tools available: FAL (gpt-image-2, genmedia-cli), ComfyUI skill, gpt-image skill*

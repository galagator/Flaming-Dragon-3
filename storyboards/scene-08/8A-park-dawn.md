# SCENE 8A — EARLY MORNING, PARK

**Script ref:** `FD3-Script.md` § SCENE 8A
**Characters:** Yake-oh, Tony
**Location:** Public park, early morning. Grass, trees, soft golden light. Birds. Quiet.
**Tone:** Calm, instructional, gentle. Contrast with 8B's intimidation.

## Beat summary

Yake-oh teaches Tony the foundational lesson — "flow like water, be light like air" — using the swan metaphor. Tony keeps misunderstanding. No conflict yet; this is the calm before 8C's ambush.

## Shot list

| # | Framing | Action | Dialogue | Refs | Notes |
|---|---------|--------|----------|------|-------|
| 8A-1 | Wide / establishing, slow pan down from treetops | Camera tilts down through leaves to reveal two figures seated cross-legged on grass. Dawn light, long shadows, mist. Yake-oh hums a low "OHM" tone. | *(humming)* | `Yake-oh-front.jpg`, `Tony-front.jpg` | Establishes location + ritual. Sets meditative tone. Low-budget indie look — handheld, not slick. |
| 8A-2 | Medium 2-shot, eye level | Tony and Yake-oh in lotus position facing each other at slight angle. Yake-oh's eyes are closed, peaceful. Tony is fidgeting, peeking one eye open. | **YAKE-OH:** *(still humming, then softly)* Flow like water… be light like air. | `Yake-oh-front.jpg`, `Tony-front.jpg` | Tony's discomfort visible — small fidgets, glances at Yake-oh. |
| 8A-3 | Close-up, Yake-oh | Yake-oh's face, serene, slight smile. Eyes still closed. | **YAKE-OH:** The first thing you need to know… | `Yake-oh-front.jpg` | Yake-oh wise-mentor moment. Calm delivery. |
| 8A-4 | Close-up, Tony | Tony's face, confused but trying to look enlightened. Eyebrows up, head tilt. | **TONY:** You mean like boiling water? | `Tony-front.jpg` | Tony's misunderstanding lands here. Small head-nod as he convinces himself he gets it. |
| 8A-5 | Medium 2-shot, slightly wider | Yake-oh opens his eyes, looks up. Gestures to the sky with one hand. | **YAKE-OH:** More like a swan taking flight. | `Yake-oh-front.jpg`, `Tony-front.jpg` | Yake-oh's upward gesture frames the swan metaphor. |
| 8A-6 | Close-up, Tony | Tony scrunches face. Genuinely lost. | **TONY:** I don't get it. | `Tony-front.jpg` | Beat of real confusion. Comedy beat. |
| 8A-7 | Medium on Yake-oh, slight low angle | Yake-oh gestures fluidly with both hands — graceful, bird-like. Demonstrating the swan's motion. | **YAKE-OH:** You know, like the way a swan can gracefully float on water but then when it's time, it just flaps its powerful wings and it's up there. | `Yake-oh-front.jpg` | Yake-oh's explanation is physical, not abstract. The contrast with Tony's literal mind is the joke. |
| 8A-8 | Close-up, Tony | Tony's face shifts from confused to impatient. He looks off-screen at an imaginary punching bag. | **TONY:** Can't we just get to breaking boards like karate on the movies? I'm sick of this wax on wax off stuff. | `Tony-front.jpg` | Tony wants action. His "wax on wax off" line is the comedic peak of the scene. |
| 8A-9 | Medium 2-shot, eye level | Yake-oh turns to face Tony directly. Stern but patient. Holds up one finger. | **YAKE-OH:** We can either train my way or hit the highway. Open your mind and let the Kung Fu in. | `Yake-oh-front.jpg`, `Tony-front.jpg` | Final beat — Yake-oh sets the terms. Tony's expression should shift to reluctant acceptance. |

## Visual continuity

- **Lighting:** Golden hour, low sun. Long shadows. Mist at grass level.
- **Wardrobe:** Yake-oh in his usual training gear. Tony in whatever 8C continues from (check scene 6 → 8A continuity).
- **Camera style:** Handheld, indie-feel. Not stabilised. Close-ups for dialogue, wide for context.
- **No effects:** No wire-work, no VFX. Just two guys in a park.

## Scene blocking (locked)

- **Yake-oh:** always screen-LEFT in two-shots (dominant-speaker convention; teacher on left)
- **Tony:** always screen-RIGHT in two-shots
- 8A-1 (establishing wide) sets this layout first — every subsequent two-shot must match
- Single-character close-ups (8A-3, 8A-4, 8A-6, 8A-7, 8A-8) are screen-position-neutral

## Aspect ratio

Panels are generated at **4:3 (1024×768)**, not 16:9. Reason: FAL's `gpt-image-2` endpoint only accepts 6 preset sizes, and the only 16:9 preset (`landscape_16_9`, 1024×576) falls below the model's 655,360-pixel floor and is rejected. The 4:3 output is the only viable aspect for this model. To produce 16:9 finals, generate 4:3 and centre-crop locally. For this storyboard iteration we accept the 4:3 aspect; if a 16:9 deliverable is needed downstream, add a post-crop step. Note: existing FD3 footage is 1280×720 (16:9), so 4:3 storyboards will not match the footage aspect for edit-room reference.

## AI generation prompt seeds

These will be expanded to full prompts when we move to image generation. Captured here so the structure is locked before we render.

- **8A-1:** "Wide shot, early morning park, two men cross-legged on grass meditating, dawn light filtering through trees, soft mist, golden hour, low-budget indie film look, handheld camera feel"
- **8A-2:** "Medium shot, two men in lotus position facing each other, one calm and one fidgeting, park setting, soft morning light"
- **8A-9:** "Medium two-shot, one man holding up a finger speaking seriously, other man looking reluctantly accepting, park, morning light"

## Status

- [x] Shot list drafted
- [x] Image generation prompts written (final version)
- [x] Panels rendered (low quality drafts + medium quality finals)
- [x] Vision-checked all 9 panels
- [x] Scene blocking locked (Yake-oh screen-left, Tony screen-right for all two-shots)
- [x] Aspect-ratio decision documented (4:3, see note above)
- [ ] Final approval from user
- [ ] Committed to storyboarding branch

## Rendered panels

All panels are 4:3, 1024×768, generated with FAL gpt-image-2 via the bundled CLI (`~/.hermes/skills/creative/gpt-image/scripts/generate.py`) using the edit endpoint with character turnarounds as references. Drafts are in `storyboards/scene-08/drafts/`; finals are in `storyboards/scene-08/finals/`.

| Panel | File | Status | Notes |
|---|---|---|---|
| 8A-1 | `finals/8A-1.png` | PASS | Wide establishing; Yake-oh screen-left, Tony screen-right |
| 8A-2 | `finals/8A-2.png` | PASS | Two-shot; Yake-oh in lotus, Tony knee-up scratching head |
| 8A-3 | `finals/8A-3.png` | PASS | Yake-oh close-up; small studs confirmed |
| 8A-4 | `finals/8A-4.png` | PASS | Tony close-up; "thinks he gets it" expression |
| 8A-5 | `finals/8A-5.png` | PASS | Two-shot; Yake-oh gesturing sky, Tony following |
| 8A-6 | `finals/8A-6.png` | PASS | Tony close-up; genuine confusion |
| 8A-7 | `finals/8A-7.png` | PASS | Yake-oh medium; swan-wing gesture, small studs |
| 8A-8 | `finals/8A-8.png` | PASS | Tony close-up; impatient, ears normal |
| 8A-9 | `finals/8A-9.png` | PASS | Two-shot; Yake-oh finger-up, Tony reluctantly accepting |

## Iteration log

- **8A-2 v1 → v3:** First two drafts had both men calm. v3 broke the lotus framing for Tony (knee up, scratching head) and the contrast landed.
- **8A-3 v1 → v2:** v1 gave Yake-oh large black gauges. v2 added explicit "small round metal stud earrings, NOT large black gauges or plugs" and the model complied.
- **8A-8 v1 → v2:** v1 had a malformed ear and waxy skin. v2 added "ears must be normally formed, symmetric" and "avoid waxy skin" — both fixed.
- **8A-2 + 8A-5 + 8A-9 finals:** Initial medium-quality renders had Tony on screen-left. Added "STRICT SCREEN POSITIONS — non-negotiable: YAKE-OH screen-LEFT, TONY screen-RIGHT" to prompts. All three re-renders now match.

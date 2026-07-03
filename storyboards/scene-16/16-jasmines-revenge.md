# SCENE 16 — JASMINE'S REVENGE (POST-CREDITS)

**Script ref:** `FD3-Script.md` § SCENE 16
**Characters:** Jasmine (and the Flaming Dragon baby)
**Location:** Same Dirt Bowl tent from Scene 12. After the credits have rolled. The tent is the only set we need to rebuild.
**Tone:** Sequel-bait stinger. Half-joke, half-genuine cliffhanger. The flame-in-pupil reveal is the punchline.

## Beat summary

Jasmine is still living in the tent after the events of Scene 13. She gives birth to a baby wearing a kung fu outfit who will become the next Flaming Dragon. The camera zooms into the baby's eyes and reveals flame in the pupils. THE END?

## Character references

- **Jasmine:** `character-turnarounds/Jasmine-front.jpg`
- **Baby:** no real reference — the prompt describes the visual (kung fu outfit, flame in eyes) explicitly. The baby is a generated prop, not a character match.

## Model

**Nano Banana Pro** (`fal-ai/nano-banana-pro/edit`) — same as Scenes 10 / 11 / 12 / 13. 16:9, multi-ref, $0.15/image. Draft quality only for this iteration.

## Shot list

| # | Framing | Action | Dialogue | Refs | Notes |
|---|---------|--------|----------|------|-------|
| 16-1 | Wide, tent interior | The same tent from Scene 12, dimly lit. Jasmine is sitting / lying on the rumpled bedding, holding a newborn. After-credits stillness. | *(no dialogue, atmospheric beat)* | Jasmine | Establishes "we're back in the tent, after the credits rolled". |
| 16-2 | Medium close-up, Jasmine + baby | Jasmine holding the baby. The baby is in a tiny yellow kung fu outfit. Jasmine is looking down at it. Sincere, soft. | *(no dialogue, expression beat)* | Jasmine | The reveal: this is a kung fu baby. |
| 16-3 | Close-up, the baby | The baby in its yellow kung fu outfit, eyes closed / opening. Cute, low-budget prop-baby feel. | *(no dialogue)* | n/a (generated prop) | The baby. Render as a clearly-AI-generated prop, not a real infant — keeps the comedy. |
| 16-4 | Extreme close-up, the baby's eye | A single eye filling the frame. In the pupil: a small FLAME shape glowing. | *(no dialogue, the visual punchline)* | n/a (generated prop) | The zoom-in. The flame-in-pupil is the "THE END?" moment. |

## Visual continuity

- **Location:** Same tent as Scene 12. Rumpled bedding, canvas walls. The tent is the only set.
- **Lighting:** Dim, after-credits feel. A single warm practical source. Cool-blue daylight from the canvas (the credits-rolled light).
- **Wardrobe:**
  - **Jasmine:** red top (canonical), rumpled. No costume change.
  - **Baby:** tiny yellow kung fu outfit — a callback to Tony's yellow tracksuit. The visual link.
- **Camera style:** Steady, slow push-in for 16-4. The zoom is the gag.
- **Tone:** The stinger is a beat of sincere emotion, then a joke (the flame eyes), then "THE END?" — the question mark is the sequel bait.

## Scene blocking (locked)

- **Jasmine:** centred in 16-1 and 16-2, screen-LEFT in 16-3 with the baby screen-RIGHT.
- **Baby:** centred in 16-3 and 16-4. The eye extreme close-up is the only beat the baby gets solo screen time.

## Aspect ratio

**16:9, 1376×768.** Same as Scenes 10 / 11 / 12 / 13. The wide frame accommodates the slow push-in without crowding.

## Status

- [x] Shot list drafted
- [x] Image generation prompts (final version)
- [x] Draft panels rendered (Nano Banana Pro, 1K resolution, 3/4 — 16-4 landed in a later rerender pass)
- [x] Vision-checked 3/4 panels
- [x] Iteration log written
- [ ] 16-3 re-render (blocked: FAL balance exhausted mid-batch)
- [ ] Committed to storyboarding branch

## Rendered panels

All panels are 16:9, 1376×768, generated with Nano Banana Pro (fal-ai/nano-banana-pro/edit) at 1K resolution. Draft quality.

| Panel | File | Status | Notes |
|---|---|---|---|
| 16-1 | `finals/16-1.png` | PASS | Tent interior, dim warm light, Jasmine in red top holding a swaddled newborn, oil lamp + camping gear in background, canvas walls visible. The model added the oil lamp + backpacks (not in the prompt) which strengthens the after-credits stinger mood. |
| 16-2 | `finals/16-2.png` | PASS | Jasmine holding a baby in a tiny yellow kung fu outfit, looking down. |
| 16-3 | `finals/16-3.png` | NEEDS REROLL | Empty-refs error (baby panel had no character ref). Re-roll uses Jasmine as tonal anchor. Blocked by FAL balance. |
| 16-4 | `finals/16-4.png` | NEEDS REROLL | Empty-refs error (extreme close-up eye shot had no ref). Re-roll uses Jasmine. Blocked by FAL balance. |

## Iteration log

- **16-1 bonus detail:** the model added an oil lamp on a wooden crate + a hanging-clothes line + camping backpacks. Not in the prompt. The additions strengthen the "they've been living in this tent" reading of the post-credits. Kept.
- **16-3 + 16-4 (empty-ref workaround):** the baby / eye panels have no character ref. Re-rolls will use Jasmine as a tonal anchor (same fix as 11-15/11-16 and 13-6).
- **FAL balance:** 53-panel batch + 4 rerenders consumed the available FAL balance. 5 remaining rerenders (11-1, 13-4, 13-12, 16-3, 16-4) blocked until top-up.

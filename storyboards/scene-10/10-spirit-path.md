# SCENE 10 — THE SPIRIT PATH

**Script ref:** `FD3-Script.md` § SCENE 10
**Characters:** Tony, Bruce Lee, Jackie Chan, Steven Seagal
**Location:** A bushland path, a creek, daytime. Spiritual/supernatural tone — but kept grounded and low-budget.
**Tone:** Surreal, emotional, comedic homage. Tony is vulnerable; the three martial artists are mythic presences in the sky.

## Beat summary

Tony walks the spirit path, questions running. He reaches a creek, plays the sax with tears in his eyes. As soon as he starts playing, he looks up to find Bruce Lee, Jackie Chan, and Steven Seagal in the sky. They deliver the "power of the Flaming Dragon" speech. Bruce Lee throws the flaming dragon headband down. Tony puts it on, his clothes change, he becomes the Flaming Dragon.

## Character references

- **Tony:** `character-turnarounds/Tony-front.jpg` (and back/sides as needed)
- **Bruce Lee:** `character-references/celebs/Bruce_Lee_1973.jpg`, `Bruce_Lee_as_Kato_1967.jpg`
- **Jackie Chan:** `character-references/celebs/Jackie_Chan_2002-portrait.jpg`, `Jackie_Chan_2025_Locarno.jpg`
- **Steven Seagal:** `character-references/celebs/Steven_Seagal_Russia_Expo.jpg`

## Model

**Nano Banana Pro** (`fal-ai/nano-banana-pro/edit`) — Google's Gemini 3 Pro Image model on FAL. $0.15/image. Multi-reference support via `image_urls` array, native 16:9 aspect ratio, strong celebrity likeness preservation.

### Model selection (Flux 2 Pro Edit comparison)

Tested both Flux 2 Pro Edit and Nano Banana Pro on the same 3 panels (10-1, 10-4, 10-15). Results:

| Panel | Flux 2 Pro Edit | Nano Banana Pro |
|---|---|---|
| 10-1 (Tony alone in bushland) | NEEDS FIX — medium shot, didn't honor "wide" | PASS on v2 with stronger framing prompt |
| 10-4 (the reveal, 3 celebs in sky) | NEEDS FIX — composition good, **likenesses didn't transfer** (vision model: "three random divine figures, not Bruce Lee / Jackie Chan / Seagal") | NEEDS FIX on first pass — composition good, **likenesses DID transfer** (vision model: "Bruce Lee's face and yellow shirt are iconic. Jackie Chan's glasses and hairstyle are accurate. Steven Seagal's beard and hair are distinct") — remaining slop is hand anatomy and waxy skin on the sky figures |
| 10-15 (Tony as Flaming Dragon) | PASS | PASS |

**Conclusion:** Nano Banana Pro preserves celebrity likenesses where Flux 2 Pro Edit does not. The $0.15 vs $0.03 cost differential is worth it for the 15 panels of Scene 10 (~$1.80 vs ~$0.45). All Scene 10 panels will be rendered with Nano Banana Pro.

### Why not Flux Pro Kontext

`fal-ai/flux-pro/kontext` ($0.04/image) is purpose-built for character/identity preservation but only accepts a single `image_url`, not an array. For multi-celeb scenes like 10-4 and 10-11, this would require compositing multiple single-celeb renders — significantly more work. Nano Banana Pro's array support + strong likeness preservation is the better tool.

## Shot list

| # | Framing | Action | Dialogue | Refs | Notes |
|---|---------|--------|----------|------|-------|
| 10-1 | Wide / establishing of the path | Bushland path, trees, dappled light. Tony walking alone, hands in pockets, head down, looking lost. Establishing the spiritual location. | *(no dialogue, atmospheric beat)* | Tony | Establishes location + Tony's mood. The "spirit path" is just a normal bush track — the low-budget indie version of a sacred journey. |
| 10-2 | Close-up of Tony's face | Tony walking, internal monologue. Worried, questioning. | **TONY (voiceover):** Why can't I kung fu? I gotta get mama back. Boy… I really love pasta. | Tony | Internal voice. Eyes look haunted. |
| 10-3 | Medium shot at the creek | Tony is kneeling/sitting at a creek in the bush, sax in his hands. He's playing it, tears streaming. Soft natural light. | *(sax playing, internal)* | Tony | The vulnerable moment. Sax + tears = indie film emotional peak. |
| 10-4 | Wide / low-angle looking up | Tony looking up. In the sky above the trees, three glowing / luminous / supernatural figures: BRUCE LEE (centre-left), JACKIE CHAN (centre-right), STEVEN SEAGAL (right, behind or smaller). They are clearly ASTRAL / divine / not physical — luminous outlines, clouds, golden light. | *(sax stops)* | Tony, Bruce Lee, Jackie Chan, Steven Seagal | The reveal. Wide so the scale reads. The three martial artists are in the sky, not on the ground. |
| 10-5 | Medium close-up of Bruce Lee in the sky | Bruce Lee, in the sky, glowing. His face is earnest, wise. | **BRUCE LEE:** Tony, it's me — Bruce. We've been watching… | Bruce Lee, partial Tony below | Bruce Lee's introduction. He is the senior martial artist / mentor figure. |
| 10-6 | Close-up of Jackie Chan in the sky | Jackie Chan, in the sky, glowing. Smiling, blunt. | **JACKIE CHAN:** You are really a little bitch. | Jackie Chan | Jackie Chan's blunt humour lands. |
| 10-7 | Close-up of Bruce Lee in the sky, gesturing | Bruce Lee, pointing down toward Tony. | **BRUCE LEE:** But don't despair, we have a little something for you. | Bruce Lee | The promise of the gift. |
| 10-8 | Close-up of Jackie Chan in the sky | Jackie Chan, encouraging. | **JACKIE CHAN:** Yeah we gonna make a man out of you boy. | Jackie Chan | Reaffirmation. |
| 10-9 | Close-up of Steven Seagal in the sky | Steven Seagal, in the sky, glowing. His face is blank / non-expressive. He says the only line. | **STEVEN SEAGAL:** DURR DURR DURR. | Steven Seagal | The Steven Seagal joke — the lamest of the three, says the dumbest line. Visually distinguished from the other two. |
| 10-10 | Close-up of Bruce Lee in the sky, dismissive | Bruce Lee, turning toward Seagal, hand up. | **BRUCE LEE:** Shut up Segal you hack. | Bruce Lee | The roast. Bruce Lee vs. Seagal rivalry acknowledged. |
| 10-11 | Wide shot of the three in the sky | All three are now in frame. Bruce Lee and Jackie Chan on either side, Seagal behind/smaller. The flaming dragon headband glows between them. | **BRUCE LEE:** We're gonna give you the power of the FLAMING DRAGON. | Bruce Lee, Jackie Chan, Steven Seagal | The gift descends. The headband — a key prop — appears in the sky. |
| 10-12 | Wide shot, headband falling | The flaming dragon headband falls from the sky toward Tony below. Tony reaches up. | *(no dialogue)* | Tony, Bruce Lee (in sky above) | The hand-off. |
| 10-13 | Close-up of Tony putting on the headband | Tony's face as the headband touches his head. His expression shifts from grief to power. | *(no dialogue)* | Tony | The transformation. |
| 10-14 | Medium shot, clothes change | Tony's clothes are changing — from his regular white shirt + black trousers to a more powerful outfit. A visual special effect. | *(no dialogue)* | Tony | The visible transformation. |
| 10-15 | Hero shot, low angle | Tony, in his new outfit and with the flaming dragon headband, looking up at the camera. He is now the Flaming Dragon. Heavy metal guitar shred implied. | **TONY:** I AM THE FLAMING DRAGON! | Tony | The resolution. Climax of the scene. |

## Visual continuity

- **Location:** Bushland path with a creek. Daylight. Dappled light through eucalyptus trees.
- **Wardrobe:** Tony in his regular outfit (white shirt, black trousers) for 10-1 through 10-13. His new "Flaming Dragon" outfit for 10-14 and 10-15. The script doesn't specify the new outfit — keeping it iconic martial arts (a tracksuit or similar) reads best.
- **The three martial artists in the sky:** They should look LUMINOUS, ETHEREAL, ASTRAL — not just three men floating. Golden rim light, soft glow, clouds around them, slightly transparent. This is the "supernatural" framing that lets us sidestep direct celebrity photorealism.

## Scene blocking (locked)

- **Tony:** on the ground, in the path
- **Bruce Lee:** in the sky, screen-LEFT
- **Jackie Chan:** in the sky, screen-RIGHT
- **Steven Seagal:** in the sky, screen-RIGHT, smaller or behind Jackie Chan (the comic "lesser" positioning)
- For 10-15 (hero shot): Tony in the foreground, the three still visible in the sky behind him

## AI generation notes for Nano Banana Pro

Per the gpt-image skill's advice on celebrity likeness:
- Frame prompts as "luminous, divine, astral, in the sky" not as "real men floating"
- Use the multi-reference pattern: pass Bruce Lee's refs for Bruce Lee, Jackie Chan's refs for Jackie Chan, etc.
- For multi-celeb scenes (10-4, 10-11): pass all three celeb refs in the same `image_urls` array, with explicit "BRUCE LEE is the first/second reference, JACKIE CHAN is the second/third reference" labels in the prompt
- For 10-1, 10-2, 10-3, 10-13, 10-14, 10-15 (Tony only): pass Tony's ref
- For wide/establishing shots, be VERY explicit about the framing: "WIDE ESTABLISHING SHOT — full body visible from head to toe with significant space above and around the character. Camera is far back from the subject so the character occupies only the lower third of the frame and the path and trees fill the rest." Otherwise the model defaults to medium shot.
- The "in the sky" / "divine" framing lets us sidestep direct celebrity photorealism — the model renders them as astral/ethereal figures, not photoreal men floating
- 16:9 aspect ratio works directly via `aspect_ratio: "16:9"` + `resolution: "1K"` (output: 1376×768)
- Cost: ~$2.25 for all 15 Scene 10 panels at $0.15 each

## Status

- [x] Shot list drafted
- [x] Image generation prompts written
- [x] Model selected (Nano Banana Pro, after Flux comparison test)
- [x] Reference images sourced (Wikimedia Commons, all openly licensed) and uploaded to FAL CDN
- [x] Test panels rendered (3 panels: 10-1, 10-4, 10-15) — 2/3 PASS, 1 needs the re-roll that's now baked in
- [x] Flux 2 Pro Edit comparison test documented
- [ ] Full 15-panel set rendered (medium quality) — pending render pass
- [ ] Vision-checked all panels
- [ ] Committed to storyboarding branch

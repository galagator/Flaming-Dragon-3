# DESIGN.md — Flaming Dragon 3 Opener

**Surface:** Decide / Learn (one idea lands per scene — the film's premise, then the cast, then the title).
**Hero frame:** the FD3 title card at 24.0s — the moment every element is on screen at once.
**Length:** 30s, 1920×1080, 30fps, ~900 frames.

---

## Style Prompt

A deliberately low-fi, VHS-warm 90s American sitcom opening. Think **early *Friends*** titles, ***Seinfeld***, ***NewsRadio*** — single-camera freeze-frames of the cast over a sax-led theme, name cards in stacked white-on-black serif, hand-drawn flame icon, fluorescent apartment warmth, baked-in CRT scanlines. The joke is that this is a low-budget kung-fu short film using the grammar of a 1994 NBC Thursday-night sitcom.

**Mood:** warm, low-stakes, gently absurd, confident. Tony plays sax (Scene 5 of the script), so the theme *is* a sax riff — credit sax as "Music by Tony." Cast freeze-frames are wide grins and crooked glasses, not action poses.

**Reference touchstones:**
- *Friends* Season 1 title cards (white serif, black background, color frame)
- *Seinfeld* Season 5 freeze-frames (Jerry, George, Elaine, Kramer — the four-square cast)
- The "Flaming Dragon" origin text is delivered in the deadpan tone of the actual script: *"Thousands of years ago, there was this bloke, who did all this awesome blokey stuff."*

---

## Colors

| Role | Hex | Notes |
|------|-----|-------|
| **Background — deep warm black** | `#0E0805` | Tinted brown, not pure black — VHS warmth |
| **Background — sitcom warm** | `#F4E8D6` | Cream / eggshell — apartment walls, card backings |
| **Surface — title card warm white** | `#FFF8EC` | Off-white for name cards (avoids sterile #FFF) |
| **Accent — flame primary** | `#E84A1F` | Saturated orange-red — the "Flaming Dragon" ember |
| **Accent — flame glow** | `#FFB347` | Warm amber — flame highlight, title glow |
| **Accent — channel chrome** | `#1B5E9F` | Sitcom blue — small UI chrome (episode title bar, "now on NBC" feel) |
| **Ink** | `#1A0E08` | Warm near-black, not pure black — sits on cream |
| **Muted** | `#5C4A3D` | For "introducing" labels and supporting text |

**Constraint:** no more than 2 colors visible per scene. The flame is the punctuation, not the wallpaper. Black-and-cream is the default; the flame only lands on the title card.

---

## Typography

**Two families, no more.**

1. **Display: `Playfair Display`** — italic for the origin crawl and the FD3 title card. Serif weight, 90s-sitcom title-card energy. Weights: 400 italic, 700, 900.
2. **Body / labels: `Inter`** — for cast name cards, episode title bars, "with...", "and..." labels. Weights: 400, 700, 900.

**Sizes (1920×1080 canvas):**
- FD3 title: 280px, weight 900, italic
- Cast names (on cards): 72px, weight 700
- Origin crawl: 56px, weight 400 italic
- Episode label ("Episode 1 / Pilot"): 32px, weight 700, Inter, all-caps, tracking +200
- "Music by Tony" credit: 28px, weight 400, italic, Playfair

**Constraint:** every label must be a hard rule (uppercase OR italic OR weight 900) — never plain weight 400 Inter, that's the AI default slop. The only place plain text lives is the origin crawl (because it's pretending to be a 1994 voiceover).

---

## Motion

**Three motion modes, applied with intent:**

1. **Static hold + cut** — 80% of the opener. Sitcom title cards are 95% still. The first time you see Tony, the frame holds for 1.5s and he blinks once.
2. **Slow ken-burns drift** — 15%. Subtle 4% scale + 8px translate over 4s. Used on the FD3 title card and one of the freeze-frames. Never on the origin text.
3. **Single-line text reveal** — 5%. Cast name cards: each name slides up 24px and fades in over 0.6s, stagger 0.12s. Used **only** on the freeze-frame cards.

**Explicitly banned:**
- Bouncing entrances (`back.out`)
- Scale-from-zero pops
- Wipes and reveals (this isn't a YouTube intro)
- Particle systems or fire effects on the title (the flame is in the icon, not the motion)
- AutoAlpha flicker
- Any easing besides `power2.out`, `power3.out`, `sine.inOut`

---

## What NOT to Do (Hard Constraints)

1. **No pure black (`#000`).** Always `#0E0805` or `#1A0E08`. Pure black reads as modern, not 1994.
2. **No pure white.** Always `#FFF8EC` or `#F4E8D6`. Same reason.
3. **No emoji, no icons-as-SVG, no fake vintage textures.** The flame is drawn as a single inline SVG path — that's it.
4. **No background music other than the user-supplied `voice/` assets** (or silence). No MusicGen, no TTS. The opener is pre-title.
5. **No `repeat: -1` on anything.** All loops are computed finite counts. (HyperFrames hard-rule anyway.)
6. **No animations of `visibility` or `display`** — `autoAlpha` only.
7. **No call to `play()` or `pause()` on media.** Framework owns playback.
8. **No async timeline construction.** All GSAP timelines built synchronously inside the script block.
9. **No Tailwind, no CSS framework, no build step.** Plain HTML + CSS + GSAP from CDN.
10. **No "Friends were there" imitation** — this is a kung-fu short, not a sitcom pilot. The frame grammar is sitcom; the content is the FD3 cast.

---

## Hero Frame Description (the moment everything is on screen)

At t = 24.0s:
- Background: `#0E0805` warm black with subtle 4% scale-up of the FD3 wordmark.
- Foreground: the FD3 wordmark "FLAMING DRAGON" in 280px Playfair italic 900, `#FFF8EC`, with a `#E84A1F` flame SVG mark to the left of the wordmark.
- Lower-left: "EPISODE 1 / PILOT" in 32px Inter 700, `#FFB347`, all-caps.
- Lower-right: "Music by Tony" in 28px Playfair italic, `#F4E8D6` 70% opacity.
- A 1px `#5C4A3D` rule runs across at 70% height, full width.
- Cast names are gone by this beat — the title card is solo.

---

## Cast (no photos in this opener)

Per user feedback, the credits sequence is **pure typography** — actor name in Playfair Display italic, "as" in Inter lowercase italic, character name in Inter all-caps flame-glow. One name on screen at a time, two at most (Max + Kim share the final beat). No freeze-frame photos, no photo grid. The cast info is here for reference, not for image generation:

- **Kristian** as Erb Dean
- **Melanie** as Mama
- **Jakey** as Yake-oh
- **Sammy** as Slarth
- **Guy** as Trubble
- **Zoe** as Zoh-baggo
- **Max** as TK-Maxx
- **Kim** as Jasmine
- **Toan** as Tony (the "breakout role" reveal — Tony's name is the largest text on screen during this beat)

If a future variant wants a photo + name combo card, pull stills from `character-references/Tony*.jpg`, `Yake-oh*.jpg`, `Erb_Dean*.jpg`, `MAMA*.jpg`, `Galen-Ji-lan*.jpg`, `Jasmine*.jpg`. The composition is set up so a `.cast-photo` background can be dropped into each `.credit` without re-rendering the timeline.

---

## Asset Inventory

- **Flame SVG** — single inline path, 180×180, in the title-card HTML. No external file.
- **Theme music** — `music/FD3 Theme v2.mp3` (3.2 MB, 163s full length). First 30s extracted to `opener/assets/theme.mp3` via `ffmpeg -i "FD3 Theme v2.mp3" -ss 0 -t 30 -y theme.mp3`. Theme starts at 3.0s (silent cold open), ducks during the Tony reveal, recovers for the title card.
- **VHS scanlines** — pure CSS pseudo-element, 2px repeating-linear-gradient at 8% opacity. No image asset.
- **No cast photos used.**

---

## Verification (gate before render)

- [ ] No `#000` or `#FFF` in the rendered HTML.
- [ ] `Playfair Display` and `Inter` are the only font families.
- [ ] Every text element has a weight/case/italic rule — no plain 400-Inter body copy except the origin crawl.
- [ ] All GSAP tweens are deterministic, no `Math.random`, no async.
- [ ] All timelines are `paused: true` and registered on `window.__timelines`.
- [ ] No `repeat: -1`.
- [ ] `data-composition-id`, `data-start`, `data-duration`, `data-track-index` are present on every timed element.
- [ ] `npx hyperframes lint --strict` passes.
- [ ] `npx hyperframes validate` passes (WCAG 4.5:1 contrast on body, 3:1 on display).
- [ ] `npx hyperframes inspect` flags no overflow.

# SCENE 00 — FLAMING DRAGON 3 OPENER

**Script ref:** `FD3-Script.md` § FLAMING DRAGON INTRO + § INTRO CREDITS
**Characters:** Tony, Yake-oh, Erb Dean, MAMA, Ji-lan, Jasmine (freeze-frames only)
**Location:** n/a — pre-title motion graphic
**Tone:** 90s American sitcom opening. Warm, low-fi, gently absurd. The joke is a kung-fu short using *Friends* / *Seinfeld* grammar.
**Render target:** `storyboards/scene-00-opener/opener/` — HyperFrames composition (HTML + GSAP → MP4).

> **Skip:** the *TV Sitcom* scene with Woman 1 and Woman 2 is **out of scope** for this opener. The user's brief is the 90s credits-grammar applied to the **FLAMING DRAGON INTRO** + cast freeze-frames + title card. The sitcom parody lives in the script for later, not here.

---

## Beat summary

Cold open (silence + black flicker, 3s) → the FLAMING DRAGON origin text on black, italic Playfair (5s) → six-up cast freeze-frame grid with sax theme and "music by Tony" (12s) → a "and…" cream-card transition (2.5s) → the FD3 title card with flame SVG and "EPISODE 1 · PILOT" (7.5s). Total 30s. Sits in front of the first scene of the film.

---

## Shot list

| # | Framing | Action | Dialogue | Refs | Notes |
|---|---------|--------|----------|------|-------|
| 00-1 | Full black, vignette | 3 seconds of black with a soft 12-pulse opacity flicker (0.85 ↔ 1.0). Letterbox bars visible. | *(silence — theme starts at 3.0s with the origin text)* | n/a | Cold open. Reads as "the TV was just turned on" — the static settles. No cast here, no text. |
| 00-2 | Black background, left-aligned, italic Playfair | "From the script of Galen Graham & Jamie Rando" eyebrow fades in. Then line 1 of the origin text reveals bottom-up: "Thousands of years ago, there was this bloke, who did all this awesome blokey stuff. He died and then throughout the ages was reincarnated so there was always a…" Then line 2 lands with a drop: "FLAMING DRAGON." (in flame orange). Attribution "— voice-over, FD3 script § FLAMING DRAGON INTRO" appears beneath in muted small caps. **Theme (FD3 Theme v2.mp3) fades in 0→0.45 over 1.5s starting at 3.0s.** | *(narrator VO, optional — use `voice/announcer/` if you have one, otherwise theme is the only audio)* | n/a | Direct lift from `FD3-Script.md` lines 8–12. Italic Playfair 400, 56px. The drop on "FLAMING DRAGON" is flame-orange, weight 700. |
| 00-3 | Black background, centered name credits — **sitcom one-at-a-time grammar, two at most at any time** | 6 single-name credits fade in one at a time (1.5s each), then 1 dual-credit beat at the end. Top eyebrow: "INTRODUCING". Bottom: "MUSIC BY Tony" (small Playfair italic). Cast: <br>• 9.5s — **Kristian as Erb Dean** <br>• 11.0s — **Melanie as Mama** <br>• 12.5s — **Jakey as Yake-oh** <br>• 14.0s — **Sammy as Slarth** <br>• 15.5s — **Guy as Trubble** <br>• 17.0s — **Zoe as Zoh-baggo** <br>• 18.5s — **Max as TK-Maxx** & **Kim as Jasmine** (side-by-side, two at most) | *(none — FD3 Theme v2 carries the credits)* | Tony (as Music by), the 8 cast members | Pure typography. Actor name in 96px Playfair italic 700 cream. Character name in 64px Inter 900 flame-glow all-caps. "as" in 32px Inter 400 muted lowercase italic. |
| 00-4 | Black background, centered "TONY" reveal | Eyebrow "AND IN HIS BREAKOUT ROLE" fades in at top. Then the credit "**Toan as Tony**" lands huge — 140px Playfair italic for "Toan", 160px Playfair italic 900 flame-orange with text-shadow glow for "Tony". Theme ducks to 0.3 for the reveal. | *(none)* | Tony | The "star" reveal. Tony's name is the largest text on screen during this beat. Holds for ~3.5s. |
| 00-5 | Black background, centered title card | The eyebrow "FLAMING DRAGON 3" fades in at top-left, then a 1px muted rule scales in from left across 70% of the height, then the flame SVG icon scales in from 0.7 with `back.out(1.2)`, then "Flaming" in 280px Playfair italic 900 cream lands, then "Dragon 3" in 200px Playfair italic 900 flame-orange. A 4% ken-burns over 3s on the whole title-card container. Bottom-left: "EPISODE 1 · PILOT" in 32px Inter 700 flame-glow, all-caps, +0.2em tracking. **Theme recovers to 0.5 for the title card.** | *(theme up to 0.5, hold to the end of the 30s)* | n/a | The hero frame at 27.5s. The flame SVG is inline in the HTML — no external asset. |

---

## Visual continuity

- **Palette:** warm black `#0E0805`, cream `#F4E8D6`, surface `#FFF8EC`, flame `#E84A1F`, flame-glow `#FFB347`, chrome-blue `#1B5E9F` (unused in v1 — reserved for "now playing" UI on a future cut), ink `#1A0E08`, muted `#5C4A3D`. No pure black, no pure white — see `DESIGN.md` § What NOT to Do.
- **Typography:** Playfair Display (italic 400/700/900) for display + Inter (400/700/900) for labels. Origin crawl is the only plain-text-400 element, on purpose — it reads as a 1994 voiceover.
- **Camera style:** none — this is a motion graphic, not photographed footage. The cast grid does a ken-burns (4% scale) and the title card does a ken-burns (4% scale). The cast cells themselves are stills from the existing `character-references/` library, so they read as continuous with the filmed material.
- **Continuity with Scenes 1–6:** the cast cells use the same stills used in `character-sheets/`, so when Scene 1 cuts to Tony in his lounge, it's the same face. The 720p / 540p softness of the original footage carries through (the stills are JPG, not pixel-perfect).

---

## Scene blocking (locked)

- **Title card centerline:** the wordmark sits at horizontal center; flame icon is to its left, vertically aligned with the wordmark's cap-height.
- **Cast grid (3×2):** Tony top-left, Yake-oh top-center, Erb Dean top-right, MAMA bottom-left, Ji-lan bottom-center, Jasmine bottom-right. Zoh-baggo, Trubble, Slarth, TK-Maxx, Bruce Lee, Jackie Chan, Seagal are intentionally **not** in the opener — they're the antagonists and the third-act, the opener is the *home team*.
- **Eyes / glasses / earrings:** all preserved in the freeze-frame stills. The opening cast grid is the first time the audience sees these features, so they should be the most flattering stills, not the action ones.

---

## Asset pulls

- **Theme music** — `../music/FD3 Theme v2.mp3`, the first 30 seconds extracted to `opener/assets/theme.mp3` via `ffmpeg -i "FD3 Theme v2.mp3" -ss 0 -t 30 -y theme.mp3`. Theme starts at 3.0s with the origin text (silent cold open), ducks during the Tony reveal, recovers for the title card. **Replace with the full track before final render if the user wants the theme to bleed past 30s.**
- **Flame icon** — inline SVG in the composition, no external file.
- **No cast photos used.** Per user feedback, the credits are pure typography (actor name + "as" + character name), no images.

---

## Render procedure

```bash
cd /mnt/d/Projects/FD3/storyboards/scene-00-opener/opener
npm install                                          # one-time
npx hyperframes lint --strict                        # catches missing data-* attrs
npx hyperframes validate                             # WCAG contrast audit
npx hyperframes inspect                              # overflow / occlusion check
npx hyperframes render --quality draft --output ../finals/opener-draft.mp4
# review the draft, then:
npx hyperframes render --quality high --output ../finals/opener.mp4
```

**Verification (per `DESIGN.md` § Verification):**
- `ls -lh ../finals/opener.mp4` — file exists, > 1 MB
- `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 ../finals/opener.mp4` — duration ≈ 30s
- `ffmpeg -i ../finals/opener.mp4 -ss 00:00:24 -vframes 1 ../finals/hero-frame.png` — extract the title-card hero frame, eyeball it
- `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 ../finals/opener.mp4` — confirm audio track is present (even if silent placeholder)

---

## What this opener is NOT

- **Not a teaser** — it doesn't reveal plot. It reveals *cast* and *title*. Plot teaser is the cut right before Scene 1.
- **Not a montage** — there's no footage in the opener. It's a motion graphic. The 90s sitcom grammar is *cast names over music*, not *footage over music*. Footage comes at Scene 1.
- **Not the sitcom parody** — the Woman 1 / Woman 2 / canned-laughter bit is in the script and is a separate scene to be shot later. This opener skips it.
- **Not using Remotion, FLUX, FAL, or any cloud image-gen.** Pure HTML + CSS + GSAP, rendered locally via HyperFrames. The user's brief was explicit: "don't use Remotion or flux, use hyperframes instead."
- **No cast photos.** Per user feedback, the credits are pure typography. The freeze-frame cast grid from v1 was removed.

---

## Future work (not in this draft)

- [ ] Pull higher-res cast stills from `character-sheets/` if a future variant wants a photo + name combo card.
- [ ] Add a fade-from-black transition that hands off cleanly to Scene 1 (Tony in his lounge, on the sax).
- [ ] Localize the title card if there's a non-English release.
- [ ] Sync the theme fade-out with Scene 1's first frame if the film starts with a hard cut rather than a fade-from-black.

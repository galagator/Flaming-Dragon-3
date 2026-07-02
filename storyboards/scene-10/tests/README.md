# Scene 10 model comparison tests

Before committing to a model for the full 15-panel Scene 10 set, I ran 3 test panels on each of two candidate models: **Flux 2 Pro Edit** and **Nano Banana Pro**. This folder preserves those test renders for posterity.

## Test panels

- **10-1** — Tony walking alone in bushland (wide establishing shot, single ref)
- **10-4** — The reveal: 3 divine figures in sky (multi-ref, the actual test of celebrity likeness)
- **10-15** — Tony as the Flaming Dragon (single ref, transformation beat)

## Results

| Panel | Flux 2 Pro Edit | Nano Banana Pro |
|---|---|---|
| 10-1 | Medium shot (NEEDS FIX on framing) | Medium shot on v1 (NEEDS FIX); PASS on v2 with explicit "wide establishing — character in lower third" language |
| 10-4 | Composition good, **likenesses didn't transfer** ("three random divine figures, not Bruce Lee / Jackie Chan / Seagal") | Composition good, **likenesses DID transfer** ("Bruce Lee's face and yellow shirt are iconic. Jackie Chan's glasses and hairstyle are accurate. Steven Seagal's beard and hair are distinct") |
| 10-15 | PASS | PASS |

## Decision

**Nano Banana Pro wins on celebrity likeness preservation.** The $0.15 vs $0.03 cost differential is worth the ~$1.35 difference for the 15-panel Scene 10 set, given that Flux's 10-4 output doesn't carry the joke the scene is making.

## Frame files

- `10-1-flux.png` / `10-1-nano-v1.png` / `10-1-nano.png` — the prompt-framing iteration (medium → wide with stronger language)
- `10-4-flux.png` / `10-4-nano.png` — the celebrity likeness comparison
- `10-15-flux.png` / `10-15-nano.png` — both clean, no real diff

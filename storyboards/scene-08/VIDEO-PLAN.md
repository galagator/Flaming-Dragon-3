# Scene 8 — Video Generation Plan

> **Model:** `bytedance/seedance-2.0/reference-to-video` (FAL)
> **Tool:** `genmedia` CLI v0.7.0

## Overview

Convert 40 storyboard panels across 5 sub-scenes into animated video clips using Seedance 2.0's reference-to-video mode. Each shot feeds the storyboard panel + character turnaround refs + dialogue audio into the model, which generates a 4–8 second animated clip with native lip-synced dialogue and SFX.

## Sub-scenes

| Sub-scene | Panels | Characters | Dialogue lines | Est. cost (720p) |
|---|---|---|---|---|
| 8A — Park Dawn | 9 | Yake-oh, Tony | 7 | ~$13.50 |
| 8B — GKD HQ | 11 | Ji-lan, MAMA, Trubble, Slarth, Zoh-baggo, TK-Maxx | 8 | ~$16.50 |
| 8C — Park Fight | 15 | Yake-oh, Tony, Zoh-baggo, TK-Maxx | 6 | ~$22.50 |
| 8D — Dispatch Elite | 2 | Ji-lan, Trubble, Slarth | 1 | ~$3.00 |
| 8E — Park Escape | 3 | Yake-oh, Tony, Trubble, Slarth | 1 | ~$4.50 |
| **Total** | **40** | | **23** | **~$60** |

## Strategy

### Reference composition per shot

Each `genmedia run` call passes:
- `image_urls`: [storyboard_panel_CDN, character_ref_1_CDN, character_ref_2_CDN, ...]
- `audio_urls`: [dialogue_line_mp3_CDN] (when dialogue exists for the shot)
- `prompt`: Shot description referencing `@Image1` (storyboard), `@Image2`/`@Image3` (characters), `@Audio1` (dialogue)
- `duration`: Matched to dialogue length + 1–2s buffer, or 5s for silent shots
- `aspect_ratio`: 16:9
- `resolution`: 720p

### Character reference CDN URLs (from cdns.txt)

```
Tony:      https://v3b.fal.media/files/b/0aa0b2ec/dlODQaeqQjB7oH_V39g9u_Tony-front.jpg
Yake-oh:   https://v3b.fal.media/files/b/0aa0b2ec/pln-j0Twj04YCH4SA8VBn_Yake-oh-front.jpg
Ji-lan:    https://v3b.fal.media/files/b/0aa0b2e4/Up9XxlhDmJdMTENf-AfrT_Ji-lan-front.jpg
MAMA:      https://v3b.fal.media/files/b/0aa0b2ed/9x5LGMpB0EZLLe0j3aIqN_MAMA-front.jpg
Trubble:   https://v3b.fal.media/files/b/0aa0b2e4/e7Vv5R_e5-MmPkDzWCCcC_Trubble-front.jpg
Slarth:    https://v3b.fal.media/files/b/0aa0b2e5/77yEMgqRygX5xm-Lw5Xl4_Slarth-front.jpg
Zoh-baggo: https://v3b.fal.media/files/b/0aa0b2e5/X8Zej5kvQiHLT-XjTCsUc_Zoh-baggo-front.jpg
TK-Maxx:   https://v3b.fal.media/files/b/0aa0b2e6/0ftlBRYLVfPDrGZAuO_6Y_TK-Maxx-front.jpg
```

### Dialogue mapping (scene 8 lines)

| Shot | Speaker | Line | Audio file | Duration |
|---|---|---|---|---|
| 8A-2 | Yake-oh | "flow like water, be light like air" | `Yake-oh/008_*.mp3` | 4.4s |
| 8A-4 | Tony | "You mean like boiling water?" | `Tony/012_*.mp3` | 1.4s |
| 8A-5 | Yake-oh | "More like a swan taking flight" | `Yake-oh/009_*.mp3` | 1.6s |
| 8A-6 | Tony | "I don't get it" | `Tony/013_*.mp3` | 1.0s |
| 8A-7 | Yake-oh | "swan gracefully float..." | `Yake-oh/010_*.mp3` | 6.3s |
| 8A-8 | Tony | "breaking boards / wax on wax off" | `Tony/014_*.mp3` | 4.7s |
| 8A-9 | Yake-oh | "train my way or hit the highway" | `Yake-oh/011_*.mp3` | 4.2s |
| 8B-2 | MAMA | "ain't signing no contract" | `MAMA/003_*.mp3` | 3.8s |
| 8B-3 | Ji-lan | "do this the hard way" | `Ji-lan/002_*.mp3` | 5.6s |
| 8B-4 | MAMA | "Get away from me vile beast" | `MAMA/004_*.mp3` | 2.7s |
| 8B-5 | Ji-lan | "SIGN THE CONTRACT" | `Ji-lan/003_*.mp3` | 1.1s |
| 8B-6 | Trubble | "Boss, you might want to see this" | `Trubble/006_*.mp3` | 1.6s |
| 8B-8 | Slarth | "Doughboy and his boyfriend" | `Slarth/005_*.mp3` | 2.8s |
| 8B-9 | Ji-lan | "You two, go take care of him" | `Ji-lan/004_*.mp3` | 1.6s |
| 8B-10 | MAMA | "Don't touch my baby boy!" | `MAMA/005_*.mp3` | 1.7s |
| 8B-11 | Ji-lan | "SSShhh… Ushi time!" | `Ji-lan/005_*.mp3` | 2.6s |
| 8C-1 | Yake-oh | "FLOW LIKE WATER!" | `Yake-oh/012_*.mp3` | 2.1s |
| 8C-3 | Zoh-baggo | "Heyyyy dough boy" | `Zoh-baggo/000_*.mp3` | 1.1s |
| 8C-4 | TK-Maxx | "How dare you train in GKD territory" | `TK-Maxx/000_*.mp3` | 4.2s |
| 8C-5 | Yake-oh | "Relax, don't do it!" | `Yake-oh/013_*.mp3` | 1.2s |
| 8C-6 | Tony | "Where's my MAMA??" | `Tony/015_*.mp3` | 1.1s |
| 8C-7 | TK-Maxx | "fettuncino brain" | `TK-Maxx/001_*.mp3` | 4.7s |
| 8C-9 | Yake-oh | "be a swan, take Kung Fu swan stance" | `Yake-oh/014_*.mp3` | 4.6s |
| 8C-10 | Tony | "It's Fettuccini!!!!" | `Tony/016_*.mp3` | 1.4s |
| 8D-2 | Ji-lan | "Trubble, Slarth, show them GKD Elite" | `Ji-lan/006_*.mp3` | 3.4s |
| 8E-2 | Yake-oh | "Let's get out of here!" | `Yake-oh/015_*.mp3` | 1.2s |

### Shots with NO dialogue (pure action/atmosphere)

| Shot | Description | Duration |
|---|---|---|
| 8A-1 | Wide establishing, pan down from trees | 5s |
| 8A-3 | Yake-oh close-up, serene face | 4s |
| 8B-1 | Wide office establishing, goons around MAMA | 5s |
| 8B-7 | Goons looking out window at park below | 5s |
| 8C-2 | Zoh-baggo + TK-Maxx arrive, interruption | 5s |
| 8C-8 | Both goons take kung-fu stances | 5s |
| 8C-11 | Zoh-baggo lands hit on Tony | 5s |
| 8C-12 | Tony lands hit, shocked expression | 4s |
| 8C-13 | Zoh-baggo's broken heel close-up | 4s |
| 8C-14 | Yake-oh KO's TK-Maxx | 5s |
| 8C-15 | Hero shot, Yake-oh + Tony standing over goons | 5s |
| 8D-1 | Ji-lan at window, shocked expression | 4s |
| 8E-1 | Wide shot, Trubble + Slarth arriving | 5s |
| 8E-3 | Tony + Yake-oh escape, running away | 5s |

## Execution order

1. **8A (pilot)** — 9 shots, ~$13.50. Test quality, lip-sync, character consistency.
2. **8B** — 11 shots, ~$16.50. Office setting, MAMA hostage, more characters.
3. **8C** — 15 shots, ~$22.50. Fight choreography, action shots.
4. **8D** — 2 shots, ~$3.00. Quick office reaction.
5. **8E** — 3 shots, ~$4.50. Escape sequence.

## Quality checklist (after each sub-scene)

- [ ] Character faces match turnarounds (especially Yake-oh's studs, not gauges)
- [ ] Lip-sync timing matches dialogue audio
- [ ] Screen positions consistent (Yake-oh LEFT, Tony RIGHT in 8A/8C two-shots)
- [ ] Lighting matches time of day (golden dawn for 8A, mid-morning for 8C)
- [ ] No AI hand/face artifacts in critical frames
- [ ] Tone matches storyboard intent (comedy, not horror)

## File structure

```
storyboards/scene-08/
├── finals/           # Source storyboard PNGs (already exist)
├── clips/            # Generated video clips (new)
│   ├── 8A-1.mp4
│   ├── 8A-2.mp4
│   └── ...
├── clips-log.jsonl   # Generation log
└── VIDEO-PLAN.md     # This file
```

## Seedance 2.0 constraints (learned from 8A pilot)

- **Minimum audio duration:** 2.0 seconds. Dialogue lines under 2s must be padded with silence (ffmpeg `apad`).
- **Minimum video duration:** 4 seconds. Duration "3" is rejected; use 4 as the floor.
- **Generation time:** ~4–7 min per clip at 720p standard. Budget ~5 min/shot for planning.

## Final results (all scenes)

117 / 127 clips rendered (92%), 9:24 of footage, ~$45 spent.

| Scene | Clips | Duration | Model | Status |
|---|---|---|---|---|
| scene-07 — Dream | 8/8 | 40s | Gemini | ✅ |
| scene-08A — Park Dawn | 9/9 | 48s | Seedance 2.0 (lip-sync) | ✅ |
| scene-08B-8E — HQ/Fight/Escape | 31/31 | 151s | Gemini | ✅ |
| scene-09 — Dirt Bowl | 7/7 | 34s | Gemini | ✅ |
| scene-10 — Spirit Path | 6/15 | 30s | Gemini | ⚠️ 9 celeb shots blocked |
| scene-11 — Dirt Bowl Return | 16/16 | 71s | Gemini | ✅ |
| scene-12 — Tent Morning | 9/9 | 39s | Gemini | ✅ |
| scene-13 — Deaths Dam | 23/24 | 112s | Gemini | ⚠️ 1 group shot blocked |
| scene-16 — Post-credits | 4/4 | 18s | Gemini | ✅ |
| scene-00 — Sitcom | 4/4 | 20s | Gemini | ✅ |

### 8A pilot results

| Shot | Status | Time | Notes |
|---|---|---|---|
| 8A-1 | ✅ | 275s | Wide establishing, no dialogue |
| 8A-2 | ✅ | 339s | Two-shot with lip-synced dialogue |
| 8A-3 | ✅ | 262s | Yake-oh close-up, no dialogue |
| 8A-4 | ✅ | rerender | Fixed: audio padded to 2.5s (was 1.38s) |
| 8A-5 | ✅ | rerender | Fixed: audio padded to 2.5s (was 1.62s) |
| 8A-6 | ✅ | rerender | Fixed: duration changed from 3→4 |
| 8A-7 | ✅ | 378s | Longest dialogue (6.3s), 8s clip |
| 8A-8 | ✅ | 414s | Tony wax-on-wax-off rant |
| 8A-9 | ✅ | 321s | Final meditation beat |

## Cost mitigation

- **Fast tier** (`bytedance/seedance-2.0/fast/reference-to-video`): ~40% cheaper, max 720p only. Use for action-only shots where 1080p doesn't matter.
- **Shorter durations**: Match duration to dialogue + 1s. Silent shots can be 4–5s.
- **Batch dialogue shots**: Some consecutive shots share characters and setting — could combine into single longer clip and cut in post.

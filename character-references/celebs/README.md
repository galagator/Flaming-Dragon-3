# Celebrity reference images — Scene 10 (The Spirit Path)

This folder contains reference photos of Bruce Lee, Jackie Chan, and Steven Seagal sourced from Wikimedia Commons. Used as character references for the Scene 10 storyboard (Bruce Lee, Jackie Chan, and Steven Seagal appear in the sky over the spirit path).

## Sourcing rationale

Scene 10 calls for direct likenesses of three real, famous martial artists. The gpt-image skill warns that direct celebrity likeness generation "may trip FAL content filters" and "ethical concerns" are a consideration. For this FD3 project, the user has confirmed:

- This is a **private screening** (parody/comedy context)
- The script is a clear homage to these martial artists
- Wikimedia Commons is the right source for openly-licensed, attribution-clear images

## Licensing

| File | Subject | License | Attribution |
|---|---|---|---|
| `Bruce_Lee_1973.jpg` | Bruce Lee, 1973 portrait | Public domain (US, pre-1978) | "National General Pictures, via Wikimedia Commons" |
| `Bruce_Lee_as_Kato_1967.jpg` | Bruce Lee as Kato (Green Hornet) | Public domain (US, pre-1978) | "ABC Television, restore by BevinKacon, via Wikimedia Commons" |
| `Jackie_Chan_2002-portrait.jpg` | Jackie Chan, 2002, USS Kitty Hawk | Public domain (US Navy photo) | "U.S. Navy photo by Photographer's Mate 3rd Class Lee M. McCaskill, via Wikimedia Commons" |
| `Jackie_Chan_2025_Locarno.jpg` | Jackie Chan, 2025 Locarno Film Festival | CC BY-SA 4.0 | "Segolene Liger, via Wikimedia Commons" (share-alike required for derivatives) |
| `Steven_Seagal_Russia_Expo.jpg` | Steven Seagal, Russia Expo 2024 | CC BY 4.0 | "Svklimkin, via Wikimedia Commons" |

The two public-domain images (Bruce Lee 1973 and 1967) can be used without restriction. The CC BY and CC BY-SA images require attribution. If FD3 is ever distributed beyond private screening, the CC-licensed images should be replaced with explicitly-licensed alternatives or rendered derivatives.

## Model choice for Scene 10

Per user direction, Scene 10 will use **Flux Pro Kontext** (`fal-ai/flux-pro/kontext`, $0.04/image) instead of gpt-image-2 for these celebrity compositions. Kontext is specifically designed for character/identity preservation, which is the right tool for placing Bruce Lee / Jackie Chan / Steven Seagal in new scenes while preserving their likeness from the reference images.

## Generation workflow

1. Upload all 5 references to FAL CDN via `genmedia upload`
2. Use `fal-ai/flux-pro/kontext` with the reference URLs and a scene-prompt that places them in the Spirit Path scene composition
3. Per the gpt-image skill's advice, framing the prompts as "in the sky / divine / supernatural" rather than direct celebrity photorealism helps with both content filter safety and the narrative beat (they are apparitions)

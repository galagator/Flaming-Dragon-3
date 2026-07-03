# Flaming Dragon 3 — Opener (Scene 00)

HyperFrames composition + storyboard for the FD3 film opener.

## Structure

```
scene-00-opener/
├── 00-opener.md                   # storyboard (this directory)
├── DESIGN.md → opener/DESIGN.md   # visual identity
├── opener/                        # HyperFrames project
│   ├── index.html                 # the composition
│   ├── hyperframes.json
│   ├── meta.json
│   ├── package.json
│   ├── AGENTS.md                  # HyperFrames auto-generated
│   ├── compositions/
│   │   └── main-graphics.html     # (template, unused — single-comp project)
│   └── ...
├── compositions/                  # (empty placeholder from scaffolding)
├── assets/                        # (empty placeholder from scaffolding)
├── refs/                          # for any external reference images
└── finals/                        # rendered MP4 outputs land here
```

## Render

```bash
cd opener
npm install
npx hyperframes render --quality draft --output ../finals/opener-draft.mp4
```

See `00-opener.md` for the full shot list and `opener/DESIGN.md` for the visual identity.

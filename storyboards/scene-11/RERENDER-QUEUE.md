# FAL re-render queue

When the FAL balance is topped up (https://fal.ai/dashboard/billing), run
`rerender3.py` to render the **3 remaining** panels:

```bash
cd /mnt/d/Projects/FD3
python3 .cache/refs/rerender3.py
```

The script has 8s cooldowns between calls (avoids FAL rate limiting)
and uses `--safety_tolerance 5` on the two content-safety panels.

The script auto-skips panels whose PNG already exists, so you can re-run
it as-is. 11-1 and 16-4 will no-op (they rendered in a previous pass);
the other 3 will actually hit FAL.

## Queue

| Panel | Why it failed | Fix baked into rerender3.py | Status |
|---|---|---|---|
| 11-1 | Model rendered "martial artist in forest" instead of "dirt-lot party wide establishing" | Stronger prompt: explicit "DIRT-LOT", "CAR HEADLIGHTS", "NOT forest", "lower-third of frame" | **DONE** — re-roll PASSED, vision-checked clean. |
| 13-4 | Content-safety rejected Ji-lan monologue prompt (HITLER / racial ideology terms) | Softened prompt + "Absurdist comedy tone — a satirical villain character" disclaimer + safety_tolerance 5 | **BLOCKED** — FAL balance still exhausted on retry. |
| 13-12 | Content-safety rejected "Ji-lan dragging MAMA" prompt (tied-hostage framing) | Softened to "she is being rescued, not harmed" + safety_tolerance 5 | **BLOCKED** — FAL balance still exhausted on retry. |
| 16-3 | Empty `image_urls` (baby panel had no character ref) | Uses Jasmine as tonal anchor | **BLOCKED** — FAL balance still exhausted on retry. |
| 16-4 | Empty `image_urls` (eye close-up had no ref) | Uses Jasmine as tonal anchor | **DONE** — re-roll PASSED, vision-checked clean. |

## Cost

3 panels remaining × $0.15 = **$0.45** to clear the queue.

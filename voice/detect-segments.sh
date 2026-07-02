#!/usr/bin/env bash
# Detect silence / speech regions in each scene's audio.
# Outputs a JSON manifest with per-segment timing.
set -u
FD3="/home/galagator/Projects/FD3"
cd "$FD3"

mkdir -p voice/notes

# Voice activity detection: speech vs silence based on RMS threshold.
# We'll output per-scene TSV: start_s, end_s, kind (speech/silence).
# Then the next stage can pull out the speech chunks.
for wav in voice/raw/*.wav; do
  base=$(basename "$wav" .wav)
  out="voice/notes/${base}.segments.tsv"
  if [ -f "$out" ]; then
    echo "SKIP $out"
    continue
  fi
  echo "DETECT $wav -> $out"
  # silencedetect outputs silence regions (start, end). The rest is speech.
  # Noise floor at -25dB: aggressive enough to catch dialog in loud-mastered
  # footage like the GKD commercial, conservative enough to find actual gaps
  # in normal scenes. Min silence duration: 0.4s.
  ffmpeg -hide_banner -loglevel info -i "$wav" \
    -af "silencedetect=noise=-25dB:d=0.4" \
    -f null - 2>&1 \
    | grep -E "silence_(start|end):" \
    | sed -E 's/.*silence_(start|end): ([0-9.]+).*/\2\t\1/' \
    > "$out.tmp"
  # Now convert silence_end + speech segments into a proper manifest
  python3 - "$wav" "$out.tmp" "$out" <<'PY'
import sys, wave, contextlib
wav_path, tmp_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

# Read wav duration
with contextlib.closing(wave.open(wav_path, 'rb')) as w:
    duration = w.getnframes() / w.getframerate()

# Parse silence regions from ffmpeg output (start,kind or end,kind lines)
silence = []
with open(tmp_path) as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        try:
            t = float(parts[0])
        except ValueError:
            continue
        kind = parts[1]
        silence.append((t, kind))

# Build speech segments
speech = []
prev_end = 0.0
open_start = None
for t, kind in silence:
    if kind == 'start':
        # Silence started — close the current speech segment
        if open_start is not None and t > open_start:
            speech.append((open_start, t))
        prev_end = t
    elif kind == 'end':
        # Silence ended — speech starts here
        open_start = t
# If audio ends mid-silence, close the last open segment at duration
if open_start is not None and open_start < duration:
    speech.append((open_start, duration))

# Write manifest
total_speech = sum(e - s for s, e in speech)
with open(out_path, 'w') as f:
    f.write(f"# segments for {wav_path}\n")
    f.write(f"# total duration: {duration:.2f}s, speech duration: {total_speech:.2f}s\n")
    f.write("start\tend\tduration\n")
    for s, e in speech:
        f.write(f"{s:.2f}\t{e:.2f}\t{e-s:.2f}\n")

print(f"  -> {len(speech)} speech segments, {total_speech:.1f}s total speech out of {duration:.1f}s")
PY
  rm -f "$out.tmp"
done
echo "DONE"
ls -la voice/notes/

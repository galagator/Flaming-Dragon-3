#!/usr/bin/env bash
# Extract audio from FD3 shot scenes. Two stages:
#  1. Full audio demux per scene → voice/raw/<scene>.wav
#  2. (Next script) Voice activity detection + per-character splitting
set -u
FD3="/home/galagator/Projects/FD3"
cd "$FD3"

mkdir -p voice/raw

for src in scenes/*.mp4; do
  base=$(basename "$src" .mp4)
  # sanitize: "GKD Commercial(1)" → "GKD_Commercial_1_"
  out_base=$(echo "$base" | tr ' ()' '___' | sed 's/__*/_/g; s/_$//')
  out="voice/raw/${out_base}.wav"
  if [ -f "$out" ]; then
    echo "SKIP $out (exists)"
    continue
  fi
  echo "EXTRACT $src -> $out"
  ffmpeg -hide_banner -loglevel error -y -i "$src" \
    -vn -acodec pcm_s16le -ar 48000 -ac 2 "$out"
done
echo "DONE"
ls -la voice/raw/

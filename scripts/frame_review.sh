#!/usr/bin/env bash
# Prepare a clip for per-second QC.
#   frame_review.sh clip.mp4 outdir [fps]
# Produces:
#   outdir/frames/f_NNN.jpg      every frame at <fps> (default 8); frame n is at t=(n-1)/fps
#   outdir/sheets/sheet_XXs.jpg  contact sheets, 2 s each at 4 fps (8 tiles), scaled to 240 px wide
#   outdir/cuts.txt              hard-cut timestamps (scene change > 0.3)
#   outdir/info.txt              duration / size / fps
# Note: this ffmpeg build has no drawtext, so timestamps are not burned in; compute them from the index.
set -euo pipefail
clip="$1"; out="$2"; fps="${3:-8}"
mkdir -p "$out/frames" "$out/sheets"
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate:format=duration -of compact "$clip" > "$out/info.txt"
ffmpeg -loglevel error -y -i "$clip" -vf "fps=$fps" "$out/frames/f_%03d.jpg"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")
s=0
while awk "BEGIN{exit !($s + 0.25 < $dur)}"; do
  ffmpeg -loglevel error -y -ss "$s" -t 2 -i "$clip" -vf "fps=4,scale=240:-1,tile=8x1:padding=4:color=white" -frames:v 1 "$out/sheets/sheet_$(printf %02d "$s")s.jpg" || true
  s=$((s+2))
done
ffmpeg -hide_banner -i "$clip" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$out/cuts.txt" || true
echo "frames: $(ls "$out/frames" | wc -l | tr -d ' ')  sheets: $(ls "$out/sheets" | wc -l | tr -d ' ')  cuts: $(tr '\n' ' ' < "$out/cuts.txt")"

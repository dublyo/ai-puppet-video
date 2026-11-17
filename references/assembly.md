# Assembling the parts and the voice pass

Run everything from the production folder, with `SK=../../../.claude/skills/ai-puppet-video/scripts` (or an absolute path). All paths below are relative to the production folder.

## 1. Clean audio per clip

For each speaking shot:

```bash
python3 $SK/jaw_windows.py clips/S2.mp4 --box 135,315,115,75      # -> e.g. [[0.5,1.0],[1.29,2.04]]
python3 $SK/voice_scan.py clips/S2.mp4 --mute clips-sfx-only/S2.mp4 --jaw 0.5-2.04
```

- Muting **jaw windows ∪ scan ranges** is the default. The creator's voice replaces those windows anyway, and the scan can miss quiet leaks.
- For silent shots (inserts), `voice_scan.py --mute` alone is enough.
- Keep the untouched originals in `clips/` and `clips-r2/`.

## 2. Edit list and build

`edit.json`:

```json
{"output": "<slug>-final-sfx-only.mp4", "size": "480x854", "fps": 24,
 "shots": [
  {"name": "S1", "file": "clips-sfx-only/S1.mp4", "in": 0.0,  "out": 4.96, "jaw": [[0.0, 0.54]], "line": "البروفيسور: «الموضوع بسيط جدًا»"},
  {"name": "S2", "file": "clips-sfx-only/S2.mp4", "in": 0.29, "out": 2.79, "jaw": [[0.46, 2.08]], "line": "سامي: «طب هاته أجرّب أنا؟»"},
  {"name": "S4", "file": "clips-sfx-only/S4-r2.mp4", "in": 0.333, "out": 3.333}
 ]}
```

Then build and re-scan:

```bash
python3 $SK/assemble.py edit.json
python3 $SK/voice_scan.py <slug>-final-sfx-only.mp4
```

`assemble.py`:
- snaps in and out points to whole frames and clamps `out` to the clip length,
- normalises size and fps, so finalised and 480p shots can be mixed,
- adds silence to clips without audio,
- writes `edit.timeline.md` with the voice-window table in final-cut time.

Deliver the SFX-only cut, the clean clips and the table.

## 3. Choosing trim points

- **Cut in** on a still, closed-mouth frame about 0.15–0.3 s before the first jaw opening. If the start frame was open-mouthed, the line starts on frame 1: accept that, or re-roll with a closed-mouth panel.
- **Cut out** about 0.5 s after the last meaningful motion, and before the dead tail. A frame-difference series near 0 means the shot has frozen.
- **Insert:** about 1.5 s of action before the payoff, the payoff itself, then 0.3–0.5 s of hold.
  - A morph frame at the payoff can be dropped or replaced with a neighbour.
  - A shape change (a neck appearing) can't be hidden that way. Cut on the pop instead, jumping from just before the morph to after the lift.
- **Never trim through a bad mid-clip jaw window** (it can't be removed). Pick or re-roll another take.
- **Never slow a clip down to fit a longer voice line:** the hands crawl. Shorten the line or re-roll.
- A deliberate button hold can be a CapCut freeze-frame.

## 4. Voice pass (Claude, after the creator sends his takes)

1. Put the takes in `voice/` (for example `S2-sami.wav`).
2. Check each take:
   - Loudness and peaks: `ffmpeg -i take.wav -af volumedetect -f null -`, aiming for peaks below −1 dBFS.
   - Noise and clicks, by ear or a spectrogram.
   - **Length against its jaw window** (from `edit.timeline.md`).
3. Flag any line longer than its window plus about 0.2 s. Suggest a faster read or a shorter line, or re-roll the shot (voice-first experiment).
4. Place each take so the first syllable lands on the window start, using CapCut through the `capcut-mcp-video` skill (mcp-cut). Keep the SFX track under the voices.
   - If mcp-cut is unavailable, make a reference mix with ffmpeg:
     ```bash
     ffmpeg -i cut.mp4 -i S2.wav -filter_complex "[1:a]adelay=5130|5130[v];[0:a][v]amix=inputs=2:normalize=0[a]" -map 0:v -map "[a]" -c:v copy out.mp4
     ```
   - Then hand over the CapCut parts.
5. Re-check the sync frame by frame at each line start and end. Deliver `<slug>-final-voiced.mp4`, and say what was not verified.

## 5. Useful ffmpeg recipes

```bash
# mute windows (keep the video stream)
ffmpeg -i in.mp4 -c:v copy -af "volume=enable='between(t,0.45,2.0)+between(t,3.45,4.15)':volume=0" -c:a aac out.mp4
# 2 fps contact sheet of a whole cut
ffmpeg -i cut.mp4 -vf "fps=2,scale=160:-1,tile=20x2:padding=3:color=white" -frames:v 1 sheet.jpg
# hard-cut times
ffmpeg -i cut.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*'
```

This ffmpeg build has no `drawtext`, so compute times from frame indexes.

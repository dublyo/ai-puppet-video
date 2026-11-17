# ai-puppet-video

A Claude Code skill for directing and producing AI felt-puppet videos end to end: channel format, character masters, series bible, story, shot list, storyboard or Blender previs, Seedance generation on Higgsfield, per-second QC, and the final SFX-only cut with the creator's own voice placed in CapCut.

It works for any cast, language or setting. The example characters (the Professor, Nora, Sami, Adam) come from the first project and are there only to illustrate.

## What it covers

| Phase | What happens |
|---|---|
| 0 | Format and audience: archetype, "made for kids" check, own IP, Shorts-first |
| 0a / 0b | Character master images, then the series bible |
| 0a-finish | Character sheets, `character.json`, README per character |
| 0c | Story adapted from a reference video → `STORY.md` |
| 1–2 | Beat sheet, second-by-second shot list, `VOICE-SCRIPT.md` |
| Route B | Blender greybox mockup used as a Seedance video reference (default for multi-shot films) |
| Route A | Picture storyboard, then one Seedance clip per shot |
| 5–7 | Frame-by-frame QC, voice-leak and jaw-window checks, A/B re-rolls |
| 8–10 | Assembly, voice-window table, voice placement in CapCut, report |

Each paid step has a free price check and needs the user's explicit approval before it runs.

## Layout

```
SKILL.md            the skill itself: pipeline, standing rules, phases
references/         detailed guides loaded on demand (characters, storyboard,
                    blender-previs, prompting, cinematography, QC, assembly ...)
scripts/            helper tools
  assemble.py           cut shots from an edit list, print voice windows
  frame_review.sh       extract frames + contact sheets for per-second QC
  frame_check.py        camera-shift check between storyboard frames
  jaw_windows.py        measure jaw-open windows from a mouth crop
  voice_scan.py         detect and mute leaked generated voices
  storyboard_*.py       generate storyboard rounds, boards and sheets
  hf_lab.py             call Higgsfield through a local Test Lab (cost / generate / upload)
  blender/              Route-B templates: shot builder, request builder,
                        numeric QC, mockup|AI side-by-side
```

## Install

Clone into your project's skills folder (or `~/.claude/skills/` to use it everywhere):

```bash
git clone https://github.com/dublyo/ai-puppet-video.git .claude/skills/ai-puppet-video
```

Claude Code picks it up automatically. It triggers on requests like "plan a puppet channel", "storyboard this episode", "make a Seedance shot" or "review this clip".

## Requirements

- Python 3 with `numpy`
- `ffmpeg` / `ffprobe`
- Google Chrome (headless) for the Arabic-safe storyboard sheets
- Blender 5.x with the `blender-mcp-cinematic` skill for Route B
- A Higgsfield account and a local Higgsfield Test Lab for generation (`hf_lab.py` never handles tokens itself)

## Notes

- Generated audio is SFX only. Character voices are recorded by the creator and added afterwards.
- Never commit generated media or Higgsfield auth files. The `.gitignore` excludes the usual outputs.

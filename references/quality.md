# Getting the best final quality

Everything in takes 1–3 was a 480p draft at standard bitrate: good for testing direction, not a final picture. This file lists the ways to raise quality, with prices checked by free `get_cost` calls on 2026-11-15.

**Prices are verified. Picture quality is not**: none of these options has been rendered yet. Test each on one shot before committing a whole episode.

## What decides quality, in order

1. **Direction and the start frame.** Framing, prop shape, expression and pose come from the storyboard panel. A wrong panel can't be fixed by resolution.
2. **Choice of take.** Two or three 480p candidates per shot (12–15 credits each) and an A/B pick improve the result more than one expensive render.
3. **Lips matching the voice.** A mouth that moves off the line reads as fake at any resolution. See "Lip-sync options".
4. **Resolution and bitrate.** Only after 1–3 are right.
5. **Finishing:** deflicker, frame rate, grade, sound.

## Resolution: three routes to 1080p

Prices are for one 5 s 9:16 clip.

| Route | Credits | Notes |
|---|---|---|
| Native Seedance 2.5 at 1080p | 80 (16/s) | A new render, so a new performance: re-run all QC. |
| Native Seedance 2.5 at 720p | 35 (7/s) | Same caveat. |
| Finalise a 480p draft (`draft_job_id`) | quoted 64 for a 4 s draft at both 720p and 1080p | Same price as a fresh 1080p render. Meant to keep the draft's performance; untested. |
| **480p take + ByteDance upscale to 1080p**, preset `aigc`, standard | **15 + 1** | Keeps the exact approved take. Upscalers sharpen but can't add real detail, and may smooth felt texture. |
| Same, `model_version: pro` | 15 + 10 | |
| `video_upscale` | 2 | Settings unknown. |

For a 20 s short (about 23 s generated): native 1080p ≈ 368 credits; 480p plus standard upscale ≈ 74.

**Recommended test (about 11 credits):** upscale one approved 480p clip with `aigc` standard and with `pro`, and compare felt texture, edges and faces at phone size and full screen. Only if the upscale looks soft or plastic, render that shot natively at 720p or 1080p.

Call shapes:
- Price check: `generate_video` with `{"model": "bytedance_video_upscale", "resolution": "1080p", "preset": "aigc", "fps": 24, "medias": [{"role": "video_references", "value": "<completed job id or media id>"}], "get_cost": true}`.
- The dedicated `upscale_video` tool has no cost preflight. It needs `provider`, `video_id` (a job id works), and the source `width` and `height`.
- `topaz_video` can't be priced by preflight.

## Free or nearly free settings

- **`bitrate_mode: "high"`** on Seedance 2.5 costs the same as standard, but **failed 8 of 8 jobs that used image_references** (2026-11-16, refunded). Keep standard, and raise quality by upscaling or finalising afterwards.
- **`draft: true`** costs the same at 480p. Keep it on for tests.
- **Panels at 2k** (`gpt_image_2_6_flare` high 2k, 2.75 credits) when the final will be 720p or more. A 1k panel is 752×1344, smaller than a 1080×1920 frame, so the start frame would be upscaled inside the model.

## Lip-sync options (the biggest open quality problem)

Prompted mouth timing missed badly in 2 of 4 speaking clips. All of the options below need the creator's recorded line first, and all are untested on felt puppet jaws.

| Option | What it does | Why try it |
|---|---|---|
| `sync_so` (roles `input_video` + `input_audio`) | Re-syncs the lips of an existing clip to an audio track | Fixes the mouth window in post, on a take already approved. `sync_mode` handles length mismatch (`cut_off`, `silence`, `remap`, …). |
| Seedance 2.5 `audio_references` | Generates the shot against the recording | Lips and body performance come from the real line. Check with `voice_scan.py` whether the reference voice is copied into the output, and mute it. |
| `intone` | One or two characters speak one to six voice recordings, to camera or to each other, from character images plus a location image | Built for exactly this. It expects "a readable front face", so a puppet may or may not pass. Up to 1080p, high bitrate. |
| `motion_control` / `hf_mult_motion_control` | Transfers motion from a driving video to a character image | A real hand puppet (or a hand) performing the line drives the AI puppet. |

Price each with `get_cost` once the audio is uploaded; earlier checks showed these need real media to quote.

Suggested order: `sync_so` on one finished clip (cheapest way to learn whether felt mouths re-sync), then Seedance `audio_references` for one shot, then `intone`.

## Other models worth one comparison shot

Quotes for 5 s at 1080p with a start image (veo3_1 is 4 s, quality high):

| Model | Credits | Notes |
|---|---|---|
| `seedance_2_5` | 80 | Our tested baseline; identity from references is strong. |
| `cinematic_studio_video_4_0` | 80 | Camera, lens and lighting controls. |
| `seedance_2_0` std | 60 | Supports Elements. |
| `wan3_0` | 17.5 | Start/end image, references, `enable_thinking` for prompt adherence. |
| `kling4_0` | 16.25 | Start/end image, up to 10 image references, Kling elements. |
| `veo3_1` | 16 | Start image only; durations 4, 6 or 8 s. |

A fair bake-off: the same approved panel and the same prompt on one shot (for example the Professor single) across two or three of the cheaper models. Judge identity, felt texture, hand count, obedience to the start frame, and voice leaks. Only Seedance 2.5 has been tested on these puppets.

## Finishing passes

| Pass | Price (5 s clip) | When |
|---|---|---|
| `video_deflicker` | 2 | Held freezes shimmer or boil. |
| `fps_boost` (ByteDance, 48 fps) | about 20 | Only if on-twos judder is visible at playback speed. CapCut's optical-flow retime is free; apply it only to the stuttering ranges, since it can warp felt. |
| Colour match in CapCut | free | Inserts and re-rolls drift slightly warmer or cooler. |
| Sound | free | Keep the generated SFX, add missing foley from CapCut's library, and normalise the creator's voice. |

## Budget guide for one finished 20 s short

| Stage | Credits |
|---|---|
| Storyboard (2k panels, with re-rolls) | 20–35 |
| 480p draft clips, two candidates for the hard shots | 70–110 |
| Lip-sync pass on speaking shots | price after the first test |
| Upscale the picked takes (standard / pro) | 5 / 50 |
| Deflicker where needed | 2 each |

Compare with about 370 for rendering every shot natively at 1080p once, with no candidates to choose from.

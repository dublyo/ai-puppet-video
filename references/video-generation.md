# Shot-by-shot video generation (Seedance 2.5 on Higgsfield)

## Request shape (`clips/request-params.json`, one key per shot)

```json
{"S1": {
  "model": "seedance_2_5", "mode": "omni_reference",
  "prompt": "<shot prompt, see prompting.md>",
  "duration": 5, "resolution": "480p", "aspect_ratio": "9:16",
  "generate_audio": true, "draft": true,
  "medias": [
    {"role": "start_image", "value": "<panel media_id>"},
    {"role": "end_image",   "value": "<end-pose panel media_id>"},
    {"role": "image_references", "value": "<master A media_id>"},
    {"role": "image_references", "value": "<master B media_id>"}]}}
```

Run it with:

```bash
python3 $SK/hf_lab.py cost clips/request-params.json   # exits 1 with no TOTAL if any key gets no price
# get approval
python3 $SK/hf_lab.py generate clips/request-params.json
python3 $SK/hf_lab.py wait <job ids> --out clips --names S1 S2 …
```

- **Modes:** `t2v`, `omni_reference` (image, video and audio references, plus start and end images), `video_edit`, `video_extension`.
- **Duration:** 4–30 s, whole numbers. The minimum is 4 s, so short shots are generated at 4 s and trimmed.
- **`draft: true`** costs the same at 480p and can be finalised later (see below). Use it on every test.
- **Media limits:** `image_references`, `start_image` and `end_image` together max 30; `video_references` max 10; `audio_references` max 10.
- **Seedance 2.5 has no Elements support.** Identity comes from the masters as `image_references`.
  - Shape, colour and costume held across 3 takes and 14 shots.
  - **Fine texture drifted:** corduroy rendered as velvet, the knit bow tie as smooth felt, and Sami's insert hands came out lighter and fuzzier. Add texture words.
  - If Elements are required, use `seedance_2_0` or `kling3_0` (Kling needs a `start_image`).

## Cost (measured with `get_cost`)

**Per-clip prices**

| Model / setting | Credits |
|---|---|
| Seedance 2.5, 480p | 3/s. Audio on, audio off, draft and `bitrate_mode: high` all cost the same (checked 2026-11-15). **But high + image_references failed 8/8 (2026-11-16): keep standard.** |
| ByteDance upscale of a 5 s clip to 1080p (`aigc`) | 1 standard, 10 pro. See `quality.md`. |
| 5 s clip / 4 s clip / 20 s single render | 15 / 12 / 60 |
| Seedance 2.5, 720p, non-draft | 7/s (28 for 4 s) |
| Seedance 2.5, 1080p, non-draft | 16/s (64 for 4 s) |
| Finalise a 4 s draft via `draft_job_id` | quoted 64 at both 720p and 1080p (odd; re-check before using) |
| Seedance 2.0 std, 5 s, 720p | 22.5 |
| Seedance 2.0 fast, 5 s | 12.5 |
| Kling 3.0, 5 s, sound off | 7.5 |

**Realistic budget for a 20 s short at 480p**

| Item | Credits |
|---|---|
| Storyboard (with the deep QC: about 3 frames generated per frame kept) | about 50–70 (test-video-05: 45 frames for 15 kept ≈ 67) |
| Clips (about 23 s generated) | about 69 |
| Re-rolls | about 40 |
| **Total** | **about 120–135, plus any finalising** |

Take 3 actually cost 24 + 69 + 42 = 135.

**Render time:** about 4 min for one 20 s job. Five 4–5 s jobs submitted together all finished in about 2 min; this varies with load.

## One long render vs shot by shot

> This table compares renders **without** a video reference. With a Blender mockup as `video_references` (Route B, `blender-previs.md`), one 20 s render matched the mockup's camera, blocking and cuts (within ±1 frame) for 60 credits on the first try.

| | One 20 s multi-shot render | One clip per shot (recommended) |
|---|---|---|
| Camera and blocking | Invented by the model | Starts from approved panels |
| Cuts | Roughly on time (within ±0.7 s) | Exact, set in the edit |
| Fixing one moment | Re-roll all 20 s (60 credits) | Re-roll one shot (12–15) |
| Best-of selection | Not possible | A/B per shot |
| Failures seen | Floating prop, lens looks, cramped two-shots | Mouth windows drift, listener freezes, prop shape changes |

## Lessons from test-video-05 rendering (2026-11-16)

- **Describe only the characters who are in the clip.** A shared header that described both Nora and the Professor made Seedance **add the absent character** and **transfer props**:
  - the Professor appeared in Nora's locked close-up (clip 5),
  - Nora appeared in his close-up (clip 7),
  - Nora's pink oven mitts appeared on the Professor's hands in the hands-only insert (clip 4).

  Build each clip's header from the characters in its START/END frames only. For inserts, name whose hands they are and what they are NOT ("bare orange-tan felt hands with olive corduroy cuffs, NOT oven mitts"). Pass only the masters of characters in the shot.
- **`bitrate_mode: "high"` + `image_references` failed 8 of 8 jobs** (7 "failed", 1 "ip_detected"). The same requests at standard bitrate all succeeded. Failed jobs were refunded automatically. Use standard bitrate with references; to get a better bitrate, upscale or finalise afterwards.
- **Check that every clip starts and ends on its storyboard frames:**
  ```bash
  python3 $SK/frame_check.py pair <START.png> <clip-first.png>
  python3 $SK/frame_check.py pair <END.png> <clip-last.png>
  ```
  - A small systematic pan (about 3% dx, under 1% zoom) comes from the 752×1344 → 480×854 conversion and is normal.
  - Larger zoom means the frame was not honoured.
  - The check is grayscale, so **also compare by eye for colour and props** (the mitts swap kept the same composition).
- Failed or blocked jobs ("failed", "ip_detected") showed as charged at submit and were refunded within minutes. Check the balance before concluding that credits were lost.

## Chaining continuation clips (in use since test-video-05)

When clip N+1 continues the same take as clip N (a shared boundary frame in the storyboard, such as test-video-05 clips 1→2 and 6A→6B), extract the **actual last frame** of the rendered clip N with ffmpeg and use it as `start_image` for clip N+1, instead of the storyboard frame:

```bash
ffmpeg -sseof -0.05 -i clips/S1.mp4 -frames:v 1 -update 1 clips/S1-last.png
```

The cut is then pixel-continuous, even if the video drifted slightly from the storyboard END. Upload `S1-last.png` with `hf_lab.py upload`.

## Start and end images

- **The start frame wins.** The clip opens on the panel. Prop shape, expression, costume state, pose and framing all carry over, mistakes included.
- **Mouth state:** if the panel shows the mouth open, the first flap is lost. Use a closed-mouth start for a line that begins the shot.
- **`end_image`** worked for a state change (shock freeze → bow-tie fix). The tail locks onto it.
- **Frozen tails happen with or without `end_image`.** The model stops once the scripted action ends: S4 froze for the last 0.75–0.96 s, S1-B for 0.4 s, and S5 for about 0.9 s. Script the action through to the end, plan any hold inside the used length, trim before the freeze, or build the hold as a CapCut freeze-frame.
- **Sharpness:** some clips soften gradually over the first 0–2 s as they settle into the model's look (S5). It didn't happen in S2. Measure it rather than assume it; held freezes can shimmer or boil slightly.

## Finalising (untested)

1. Record each picked take's job id.
2. Run `get_cost` with `{model, mode, draft_job_id, resolution: "720p"|"1080p"}`, show the price and get approval. Finalise within 7 days.
3. Finals are new renders: re-run `voice_scan.py`, `jaw_windows.py` and the trim checks on them.
4. Compare the price against a fresh non-draft render of the same shot (28 credits at 720p for 4 s). A fresh render is a new performance, though.

## Re-roll strategy

1. Re-roll only the shots with verified major issues, after showing the user the reason and the price.
2. Change only the prompt lines tied to the failure. If the panel caused it (shape, framing, gag state), fix the panel first.
3. Compare A against B frame by frame and pick per shot. In take 3 the picks were S1 = A (the re-roll broke the jaw window), S4 = B and S5 = B.
4. Run the full QC on every new clip.

## Known model behaviours

- **Timing is approximate.** These are the measured mouth windows in take 3:

  | Clip | Planned | Rendered | Result |
  |---|---|---|---|
  | S1 | 1.5 s | 0.54 s | Bad miss |
  | S2 | — | — | About on time |
  | S3 | 3.0 s | 2.6 s | Close |
  | S5 (A) | 2.0 s | 0.8 s, about 1.3 s late | Bad miss |
  | S5 (B) | 2.5 s | 1.35 s, about 1.1 s late | Bad miss |

  So 2 of the 4 speaking clips missed badly. Planned freezes also get shortened (S5-B held 0.71 s of a planned 1.0 s).
- **The listener freezes** in two-shots even when given actions, apart from occasional blinks.
- **Motion is often on twos** (about 12 fps updates), sometimes irregular. The reviewers suspect draft mode. That's unverified, so check finalised renders before retiming. Prefer finalising over optical-flow retiming, which can warp felt; if you must, retime only the stuttering ranges.
- **State changes snap.** The lid sat half-dissolved in the rim for 1–2 frames at the pop, and the bow tie went from 25–30° to level in one 24 fps frame. See the QC catalogue for edit fixes.
- **Felt hands blur** into mittens in fast motion and read again at rest.
- **Native audio:** the SFX are good (lid creak, a crisp pop on time). Voices leak whenever the prompt implies speech text. See `prompting.md`.

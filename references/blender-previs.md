# Route B: Blender previs → Seedance 2.5 video reference

Proven on test-video-06 «نظرية التصفية» (2026-11-16):
- **Result:** a 20 s, 7-shot film in one generation, 60 credits, first try. Camera, cuts, who is in each shot, prop custody and timing all matched the previs. The user judged it a full success.
- **Before:** the same story via Route A (storyboard frames + 8 start/end clips) cost about 67 + 120 credits and still had 3 clips with camera drift, intruding characters and transferred props.
- **Evidence:** `campaign-puppet/production/test-video-06-blender-pilot/`: `TEST-REPORT.md` (pilot and full results), `scripts/`, `review/*/compare/`.
  - The final mockup is v026 (`refs/full-20s-v026.mp4`).
  - The user gave the "full success" verdict in chat on 2026-11-16.
  - **Proven only on a dialogue-free film** (jaws closed; the creator's voice is added later, see §1).

**Core idea:** the model stops guessing where things are. A colour-coded Blender mockup fixes the camera, lens, cuts, blocking and every prop's position and timing. Seedance re-skins it with the real puppets from the masters.

> The grey-box decides **where and when**. The reference images decide **what it looks like**.

But Seedance copies stand-in **shapes** too (see §5), so the mockup must not contain shapes that look like something else.

## 1. When to use which route

| Use Route B (Blender) when | Use Route A (storyboard frames) when |
|---|---|
| Several shots or cuts must share one consistent world | One single shot |
| Props move between hands or places (custody matters) | No prop handling |
| Exact camera, framing or timing matter | Loose framing is fine |
| A character must be absent from some shots | Everyone is always in frame |

Route B replaces Route A's phase 3 (the picture storyboard) and phase 4 (clip-by-clip generation). The **Blender frames are the storyboard**, and they cost nothing. The only paid images are the 1–2 look frames for `image_references` (see §6).

Phases 1–2 (story, shot list) and 5–10 (QC, assembly, voice pass, report) are shared. Jaw-window steps apply only when the mockup animates mouths. Spend gates still apply.

**Dialogue is untested in Route B.** test-video-06 had no lines (jaws closed). For a film with lines:
- animate the stand-in mouth open and close inside each line's window in Blender,
- replace the prompt's "jaws closed" with "<character>'s jaw opens and closes only while his stand-in mouth moves",
- test it in the 10 s pilot and measure with `jaw_windows.py` before the full run.

## 2. Setup

- Blender 5.1 runs live with the Blender Lab MCP bridge on port 9876.
- From the `blender-mcp-cinematic` skill (`~/.claude/skills/blender-mcp-cinematic/scripts/`), use only:
  - `launch_live.sh <project>/renders [scene.blend]`,
  - the bridge rules,
  - `kit.save_version`,
  - `render_preview.sh`.

  Ignore its pointer to cinematic-previz and its Cycles look stills, Meshy and final-render steps. In Route B, Seedance renders the final pixels.
- Never run long jobs through the bridge: it times out at 300 s and blocks the window.
- Render in a background Blender from a saved `.blend`: `~/.claude/skills/blender-mcp-cinematic/scripts/render_preview.sh <blend> <outdir> 100 1`.
  - The arguments are the resolution percent and the samples. The Workbench engine, 720×1280 and 24 fps come from the `look` part.
  - With colander booleans, 480 frames took about 70 s.
- **Template:** `scripts/blender/build_shot_example.py` (the full test-video-06 scene). Copy it into `<project>/scripts/build_shot.py` and adapt the constants.
  - Parts: `look`, `set`, `puppets`, `props`, `cameras`, `animate`.
  - Run a part live with `PART='animate'; exec(open(F).read())`.
- Save a new version after every accepted change: `import sys; sys.path.insert(0, "/Users/dribrahimm/.claude/skills/blender-mcp-cinematic/scripts"); import kit; kit.save_version("<project>/<slug>-previs-v0NN.blend")`. It refuses to overwrite, and the template does not import `kit` itself.

## 3. Build conventions (each one cost a failed iteration)

**Space and directions**
- **World:** metres, Z up. The counter top is at 0.80 and the cameras sit on the −Y side (the 180° line runs along X).
- **Puppets face −Y,** so a puppet's RIGHT hand is at −X. Getting this wrong crosses the arms.
- **Rotation sign:** a head or eye rotation of +X looks DOWN. v001 had every head and eye inverted.
- **Pour axis:** tip a pot about its handle axis (X) toward the camera. A pour over the side a hand holds reads as coming out of the hand.

**Stand-ins**
- Puppet proportions: big head, short body. The torso is raised so the counter sits at the waist.
- **Each character has unique colours,** used nowhere else. **[Example]** test-video-06:
  - Nora: plum cardigan, chestnut bob, PINK mitts.
  - The Professor: olive suit, dark ring of hair, burgundy bow tie, bare orange-tan hands.
  - Props: red colander, red knob.
  - The prompt maps each colour to its puppet.
- **Eyes:** an open eye has no lid geometry; a thin lid line read as spectacles. A closed lid covers the eye, and the pupil is hidden.
- **Contents never shrink in place.** Pasta and water leave over the lip, and are hidden (scale 0.001 or z −5) only once they are outside the rim. Shrinking inside the pot reads as a vanishing prop.

**Keying and idempotence**
- **Key every pose from constants, never from the current pose.** After `animation_data_clear()` an object keeps its last evaluated pose, so offsets taken from it drift on every rebuild. That is how the lid ended up in the sink at f84.
- Run `animate` twice and diff the world matrices; they must agree to under 1 mm.
- **Prop custody by baking:** `follow(prop, hand, f0, f1)` keys the world matrix every frame. Key carried props before anything reads their pose; the knob taps read the lid.
- **Hiding a character:** in Blender 5, `keyframe_insert('hide_render')` silently produced a detached action. Instead, key the character's ROOT to z −10 for the frames where they must not exist (shots they aren't in, and after an exit, so no shadow is left behind).

**Heavy geometry and lighting**
- **Booleans on animated props** (colander holes): set `show_viewport=False` and keep them render-only. Otherwise every `frame_set` during baking re-evaluates them and the bridge hangs.
- **Workbench shadows are scene-wide.** Light from high (`light_direction ≈ (0.15, 0.35, 0.92)`, shadow intensity about 0.35) so no head silhouette lands on the wall, where it can become a ghost figure.
- **Ceilings:** don't add a ceiling slab; under Workbench its shadow darkens the whole set. Make the walls tall enough that angled cameras never see past them.

## 4. Camera and staging

- **Search cameras numerically, don't guess.** Project the vertices with `world_to_camera_view` and score the candidates:
  - head margins of at least 3–4%,
  - eyes on the upper third,
  - headroom and side margins,
  - at least 30° off the previous setup's axis (the 30-degree rule), or a clear size change,
  - key props visible,
  - props separated on screen when the story needs them apart.

  `scripts/blender/qc_checks.py` has the helpers (`bbox_extent`, `where`, `inside`).
- **Intruders:** check every vertex of every character who must not be in a shot against that shot's frustum (`inside(...)`). Also check the pot and hands in a close-up of someone else.
- **Avoid long reaches.** Character roots stand at y = 0.45: about 0.45 m behind the sink centre, 0.24 m behind its back edge. Stretch-cylinder arms therefore get very long when reaching the pot.
  - Keep reaches short and fast, approach from above, and keep waiting hands at chest height.
  - A long arm reaching behind the pot came back as a dark slab (pilot), and still as a greyish sleeve in full-v1.
- **Raised arms:** raise the camera-side hand and keep the arm outside the head silhouette for that shot's camera (shot 2: his LEFT hand), so it never crosses the face.
- **Route hands away from props they must not touch.** A hand that merely passes near the colander was rendered as reaching into it, which contradicted the gag.
- **Cut on action.** Start a gesture 2–3 frames before the cut.

## 5. What Seedance copies from the stand-ins (pilot findings)

| Stand-in shape | Rendered as | Rule |
|---|---|---|
| Thin, wavy, open water stream from the lip | ✅ Convincing clear water | Keep water streams thin, open-ended (curve with bevel, `use_fill_caps=False`), uneven and fanned. The stream leaves visibly over the lip with an air gap from the pot wall. |
| Thick translucent tube + round blobs (gush) | ❌ Milky white tube with egg shapes | Never use blob spheres or a thick core. Let the pasta carry the volume. |
| Three straight parallel streams | ❌ Look like rods (caught in the mockup) | Fan them out, vary the thickness, stagger the timing, add wobble. |
| Long thick stretch-cylinder arm reaching behind the pot | ❌ Dark grey slab or board (pilot); greyish sleeve f124–140 even after the fix (full-v1) | Thinner arms (radius about 0.036), short reaches, no long horizontal bars. |
| Hand path passing near a prop | ❌ Hand reaching into the prop | Route hands clear of props, and say so in the prompt. |
| Block hand with only the centre finger up | Reviewers read it as an obscene gesture (caught before the render) | Raise the thumb-side finger; curl the centre finger and thumb. |
| Dark discs on the colander | Read as polka dots (review) | Real boolean holes, render-only. |
| Pot hidden behind the colander in a two-shot | Reads as "pot in the colander" (review) | Separate them on screen with the camera angle. |
| Colour-coded puppets, glass lid with red knob, red colander, yellow elbow pasta | ✅ Mapped correctly to the masters and real props | Keep the unique colours and give the mapping in the prompt. |

## 6. QC before any spend

1. **Numeric** (`scripts/blender/qc_checks.py`):
   - BVH overlaps for every prop–body, prop–prop and hand–hand pair, over the frames where they could meet.
   - Frustum intruders per shot.
   - Edge margins and the eye line per shot.

   Allowed contacts: intended grips, a lid seated in its rim, a held colander.
2. **Visual, every second:** run `bash $SK/frame_review.sh renders/mockup-vNNN.mp4 review/mockup-vNNN` (frames at 8 fps, plus 2 s contact sheets at 4 fps) and read every sheet. Also build contact sheets of every shot's start, middle and end plus every cut pair, and step through ±0.3 s at 24 fps around every custody change or state change.
3. **Independent multi-lens review** (story/cause→effect, continuity/custody, AI-misread risk, cinematography), plus one skeptic per lens who tries to refute each finding.
   - Three rounds found 37 → 34 → about 20 real issues; most were invisible to a single pass.
   - Re-run the round after big changes.
4. **Look frames (paid, gate a).** If no approved frame of this set exists, generate 1–2 look frames with `gpt_image_2_6_flare`:
   - 9:16, `batch_size: 1`, about 1.5 credits each at 1k,
   - the masters as references, plus a Blender still from the same camera so the geography matches,
   - prop states that match the mockup at the film start.

   Show the `get_cost` before generating. test-video-06 reused S1a and S2a from test-video-05's Route A storyboard (`test-video-05/storyboard/final/`).
5. Show the user the mockup video and board (**approval 1**), together with the look frames and the `get_cost` of the pilot and the full film (gate b).

## 7. The request

**Pilot first.** Cut 10 s from the hardest shots. ffmpeg's `n` is 0-based, so n = Blender frame − 1. test-video-06 used Blender f1–127 + f197–309:

```bash
ffmpeg -i renders/mockup-vNNN.mp4 -vf "select='between(n,0,126)+between(n,196,308)',setpts=N/24/TB" -an -r 24 -frames:v 240 refs/pilot-cut-10s.mp4
```

- Check with ffprobe that it has exactly 240 frames.
- Write a pilot request whose per-shot seconds are re-timed to the cut (the joins are new cuts), describing only the shots in the cut.
- Price it (30 credits), approve, generate, QC with §8, and fix the mockup.

Then run the full film (20 s = 60 credits). The Higgsfield tutorial cites up to 30 s per generation; confirm the duration with `get_cost`. Split longer films at a cut into parts of 30 s or less.

```json
{"model": "seedance_2_5", "mode": "omni_reference", "prompt": "<from build_request_example.py, see the template below>", "duration": 20, "resolution": "480p", "aspect_ratio": "9:16",
 "generate_audio": true, "draft": true,
 "medias": [{"role": "video_references", "value": "<mockup mp4>"},
            {"role": "image_references", "value": "<master A>"}, {"role": "image_references", "value": "<master B>"},
            {"role": "image_references", "value": "<set/prop look frame 1>"}, {"role": "image_references", "value": "<set/prop look frame 2>"}]}
```

- **No `start_image` or `end_image`.** Blender is the single source, so a start frame can't fight the video. Standard bitrate.
- **Commands** (from the repo root, with the Test Lab running and the sandbox off; see `hf_lab.py`):
  1. Copy `scripts/blender/build_request_example.py` to `<project>/scripts/build_request.py`. It writes `../clips/request-full.json` relative to itself. Edit the PROMPT and the `mid()` substrings to match your uploaded file names.
  2. `python3 $SK/hf_lab.py upload <project>/refs/full-20s-vNNN.mp4 <masters> <look frames> > <project>/clips/media-ids.json`. The mp4 uploads as `video/mp4` and is confirmed as type `video`.
  3. `python3 <project>/scripts/build_request.py <project>/clips/media-ids.json`
  3b. **Prompt review (gate):** check the generated prompt against the §7 prompt template items 1–8 and the mockup board. Per-shot seconds must match the measured cuts. The colour → character/prop mapping must be complete. Each shot names only the characters visible in it. There are no quotes, dialogue or syllable counts, and there is a SOUND block (prompting.md §8 items 1–2). Show the prompt to the user with the get_cost.
  4. `python3 $SK/hf_lab.py cost <project>/clips/request-full.json`, then get approval.
  5. `python3 $SK/hf_lab.py generate <project>/clips/request-full.json`
  6. `python3 $SK/hf_lab.py wait <job> --out <project>/clips --names full-v1`
- **Image references:** the masters of the characters in the film, plus 1–2 set or prop look frames (§6 step 4).
  - **Don't pass an image whose content contradicts the mockup.** A frame of him holding the pot in the last shot could bring the pot back after it has been set down.

**Prompt template** (`scripts/blender/build_request_example.py`):
1. Live-action felt puppets, a real kitchen, no puppeteers.
2. "The reference video is a colour-coded grey-box animation of this exact scene. Copy it exactly for camera position, lens, framing, cut timing, blocking, every movement and its timing. Replace its stand-ins with the real characters and props from the reference images; never copy the stand-in look."
3. Name the stand-in failure modes: stretched tubes are normal arms (never boards or slabs), water is clear and thin (no tubes, no egg-shaped drops).
4. The colour → character and colour → prop mapping. Only one character wears the mitts.
5. "Only the characters visible in the reference video appear in each shot; never add a person." Jaws closed, no lens looks.
6. Story-critical negatives, e.g. "after he sets the colander down he never touches it again; he holds the pot only by its two side handles."
7. SOUND: foley only, no voice, no music, plus the SFX list.
8. Per-shot timing in seconds that matches the cuts (`0 to 3.5 s, wide shot: …`). No quotes and no syllable counts.

## 8. After the render: the side-by-side comparison is MANDATORY

Run this after **every** Route-B generation, pilot and full alike, before any verdict. **Always send the side-by-side video to the user** with the report. The user asked for this explicitly after test-video-06: judging the AI result next to its mockup is how they decide.

```bash
python3 $SK/blender/side_by_side.py --mockup refs/<mockup>.mp4 --ai clips/<result>.mp4 \
        --out review/<result>/compare --cuts <first 0-based frame of every shot after the first>
```

It writes:

| Output | What it shows |
|---|---|
| `side-by-side.mp4` | Mockup LEFT, AI RIGHT, with the AI audio. The mockup is resampled to the AI fps. |
| `shot-NN.png` | Per shot, five time-aligned columns: mockup on top, AI below. |
| `cuts.png` | Every cut pair (last frame before, first frame after). |
| `overview.png` | The start, middle and end of every shot. |
| `compare.json` | Frame counts, fps, sampled frames (mockup and AI), the `alignment` used, and the **measured cut offsets**: the peak frame-difference near each planned cut, for both videos, in mockup frames (`offset_frames`) and seconds (`offset_seconds`). |

The comparison is aligned by time, not by frame number:
- `--cuts` and every frame number in the report are mockup frames.
- Mockup frame i is t = i / mockup fps. Its AI partner is AI frame round(t × AI fps).
- With equal fps that is the same index, so the 24 fps results below are unchanged.
- If the AI comes back at another fps, `warnings` says so. The sheets and offsets are still correct: a 30 fps copy of pilot-v1 measured −0.8, +1, +1 against the 24 fps −1, +1, +1.

Thumbnails are cached in `<out>/_frames`, keyed by `_frames/signature.json` (path, size and mtime of each input, plus `--thumb`). Re-running into the same `--out` with a new AI file wipes the stale AI thumbnails, so a re-roll can reuse its folder safely.

Read every sheet. The cuts sheet catches what the shot sheets hide.

On test-video-06 every AI cut landed within ±1 frame of the mockup:
- the 20 s film: −1 on 5 of 6 cuts, 0 on the cut into shot 4,
- the 10 s pilot: −1 on its first cut, +1 on the other two.

That is harmless; re-time it in the edit if it matters. A cut more than ±1 frame off is flagged in `warnings`.

Then:
- Zoom on hands, water, props and every flagged cut, at full size, from the AI file.
- Run `voice_scan.py`. Mute any voice-like range in a `-sfx-clean` copy.
- Expected residuals:
  - a cut can land one frame early or late,
  - a long reach can still read as a greyish sleeve (full-v1: his far arm reaching for the handle, f124–140), smaller than the pilot's slab,
  - lips can sit slightly parted in close-ups.
- Then continue with the shared phases 5–10. Route B differs in three ways:
  - **Re-roll:** fix the mockup and re-render the whole film, or render a cut of 30 s or less containing the bad shots and splice it in at a cut during assembly (gate c).
  - **Phase 7 prices** scale with the full length. A native 1080p 20 s render is 16 credits/s = 320; price the upscale with `get_cost`.
  - **Phases 8–10** (assemble, voice pass, report) are unchanged.

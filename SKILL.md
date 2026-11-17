---
name: ai-puppet-video
description: Direct and produce AI felt-puppet videos for any cast, language or setting, end to end. Covers the channel format and audience strategy (archetype, made-for-kids check, own IP, Shorts-first), character master images, a series bible, then character sheets and character.json, a story adapted from a reference video, the beat sheet, second-by-second shot list and voice-script plan, a Blender mockup as a Seedance video reference (Route B) or a storyboard then clip-by-clip Seedance 2.5 on Higgsfield (Route A), prompt review, per-second QC with voice-leak and jaw-window checks, re-rolls, an SFX-only cut, and the creator's voice placed in CapCut. Use when the user wants to plan a puppet channel, create puppet characters or a character sheet, write a series bible, adapt a reference video, write a voice script, or make, plan, storyboard, prompt, re-roll, review, fix or assemble an AI puppet or talking-character video, a Seedance/Kling/Higgsfield shot, or a Blender previs for AI video, even if they don't name the skill.
---

# AI puppet video: from characters to final cut

**General skill for any felt-puppet cast.** The first project's characters (the Professor, Nora, Sami, Adam) appear only as examples. A cast-specific skill (for example one dedicated to the Professor and Nora's own channel) should be a separate skill that builds on this one.

**The whole pipeline:**
1. **0** format and audience: archetype, honest "made for kids" classification, own IP, Shorts-first (`references/channel-strategy.md`).
2. **0a** character images: material anchor → hero head → wardrobe → full-body masters for the cast (`references/characters.md` §1 stages A–E).
3. **0b** series bible: the dramatic world, plot engine and relationships built on those masters.
4. **0a-finish** full description and character sheets: detail sheets 01–05, one-cell fixes, then `character.json` + README filled from the approved bible (`references/characters.md` §1 stages F–G, §6).
5. **0c** idea from a reference video, adapted to the cast → `STORY.md`.
6. **1–2** beat sheet, silent/dialogue decision, second-by-second shot list and `VOICE-SCRIPT.md` with planned windows.
7. **Route B** (Blender mockup checked every second → prompt review → pilot → full Seedance render) or **Route A** (picture storyboard → clip by clip), each with its spend gates.
8. **5–7** frame-by-frame QC (Route B: mockup|AI side-by-side), A/B re-rolls, final quality.
9. **8** assemble the SFX-only cut and the measured voice-window table; refit `VOICE-SCRIPT.md`.
10. **9** the creator records and voice-changes → Claude reviews the takes and places them in CapCut.
11. **10** report.

User approvals: 0 the format, 0a each master-level image, 0b the bible statuses, 0a-finish the sheet set, 0c `STORY.md`, the storyboard or mockup with its prompt and budget (gates a/b), each re-roll or finalisation (gate c), and the final cut.

This skill packages what we learned producing «البرطمان العنيد» (The Stubborn Jar) and «نظرية التصفية» (The Draining Theory, colander), 20 s Egyptian puppet sitcom tests on Higgsfield. Every rule here exists because a take failed without it. The evidence is in `campaign-puppet/production/test-video-0{1,2,3,5}/` and, for the Blender route, `test-video-06-blender-pilot/TEST-REPORT.md`.

**Core insight:** an AI video model fills every gap you leave with its own guess. It decides where the prop goes, who looks where, when mouths move, and how tight the frame is. Quality comes from:
- removing gaps before spending credits: a second-by-second plan and a picture storyboard the model must start from,
- one shot per generation (Route A), or one generation locked to a Blender video reference (Route B),
- a measured, frame-by-frame review of what actually rendered.

Prompt words steer the model; they don't guarantee anything. The start frame controls far more than the prompt does, and a video reference controls more than both.

## Standing rules for this user (do not skip)

1. **No character voices in generated video, ever.** Generated audio is foley and SFX only; lips move silently.
   - The creator records the lines himself and voice-changes them.
   - **Claude** then reviews his audio and assembles it onto the video in CapCut (phase 9).
   - Seedance's Arabic voices were rejected as "very bad".
2. **Storyboard first.**
   - **Route A:** a shot-by-shot storyboard as images in Higgsfield with `gpt_image_2_6_flare`.
   - **Route B:** the Blender mockup video and board, plus the 1–2 flare look frames used as set and prop references.

   Either way, show it with the video budget and wait for approval before generating any video.
3. **Check every second.** Audit at 8–24 fps, with zooms on hands, props and mouths. A jar floated for 2 frames in take 1, and a 1 fps review missed it.
4. **Cinematography is part of the job.** Plan the angle, the cutting between speakers, the space between characters, the 180° line and rule-of-thirds ("golden") framing for every shot.
5. **Identity = each character's approved master image, read-only:** `<cast-root>/<character_id>/00-master-full-body.png` (made in phase 0a, `references/characters.md`).
   - Upload copies; never edit the files.
   - The image wins every conflict with text, sheets or old prompts.
   - When a redesign is rejected, mark every superseded file and snapshot at once. For the first project's superseded v2 material, see "Example project notes" at the end.
6. **Spend gates.** Every paid call is preceded by a free `get_cost: true` check and an explicit user OK:
   - (0) character images in phase 0a: on Higgsfield `get_cost`; on a tool without a price check (ChatGPT imagegen), state the number of images and that the cost comes from that subscription,
   - (a) the storyboard frame budget,
   - (b) the video budget, approved together with the storyboard,
   - (c) each re-roll or finalisation, shown with its verified reason and price.

   Report the actual credits from the run logs. The balance can also change from outside the session.
7. **Route B: always show the mockup next to the AI result.** After every Blender-previs generation, build the side-by-side with `scripts/blender/side_by_side.py` and send it with the report.

## Two routes: pick one per film

| | **Route B: Blender previs (default for multi-shot films)** | **Route A: storyboard frames + clip-by-clip** |
|---|---|---|
| How | Build the scene in Blender with colour-coded stand-ins, animate every shot, render a mockup, and upload it as `video_references` with the masters as `image_references`. One generation renders the whole film. | Phase 3 picture storyboard, then phase 4: one Seedance clip per shot from start/end frames. |
| Proven | test-video-06: 20 s, 7 shots, **60 credits, first try**. Camera, cuts, cast per shot, custody and timing all matched. The user called it a full success. | test-video-03/05: works per clip. Camera drift, intruding characters and prop transfer kept recurring (05: about 67 + 120 credits, 3 clips still wrong). |
| Use when | Several shots, props changing hands, characters absent from some shots, exact framing or timing. **Proven only on a dialogue-free film** (jaws closed). Lines are untested; see `blender-previs.md` §1. | A single shot, or no Blender available. |
| Read | **`references/blender-previs.md`**, plus the `blender-mcp-cinematic` skill for the live Blender. | Phases 3–4 below. |

Route B replaces phases 3–4. The Blender frames are the storyboard (free). They are shown to the user as **approval 1**, together with the 1–2 flare look frames (gate a) and the `get_cost` of the pilot and the full film (gate b), plus the full request prompt for review. Then:
- a 10 s pilot (30 credits, approval 2),
- the mockup fixes,
- the full film (approval 3).

Phases 1–2 and 5–10 apply to both routes; jaw-window steps apply only when the mockup animates mouths. Seedance copies stand-in **shapes**, not only motion; design the mockup by the table in `blender-previs.md` §5.

**Always compare the Blender mockup with the AI result side by side** after every Route-B render (pilot and full). Run `scripts/blender/side_by_side.py`: it writes the mockup|AI video, frame-aligned per-shot sheets, the cut pairs and the measured cut offsets. Send the video to the user with the report. This is a standing rule for this user.

## Project layout (one folder per test or episode)

Cast and world (phases 0a, 0b and 0a-finish, once per series; `references/characters.md` §6 and `references/series-bible.md` §0):

```
<cast-root>/                       e.g. campaign-puppet/puppet-channel-concepts/
  STORY-AND-CHARACTERS.md  cast.json  MANIFEST-CONTRACT.md
  <character_id>/  00-master-full-body.png  01..05 sheets  character.json  README.md  SHEET-INDEX.md  WORLD.md  generation-prompts*.txt
```

Reference video (phase 0c, one folder per reference video):

```
<project>/production/reference-<slug>/   BREAKDOWN.md  adaptations.json  frames/  sheets/  audio16k.wav
```

Per episode or test:

```
<project>/production/<slug>/                  e.g. campaign-puppet/production/test-video-06-blender-pilot/
  STORY.md  SHOT-LIST.md  VOICE-SCRIPT.md  TEST-REPORT.md
  storyboard/  uploaded.json  params.json  P1-v1.png …  panels.json  STORYBOARD-<slug>.png
  clips/  request-*.json  media-ids.json  jobs-*.json  S1.mp4 | full-v1.mp4 …   (first renders, untouched)
  scripts/  build_shot.py  build_request.py  qc_checks.py     (Route B)
  <slug>-previs-v001.blend …                                   (Route B, never overwritten)
  renders/  mockup-vNNN.mp4  qc/BOARD-vNNN.png                 (Route B mockups)
  refs/  pilot-cut-10s.mp4  full-20s-vNNN.mp4                  (Route B video references)
  clips-r2/                                     (re-rolls)
  clips-sfx-only/                               (voice-muted copies for the edit)
  review/  frames/ sheets/ *.json              (QC material)
  voice/                                        (creator's voice takes, phase 9)
  edit.json  edit.timeline.md  <slug>-final-sfx-only.mp4  <slug>-final-voiced.mp4
```

Scripts live in `.claude/skills/ai-puppet-video/scripts/`. Run them from the production folder with `SK=../../../.claude/skills/ai-puppet-video/scripts` (or an absolute path).

## The pipeline

### 0. Pre-production (new cast, or a new episode idea)

Skip any part the project already has, but check that what exists is approved, not just "delivered".

**0. Format and audience, decided first** (`references/channel-strategy.md`)
- Pick one of the 7 puppet-channel archetypes with the user. This AI pipeline fits the scripted visual ones best: sitcom, micro-skit, lore.
- **Classify the audience honestly** with YouTube's factors (actual audience, subject, characters, language, activities, songs): "made for kids" means children (under 13 in the US) are the main audience or one of the audiences, not only preschool. Puppets alone don't make it child-directed, and a "13+" line doesn't make it adult. Never pick "Not made for kids" to keep comments, ads or merch. For an adult series, make the topics, humour, pacing and design truly adult; for a child-directed one, label it and plan monetization for it.
- **Own 100% of the IP:** never build on third-party characters.
- One format per channel. Design every episode Shorts-first: a hook within 1 s, a payoff that reads on mute, subtitles.
- These choices feed 0a (characters that read at thumbnail size, one signature gimmick each) and 0b (the format and audience in the bible).

**0a. Character images, image-first** (`references/characters.md` §1 stages A–E)
- Order (part 1): material/realism anchor → controlled head comparison → wardrobe edit on the chosen head → full-body master `00-master-full-body.png` → supporting-cast masters (the hero master as a material/proportion reference only, plus a do-not-reuse list). Then run 0b.
- Each master-level choice (head pick, wardrobe pick, full-body master, each supporting master) is approved before the next.
- State the digit count in caps in every prompt.
- Paid images: spend gate (0) in standing rule 6, then approval.

**0b. Series bible** (`references/series-bible.md`)
- Premise, viewer promise and dramatic question.
- The lead's (or each ensemble lead's) want, flaw and guardrail. The cast as different pressures on one flaw, each with a guardrail against a stereotype.
- A relationship table. Catchphrases with exact text and a usage trigger, plus at least one silent visual catchphrase.
- The episode formula (7-step [Example] engine, adapted to the lead's flaw), a guest policy, visual world rules, and voice/dialect left null until approved.
- Label every statement APPROVED, EXPLANATION or PROPOSED. Unknown is null, never invented.
- **Approval gate.** Show STORY-AND-CHARACTERS.md and cast.json; only items the user explicitly approves become APPROVED, everything else stays PROPOSED or null.

**0a-finish. Full description and character sheets** (`references/characters.md` §1 stages F–G, §3–§6)
- Order (part 2), after the bible (0b) is approved: detail sheets 01–05 (expressions chosen from the bible persona) → one-cell targeted fixes → `character.json` + README.
- Sheets 01–05 can be generated as one batch from the approved master, then reviewed and approved as a set; record per-sheet status honestly.
- Repeat the identity-lock paragraphs verbatim in every sheet prompt. QC every sheet against the master (rotations, mirrored hair, palm/back thumb side, leg length).
- Write `character.json` (visual invariants from the master and sheets, wardrobe, `unresolved` = null, `reusable_prompt`, plus persona, relationships and catchphrases copied from the approved bible and cast.json, never invented here) and a README.

**0c. Idea → STORY.md** (`references/idea-from-reference.md`)
- From a reference video:
  1. `BREAKDOWN.md`: second-by-second table, why it's funny (mechanics), risks, originality line.
  2. Three adaptations (faithful / lead-twist / ai-proof).
  3. Score on *named* criteria, graft, then map the roles onto the cast.
  4. Run the visible-logic gate: every effect has an on-screen cause, every state change is performed by a character, it reads on mute, and lines are natural idiom.
  5. Write `STORY.md` in the user's language.
- Adapt mechanics, never copy footage, music, staging or dialogue.
- **Approval gate.** On rejection, record the user's words and root cause, version the file, and list what changed.

### 1. Story → beat sheet

- If phase 0c already produced an approved `STORY.md`, turn it straight into the beat sheet.
- Decide here whether the film is **silent, dialogue, or silent with one voiced button** (`references/voice-script.md` §A). The hybrid is the recommended default.

- **Only if there is no approved STORY.md:** run `references/idea-from-reference.md` from Step 2 using a bible seed (2–3 drafts scored on the named criteria in its Step 3 table), then the visible-logic gate and the STORY.md approval.
- Prefer one hero prop, a visual problem, an escalation and a visual payoff. Every extra object is something the model can lose.
- **Avoid:**
  - phones and screens (they render UI and text),
  - many loose objects (falling books),
  - anything that needs text on screen.
- If the puppets have short legs or no visible legs, frame waist-up behind a counter to hide them. [Example] the first cast's short comic legs.
- Keep lines short and give each shot one speaker. Our measured jaw windows were only 0.5–2.6 s, so roughly 3–5 syllables per second of window ([Example] Egyptian Arabic; calibrate per language/performer, `references/voice-script.md` §B.3). Plan to speed lines up, or use voice-first lip-sync (see experiments).
- Draft `VOICE-SCRIPT.md` (planned windows) with the shot list. Refit it to the measured windows after QC (`references/voice-script.md`).

### 2. Second-by-second shot list (`SHOT-LIST.md`)

For each shot, write down:
- **Shot size and angle, and why.**
  - an establishing two-shot first,
  - a slight low angle for a pompous line,
  - a high-angle insert for the payoff,
  - a match frame back to the opening two-shot for the punchline.
- **Framing.**
  - Which third each face sits on, with look room toward the other character.
  - Eyes on the upper third line.
  - Characters fully inside the frame.
  - Foreground in the bottom fifth.
  - Faces, hands and the payoff out of the bottom 15–20% and the right-edge button column (platform UI).
- **The 180° line:** A is always screen-left looking right, B screen-right looking left. Set it up in shot 1.
- **Action per second**, with sub-timings, and **prop custody per second** (who holds each prop, or where it rests; a prop is never "in the air").
- **The mouth window and SFX** for each line.
- **End state → next start:** hands, prop, lid and gaze at the end of each shot, matched to the start of the next.
- **The listener problem:** a character who isn't acting freezes in a two-shot, even when you prompt actions for him (tested twice). Plan a separate reaction single for the listener, or keep two-shots short.

See `references/cinematography.md`.

### 3. Picture storyboard (approval gate)

**Deep-check every image before the storyboard is shown.** Follow `references/storyboard-qc.md` step by step; it is mandatory.
1. Write a state ledger first: per frame, the camera, each character, and every prop's exact location and state.
2. Generate in dependency rounds (`scripts/storyboard_rounds.py`). Reference each frame to the frame it must match. Make END frames as an **EDIT of the START** (START as Image 1; "EDIT Image 1, do not re-compose it … change only …"). In test-video-05 the masters-first FRAMING LOCK form still drifted 6–14% on clips 1 and 4; EDIT mode gave 0% on the first try for clips 1, 2 and 4.
3. Stage A, per frame: identity, sides, custody, prop type, gag state, hands, eyes, composition, set.
4. Stage B, START↔END of each clip: `scripts/frame_check.py pair` (camera shift, blend, diff).
5. Stage C, every cut END(N)→START(N+1): state, geography, grade, overlap, cut type.
6. Stage D: an independent review, a fix loop, and `storyboard_boards.py plan.json --check` must report no unplanned camera moves. Only then show the boards.

See `references/storyboard.md` for prompts and layout. In short:
- Use `gpt_image_2_6_flare`, 9:16, high, `batch_size: 1`. `batch_size: 2` bills double and returns one image.
  - 1k (752×1344, 1.5 credits) is enough for 480p tests.
  - Use 2k (2.75 credits) when the final will be 720p or more, so the start frame isn't smaller than the video.
- Reference each frame to the frame it must match:
  - an END frame → its START, in EDIT mode,
  - a cut-in → the frame before the cut,
  - a new setup → the masters first, then the nearest approved frame of the same set.
  
  Don't feed panel 1 into every frame: its props get copied back (the colander reappeared in the sink).
- Frame every panel about 10% looser than the final shot. Edits can punch in but can't widen a shot.
- Measure the edge margins in pixels.
- Check custody, sides, fingers, hands and identity. Re-roll failures.
- **The start frame decides** prop shape, expression, costume state and pose more than the prompt does. Any state that differs from the master (a crooked bow tie) tends to revert to the master's version, so measure it in the panel before approval.
- Build one board per clip plus the transitions sheet with `scripts/storyboard_boards.py plan.json --check`, and send them with the `get_cost` total of every planned clip. **Wait for approval.**

### 4. Shot-by-shot video generation

See `references/video-generation.md` and `references/prompting.md`. In short:
- **Route A: one clip per shot,** not one multi-shot render without a video reference (Route B locks a multi-shot render with a Blender mockup). Use Seedance 2.5, `omni_reference`, 480p for tests, 9:16, `draft: true` (no extra cost). Leave `bitrate_mode` at standard when passing image references: high failed 8 of 8 jobs.
- For hard shots, render two 480p candidates and pick. More takes improve the result more than more resolution does.
- The minimum length is 4 s; generate 4–5 s and trim.
- `start_image` = the shot's panel; `end_image` = the end-pose panel when the state changes. `image_references` = the masters of the characters in the shot.
- **Describe only the characters who are in the clip,** and pass only their masters. A header that mentions an absent character makes Seedance add them or move their props: Nora's oven mitts ended up on the Professor's hands.
- Use **standard bitrate** when passing `image_references`. With high bitrate, all 8 jobs failed (refunded).
- Check that each clip's first and last frames match its storyboard START and END (`frame_check.py pair`, plus an eye check for colour and props).
- **Never put quoted dialogue or syllable or word counts in a video prompt.** Seedance reads them aloud: it said "eight syllables" and "fourteen syllables" despite "absolutely no voices". With those removed, the three re-rolls came out with no voice at all.
- The mouth wording ("jaw keeps opening and closing quickly and continuously … shuts at X s") avoids voice leaks. It does **not** control the rhythm or the window. Expect drift and measure it.
- **Audio strategy:**
  - **A** (used so far): `generate_audio: true`, then mute (phase 5).
  - **B:** `generate_audio: false` (same price) and add SFX in CapCut. Use B when a shot keeps leaking, or when muting would kill the key SFX.

### 5. QC: every second (gate)

See `references/qc-checklist.md`.
1. `frame_review.sh` → frames, contact sheets, cut times.
2. `jaw_windows.py` → measured jaw-open windows per speaking shot.
3. `voice_scan.py --mute … --jaw <windows>` → the voice-muted copy. It mutes the detected voice **and** every jaw window: the creator's voice replaces those windows anyway, and the scanner can miss quiet leaks. Spot-check the result by ear or with Whisper.
4. Audit every frame against the shot list and the failure catalogue:
   - Step through ±0.3 s at 24 fps around every state change (pop, lid off, tie fixed) to find morph, teleport or snap frames.
   - Measure claims (bounding boxes, frame differences) rather than eyeballing them.
5. Before anything costs more credits, get an independent second opinion: a reviewer per shot plus a skeptic who tries to refute each finding. Only verified findings count.

### 6. Re-roll and pick (A/B)

- Re-roll only the shots with verified major issues, after the user OKs the price.
- Change only the prompt lines tied to the failure. Fix the start or end panel if the image caused it.
- Compare A against B frame by frame and pick per shot. A re-roll is not automatically better: our S1 re-roll fixed the drift but opened the jaw outside its window, and the first take won.

### 7. Raise the picked takes to final quality (untested so far)

See `references/quality.md` for the priced options. In short, for a 5 s clip:
- **Upscale the approved 480p take** with ByteDance (`aigc` preset): 1 credit standard, 10 pro. It keeps the exact performance you approved. Test this first.
- **Native 1080p render:** 80 credits (720p: 35). It is a new performance, so re-run phase 5.
- **Finalise the draft** (`draft_job_id`, within 7 days): quoted the same as a fresh 1080p render.

Price each with `get_cost` and get approval. `assemble.py` normalises size and fps when resolutions are mixed.

### 8. Assemble

See `references/assembly.md`.
1. Write `edit.json` (file, in, out, `jaw`, `line`, optional `mute`) and run `assemble.py`. It trims on whole frames, concatenates, and writes `edit.timeline.md` with the **voice-window table** in final-cut time.
2. Re-scan the cut.
3. Deliver the SFX-only cut, the clean clips, and the table, so the creator records to the mouths.

### 9. Voice pass (Claude)

The full method is in `references/voice-script.md`: fit table, recording guidance for the creator, take review and placement.

When the creator sends his voice-changed takes (into `voice/`):
1. Check each take: level, clipping, noise, and its length against its jaw window. Flag any line that won't fit, and suggest a faster read or a shorter line. Never slow the picture down to fit a line.
2. Place each take on its jaw window in CapCut with the `capcut-mcp-video` skill (mcp-cut), keeping the SFX track.
3. Re-check the sync frame by frame. Deliver the voiced cut and say what isn't verified.

If mcp-cut is down, build the voiced cut with ffmpeg (`adelay` + `amix`) and hand over the CapCut-ready parts.

### 10. Report

Write `TEST-REPORT.md` with:
- the settings, job IDs and the actual credits from the run logs,
- what worked and what's still wrong (verified, timestamped, with severity),
- the voice windows,
- the next step.

Summarise for the user in short Egyptian Arabic, whatever the series language.

## Quick reference: failures and what actually worked

| Failure | Status of the fix |
|---|---|
| Prop floats or vanishes | **Fixed** (takes 2–3): custody per second, plus an insert where one hand anchors the prop on the surface. |
| Singles don't read as a conversation; characters look into the lens | **Mostly fixed:** establishing two-shot, the 180° line, "head three-quarters toward X, eyes on X". There were still occasional lens looks, especially during grooming beats. |
| "Rubbing palms" read as prayer | **Fixed:** "hands never press palm to palm" plus a hands-apart gesture (the exact gesture isn't obeyed). |
| Two-shot squeezed into 9:16 | **Improved:** the chest-up recipe plus a 10%-looser storyboard. Verify the margins in the panel. |
| Voices leak | **Fixed** by removing quotes and counts. Still run `voice_scan.py` and mute the jaw windows. |
| Mouth window short, late, or outside the plan | **Not fixed by prompting.** Measure with `jaw_windows.py`, fit the lines to it, or test voice-first lip-sync. |
| Jar grows a neck when the lid comes off | **Not fixed:** the prompt alone failed twice. Hypothesis: fix the jar in the storyboard (a straight jar with a flush lid, or a visible neck under a lid of the same width). Cut on the pop in the meantime. |
| Lid twist not readable | **Not fixed:** the side-grip wording was ignored 4 times. Carry the payoff on the pop and lift in the insert; draw the grip in the panel; give the lid a visible non-text mark. |
| Listener freezes in a two-shot | **Not fixed:** the prompt actions failed twice. Use a reaction single (untested). |
| Face balloons during strain | **Fixed:** "felt head keeps its exact shape; strain via eyes, brows, trembling". |
| Storyboard set drift or swapped sides | **Fixed:** sides in capitals, and each frame referenced to the frame it must match. |
| Camera drifts between a clip's START and END frames | **Fixed:** the END generated as an EDIT of the START; `frame_check.py pair` / `storyboard_boards.py --check` must pass. |
| A prop slides, vanishes or changes type between frames | **Fixed:** a state ledger, the exact spot named in every prompt, the type locked in the header, and Stage A checks. |
| Camera drift, intruding characters, props jumping across a multi-shot film | **Fixed by Route B:** the Blender mockup as `video_references`. Locked across 7 shots in one 20 s render. |
| Stand-in shapes copied literally (water blobs → white 'eggs', long arm → dark slab, hand path near a prop → hand in the prop) | **Mostly fixed in the mockup** (full-v1 still had a greyish far-arm sleeve over f124–140): thin, open, fanned water curves; short reaches; hands routed clear of props; a prompt line naming each failure mode (`blender-previs.md` §5). |
| Mitts or props transferred between characters | **Fixed by Route B** and unique colour coding per character, with the mapping stated in the prompt. |

## Open experiments

Details and prices are in `references/quality.md`. All are untested; try each on one 4–5 s shot, with `get_cost` first.

1. **Lip-sync from the creator's recorded voice (most valuable).** In suggested order:
   - `sync_so`: re-sync the lips of an already approved clip to his audio.
   - Seedance `audio_references`: generate the shot against his recording, then mute the clip.
   - `intone`: one or two characters speaking voice recordings to each other.
   - Motion transfer from a real hand puppet (`motion_control`, `hf_mult_motion_control`).
2. **Upscaling a 480p take to 1080p** (1–10 credits) against a native 1080p render (80).
3. **A one-shot model comparison** at 1080p: `kling4_0`, `wan3_0` and `veo3_1` quote 16–17.5 credits for 5 s, against 80 for Seedance 2.5. Only Seedance 2.5 has been tested on these puppets.
4. A reaction-single pattern for the silent partner.
5. Fixing the jar shape in the storyboard; a lid design with a visible edge mark.
6. Whether the on-twos judder disappears in non-draft renders.

## Files

- `references/channel-strategy.md`: **phase 0**:
  - the 7 puppet-channel archetypes with their engines,
  - honest "made for kids" classification, owning the IP,
  - character, episode, title and thumbnail implications,
  - real-puppetry craft rules (eyeline, eye-level camera, soft light, jaw on vowels, voice pitch) mapped to prompts and QC,
  - a pre-launch checklist.
- `references/characters.md`: **phases 0a and 0a-finish**: image-first character creation, master spec, sheet prompt skeleton, hand/angle one-cell fixes, sheet QC, folder and `character.json` contract, guests.
- `references/series-bible.md`: **phase 0b**: premise, hero, cast as a dramatic system, catchphrases and callbacks, episode formula, continuity, guests, world rules, voice/dialect, avoid list, fill-in template.
- `references/idea-from-reference.md`: **phase 0c**: reference-video breakdown, three adaptation lenses, named scoring, graft, cast mapping, visible-logic gate, `STORY.md` template, originality boundaries, rejected-idea lessons.
- `references/voice-script.md`: silent vs dialogue, line-writing rules and the syllable/window fit, the `VOICE-SCRIPT.md` template, recording guidance, take review, placement, dialogue on Route B (untested).
- `references/blender-previs.md`: **Route B**: Blender build conventions, what Seedance copies from stand-ins, numeric camera and intruder QC, the review loop, the request and prompt template, results.
- `references/storyboard-qc.md`: **the mandatory deep image check**: ledger, reference chain, EDIT-mode END frames, stages A–D, tool calibration, the failure list.
- `references/storyboard.md`: panel prompts, params.json format, the review checklist, the sheet.
- `references/video-generation.md`: Seedance parameters, media roles, costs and budget, finalising, model behaviours.
- `references/prompting.md`: templates, wording that worked or backfired, image numbering.
- `references/cinematography.md`: 180°, thirds, 9:16 coverage, pacing, safe zones.
- `references/puppet-look.md`: puppet vocabulary, identity, hands, mouths, props and screens.
- `references/qc-checklist.md`: per-clip checklist and the failure catalogue.
- `references/assembly.md`: trimming, muting, edit.json, the voice pass, ffmpeg recipes.
- `references/higgsfield-mcp.md`: call shapes, the upload flow, prices, gotchas.
- `references/quality.md`: routes to final quality (upscale, native HD, bitrate), lip-sync options, other models, finishing passes, budget.
- Scripts:
  - `hf_lab.py`: Test Lab calls for cost, generate, upload, wait and balance.
  - `storyboard_rounds.py`: generate frames in dependency rounds with per-frame references; dry-run, resume without paying twice (`--resubmit K` / `--resubmit-failed` to pay again on purpose), `--only … --tag vN` re-rolls.
  - `frame_check.py`: START↔END camera check (zoom and pan, blend, diff) and frame strips.
  - `storyboard_boards.py`: per-clip boards plus the transitions sheet; `--check` flags unplanned camera moves.
  - `storyboard_sheet.py`: renders one annotated board, Arabic-safe.
  - `frame_review.sh`: frames, sheets and cuts.
  - `jaw_windows.py`: measured jaw-open windows.
  - `voice_scan.py`: detect and mute voices plus jaw windows.
  - `assemble.py`: edit list → cut, timeline and voice table.
  - `blender/build_shot_example.py`: the full test-video-06 scene builder (set, colour-coded puppets, props, cameras, animation) to copy and adapt.
  - `blender/qc_checks.py`: the helpers (`overlaps`, `inside`, `where`, `bbox_extent`) plus the test-video-06 check block. Copy it to `<project>/scripts/qc_checks.py`, rewrite the block with your object names, cameras and frame ranges, and save each result to `review/qc-vNNN.json`.
  - `blender/build_request_example.py`: the 20 s `omni_reference` request with the mapping prompt.
  - `blender/side_by_side.py`: **mandatory after every Route-B render**: mockup|AI video, frame-aligned per-shot and cut sheets, measured cut offsets.

## Example project notes (campaign-puppet, not rules for other casts)

- **Cast root:** `campaign-puppet/puppet-channel-concepts/` (professor, nora, sami, adam). Identity is the v1 masters there.
- **The v2 redesign was rejected on 2026-11-15.** These are superseded (the project docs were re-pointed to the v1 masters and bannered on 2026-11-16):
  - `production/DESIGN-V2.md`
  - `production/design-v2-prompts.json`
  - `production/generated-v2/` (`*-v2-candidate-*` images)
  - `production/PRODUCTION-RUNBOOK.md`
  - `HIGGSFIELD-HANDOFF.md`
  - the v2/Elements rows of `CAMPAIGN-PLAN.md`
  - the old `production_branch: "v2_redesign_candidates"` value in `cast.json` (now `"v1_masters"`)
  - the v2 lines in the bible and WORLD.md snapshots
- **Series and test language:** Egyptian Arabic.
- **Tests:** test-video-01…06. test-video-06 (Route B) is the reference production.

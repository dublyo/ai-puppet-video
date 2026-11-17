# QC: check every second

## Contents
1. Tools
2. Per-clip checklist
3. Independent review pattern
4. Failure catalogue (symptom → cause → fix → status)

## 1. Tools

Set `SK` to the skill's scripts folder and run from the production folder:

- `bash $SK/frame_review.sh clips/S1.mp4 review/S1`: 8 fps frames (`f_NNN.jpg`, t = (n−1)/8), 2 s contact sheets and hard-cut times.
- `python3 $SK/jaw_windows.py clips/S1.mp4 --box X,Y,W,H`: the measured jaw-open windows.
  - Pick the box on an open-mouth frame. Keep the other puppet and red props (the bow tie) out of it.
  - If the whole clip reads "open", the box is wrong.
- `python3 $SK/voice_scan.py clips/S1.mp4 --mute clips-sfx-only/S1.mp4 --jaw a-b,c-d`: mutes the detected voice plus the jaw windows.
  - Treat a CLEAN result as "probably clean". It missed S1's quiet 0.2 s leak and S3's 0.5–0.95 s onset.
  - Spot-check by ear, or run `whisper-cli -ng` (Metal is blocked here). Whisper prints hallucinated sounds like "(slurping)" for non-speech; real words are the red flag.
- **Native-fps stepping** around actions and state changes:
  `ffmpeg -ss T-0.3 -t 0.6 -i clip.mp4 -vf "crop=…,scale=…" $TMPDIR/step_%02d.png`.
  The take-1 floating jar lasted about 2 frames (16.1 s) and was invisible at 1 fps.
- **Measure, don't eyeball:** prop bounding boxes before and after, frame-difference series for freezes, pixel margins to the frame edges.

## 2. Per-clip checklist (every frame)

**Physics and continuity**
- [ ] Every prop is held by a named hand or resting on a surface. Nothing floats, appears or vanishes. The lid is always on the jar or in a hand.
- [ ] Rigid props keep their height, width and shape: no squash under pressure, no neck appearing when the lid comes off.
- [ ] **State changes** (pop, lid off, tie fixed): step through ±0.3 s at 24 fps for morph, teleport or snap frames.
- [ ] Across cuts, the end of shot N matches the start of shot N+1 (hands, prop, lid, gaze).

**Hands**
- [ ] The digit count in `visual_invariants.hands` (**[Example]** 3 felt fingers plus a thumb). No extra, merged or human hands. Never palm to palm.
- [ ] Insert hands show the right character's cuff colour and enter from his screen side.

**Identity**
- [ ] It matches the masters: shape, colour, costume, texture (corduroy ribs, knit). The signature item is on the right character only. No face ballooning.

**Mouth**
- [ ] The jaw opens only in the speaker's window, and the listener's mouth is shut.
- [ ] The windows were measured with `jaw_windows.py` and noted for the voice table.

**Eyes and geography**
- [ ] The 180° line holds. Nobody looks into the lens, including during grooming beats. Eyelines connect.
- [ ] Eye focus is alive: eyes on the partner or object, never drifting upward (an upward tilt reads lifeless; `channel-strategy.md` §6). No hard nose or brow shadow across the mouth.

**Composition**
- [ ] Thirds, look room, nobody touching or cropped by the frame edges (measure in pixels), no tangents, foreground in the bottom fifth, the payoff clear of the bottom 15–20%.

**Life**
- [ ] Nobody is a frozen still while the other character acts.
- [ ] No dead tail: once the frame difference stays near 0 at the end, trim before it.

**Audio**
- [ ] The voice-muted copy exists, with jaw windows plus scan ranges. The SFX land on the action.

**Story**
- [ ] Each beat reads without sound.

## 3. Independent review pattern (before spending more credits)

1. One reviewer per clip checks every frame against the shot list and this checklist.
2. A **skeptic** opens the cited frames, tries to refute each finding, corrects the severities and lists misses.
3. Report only verified findings: blocker / major / minor, with timestamps.

For re-rolls, the reviewer compares A against B per shot and gives a pick plus trim points; the skeptic re-measures. In take 3 the reviewer and skeptic agreed on every pick.

Run this as a multi-agent workflow when the user has opted in. Otherwise do it inline with the same rigour.

## 4. Failure catalogue

| # | Symptom (where) | Cause | Fix | Status |
|---|---|---|---|---|
| 1 | Jar floats with no hand (take 1, 16.1 s); lid vanishes (17 s) | No per-second custody; opened one-handed | Custody per second; an insert with one hand anchoring the jar | **Fixed** (takes 2–3) |
| 2 | "Rubbing palms" → palms pressed together for 7 s, read as prayer (take 1) | Vague gesture | "never palm to palm" plus a hands-apart gesture | **Fixed** (the exact gesture isn't obeyed) |
| 3 | Singles centred and frontal, looking into the lens, no geography (take 1) | No camera or eyeline instructions | Establishing two-shot first, 180°, "eyes on off-screen X" | **Mostly fixed** |
| 4 | Whole apricots instead of jam (take 1) | Ambiguous prop | "smooth spread, no fruit pieces" | **Fixed** |
| 5 | Two-shot faces at 20% and 78%, cropped, counter 30% of the frame (take 2) | Landscape composition in 9:16 | Chest-up recipe; panels 10% looser; measure margins | **Improved**; the panels were still tight |
| 6 | Jar shrinks about 15% under a pressing hand (take 2) | Non-rigid prop; palm pressing down | Rigid wording; side grip drawn in the panel | Not seen in take 3's two-shot |
| 7 | Lid hidden by palms; twist unreadable (takes 2–3, both S1 takes, both S4 takes) | Default palm-over-lid pose; plain lid | Side-grip wording was **ignored 4/4**. Draw the grip in the panel; give the lid a visible edge mark; carry the payoff on the pop and lift | **Not fixed** |
| 8 | No "caught out" reaction (take 2) | No explicit freeze | "frozen still, eyes wide, brows high, jaw shut" | **Improved**; the freeze is still shortened (0.71 of 1.0 s) |
| 9 | Punchline ends 0.1 s before the clip does (take 2) | No button planned | Line done by T−1 s plus a hold; or a CapCut freeze-frame | Planned in take 3 |
| 10 | Storyboard: jar in the wrong hand; sides swapped (take 3, round 1) | No custody or side constraints, no set reference | Custody negatives, sides in capitals, each frame referenced to the frame it must match (not panel 1 everywhere; see storyboard-qc.md) | **Fixed** |
| 11 | **Voices leaked** despite "no voices"; it said "eight syllables" / "fourteen syllables" (take 3) | Counts and quoted lines in the prompt | Remove them; SOUND block; mute jaw windows plus scan ranges | **Fixed** (the re-rolls were clean) |
| 12 | Jaw window short or late (S1 0.54 of 1.5 s; S5 about 1.1–1.3 s late) | Loose timing in the model | Measure; fit the lines; voice-first lip-sync experiment | **Not fixed** |
| 13 | Jaw opens outside its window (S1-B, 2.0–2.67 s) | Same | Reject the take in A/B | — |
| 14 | Jar grows a threaded neck when the lid comes off (S4 A and B) | The lid-on panel hid the neck; prompt wording failed twice | Hypothesis: a straight jar with a flush lid in the panel, or a visible neck under a lid of the same width. Cut on the pop | **Untested** |
| 15 | Listener frozen like a still (S5 A and B) | The model animates only the actor; prompted actions gave blinks at best | Reaction single; short two-shots; draw the listener mid-reaction in the panels | Prompt fix **failed 2/2**; structural fix untested |
| 16 | Head balloons during strain (takes 1–2, S1-A) | "cheeks puffed" or strain wording | "felt head keeps its exact shape" | **Fixed** in S1-B |
| 17 | Bow-tie fix shows no change (takes 2–3) | Master tie reads nearly level (only a mild tilt); the panel reverted to it | Measure the tilt in the panel; re-roll until visible | **Partly** (S5-B showed it) |
| 18 | Dead freeze in the last 0.4–0.96 s (S1-B, S4, S5) | The model stops when the scripted action ends; `end_image` adds a lock | Script action to the end; trim before the freeze; deliberate freeze-frame in CapCut | Edit fix |
| 19 | Character drifts or leans toward the camera (S1-A) | No "stays in place" | "stays standing upright in place, elbows near his sides" | **Fixed** in S1-B |
| 20 | Morph, teleport or snap at a state change: half-dissolved lid for 1–2 frames, a lid flip, the tie snapping level in one frame (S4, S5) | Model interpolation | Drop or duplicate-replace 1–2 frames, or cut on the action. A shape change (a neck) can't be hidden | Edit fix |
| 21 | Lid underside (white or silver) faces the camera, reads as a coconut shell (takes 2–3) | Prompt can't steer a handheld prop's orientation | Prop design: the inside of the lid is the same dull gold, no white liner; draw the end pose | **Untested** |
| 22 | Insert hand without the character's cuff (take 2) | No cuff wording | "both hands show the teal rolled cuff" | Fixed in take 3 |
| 23 | Lens look while grooming (fixing the bow tie, take 2) | Self-focused action pulls the face to the camera | Restate the eyeline in that beat | Partly |
| 24 | Felt texture drift (velvet corduroy, smooth knit, fuzzy insert hands) | References alone don't lock texture | Texture words; a master hand-crop reference for inserts (untested) | Minor |

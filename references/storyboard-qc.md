# Deep storyboard QC: check every image before the storyboard is shown

This procedure distils how the «نظرية التصفية» storyboard (test-video-05, 2026-11-15/16) was checked and fixed. A blind test confirmed it: an agent applied it to that storyboard's first-round frames without being told the answers, and found all the known errors (22 defects). Follow it every time.

**Why it matters:**
- A storyboard frame becomes the START or END image of a video clip. Every mistake in it is rendered into the video, and a video credit costs 8–10 times more than a frame.
- In test-video-05:
  - My own first pass found 8 bad frames out of 14.
  - After I fixed them, an independent 3-reviewer check still found 5 major issues I'd missed.
  - After those were fixed too, the camera-check tool still found unplanned camera moves in 4 of 8 clips. My eye and the reviewers had both missed them.

**Never show the user a storyboard that hasn't passed all four stages.**

## Contents
1. Before generating: the state ledger
2. How to generate: the reference chain and dependency rounds
3. Stage A: per-frame check
4. Stage B: within-clip START↔END check
5. Stage C: cross-cut END(N)→START(N+1) check
6. Stage D: independent review, fix loop, and gate
7. Failures caught in test-video-05 (what to look for first)
8. Tools

---

## 1. Before generating: the state ledger

Write a **state ledger** in `storyboard/ledger.md` before any frame exists (worked example: `campaign-puppet/production/test-video-05/storyboard/ledger.md`). It has one row per frame, and one column per thing that must stay true.

| Frame | Camera / framing | Nora | Professor | Colander | Pot / lid | Sink | Bow tie |
|---|---|---|---|---|---|---|---|
| S1a | WIDE 3/4 high | left, mitts, holds the pot | right, entering | **in the sink** | Nora; lid on | colander only | crooked |
| S1b | = S1a | left, mitts, holds the pot | right, hand leaving the colander | **counter, left of the faucet** | Nora; lid on | **empty** | crooked |
| … | | | | | | | |

**Rules:**
- **Every prop has exactly one location per frame:** a named hand, or a named surface spot ("counter, left of the faucet"). Write the spot exactly, because the model will move it otherwise.
- **Lock prop types and shapes in words,** in the header of every prompt: for example "SMALL short-cut macaroni (ditalini-size)". Otherwise the model changes pasta size between frames.
- **Gag start-states that differ from the master** must be written in every frame where they apply (crooked bow tie: one wing much lower, about 30°). The image model drifts back to the master.
- **Characters' sides and facing** are written per frame (A LEFT facing right, B RIGHT facing left, never swapped).

The ledger is what every check below compares against.

## 2. How to generate: the reference chain and dependency rounds

- **Image numbering:** Images 1–2 are the character masters, in a fixed order. Image 3 onward are frame references.
- **Reference each frame to the frame it must match. Don't reference everything to frame 1.**

  | Frame | Reference it to |
  |---|---|
  | END of a clip | its own START frame |
  | First frame of a cut-in | the frame just before the cut |
  | Reaction close-up END | its START |
  | A frame whose prop state comes from elsewhere | the frame that shows that state, as an extra reference (for example the insert that shows the pasta, for the wide that shows the sink later) |

  Referencing everything to the establishing frame copied its props back into later frames: the colander reappeared in the sink after the Professor had moved it.
- **Make END frames as an EDIT of the START frame. This is the strongest camera lock found so far.**
  - Pass the START frame as **Image 1**. Make it the only reference when the characters are already in it; add the masters after it only if a character is missing from START.
  - Write: "Image 1 is the START of this same shot. **EDIT Image 1, do not re-compose it**: keep its camera, crop, set, light and both puppets' size, position and costumes pixel-identical. **Change only this:** …"
  - In test-video-05 the usual approach (masters as Images 1–2, START as Image 3, plus a FRAMING LOCK sentence) still drifted 6–14% in 3 tries for clips 1 and 4. The EDIT phrasing with START as Image 1 gave **0.0% zoom and 0 px pan** on the first try, for clips 1, 2 and 4.
  - Keep the header short in edit mode (puppet look, no text). Don't restate the full identity of characters who are already in Image 1, because that invites a redraw.
- **Other frames** (new shots, cut-ins, new angles) use the normal form: masters first, then the frame it must match. Say what to keep ("Keep EXACTLY the camera position, lens, height, framing and pixel positions of … from Image 3") and what changes ("only the characters' actions change").
- **Generate in dependency rounds.** A frame can only reference frames that already exist. `scripts/storyboard_rounds.py` computes the rounds from the refs, uploads outputs for the frames downstream, and can resume after a crash. A re-run recovers recorded jobs and never pays for a recorded frame again unless you pass `--resubmit K` or `--resubmit-failed`.
- **Shared boundary frames.** For a continuous take, START(N+1) can be the same image as END(N): a seamless continuation. Use this to split a long or complex action, such as the colander going onto a head, at a middle keyframe instead of asking the video model to invent it.

## 3. Stage A: per-frame check

Open **every frame at full size** (Read the PNG), and compare it against the ledger row and the masters. Zoom with ffmpeg crops for hands, small props, eyes and the bow tie.

| Check | What exactly to look for |
|---|---|
| **The frame shows the right moment** | It isn't a copy of a neighbouring frame. In round 1, S5b came out as a replay of the opening shot instead of Nora's close-up. |
| **Identity** against the masters | Hair, face, costume, texture. The signature item is on the right character only. No puppeteers or human parts. |
| **Sides and facing** | A left facing right, B right facing left, in every frame including the end poses. |
| **Prop custody** | Every prop is in its ledger location, with no duplicates. Count the props: in round 1, a second pot appeared in the sink. |
| **Prop type and shape** | The same pasta size, the same pot, the same lid knob colour, the same colander. |
| **Gag state** | The crooked tie is visibly crooked, the mitts are on the right hands, the hands are bare where they should be. |
| **Hands** | The digit count in `visual_invariants.hands` (**[Example]** 3 felt fingers plus a thumb), gripping the handle (not floating beside it), never palm to palm. |
| **Eyes** | Looking where the beat needs: at the jar, the colander, the other character. Nobody looks into the lens. Measure pupil position when a glance is the beat. |
| **Composition** | Thirds, look room, a margin beyond the outer shoulders (measure it), foreground in the bottom fifth, nobody cut at the eye or nose, the payoff clear of platform UI. |
| **Set consistency** | One sink only, the faucet in its place, the same wall, shelf and window, the same warm grade. |

Record every failure with its frame, the ledger column and the fix.

## 4. Stage B: within-clip START↔END check

The video model interpolates from START to END. **Anything that differs and isn't the scripted action becomes an unwanted motion.**

Run `scripts/frame_check.py pair START.png END.png --out review/clip<N>` for every clip (or `storyboard_boards.py plan.json --check` for all of them), then look at its outputs:
- `pair.jpg`: side by side.
- `blend.jpg`: a 50/50 blend. Fixed set elements (sink edges, faucet, shelf, window) must appear **single, not doubled**.
- `diff.jpg`: the difference. Only the acting areas should light up.
- The printed measurements: a whole-frame zoom and pan, the zoom in two set-only bands (top 30% wall and shelf, bottom 20% counter), and a tile-agreement fit.
- **Verdicts:**
  - SAME CAMERA.
  - SLIGHT DRIFT: 2% or more zoom, or more than 1.5% pan. It is acceptable for a short clip with no planned move.
  - CAMERA MOVED: whole-frame zoom of 4% or more, both bands agreeing on 3% or more, or more than 3.5% pan.
- **Notes:**
  - "zoom DIRECTION uncertain": the bands disagree, so decide push-in or pull-back by eye. If the props are larger in END, it's a push-in.
  - "weak match": judge the clip by eye.

**Calibration** (test-video-05, 16 known pairs, truth checked by eye on the blends):

| Truth | Pairs | Tool verdict |
|---|---|---|
| Camera moved | S1a→S1b v1 and v3, S2a→S2b v3, S3a→S3b v3 (a pull-back; the bands read −8%/−4% while the whole frame read +18%, so the direction note fired), S4a→S4b v6, S5a→S5b v2, S6a→S6b v1, S7a→S7b v3 | CAMERA MOVED, 8 of 8 |
| Planned push-in | S3a→S3b v4 (+13%) | CAMERA MOVED, accepted through `planned_move` (push-in up to 15%) |
| Same camera | S1a→S1b v8, S1b→S2b v8, S4a→S4b v7 (all three EDIT mode), S5a→S5b v3 | SAME CAMERA, 4 of 4 |
| Same camera | S6a→S6m | SLIGHT DRIFT (cautious) |
| Slight drift | S6m→S6b, S7a→S7b v6 | SLIGHT DRIFT, 2 of 2 |

The magnitudes are approximate. Close-ups with big pose changes give weaker matches, so always look at `blend.jpg` too.

**Check:**
- **Same camera and framing,** unless a move is planned (write it into the plan as `planned_move`, e.g. a push-in of at most 15% as measured by the tool, in the planned direction). Test-video-05 clip 3 came out as a pull-back when a push-in was planned.
- **Only the scripted action changes.** Prop positions that nobody touches are pixel-stable: the colander must not slide, the pasta mound must not thin out, the lid must not move.
- **Background content is identical.** No new sink, faucet or colander appearing in a locked close-up (test-video-05 S5b).
- **The amount of change fits the clip length.** If START and END are far apart (walk over, flip, place, walk out in 3 s), add a middle keyframe and split the clip.

## 5. Stage C: cross-cut END(N)→START(N+1) check

Build the transitions sheet (`scripts/storyboard_boards.py`) and check every pair.

| Check | Rule |
|---|---|
| **Cut type** | Name it and judge it: continuation (same frame), cut-in, reaction cut, action cut, insert, back to wide. Two near-identical framings with changed poses make a **jump cut**. Either make the second a real cut-in (faces about 1.7× larger) or start it on the exact END frame. |
| **State carries over** | Hands and who holds what, prop locations, lid on or off, the tie's state, mitts, eyelines. In test-video-05, S6b ended with both hands on the pot, so S7a had to start that way too, not with a hand already scratching his head. |
| **Geography** | The sink, faucet and window keep the same relative position from one setup to the next. A close-up can't put a sink behind a character when the wides have it in front. |
| **Grade** | Colour temperature matches across the cut. A cool steel insert between warm wides jars. |
| **Action overlap** | An action cut must overlap: the tilt starts in shot N and continues in N+1. It must not jump from a level pot to half the pasta already in the sink. |

## 6. Stage D: independent review, fix loop, and gate

1. **The independent check.** Use reviewers who did not write the prompts: split the clips into 2–3 groups, and give one group also identity across all frames. Run them as a workflow if the user has opted in; otherwise do a fresh, careful pass yourself, with the ledger and the tools.
   - Give them the STORY, the ledger, the panel prompts, the frame paths and the masters.
   - Ask for strict, measured findings: pixel positions, blends, pupil positions. Severity is blocker, major or minor, each with a fix.
2. **Fix in dependency rounds.**
   - Re-roll every blocker and major, plus cheap minors.
   - Change only the prompt lines tied to the failure, and point the references at the frame each one must match.
3. **Re-check every re-rolled frame and its neighbours** (stages A–C). A fix can break a neighbouring transition: the S2b fix once moved the colander to the other side of the faucet.
4. **Run `storyboard_boards.py plan.json --check` last.** It must print "UNPLANNED CAMERA MOVES in clips: none".
   - In test-video-05 the storyboard had passed my review and the 3-reviewer check, yet this tool still found drift in 4 of 8 clips. Three of those clips (1, 2 and 4) were fixed in EDIT mode, and clip 7 was re-rolled with a FRAMING LOCK.
5. **Loop until there's no blocker or major.** Typical cost is 2–4 rounds. In test-video-05 the storyboard took 45 frames to get 15 good ones, about 67 credits in total.
6. **Gate.** Only then build the boards and show the user:
   - one board per clip (START, KEY POSE if any, END),
   - the transitions sheet,
   - the video price.

   Wait for approval.

## 7. Failures caught in test-video-05 (look for these first)

| Failure | Where | Fix that worked |
|---|---|---|
| A prop reappears in its old place | Colander back in the sink in S2a–S3b | Reference the frame after the move (S1b), not S1a. Write "nothing inside the sink; the colander is NOT in the sink". |
| The wrong moment rendered | S5b replayed the opening shot | Reference the shot's own START. Write "reproduce Image 3 exactly; the only change is …". |
| Wrong contents | A second pot in the sink (S6a) | "ONLY a mound of macaroni with the lid on top; NO second pot". |
| Camera changes within a clip | S1a vs S1b zoomed out; S3a→S3b pulled back; S6a→S6b dropped about 120 px; S4b drifted 14%. These were still there after a "fixed" round: my eye missed them and the tool caught them. | Generate the END in EDIT mode (START as Image 1, "EDIT Image 1, do not re-compose it … change only …") and verify with `frame_check.py pair`. |
| Prop type changes across frames | Small pasta in the pot, large elbows in the sink | Lock the type in the header; pass the frame showing it as a reference. |
| A prop slides in an untouched shot | The colander changed sides of the faucet in clip 2 | Name the exact spot ("left of the faucet, partly behind its base"). |
| The gag state is invisible | The bow tie was never clearly crooked | "One wing hangs much lower than the other, about 30°" in every frame; verify by zooming. |
| Too much action between two keyframes | The colander onto his head and the exit in one 3 s clip | A middle keyframe (S6m) and a split clip (6A/6B) with a shared boundary frame. |
| The action doesn't overlap the cut | S3b level pot → S4a half poured | S3b shows the tilt and the lid starting to slide; S4a starts with the first pieces falling. |
| An awkward crop | Nora's face cut at the eye by the frame edge | Back turned, or fully in or fully out of frame. |
| Geography cheated in a close-up | A sink and faucet behind Nora in her close-up | "Same background as Image 3, nothing new in frame". |
| A cool grade in an insert | S4a/S4b cooler than the wides | "warm golden kitchen light, same grade as the wide shots". |

## 8. Tools

| Script | Use |
|---|---|
| `scripts/frame_check.py pair A B --out DIR` | Zoom and pan (whole frame plus two set bands), tile agreement, blend, diff, side by side. Verdicts: SAME CAMERA, SLIGHT DRIFT or CAMERA MOVED, plus direction and weak-match notes. |
| `scripts/frame_check.py strip F1 F2 … --out file.jpg` | One strip of frames in story order, for a quick visual pass. |
| `scripts/storyboard_rounds.py spec.json` | Dependency rounds, upload, generate, download, resume. `--dry-run` shows the rounds and cost first; `--only K1,K2 --tag v2` re-rolls specific frames; `--resubmit K` / `--resubmit-failed` pay again for a frame whose job is already recorded. |
| `scripts/storyboard_boards.py plan.json` | Per-clip boards plus the transitions sheet. Resolves frames through `selected.json` and copies them to `final/`. `--check` runs `frame_check pair` on every clip; it flags unplanned moves, wrong-direction or oversized planned moves, failed checks and weak matches, and exits 1 if anything is flagged. |
| `scripts/storyboard_sheet.py` | Renders one board, Arabic-safe; used by `storyboard_boards.py`. |

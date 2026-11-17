# Picture storyboard (approval gate)

**Why it matters:**
- A storyboard frame costs 1.5 credits; a wrong video shot costs 12–15 or more.
- The panels become the `start_image` and `end_image` of each clip, so the approved picture is literally what the video starts from.
- In take 3, the set, framing, lighting and identity carried over almost exactly. So did the panels' mistakes: tight edges, a straight bow tie, a lid-on jar with a hidden neck.

## Steps (the full procedure, with its checks, is in `storyboard-qc.md`; follow it)

Run from the repo root with `SK=.claude/skills/ai-puppet-video/scripts`. Calls to the Test Lab need the sandbox off.

1. **Ledger.** Write `storyboard/ledger.md`: one row per frame; the camera, each character, and every prop's exact spot and state. A worked example is `campaign-puppet/production/test-video-05/storyboard/ledger.md`.
2. **Spec.** Write `storyboard/spec.json` for `storyboard_rounds.py`. The docstring documents the format.
   - New setups and cut-ins: masters first, then the frame they must match.
   - END frames: `"mode": "edit"` with their START as the only ref (EDIT template in `prompting.md`).
   - Middle keyframes for long actions; shared boundary frames for continuous takes.
3. **Price and ask.**
   ```bash
   python3 $SK/storyboard_rounds.py <spec> --dry-run
   ```
   This prints the rounds and the price. Budget about **3×** the frame count for re-rolls: test-video-05 kept 15 of 45 generated frames, about 67 credits. Show the dry-run price (with the 3× re-roll allowance) and wait for the user's OK before generating (standing rule 6, gate a).
4. **Generate:**
   ```bash
   python3 $SK/storyboard_rounds.py <spec>
   ```
   It uploads the masters, runs the dependency rounds, records job IDs and is resumable. Re-roll specific frames with `--only K1,K2 --tag v2`.
   - **Re-run = recover, never pay twice.** Each job ID goes into `jobs-<tag>.json` right after its submit. A re-run first waits on recorded jobs whose PNG is missing. If any is still pending, failed, or completed without a saved PNG, it stops and submits nothing; re-run later.
   - A recorded frame is paid again only on purpose: `--resubmit-failed` for jobs that ended failed/nsfw/canceled, or `--resubmit K` for a named frame (a stuck job). Price it and get the user's OK first. The old job ID is kept in `jobs-<tag>-superseded.json`.
5. **Select.** Write `storyboard/selected.json` (`{"S1b": "S1b-v8.png", …}`).
6. **Check:** stages A–C of `storyboard-qc.md`, then stage D (independent review). Fix and re-check until there's no blocker or major.
7. **Boards and camera gate.** Write `storyboard/plan.json` (the clips with START, optional KEY POSE and END, plus planned moves), then run:
   ```bash
   python3 $SK/storyboard_boards.py <plan> --check
   ```
   It must print `CAMERA CHECK: all clips pass`. It writes `boards/CLIP-*.png` and `boards/TRANSITIONS.png`, and copies the selected frames to `final/`.
8. **Send** every board (SendUserFile, display "render") with the `get_cost` total for the planned clips. **Stop until the user approves.**

## Per-panel review checklist

- **Screen sides** are correct in every panel, including end poses. Round 1 swapped them in the last panel.
- **Prop custody** matches the shot list. Round 1 put the jar in Sami's hand in his offer shot.
- **Prop shape in every state.** If a lid-on jar hides its neck, the open jar will grow one in the video. Draw a straight jar with a flush lid, or show the threaded neck under a lid of the same width. This fix is a hypothesis; it hasn't been tested yet.
- **Gag start-states** are actually visible: measure them, don't trust the prompt. Flare drew the "tilted 30°" bow tie level, because states that differ from the master revert toward the master.
- **Margins:** frame about 10% looser than the final shot, and measure in pixels. No character, hair or shoulder may touch an edge, because CapCut can punch in but never widen. The approved S1 and S5 panels were too tight, and every clip inherited it.
- **Hands:** the digit count in `visual_invariants.hands` (**[Example]** 3 felt fingers plus a thumb), never palm to palm, nothing human.
- **Mouths:** closed in panels where a line starts the shot. An open-mouth start loses the first flap.
- **Identity** against the masters, including texture (corduroy ribs, knit). The signature item is on the right character only.
- **Composition:** thirds, look room, eyes on the upper third, foreground in the bottom fifth, nobody looking into the lens, the payoff kept out of the bottom 15–20% (platform UI).
- **Set consistency** with the neighbouring frames of the same setup.

## Sheet layout (what the user sees)

The sheet is a header line followed by one card per panel.

**Header line:** title · format · model · resolution · "one clip per shot" · the 180° statement · "audio = SFX + foley only, NO voices".

**Each card has:**
- the shot number and final-cut time range,
- the frame,
- **Camera:** shot size, angle, framing,
- **Action:** beats with sub-timings and custody,
- **Line box (Arabic, right-to-left):** `<speaker> · شفايف فقط` + «line», or «بدون كلام» / «صمت — وقفة»,
- **SFX:** the list.

**Footer:** model, settings, references.

Pillow can't shape Arabic here (no raqm), which is why the script renders through headless Chrome.

## Costs (measured)

| Item | Credits |
|---|---|
| flare high 1k | 1.5 |
| flare medium 1k | 0.5 |
| flare medium 2k | 1 |
| flare high 2k | 2.75 |
| Take-3 storyboard total | 24 |

How the take-3 total broke down:
- Round 1: 6 panels × 3 = 18, of which 9 were wasted by `batch_size: 2`.
- Round 2: 4 re-rolled panels × 1.5 = 6.

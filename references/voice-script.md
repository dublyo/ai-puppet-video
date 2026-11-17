# Voice script, recording and voice pass (phases 1–2 decision, phase 5 measure, phase 9 place)

Part of the general `ai-puppet-video` skill: it works for **any** felt-puppet cast, setting and language. Facts from the first project (`campaign-puppet`: the Professor, Nora, Sami, Adam; Egyptian Arabic) appear only as **[Example]** lines and are never rules for a new cast. A character-specific skill for one cast is a separate thing; this file stays general. Evidence paths are relative to `/Users/dribrahimm/1-AI-Influncer/campaign-puppet/production/` unless absolute or noted otherwise: bare `test-video-0N/…` paths are under `production/`; `cast.json`, `STORY-AND-CHARACTERS.md` and `<char>/character.json` are under `campaign-puppet/puppet-channel-concepts/`. Bare `.md` names such as `prompting.md` or `qc-checklist.md` are this skill's `references/` files.

The decision (silent vs dialogue) is made at the story stage. Craft rules from real puppetry (`channel-strategy.md` §6): the jaw opens on vowels, and each character voice sits clearly above or apart from the performer's own. Lines are drafted with the shot list, refitted to the *measured* mouth windows after QC, recorded by the creator, then placed by Claude in CapCut.

## 0. Pipeline position and the standing audio rule

```
story beat sheet -> [A. decide: silent or dialogue] -> shot list (line + planned mouth window per shot)
 -> [B. draft VOICE-SCRIPT.md, planned windows] -> storyboard / previs -> generation (NO lines in prompts)
 -> QC: jaw_windows.py -> [C. VOICE-SCRIPT.md, measured windows, refit lines] -> assemble.py (SFX-only cut + voice table)
 -> [D. creator records + voice-changes] -> [E. Claude reviews takes] -> [F. place in CapCut, verify sync] -> report
```

- **Rule:** generated video carries foley and SFX only. Mouths move silently.
  - The creator records the lines and runs them through a voice changer.
  - Claude reviews the takes and assembles them.
  - Why ([Example]): take 1 voiced all 4 Egyptian lines in order (`test-video-01/TEST-REPORT.md`), but the user then judged Seedance's native Arabic voices "very bad" (memory `video-direction-and-voice-workflow.md`).
- **Superseded:** test-video-02 used the native audio as a "guide track" for mouth timing (`test-video-02/SHOT-LIST.md`). Since take 3, guide audio is not used. The measured jaw windows replace it.

## A. Does the film need lines at all?

**Purpose:** decide before the shot list. Lip timing is the biggest unsolved quality problem.
- Prompted mouth windows missed badly in 2 of 4 speaking clips (`references/video-generation.md`, "Known model behaviours").
- `lip_sync_validated: false` in `cast.json`.

| Choose **silent comedy** when | Choose **dialogue** when |
|---|---|
| The gag reads from action: a visible cause, then the effect, then a reaction close-up | The joke is verbal: a line pays off something just said |
| You want it to work in any language with no lip risk | The series identity lives in catchphrases |
| **[Example]** «نظرية التصفية» (test-video-05). The reference video works "with no words at all", and "no words means no lip problem" | **[Example]** «البطيخة». «حمرا… ومسكّرة» is answered by «طلعت قرعة» (`test-video-04/STORY.md`) |

- **Hybrid (recommended default):** a silent film with one optional voiced button at the end, on a reaction single.
  - **[Example]** optional «ده كان جزء من التجربة» in shot 7 (`test-video-05/STORY.md`, "جملة اختيارية").
- **Pitfall: don't gut the story to dodge the model** (memory `story-logic-before-model-limits.md`).
  - The user rejected the one-word line «بسيط؟» as "weak and unclear".
  - A line must be natural idiom and land as a joke.
  - Solve window problems with production technique (a dedicated single, re-rolls, lip-sync tests), not by deleting meaning.
- If the film is silent, `edit.timeline.md` has an empty voice table ([Example] `test-video-05/edit-rough.timeline.md`). Skip steps C–F.

## B. Writing lines that fit puppet mouths

**Inputs:** the beat sheet, the cast file's catchphrases and dialect fields, and the shot list.

**Rules**

1. **One speaker per shot.** Put each line in its own single when possible.
   - The listener's jaw must stay shut. The listener also freezes in two-shots: prompt fixes failed 2 of 2 times (`qc-checklist.md` #15).
   - So give reactions their own single.
2. **Short, complete, punchy.** Aim for 2–5 words, one idea per line.
   - **[Example]** «طلعت قرعة» is two words and is "suitable for a short mouth opening" (`test-video-04/STORY.md` §3).
3. **Budget syllables against the window** ([Example] Egyptian Arabic, calibrated on this creator's reads; recalibrate for each language and performer by timing 3–4 of their comfortable and fast reads):
   - comfortable rate **C** ([Example] ≤ 4 syllables/s),
   - hard ceiling **M** ([Example] 5 syllables/s),
   - above M: rewrite.
   - The skill's range is "3–5 syllables per second of window" ([Example] Egyptian Arabic).
4. **Plan windows with slack.** Rendered windows came out shorter or later than planned (`video-generation.md`):

   | Planned | Rendered |
   |---|---|
   | 1.5 s | 0.54 s |
   | 3.0 s | 2.6 s |
   | 2.0 s | 0.8 s, about 1.3 s late |
   | 2.5 s | 1.35 s, about 1.1 s late |

   Rendered/planned ratios ranged 0.36–0.87, so no fixed ratio is safe. Draft the shortest version that still lands the joke, keep a one- or two-word fallback, and fit the final line only to the measured window (phase 5) at the ceiling rate M.
5. **Start the shot with the mouth closed.** If the start panel shows an open mouth, the first flap is lost (`video-generation.md`, "Start and end images").
   - Cut in 0.15–0.3 s before the first opening (`assembly.md` §3).
6. **Leave a button.** The punchline should end by about T−1 s, followed by a hold; otherwise use a CapCut freeze-frame.
   - Take 2 ended the line 0.1 s before the clip ended (`test-video-02/TEST-REPORT.md`).
7. **Dialect and idiom.** Write in the series' spoken dialect, not formal language.
   - **[Example]** Egyptian forms such as هاته، أجرّب، الإيد. Prefer a known idiom that answers the previous line.
   - The cast file's `test_language` is a script choice, not an approved voice casting (`cast.json` `series.test_language`).
8. **Catchphrases.** Use one only when the situation earns it, and change its cause or result each time it comes back.
   - Only lines marked `approved` in the cast file count as catchphrases.
   - Never invent a catchphrase or voice for a character whose `catchphrases.status` is `not_yet_approved`. Propose it instead.
   - Evidence: `<char>/character.json` `catchphrases.frequency`; `STORY-AND-CHARACTERS.md` §10 and §18.6.
9. **Localization.** Translate a catchphrase for memorability and timing, not word for word. Re-check every language version's syllables against the windows (`STORY-AND-CHARACTERS.md` §15).
10. **Never put a line, quote or count into a video prompt.**
    - Seedance spoke "eight syllables" and "fourteen syllables". Those match the true counts of the two lines (`test-video-03/TEST-REPORT.md`).
    - With them removed, all three re-rolls were clean.
    - The prompt carries only: `0.0-1.5s: <action>; during these 1.5 seconds his felt jaw keeps opening and closing quickly and continuously, a steady silent puppet-mouth rhythm, and it shuts at 1.5s.` (`prompting.md` §2).
    - That wording prevents voice leaks but does **not** control timing.

**Worked fit check** (**[Example]** take 3, Egyptian Arabic, C = 4 / M = 5; final-cut windows from `test-video-03/TEST-REPORT.md`)

| Line | Syllables | Window | Rate | Verdict |
|---|---|---|---|---|
| «الموضوع بسيط جدًا» | 7 | 0.54 s | 13/s | Impossible: re-roll or one word |
| «طب هاته أجرّب أنا؟» | 8 | 1.62 s | 4.9/s | Usable, tight |
| «لأ… اكتب يا سامي: نسخّن الإيد الأول» | 14 | 2.63 s | 5.3/s | Over ceiling (13 max at 5/s): trim one word or accept a fast read, then re-check |
| «ده كان جزء من التجربة» | 8 | 1.34 s | 6.0/s | Too fast |

## C. VOICE-SCRIPT.md (one per production folder; required unless the film is silent)

It has two passes:
- **Planned:** written with the shot list. Windows come from the plan.
- **Measured:** updated after QC from `jaw_windows.py` and `edit.timeline.md`. Re-measure after any re-roll or finalise, because a finalised or native-HD render is a new performance. An upscale keeps the performance (`video-generation.md`, "Finalising").

```markdown
# VOICE-SCRIPT: <slug>
Mode: silent | dialogue | silent + button     Language/dialect: <lang>     Cut: <slug>-final-sfx-only.mp4
Rate budget (this language/performer): comfortable <C> syl/s, ceiling <M> syl/s ([Example] Egyptian Arabic: 4 / 5). Windows below are MEASURED in final-cut time
(source: edit.timeline.md, <date>). Status: PLANNED -> MEASURED -> RECORDED -> PLACED -> VERIFIED

| # | Shot | Cut window (s) | Len (s) | Char | Line (original) | Transliteration | Translation | Syl | Max syl (len×C / ×M) | Fit | Delivery note | Take file | Status |
|---|------|----------------|---------|------|-----------------|-----------------|-------------|-----|----------------------|-----|---------------|-----------|--------|
| 1 | S2 | 5.13–6.75 | 1.62 | <B> | <line> | <translit> | <gloss> | 8 | 6 / 8 | TIGHT | quick, curious, rising question | voice/S2-<b>-t1.wav | MEASURED |

## Silent beats (no voice; SFX only)
| Shot | Window | What the audience must read without sound |

## Notes for the creator
- First syllable lands on the window start; finish ≤ window end + 0.2 s.
- Lines marked TOO LONG: <shorter alternative> or faster read.
```

- **Fit values:**
  - OK: within len×C,
  - TIGHT: within len×M,
  - TOO LONG: rewrite, re-roll the shot, or test lip-sync.
- The `line` text also goes into `edit.json` `shots[].line`. `assemble.py` prints it in the voice-window table.

## D. Recording guidance for the creator

**Source:** `assembly.md` §4. Items marked "proposed" are untested here.

- **Picture to record against:** the SFX-only cut and the voice table, so he reads to the mouths.
- **Takes:**
  - Proposed: 2–3 takes per line, at a natural pace and one faster.
  - Read the line as written. If it doesn't fit, tell Claude rather than improvising longer.
- **Levels:** after processing, peaks below −1 dBFS with no clipping. A quiet room, no reverb, no music.
  - Proposed: raw peaks around −6 dBFS, the same mic distance, and about 1 s of room tone before the line.
- **Voice changer:**
  - Run it after recording.
  - Use one fixed preset per character for the whole series.
  - Record that preset in the cast file's `voice_id` / `voice_sample` fields. They are empty today, and `voice_cast_selected: false` in `cast.json`.
  - Check that the changer doesn't stretch the length.
- **Files:** one file per line, in `voice/`.
  - Existing convention: `S2-sami.wav`. Proposed: `voice/<shot>-<char>-t<N>.wav`, keeping the raw takes in `voice/raw/`.
  - Proposed format: WAV, mono, 48 kHz (`assemble.py` resamples to 48000).

## E. Review of the takes (Claude)

**Inputs:** `voice/*.wav`, `edit.timeline.md` and VOICE-SCRIPT.md.

1. Check loudness and peaks: `ffmpeg -i take.wav -af volumedetect -f null -`. Peaks should be below −1 dBFS.
2. Check noise and clicks by ear or with a spectrogram.
3. Compare length to the window. The speech length excludes leading and trailing silence. Flag any line longer than its window plus about 0.2 s.
4. Fix options in order:
   1. a faster read,
   2. a shorter line with the same meaning,
   3. pick or re-roll a take with a longer window,
   4. lip-sync experiments (below).
   - **Never slow the picture down:** the hands crawl (`assembly.md` §3).
   - **Never trim through a bad mid-clip jaw window.**
5. Optional: run Whisper on the take to confirm the words. `whisper-cli -ng` works here; Metal is blocked.

## F. Placement and verification (existing skill steps)

1. Place each take so its **first syllable lands on the window start**. Use CapCut through the `capcut-mcp-video` skill (mcp-cut), keeping the SFX track under the voices.
2. If mcp-cut is down, make a reference mix with ffmpeg and hand over the CapCut-ready parts:

   ```
   ffmpeg -i cut.mp4 -i S2.wav -filter_complex "[1:a]adelay=5130|5130[v];[0:a][v]amix=inputs=2:normalize=0[a]" -map 0:v -map "[a]" -c:v copy out.mp4
   ```

   (`assembly.md` §4)
3. Re-check sync frame by frame at each line's start and end.
4. Deliver `<slug>-final-voiced.mp4` and state what was not verified.
5. Write the actual windows and remaining sync errors into `TEST-REPORT.md`, and set VOICE-SCRIPT status to VERIFIED.

## QC tools that feed the voice table (from the script docstrings)

**`jaw_windows.py clip --box X,Y,W,H`**
- Counts mouth-interior pixels (red lining or dark cavity) per frame and auto-thresholds. It prints `edit.json "jaw"` ranges in clip time.
- Validated within about 0.05 s of manual reviews (S2 0.50–2.04 against 0.46–2.08).
- **For a new cast:** the colour test assumes orange or tan fleece with a red mouth lining. Red or very dark fleece or clothing near the mouth breaks it.
  - Pick the box on an open-mouth frame.
  - Keep the other puppet and red props (a bow tie) out of the box.
  - If the whole clip reads "open", the box is wrong.
  - Calibrate on one clip against a contact sheet before trusting it.
  - The colour test has no flag. If calibration fails, copy `jaw_windows.py` to `<project>/scripts/` and adapt the `mouth = …` line for your fleece and mouth-lining colours; never edit the skill copy.

**`voice_scan.py clip --mute out.mp4 --jaw a-b,c-d`**
- Detects sustained harmonic audio at 85–300 Hz.
- **A CLEAN result is not proof of silence.** It missed a quiet 0.2 s leak and a 0.5–0.95 s onset.
- Default: mute the scan ranges together with every jaw window. The creator's voice replaces them anyway.
- Leaks happen even with closed jaws: the Blender pilot showed voice-like audio at 3.55–4.25 s (`test-video-06-blender-pilot/TEST-REPORT.md`).

**`assemble.py edit.json`**
- Snaps in and out points to whole frames and clamps `out` to the clip length.
- Normalises size and fps, and adds silence to clips without audio.
- Writes `edit.timeline.md` with "Line | Mouth window in final cut".
- Afterwards, re-scan the cut with `voice_scan.py`.

## Open: dialogue on the Blender route (untested)

**Status:** test-video-06 was dialogue-free, with jaws closed (`references/blender-previs.md` §1). The planned method:
- animate the stand-in mouth open and shut inside each line's window,
- change the prompt from "jaws closed" to "<character>'s jaw opens and closes only while his stand-in mouth moves",
- test in the 10 s pilot before the full film.

**What to test in the pilot:**
1. **Timing offset:** `jaw_windows.py` windows on the AI render against the mockup's keyed windows. Report the offset in frames, like the cut offsets from `side_by_side.py`.
2. **Listener stays shut:** run a jaw box on the listener as well.
3. **Leaks:** whether moving stand-in mouths make Seedance voice audio, checked with `voice_scan.py` plus Whisper.
4. **Shape copying:** whether the stand-in mouth's shape or colour is copied literally into the result. Seedance copies stand-in shapes (`blender-previs.md` §5).
5. **Calibration:** whether `jaw_windows.py` still calibrates on the rendered mouth.

**Pass criteria (proposed):** windows within ±2 frames of the mockup, no listener flaps, no voiced audio. If the timing is reliable, VOICE-SCRIPT windows can be fixed before generation (voice-first: record, then key the mouths to the recording).

**Other untested lip-sync routes** (`references/quality.md`, "Lip-sync options"):
1. `sync_so` re-sync of an approved clip (cheapest first test),
2. Seedance `audio_references` (mute the output afterwards),
3. `intone`, which needs "a readable front face".

## Pitfalls index

| Pitfall | Evidence |
|---|---|
| Quoted lines or counts in a prompt get spoken; the voice ban alone isn't enough (4 of 5 leaked) | `prompting.md` §6; `test-video-03/TEST-REPORT.md` |
| The prompted window is ignored or late | `video-generation.md` table |
| An A/B re-roll can break the jaw window (S1-B opened at 2.0–2.67 s, so take A won) | `test-video-03/TEST-REPORT.md` |
| A vague one-word line written to dodge the model was rejected | memory `story-logic-before-model-limits.md` |
| A frozen listener in a two-shot | `qc-checklist.md` #15 |
| The voice-scan miss rate | `voice_scan.py` docstring |
| A wrong jaw box (red props) | `jaw_windows.py` docstring |

**[Example] Superseded items:**
- The v2 redesign was rejected on 2026-11-15. Superseded files: SKILL.md → Example project notes. This doesn't change any voice field.
- The native-audio guide track of take 2 is superseded.
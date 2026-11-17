# Phase 0c: from a reference video (or a seed) to an approved STORY.md

Part of the general `ai-puppet-video` skill: it works for **any** felt-puppet cast, setting and language. Facts from the first project (`campaign-puppet`: the Professor, Nora, Sami, Adam; Egyptian Arabic) appear only as **[Example]** lines and are never rules for a new cast. A character-specific skill for one cast is a separate thing; this file stays general. Evidence paths are relative to `/Users/dribrahimm/1-AI-Influncer/campaign-puppet/` unless absolute; paths starting with `test-video-0N/` or `reference-<slug>/` are under `production/`.

Use this when the user hands over a reference clip, or when an episode idea is needed. Fit every idea to the channel archetype and the Shorts-first shape (`channel-strategy.md` §1, §5), and never base it on third-party characters (§3). Without a clip, skip Step 1 and start from a bible seed (`series-bible.md` §7), then run Steps 2–7 the same way. The visible-logic gate (Step 5) is never skipped.

This is the method the project used to turn a reference clip into the felt-puppet episode «نظرية التصفية» (the Draining Theory, colander). It is written for any puppet cast. Project facts appear only as **[Example]** notes.

---

## 0. Inputs you need before starting

| Input | Why it's needed | [Example] |
|---|---|---|
| Reference video file | The thing being analysed | `/Users/dribrahimm/1-AI-Influncer/sources-vid/video---fb.mp4` (15.9 s, 9:16, 30 fps) |
| Series bible: premise, each character's flaw/want, relationships, episode template | Adaptations are judged on fit with it | `puppet-channel-concepts/STORY-AND-CHARACTERS.md` §6–§10 |
| Approved catchphrases, spoken and visual, with the use for each | Used only "when the situation earns the line" | `cast.json` → `professor_catchphrases.frequency` |
| Current identity masters, and which design versions are superseded | Story props must fit the real character designs | v1 masters only; superseded files: SKILL.md → Example project notes |
| Known model limits from earlier tests | Go into the risk table, never into story cuts (see §6) | ai-puppet-video SKILL "failures" table |
| Standing user rules: language, voices, spend gates | | No generated voices. The creator records the lines. Egyptian Arabic |

---

## Step 1. Analyse the reference video (`BREAKDOWN.md`)

**Purpose:** find out *why* it works, so the mechanics can be carried over without the content.

**Extract the material (free, local):**
- Specs: duration, resolution and aspect, fps (ffprobe).
- Frames at 8 fps into `frames/` (frame n is at t = (n−1)/8). [Example] 127 frames.
- Contact sheets of 2 s each at 4 fps into `sheets/sheet_<NN>s.jpg`, one horizontal strip of 8 frames per sheet. Read every sheet as an image.
- Mono 16 kHz audio (`audio16k.wav`), run through Whisper. Mark the result as a "rough machine reading": the [Example] "Get out!" may have been part of the music.
- Measure the hard-cut timestamps exactly. [Example] cuts at 11.03, 12.13 and 13.97 s, after one 11 s take.

**Output: `production/reference-<slug>/BREAKDOWN.md` (adaptations.json goes in the same folder), with these sections:**
1. **Specs and audio:** music, dialogue present or not, and any vocal sounds with their timestamps.
2. **Second-by-second table** with columns `Time | Camera | Action`. Bold the key beats: the takeover, the mistake, the reaction cut. Name each camera change ("Hard cut to a close-up of her face in profile").
3. **"Why it's funny":** a numbered list of the comedic mechanics, one per line. The [Example] list is a good generic checklist to test any reference against:
   - Works with no dialogue, so it is universal and works on mute.
   - Contrast of competence: one character is prepared, the other overconfident.
   - A slow, serious build. "The longer the build, the harder the fall."
   - One silly mistake that anyone reads instantly.
   - The reaction is the punchline: a cut to the frozen face.
   - The reaction escalates, for example an exit.
   - A button on the person who caused it: alone and clueless, a second laugh.
   - A relatable trope ("he takes over to help and ruins it").
   - A home-video or handheld feel.
   - Editing rhythm: a slow build, then fast cuts (11 s, then 3 cuts in 5 s).
4. **"Why this format suits <cast>":** map the trope onto the bible's premise and character flaws, and list the production gains. [Example] No dialogue meant no lip-sync, which removed "our biggest open quality problem". It needed one location and two characters.
5. **"Risks for AI generation and how to handle them"** table (`Risk | Handling`): particles and liquids, long takes, state changes, readability of key contrasts (show the mitts and the bare hands in one frame), music.
6. **Originality boundary (required line):** "Don't reuse the reference's music, footage or exact staging. We adapt the comedic structure, not the content."

**QC:**
- Every row in the table is backed by the sheets.
- Cut times are measured, not guessed.
- Every "why funny" point names a mechanic that can be moved to a new story, not a description of the plot.

---

## Step 2. Generate 3 adaptations through different lenses (`adaptations.json`)

**Purpose:** avoid the first-idea trap. Each draft pushes in a different direction, so the best parts can be merged later.

**The three lenses that were used (they generalise well):**

| Lens | Brief | [Example] result |
|---|---|---|
| `faithful` | Keep the reference's structure closely, re-cast it with the series' characters, and improve it | «نظرية التصفية»: he removes the colander himself, then the pasta lands in the sink |
| `<lead>-twist` | Build from the lead's specific flaw and the local culture; keep the structure, change the task | «الشهقة العلمية»: the molokhia "gasp" ritual, and the taqliya poured into the rice |
| `ai-proof` | Choose the beats easiest for the model to render while keeping the structure | «خبير البيض»: the egg goes in the bin, the shells go in the pan |

**Schema for each draft (use it exactly):**
```json
{"lens","title_<lang>","logline_<lang>","why_funny",
 "shots":[{"n","time","camera","action","props_custody","sfx_music","line"}],
 "setup_plant","ai_risks":[...],"differences_from_reference"}
```
- `why_funny`: numbered points, each tied to a visible beat ("at 2.5 s we see HIS hand take the colander").
- `setup_plant`: list every object or state the payoff needs, and the shot where it first appears. "Everything the mistake needs is on screen before it happens, so it reads with no dialogue."
- `differences_from_reference`: "What we kept: its comedic STRUCTURE …" plus a numbered list of "what changes". Changes always include the setting or task, the mistake, how the preparedness is shown, the reaction (fit to the bible), the button, the shot breakdown, and our own royalty-free music and SFX.

---

## Step 3. Score, pick, graft, fix (`adaptations.json → verdict`)

**Output:** `verdict = {scores[], winner, grafted[], final{...same schema...}}`.

**Scoring:**
- Each criterion is scored 0–10. Give each draft a total and a one-paragraph note naming its strengths, its weaknesses and the ideas worth stealing.
- **Pitfall:** the project's adaptation scores use letters a–e that are never defined in the file. **Always write the criteria names into the JSON.**

The criteria the project actually reasoned with, taken from the notes and from `test-video-01/STORY.md`:

| Criterion | What it checks |
|---|---|
| Mute laugh / visual payoff | Does the disaster read on mute? Is it big ("a whole pot in the sink") or small ("a small spot in a pot")? |
| Visible cause → effect | Can the audience *see* why it happened, or must they track geography they might miss? |
| Character/bible fit | [Example] the egg idea was marked down because "too stupid for the Professor … breaks the bible". His flaw is being confidently wrong in theory, not incompetent. |
| Local or cultural specificity | Is the mistake a believable expression of the lead's flaw (a real local practice) rather than random stupidity? [Example] believable overconfidence |
| Freshness | [Example] the egg gag was marked down as "a well-worn internet gag" |
| AI feasibility | Count of in-shot state changes, particles and liquids, small or fiddly props handled by felt hands, and a shot cap (7 was used) |
| Usefulness as a test | Only when the episode doubles as a pipeline test |

**Graft:**
- List each borrowed element as `"From <lens>: <element> — <why it helps>"`.
- [Example] grafts:
  - Closing his eyes and pouring "by feel" gives a *visible reason* nobody catches the lid.
  - The music cuts dead on the impact.
  - A freeze-frame protects the reaction hold, because models shorten holds.
  - The build is a single on the lead, so the listener-freeze problem can't hit.
  - The plant stays visible for the whole film.
  - All hand moves are "slow, careful, precise".
  - One approved set still is the reference for every shot of that set.

**Own fix:**
- Remove *risk that adds no story* without cutting story beats.
- [Example] The lid was already on the pot from frame 1. That deleted a lid-placement state change and took the film from 9 shots to 7. The story beat (his "lid is the strainer" theory) was kept and shown by tapping the knob and raising a finger.

---

## Step 4. Map the chosen story onto the cast's personalities

Each role in the reference becomes a series character. Each reaction or escalation is rewritten so it follows that character's documented temperament.

| Reference role ([Example] roles from the colander reference; list your reference's own) | Generic mapping rule | [Example] |
|---|---|---|
| Overconfident fixer | The lead's core flaw drives the mistake. Give the lead a silent gesture that shows the flaw's logic ([Example] a "theory" gesture for overconfidence) | Taps the lid, raises a wise finger, measures with his thumb, closes his eyes "like a surgeon" |
| Competent partner | Shows the right way, or is visibly prepared, in frame 1 | Quilted mitts, steam, a red colander in the sink |
| Partner's reaction | Rewrite it to fit their bible temperament. Don't copy the reference's emotion | Reference: scream, mitts thrown. Calm Nora: an eye-slide to the colander, then she crowns him with it, pats it and leaves ("wit, not rage") |
| Button | Use the lead's catchphrase, visual and/or spoken, only if earned. Mark the spoken line optional | Straightens the bow tie while wearing the colander; optional «ده كان جزء من التجربة» |
| Plant → payoff loop | The object he dismisses becomes the punishment | The colander becomes a helmet: "a ready-made meme image" |

**Bible check questions (series-bible.md §7 review questions; [Example] project bible STORY-AND-CHARACTERS.md §9):**
- Is the goal clear from one action?
- What does the lead stand to lose ([Example] his reputation)?
- Did his own choice cause the next problem?
- Does the ending come out of the scene?
- Can we end before over-explaining?

Escalation is a chain: "he did X, so Y happened, so he chose Z." Repeating the same reaction louder does not count as escalation.

---

## Step 5. Apply the visible-logic rules (hard gate before showing the user)

Source: memory `story-logic-before-model-limits.md`, plus the rejections below.

1. **Every effect has an on-screen cause:** who does what, with what. Nothing happens "off-screen or by talking". [Example] An upgrade on the reference: the colander is planted, and the audience *watches his own hand remove it*. That turns surprise into **dramatic irony** ("no no no, he's going to do it"), which makes every expert move after it suspense.
2. **Every state change is performed on camera by a character.** If an object changes state, the story must show who changes it. Fix the shot technique, not the story.
3. **The failure has a visible mechanism.** [Example] Both hands are on the handles, nobody holds the lid, the lid slides, the pasta follows, and the lid lands on top of the mound.
4. **Read it as an audience member.** The user "reads the idea as an audience member; a missing on-screen cause or a line that doesn't land is a failed idea, however safe it is to generate."
5. **Lines are natural local idiom, and each pays off something said or shown just before.** [Example] «طلعت قرعة» answering «حمرا… ومسكّرة». Prefer a joke that works silently. Treat any spoken line as optional, recorded by the creator.
6. **Use high-contrast plants:** a bright red colander in a steel sink, contrasting colours, one distinctive mark per tracked prop (a red lid knob), and no text.
7. **Characters' "freeze" has to be part of the joke.** Two-shots only where the listener's stillness is funny; otherwise give the reaction its own single.

---

## Step 6. Why ideas were rejected (learn these)

| Idea | Verdict | Root cause | Evidence |
|---|---|---|---|
| «البطيخة» v1 | Rejected. "هتفتح ازاي؟ بالكلام بس؟" | The watermelon appeared cut open with nobody cutting it. The in-shot cut was removed to avoid a model state change. | memory note; `test-video-04/STORY.md` "what changed" |
| «البطيخة» v1 line «بسيط؟» | Rejected as unclear | A one-word line written to fit a short mouth window | same |
| «البطيخة» v2 | Rejected: "not funny" | Fixed the logic but stayed a talk-driven joke: prediction, cut, deadpan line. The user then supplied a silent-comedy reference instead. **Inference, not recorded by the user:** the lead *predicts* wrongly instead of *causing* a disaster. The payoff depends on dialogue, and the build is short. Its §5 shows the idea was designed around "lessons learned" model limits. | `test-video-04/STORY.md`; memory note |
| Egg (`ai-proof` lens) | Lost on score | Stale internet gag; the lead becomes stupid rather than overconfident (breaks the bible); felt hands with eggs are hard to render | `adaptations.json` verdict |
| Molokhia gasp (twist lens) | Lost on score | Small disaster on mute; the cause is pure left/right geography across two pots | same |
| "Focus" phone episode / EP01 | Low score (28) in test-01 | Weak visual ending (blank paper); phone screens render UI and text | `test-video-01/STORY.md` |

**Notes on EP01:**
- `EP01-PHONE-BREAK.md` is a dialogue-heavy 38 s "useful idea" episode. It points to the **superseded** `DESIGN-V2.md` and uses a phone. Treat it as an example of the *value-episode* format (problem → advice → small success → flaw undoes it), not as an approved template.
- A good rule from it: "keep the first success visible, or the useful idea disappears."

**Meta-lesson:**
- Don't pre-shrink the story to dodge model risk.
- Handle the risk with production technique: start and end frames, two candidates, a fallback split or cut on the sound, a CapCut freeze-frame, a mid-action panel, or for multi-shot films the Blender previs route (Route B), which fixed custody and intruders in test-video-06.

---

## Step 7. Write `STORY.md` for approval (in the user's language)

**Path:** `production/<episode-slug>/STORY.md`.
- [Example] Written in Egyptian Arabic.
- The header gives the status ("an idea for reading and approval; no storyboard, video or credits spent") and links the reference and `BREAKDOWN.md`.

**Sections (from `test-video-05/STORY.md`):**
1. **What I understood from the video:** 5–6 beats with timestamps, "why it's funny" in bullets, and "why it's exactly what we need" mapped to the bible.
2. **Our version:**
   - The story as one paragraph.
   - "What we added to make it funnier than the reference" (the improvements, each with a reason).
   - A shot table: `# | time | shot/camera | action | sound`. State the 180° rule above the table and bold the visible cause and the payoff.
   - Mark any spoken line as optional.
3. **Model risks and handling** table. Every risk gets a fallback that keeps the beat.
4. **Estimated cost table**, "to be confirmed with a free price check before any spend".
5. **After a rejection:** add a "what changed from v<N>" bullet list at the top. Bump the version, never overwrite silently (pattern from `test-video-04/STORY.md`).

**Approval gate:** stop and wait for the user. Next comes SKILL.md phase 1 (beat sheet, silent/dialogue decision), phase 2 (shot list), then Route B (Blender mockup) or Route A (storyboard).

---

## Copyright and originality boundaries

**Keep from the reference:**
- The comedic structure.
- The trope.
- The reference's pacing *shape* ([Example] a slow build of about 9–11 s, then fast cuts).
- Generic mechanics: plant, contrast, reaction cut, button.

**Never copy:**
- Footage, frames used as image references, music, the exact staging or blocking, dialogue, people's likenesses, or brands.

**Change at least these:**
- The setting or task, or a key twist on it.
- The mechanism of the mistake. Make the cause visible and planted.
- The reaction, fit to the character.
- The button.
- Characters: puppets replace actors.
- Music: our own royalty-free track (CapCut library) and our own SFX.

**Process:**
- Store reference material only under `production/reference-<slug>/`, for analysis.
- Document the boundary in `differences_from_reference` for every draft.

---

## Pitfalls seen in practice

- **Undefined score letters.** `adaptations.json` uses a–e with no definitions. Always name the criteria.
- **Plan length grows.** The 7-shot, 18.5 s plan came out as an 8-clip, 27.5 s rough cut (`test-video-05/edit-rough.timeline.md`). Budget the duration with slack, and plan in the story to tighten the build.
- **Characters drift in production.** In the same rough cut, mitts went onto the wrong character (C4) and a character intruded (C7), even though the prompts named who wore the mitts. Prompt wording did not fix it. For any multi-shot story with props changing hands, plan Route B (Blender previs, colour-coded per character, `blender-previs.md`) and list custody per second in the risk table. On Route A, the mitigation is SKILL.md's "Describe only the characters who are in the clip": an absent character named in a prompt header pulled the mitts across.
- **The model shortens reaction holds.** Plan the freeze-frame in the story.
- **The cast's real proportions limit blocking.** [Example] Short puppet legs and a counter-height sink: add a step stool, which is also a small extra joke.
- **Superseded docs still recommend old assets.** Check what is superseded before quoting design files in a story.

---

## Template checklist: from "here is a video" to an approved STORY.md

1. Probe the specs. Extract frames at 8 fps, 2 s sheets at 4 fps, 16 kHz audio and a Whisper pass. Measure the cuts.
2. Read every sheet and write the time/camera/action table.
3. Write "why funny" (mechanics), "why it fits <cast>", AI risks, and the originality line → `BREAKDOWN.md`.
4. Write 3 drafts (faithful / `<lead>`-twist / ai-proof) in the full schema → `adaptations.json.drafts`.
5. Score them on named criteria, write a note per draft, pick a winner, list the grafts, and apply your own risk fixes that keep every beat → `verdict.final`.
6. Map the roles onto the cast: flaw-driven mistake, temperament-true reaction, earned catchphrase button, plant → payoff loop.
7. Run the visible-logic gate: every effect has an on-screen cause, a character performs every state change, the lines are natural idiom paying off a setup, and it works on mute.
8. Write `STORY.md` in the user's language: understanding, our version and improvements, shot table, risks with fallbacks, `get_cost`-pending budget.
9. Present it and wait. On rejection, record the user's exact words and the root cause (in memory as feedback), version the file, and add a "what changed" list.
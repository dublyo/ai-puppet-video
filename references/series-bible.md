# Phase 0b: the series bible (world, drama, cast as a dramatic system, comedic engine)

Part of the general `ai-puppet-video` skill: it works for **any** felt-puppet cast, setting and language. Facts from the first project (`campaign-puppet`: the Professor, Nora, Sami, Adam; Egyptian Arabic) appear only as **[Example]** lines and are never rules for a new cast. A character-specific skill for one cast is a separate thing; this file stays general. Evidence paths are relative to `/Users/dribrahimm/1-AI-Influncer/campaign-puppet/` unless absolute.

Written after the masters exist and before the detail sheets, `character.json` persona fields and any episode idea. Put the chosen channel archetype, audience classification (who the series is for and why, judged by YouTube's made-for-kids factors, not a "13+" line) and Shorts-first episode shape from `channel-strategy.md` into §3. Every later phase pulls from it: idea scoring, beat sheet, prompts, cast-per-shot lists and voice script.

Source evidence is in `/Users/dribrahimm/1-AI-Influncer/campaign-puppet/puppet-channel-concepts/`: `STORY-AND-CHARACTERS.md`, `cast.json`, `MANIFEST-CONTRACT.md`, `<char>/README.md`, `<char>/character.json` and `<char>/WORLD.md`. The four WORLD.md files are byte-identical by md5. The archive analysis is at `puppet-channel-concepts-archive/2026-11-15/original-root/awkward-puppets-shouqi-story-analysis-2026-11-14-ar.md`.

## 0. What the bible is for and where it sits

The bible comes before the story beat sheet (phase 1 of `ai-puppet-video`). It answers three questions: who these puppets are, why they clash, and what an episode always does. Every later prompt pulls from it: idea scoring, the beat sheet, `reusable_prompt`, `negative_constraints` and the cast-per-shot list. The goal is that **any writer or AI can pick it up cold**, "without reading old conversations" (STORY-AND-CHARACTERS.md, line 10).

### Output structure (this layout worked)

```
<series>-concepts/
  STORY-AND-CHARACTERS.md   human bible: premise, origins, cast, relationships, engine, template, sample episode, seeds, rules, handoff summary, open decisions
  cast.json                 CANONICAL machine record: premise, core cast ids, roles, catchphrases, guest policy, null slots for undecided items
  MANIFEST-CONTRACT.md      field definitions shared by every character.json
  <char_id>/
    00-master-full-body.png   identity anchor (wins every conflict)
    01..05 sheets             head turnaround, body, expressions, material details, illustrative scene
    character.json            persona, relationships, catchphrases, visual_invariants, wardrobe_variants, negative_constraints, unresolved, reusable_prompt
    README.md                 "start here" for a collaborator
    WORLD.md                  portable snapshot of shared world context (identical in every folder)
    SHEET-INDEX.md, generation-prompts*.txt   provenance only
```

**Single source of truth.** cast.json is the authority. WORLD.md copies are "portable snapshots" kept in sync with it. Exact catchphrase text is hashed, and every copy carries the hash: SHA-256 of the canonical JSON, keys sorted, separators `,` and `:` (MANIFEST-CONTRACT.md). Each character folder still has to make sense when shared on its own.

**Approval gate.** Show STORY-AND-CHARACTERS.md and cast.json; only items the user explicitly approves become APPROVED, everything else stays PROPOSED or null.

## 1. Label every decision by status

Every statement in the bible gets one of three labels (STORY-AND-CHARACTERS.md lines 12–15):

- **Approved (ثابت معتمد):** something the user chose.
- **Creative explanation (شرح إبداعي):** why an approved choice works. It adds no new facts.
- **Proposed (تطوير مقترح):** plots, episode goals, season arcs, new gags. Listing it does not approve it.

**Undecided means `null`, never invented.** Example from cast.json: `"channel_name": null, "voice_id": null, "dialect_performance_approved": null`. Each character has its own `unresolved` block, for example `personal_name, voice, accent, nationality, exact_age, occupation, final_set_design, episode_duration`.

Keep an **"open decisions"** list at the end of the bible (line 575).

**QC:** for any sentence a downstream AI might treat as canon, check whether it is approved, explanation or proposal. Rule 5 of the handoff (line 543) says an example episode must not turn into backstory.

## 2. Mine references for mechanisms, not characters

- **Purpose:** learn what to borrow from 1–3 reference channels.
- **Method:** read 3–4 episode transcripts per channel. Then extract the structure: recurring trait, pressure from another character, escalation, callback.
- **Output:** a table with three columns: reference, principle studied, how we apply it (§4 table, line 97).
- **Formula found** (archive analysis, "النتيجة"): **a character we know + a persistent flaw + a new situation that presses on the flaw + escalation + a payoff.**
- **Mechanisms that carry over to an original cast:**
  - want vs flaw,
  - a counterpart with its own goal (not a passive listener),
  - expectation, then a twist in the form the joke takes,
  - a fast entry into the problem,
  - a payoff that exposes the character's logic instead of a moral lecture,
  - names that carry a relationship function.
- **Guardrails:**
  - Record that the analysis is creative reading, "not causal proof that the style increases views".
  - Say in writing that no cast member copies a reference character. The bible states there is no attribution mapping any supporting character to a source character (line 127).
  - The English handoff states: "Do not substitute a source creator's character, dialogue, voice or story."

**[Example]** Awkward Puppets gave the physical-puppet-in-a-real-place form and the scene structure. Shouqi El-Domyati gave local-dialect dialogue and repetition that "returns in a different situation or with a new result". A Hotel Ep. 2 clip was used only as a proportions reference.

## 3. Premise, promise and dramatic question

Write these four items, each one sentence long:

1. **Premise:** `<hero or ensemble> who <want> but <flaw-driven behaviour> in <situation type>`. **[Example]** `<hero> who is good at X in theory but, while trying to <want>, his behaviour exposes the contradiction`.
2. **Viewer promise:** the familiar truth the audience will laugh at. **[Example]** "We all sometimes know the solution and find an excuse not to do it."
3. **Emotional value:** why the audience roots for the lead despite the flaw. **[Example]** empathy for someone protecting their self-image. Laugh at the defences, but keep the hero smart, well-meaning and able to learn, "so he stays a hero we want to return to" (line 35).
4. **Recurring dramatic question:** **[Example]** "Will he solve the problem, or choose to look knowledgeable even if he complicates it?"

Also define these:

- **Format:** for example, an everyday-life puppet sitcom with recurring characters. Topics (habits, money, work, phone, procrastination) are *situations*; the hero's flaw and the relationships are the connective tissue (line 25).
- **Audience:** who the puppets portray and who watches; this decides the allowed topics. Unknown = null. **[Example]** puppets "portray adults", which allows adult topics (work, marriage, money).

Record **how the idea evolved** as a short table with three columns: stage, what was done, effect on the current version (§3). That table keeps later agents from re-proposing rejected directions.

## 4. The hero

Fields for the hero (`character.json → persona`, plus the bible):

- **Stable dramatic want:** **[Example]** to preserve his image as the one with the answer.
- **Flaw:** **[Example]** can't admit being wrong.
- **Inner need (proposed):** **[Example]** learn that asking or admitting ignorance doesn't lower his worth. Change comes in small steps because the flaw is the comedy source.
- **Function in an episode:** **[Example]** makes a promise or explanation, then defends it. Sometimes his analysis is right but his way of imposing it breaks the solution.
- **comic_function** and **guardrail:**
  - **[Example]** guardrail: "Do not make him simply incapable of understanding. Preserve the contrast between his theoretical confidence and his own behaviour."
- **Visual contradiction that supports the flaw:** **[Example]** a baby face plus a high professorial forehead and a jacket give "seriousness vs exaggeration from the first shot".
- **Performance direction:** **[Example]** starts calm and confident, hesitates when the contradiction appears, then re-arranges his words or his signature prop. "We don't need shouting at every escalation."

## 5. The cast as a dramatic system

Design each supporting character as a **different kind of pressure on the same flaw**. Avoid generic "friends".

| Role slot (general) | Pressure type | [Example] |
|---|---|---|
| Practical partner or assistant | The practical question: "OK, where do we start?" | Sami: may reach the simpler solution; has his own goals; can also be wrong. |
| Intimate who knows the truth | Memory of the hero's real behaviour vs his stated image | Nora, wife and *equal partner*: enters with her own need (use the table, keep an agreement); her remark counts "because she knows him, not because she wins every argument automatically". |
| Rival | Status: turns a task into a contest | Dr Adam: his solution may be sound; he can also fall into vanity; "not a villain". |

**Rules that held:**

- **Every character enters wanting something.** Supporting characters make choices that affect the outcome (line 209).
- **Not every character appears in every episode.** Two characters can be enough.
- **Each character needs a `guardrail` against a stereotype.** Fill the field for every character. v1 filled it only for the hero and Sami; Nora's and Adam's live in WORLD.md and their prompts. **[Example]** Sami must not be shown as "a vacant fool or a child merely to give the professor someone to lecture". Nora is "not a permanently angry spouse". Adam is "not a sinister villain".
- **Professions that imply authority get scoped.** **[Example]** "an everyday-life professor, not a specified licensed clinician"; Adam is "an academic, not a physician". This avoids implied professional or medical advice.
- **The relationship table** has three columns: relationship, pressure it creates, example use (§7).
  - **Status games:** the rival makes the hero switch goals, from "solve it" to "prove my solution is more complex".
  - **Undefined side-to-side relationships stay explicit nulls:** "Same recurring cast; no additional individual relationship dynamic has been established."
  - **No new kinship or history** gets added for convenience.
- **Visual contrast mirrors the dramatic contrast.** **[Example]** The rival's broad jaw, neat hair and burgundy blazer contrast with the hero's sparse hair and crooked bow tie (line 191).

## 6. Comedic engine, catchphrases and callbacks

Keep **three kinds of repetition** separate (§10, archive analysis):

1. **Catchphrase:** a verbal or physical marker of a character.
2. **Persistent flaw:** the same defence across changing situations.
3. **In-episode callback:** a detail planted early that returns at the payoff with a *changed* meaning or effect.

**The catchphrase table records exact text plus a usage trigger.** **[Example]** from cast.json:

- "الموضوع بسيط جدًا": "Before he makes an ordinary situation more complicated."
- "ده كان جزء من التجربة": "After a failure, as an attempt to regain dignity."
- "اكتب يا سامي": "While declaring an overconfident conclusion that events may then correct."
- Visual: "Straighten the crooked bow tie: a small attempt to recover composure."

**Rules:**

- `"frequency": "Use when the situation earns the line; do not force every catchphrase into every episode."`
- Repetition works when its **cause or result changes**. A favourite line repeated by itself does not count.
- **Every series needs at least one silent visual catchphrase.** The video pipeline is SFX-only with silent lips (ai-puppet-video rule 1), so a physical gag carries identity without dialogue. Note the known risk: a costume state that differs from the master, such as a crooked tie, tends to revert to the master's state (SKILL.md phase 3).
- Supporting-cast catchphrases stay `"status": "not_yet_approved"` until the user picks them. A line the hero *says to* a character belongs to the hero (sami/character.json note).

## 7. Episode formula

This is the 7-step template (§9). Each step has a review question.

This 7-step formula is the **[Example]** engine for a single hero whose flaw is refusing to admit a mistake. For another flaw or format, keep the same jobs (problem → lead's flaw-driven choice → test → worse choice → concrete escalation → payoff → short reaction) and rewrite steps 2 and 4 and their review questions for your lead's flaw. An ensemble may rotate the lead per episode.

| Step | Dramatic job | Review question |
|---|---|---|
| 1. Present problem | Who wants what, why now | Is the goal clear from one action or one short line? |
| 2. Confident promise | Hero offers a method or explanation | What does the lead stand to lose (**[Example]** his reputation)? |
| 3. Test | A question or action shows the first gap | Does the other character change the scene's direction? |
| 4. Defensive choice | Adds a condition or step instead of admitting the gap | Did the next problem come from his choice? |
| 5. Concrete escalation | Cost rises or the goal recedes | What actually changed? |
| 6. Payoff | Reveals the contradiction or returns the planted detail | Does the ending come out of the scene? |
| 7. Short reaction | A look, a gesture or one line | Can we end before over-explaining? |

- **Escalation is a cause-and-effect chain:** "he did this, so this happened, so he chose this". Louder repetition is not escalation.
- **Stakes stay small and self-made:** lost time, extra effort, extra spending, a broken agreement, a slight loss of trust. No external catastrophe. Balance matters: failure must have weight, but not painful punishment (warm comedy).
- **Ticking clock:** a deadline inside the story is a dramatic deadline, not the video length.
- **The lesson lands through action; no closing lecture.**
- **Sample episode pattern** (§13, "تنظيم التنظيم"): a rejected simple solution (a box) returns as both the fix and the exposure of the contradiction.
- **Episode seeds** are written as a table with three columns: topic, proposed conflict, payoff opportunity (§14). Every seed is marked untested.

## 8. Continuity log and season arc

Keep a per-episode log (§11) with these fields:

- `episode # / title / status (draft | approved | produced)`
- `characters present`
- `goal & explicit promise`
- `new facts (approved version only)`
- `who knows what`
- `carry-forward hook`
- `passing exaggeration (NOT canon)`

Each episode closes its own problem. A small carry-forward hook must be understandable to a new viewer. Reference images and sets do not prove that events happened.

**Proposed season arc** (§12):

1. Full confidence.
2. The pattern appears.
3. Raised stakes.
4. A cosmetic fix that creates new complexity.
5. A real choice, where the hero once listens or asks for help.
6. Limited progress, after which the flaw returns in a new form.

The arc must not erase the character the audience loves.

## 9. Guests and extras

Ask the user whether guests and extras are allowed and record it in cast.json → `episodic_character_policy.user_authorized` (null until answered). **[Example]** the first project authorised them.

| Tier | Role | Identity requirement |
|---|---|---|
| Core | Recurring relationships | Approved masters and sheets |
| Story guest | Speaks or affects the plot | A distinct selected image, reused in every shot of that story; internal ID `guest_<ep>_<role>`, not printed or spoken |
| Background extra | Gives a sense of place | Count, position and activity specified; distinct faces; no full sheet needed |

**Rules:**

- A guest has a simple objective that collides with the hero's complication, without being sarcastic all the time.
- **Flags:** `automatic_permanent_cast_membership: false`, `automatic_preexisting_relationship_or_backstory: false`, `core_identity_changes_authorized_by_guest_policy: false`.
- The hero's signature item is banned on guests. Do not clone core faces.
- An extra who starts speaking is promoted to guest.

**Template** (STORY-AND-CHARACTERS.md §17b). A core image is passed as a reference "ONLY for this series' handmade puppet materials, photographic realism and comic proportions. Do not copy the reference character's face, hair, costume…", then:

```
Guest role: <role>. Internal character ID: <id>. Do not print this ID.
Story function: <what guest wants>. Distinct design: <head shape, nose, brows, hair silhouette, eye colour>.
Wardrobe: <role clothes>. … Do not reproduce any main cast member. No <hero signature item>…
```

§17 has more templates: a 6-panel sheet for the same guest, a lead-plus-guest scene ("Preserve each identity separately; do not blend their faces or outfits"), a background-extras edit ("Add exactly <N>… Change only what is necessary") and a local correction ("Change ONLY <issue>… Preserve…").

## 10. Visual and world rules

**Shared world invariants** go in every `character.json → visual_invariants`. **[Example]** values:

- **Medium:** "Photographed physical handmade fleece/felt puppet… not a human, smooth plastic CGI, or illustration."
- **Proportions:** oversized head, compact torso, very short chunky legs. Preserve the silhouette from the master "rather than inventing numeric measurements".
- **Hands:** `{total_digits_per_hand:4, fingers:3, thumbs:1}`.
- **Seating:** feet dangle on a normal-height seat. "Do not lengthen legs to reach it."
- **Leg length vs hem length:** keep them separate (cropped trousers ≠ longer legs).
- **Identity anchors per character:** eye colour, face shape, hair silhouette and sweep direction ("do not mirror the hairstyle when rotating"), material, wardrobe, footwear.

**Rules that held:**

- **One signature item belongs exclusively to the hero.** Its *colour* need not be exclusive. **[Example]** burgundy is shared with the rival's blazer.
- **Palette logic:** choose one coherent palette logic for the whole cast and record it in `visual_invariants.fleece_color`. Once it is approved, changing it is a deliberate redesign decision. **[Example]** v1 used "a shared warm honey-tan/orange family, not four deliberately separated palettes". That kept one world but made the cast harder to tell apart (characters.md §9), so separate the characters by silhouette, nose and head shape.
- **Wardrobe variants** are an array of `{id, status, reference, items[]}`. Rejected variants are named in `negative_constraints`. **[Example]** "Do not use the rejected old short NECKTIE concept."
- **Sets and decor are "illustrative, not approved final sets"** until the user picks a set.
- **Source priority:** approved master image > detailed sheets > historical prompts. A text description never replaces the image, and old prompt wording never overrides it.
- **Motion honesty:** static sheets don't prove a rig or lip-sync. The production target is fixed eye structures, a hinged jaw and head/body acting.
- **Production references are clean single-view images,** with no grids or printed labels.

## 11. Voice, dialect and localisation

- **Voice, accent and dialect stay `null` until the user approves them.** Words like "confident" or "calm" are character direction, not voice casting (line 338). **[Example]** For this user, voices are recorded by the creator and voice-changed. Generated audio is SFX only, and Seedance Arabic voices were rejected (SKILL.md rule 1).
- **Localisation rule:** "Preserve roles and joke function; adapt dialogue/examples naturally." Translate a catchphrase for memorability and timing, not word for word. Re-test each language version.
- **Never make nationality or accent the joke.** Designs avoid national costume and country symbols.
- **Dialogue tests** are recorded as a test language, not final casting. **[Example]** `"test_language": "Egyptian Arabic; script/test choice, not approved final voice casting"`.
- **Performance notes per character** (`visual_invariants.performance`). **[Example]** Nora: "knowing side glance, slight eyebrow lift and calm smile; varied reactions without habitual anger". Adam: "restrained self-confidence… embarrassment and warm laughter".

## 12. What to avoid

- Stereotypes per role: the fool, the angry wife, the villain. Use the guardrail fields.
- National or accent humour.
- Implied licensed professions (medical, clinical).
- New kinship or backstory without a decision.
- Treating proposals as canon.
- **Production constraints** (from the ai-puppet-video skill): phones, screens and on-screen text in stories, many loose props, and lines longer than the jaw window. Prefer one hero prop with a visual problem and a visual payoff.

## 13. How the bible feeds ideas and prompts

1. **Idea generation:** pick a topic from the hero's `persona.domains` (fill it for each character; v1 has it only for the hero). Map it to the 7-step formula, choose which pressure character tests the hero, and pick a catchphrase whose trigger fits. Then run idea-from-reference.md Steps 2–7 (named scoring criteria in its Step 3 table).
2. **Prompts:** each `character.json.reusable_prompt` is a full identity paragraph with a `[requested scene, pose, expression, framing]` slot, ending in "change only the requested scene/pose/expression". `negative_constraints` become the "Do not…" lines.
3. **Cast per shot:** describe and attach only the characters present in that shot. Naming an absent character makes the model add that character or move their props (SKILL.md phase 4: Nora's oven mitts ended up on the Professor's hands).
4. **Ensembles:** "obtain the actual references for every character appearing; do not infer another character's exact face from a text description" (WORLD.md). "A typed filename alone does not supply an image."

## 14. Pitfalls (with evidence)

- **Stale prompt text overriding chosen images.** Old "natural hair" wording conflicted with the chosen puppet-fibre hair (STORY-AND-CHARACTERS.md line 57). A historical prompt labelled a hand RIGHT with the wrong thumb orientation (adam/README.md). Fix: source priority, and keep prompts as provenance only.
- **Stale "pending review" lines creating fake approval gates** (line 573). Fix: current status lives only in cast.json and character.json.
- **Inferred back views treated as measured.** Sami's rear pockets, Nora's rear bob (sami/README.md, nora/README.md). Fix: label them "inferred, provisional".
- **Approval granularity.** "User agreed to continue" ≠ approval of every panel. Record the exact status: `delivered_user_continued` vs `delivered_pending_separate_user_approval` (cast.json).
- **Snapshot drift** between WORLD.md copies. Fix: the hash plus a sync rule (MANIFEST-CONTRACT.md).
- **Short legs vs cropped hems confused** (STORY-AND-CHARACTERS.md line 327).

## 15. [Example] Superseded and conflicting material

- **v2 redesign** (superseded files: SKILL.md → Example project notes): text-only regeneration with new palettes (Professor biscuit-cream, Sami sage-teal, Nora terracotta, Adam mauve, Adam's blazer in navy), felt-panel hair, closed mouths with a hinge seam, and relative heights 100/108/96/112. Its stated motivation was cleaner provenance from the third-party reference lineage and stronger cast separation. **The user rejected it on 2026-11-15** (SKILL.md → "Example project notes"). v1 masters are identity again.
  - **Conflict (resolved 2026-11-16):** the bible files (STORY-AND-CHARACTERS.md, WORLD.md, the READMEs, SHEET-INDEX.md files) and the manifests used to say v1 is "not a generation reference" and v2 is planned (`cast.json` had `production_branch: "v2_redesign_candidates"` and `v1_allowed_as_v2_generation_input:false`). They now point to the v1 masters (`production_branch: "v1_masters"`, `v1_masters_are_identity_reference: true`), and the v2 docs carry dated SUPERSEDED banners. Any older v2 line still found outside those banners is stale; ignore it.
  - **Lesson for a general skill:** when a redesign is rejected, update the canonical record and every snapshot together. Otherwise later agents follow dead guidance.
- **Rejected concepts kept as history, not reference:**
  - the loop-shaped hair lock,
  - options A–C of the four-way face comparison (D was chosen),
  - the short-necktie outfit,
  - long-leg proportions.

## 16. Fill-in template for a new series

```markdown
# <Series working title> — Story & Character Bible   (date, version)
Status legend: APPROVED / EXPLANATION / PROPOSED. Unknown = null.
## 1 Premise (1 sentence): <hero> who <strength> but <flaw-driven behaviour> while trying to <want>.
Viewer promise: <familiar truth>.  Dramatic question: <will X … or …?>  Emotional value: <why we root for the hero>
Format / platform / length: <sitcom shorts, 9:16, null s>   Audience & age band: <…>   Test language: <…> (not final casting)
## 2 Evolution log: | stage | what was done | effect |
## 3 References → mechanisms: | reference | principle | our application |  (no character copying)
## 4 Hero: want / flaw / inner need (proposed) / episode function / comic_function / guardrail / visual contradiction / performance
## 5 Cast system: per character → role slot, pressure type, own goals, guardrail vs stereotype, visual contrast, performance notes
Relationships: | pair | pressure | example use |   unknown pairs = "not established"
## 6 Comedic engine: catchphrases | exact text | trigger |; visual catchphrase; callback rules; frequency rule
## 7 Episode formula (7 steps + review questions); stakes scale; ticking-clock note
## 8 Sample episode (PROPOSED) + seeds | topic | conflict | payoff |
## 9 Continuity log fields; season arc (PROPOSED)
## 10 Guests & extras policy (tiers, IDs, flags, signature-item ban)
## 11 Visual world rules: medium, proportions, hands, seating, identity anchors, signature item, palette logic, sets=illustrative, source priority
## 12 Voice/dialect: null until approved; localisation rule; no accent/national jokes
## 13 Avoid list (stereotypes, professions, taboo topics, platform/model constraints)
## 14 Open decisions: channel name, names, voices, set, duration, first scripts
## 15 English handoff summary (for any AI)
```

The companion `cast.json` uses `series{premise, format, channel_name:null, test_language, international_localization, episode_duration_final:null}`, `core_cast_ids`, `catchphrases{status, spoken[{text, usage}], visual[{action, usage}], frequency}`, `episodic_character_policy{…}` and `characters[{character_id, display_name, role, manifest, approval_status, master, voice_id:null}]`. Each `character.json` follows the MANIFEST-CONTRACT fields: `persona{age_category, role, traits, comic_function, guardrail, domains, occupation}`, `relationships[]`, `catchphrases`, `visual_invariants`, `wardrobe_variants[]`, `negative_constraints[]`, `unresolved{}` and `reusable_prompt`.
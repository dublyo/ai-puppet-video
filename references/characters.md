# Phase 0a: create the puppet characters (images first, then the series bible, then sheets and the full description)

Part of the general `ai-puppet-video` skill: it works for **any** felt-puppet cast, setting and language. Facts from the first project (`campaign-puppet`: the Professor, Nora, Sami, Adam; Egyptian Arabic) appear only as **[Example]** lines and are never rules for a new cast. Use `<placeholders>` for your own cast. A character-specific skill for one cast is a separate thing; this file stays general. Evidence paths are relative to `/Users/dribrahimm/1-AI-Influncer/campaign-puppet/` unless absolute.

**Before you start:** decide the format and audience (`channel-strategy.md`). Characters must read at thumbnail size, carry one signature gimmick each, match the honestly classified audience (clearly adult for an adult series; puppets alone don't make it child-directed, and adult looks alone don't make it adult), and be 100% original.

**Order:** realism anchor → head comparison → wardrobe → full-body master → supporting-cast masters → **(phase 0b: series bible, `series-bible.md`)** → detail sheets 01–05 → targeted fixes → `character.json` + README, with persona, relationships and catchphrases copied from the approved bible/`cast.json` (never invented here).
- Each master-level choice (head pick, wardrobe pick, full-body master, each supporting master) is approved before the next.
- Sheets 01–05 can be generated as one batch from the approved master, then reviewed and approved as a set. Record per-sheet status honestly.

**Image tool:** v1 used the ChatGPT `imagegen` tool (§0). Any strong image model that accepts reference images works. For a Higgsfield tutorial or production, `gpt_image_2_6_flare` is the natural choice (`references/storyboard.md` has call shapes and prices). Whatever the tool:
- attach the approved image every time (text-only regeneration lost the identity, §8),
- price paid calls with `get_cost`,
- get the user's OK before each paid batch (standing rule 6).

## 0. Principles

1. **The image is the identity, not the text.** The Nora and Adam READMEs say "A text prompt alone is not an identity reference", and every generation after the master attaches the master image. Use this source priority everywhere: **approved master image > detailed sheets > historical prompts > written descriptions**. Evidence: `professor/character.json` → `source_priority`.
2. **Approve each master-level image before generating the next.** Each stage starts from the image the user approved at the stage before. Sheets 01–05 may be generated as one batch from the approved master and approved as a set.
3. **Never redesign while extending.** Every sheet prompt opens with `Use case: identity-preserve` and the line "Preserve this ONE particular … puppet, never redesign him / not a new woman / not a generic variation."
4. **Record status honestly.** "Delivered" is not "approved". An internal QC pass is not user approval. Details the generator invented are labelled "inferred", not canonical.

**Tool used for all of v1:** the built-in Codex/ChatGPT `imagegen` (`image_gen`) tool, one call per asset, with local reference images attached. Record this in `generation_provenance.generator`. Corrections use `Use case: precise-object-edit` on the generated sheet itself. The rejected v2 run used Higgsfield `gpt_image_2` with text-only prompts (see §8).

## 1. Stage order and why

| # | Stage | Input refs | Output | Why this order |
|---|---|---|---|---|
| A | **Material/realism anchor** | an earlier puppet portrait or a user-supplied photo of a real felt puppet; if neither exists, first generate and approve one generic material-test puppet head (no design intent). Mark it "MATERIAL AND PHOTOGRAPHIC REALISM REFERENCE ONLY" | — | Locks the "photographed handmade puppet" look before any face is designed. |
| B | **Head concept comparison** (hero) | A | 3–4 square head-and-shoulders candidates `a-<name>.png …` | Faces are compared under identical conditions. |
| C | **Wardrobe comparison** (on the chosen head) | chosen B as **edit target** | 3 waist-up outfit candidates | Clothing is chosen without the face drifting. |
| D | **Full-body master** `00-master-full-body.png` | chosen B + C | portrait 2:3, 1024×1536 | Becomes the single identity, proportion and wardrobe anchor. |
| E | **Supporting-cast masters** | hero master as "ONLY the universe/material/body-proportion reference" | one full-body 2:3 per character | Gives one world and one construction with distinct faces. |
| — | **Phase 0b: series bible** (`series-bible.md`) | approved masters | world, persona, relationships, catchphrases | Sheets and `character.json` need the persona (expressions, roles). |
| F | **Detail sheets 01–05** per character | that character's master (+ earlier sheets) | mostly 3:2 boards, 1536×1024, and one 9:16 scene | They add the unseen angles, the construction and the seated logic. |
| G | **Targeted QC corrections** | defective sheet + master | the same file, fixed in one cell | Cheaper and safer than a full regeneration. |

Evidence: `puppet-channel-concepts-archive/2026-11-15/original-root/{four-way-comparison-v1,professor-outfits-v1,supporting-cast/concepts-v1}/`.

**Controlled comparison pattern (stage B).** Fix everything except the variable being tested:

> "One square studio photograph, centered straight-on head-and-shoulders portrait … Wear a completely plain oatmeal-coloured cotton crew-neck sweatshirt … warm light-grey studio backdrop … 85mm photographic lens feel … Restrained amused expression."

Add a "SHARED CONSTRUCTION" paragraph that is identical across all candidates.

**Wardrobe edit pattern (stage C):**

> "Input image 1 is the EDIT TARGET and exact identity anchor … This is a wardrobe edit, NOT a new character. … Same eye-level camera, same centered stance, head size and framing across this wardrobe series. Change only his clothing."

**Proportion correction lesson.** **[Example]** The first professor master had human-length legs. The user asked for distinctly short comic legs. The fix regenerated the master with two images and labelled the role of each:

> "Image 1: approved portrait, exact face … Image 2: previous full-body attempt; retain its materials … but it is specifically WRONG in leg length. DO NOT preserve its long-leg proportions."

It also gave proportion targets as design intent: "about 2.8 to 3 head-heights: head ~35 %, torso/hips ~40 %, legs including shoes ~25 %". It added the anti-shortcut line "DO NOT merely shrink the whole existing full-body image. Actually compress the anatomical LENGTH OF BOTH LEGS by approximately 55–65 percent." Every body-dependent sheet (02–05) was rebuilt from the corrected master; the head-only turnaround (01) was kept, since leg length does not affect it. The long-leg sheet is archived. Evidence: `professor/generation-prompts.txt` header and `00-master-full-body-short-legs`.

**Supporting-cast pattern (stage E).** Attach the hero master with the role stated as "ONLY the universe/material/body-proportion reference … Create ONE NEW DISTINCT ADULT CHARACTER, NOT a costume swap or clone of his face." Then give an explicit **do-not-reuse list** of the hero's signatures, for example "Do NOT reuse the professor's bald crown, huge high forehead … olive jacket or signature burgundy bow tie. No bow tie of any kind for these supporting characters." Also ask for "Distinct appearance should remain clear at a small thumbnail size." Approve each supporting character's name and dramatic role first (a one-line role from the bible draft). Then open the prompt with `Character: <NAME>, <role and temperament>` plus one anti-stereotype expression line (**[Example]** Sami: "Avoid a confused or foolish expression"). Evidence: `puppet-channel-concepts-archive/2026-11-15/original-root/supporting-cast/concepts-v1/generation-prompts.txt` (header: "Roles already approved").

## 2. The master `00-master-full-body.png`: spec

- One character, front-facing, standing, full body "from top of head to feet, no crop", both feet flat and separated, arms slightly away from the torso so the hands are countable.
- Plain warm light-grey seamless studio, soft neutral light, portrait 2:3.
- No text, props or other characters.
- Mouth: v1 used an open friendly smile with the tongue showing. Closed-mouth views exist only on later sheets. For video, also get a closed-mouth view (see §8 and the jaw notes in `references/puppet-look.md`).
- Medium vocabulary that worked: "Physical handcrafted television puppet, tangible short <color> fleece, seams, cloth and fibers, photographed photorealistically. No human skin, no shiny CGI toy finish." Add the cast's age/species guardrails. **[Example]** "adult … not a child, infant or toddler" and "not a human with a medical condition".

**The master is the read-only identity reference for video.** The video skill uploads **copies** of `<id>/00-master-full-body.png` as image references, never edits the file, and checks the md5 or sha256 against `assets[].sha256` if in doubt. Pass only the masters of the characters in a shot. Production notes add two rules:
- "For future production references, use clean single images per angle, no panel grids or printed titles" (all SHEET-INDEX "next production" sections).
- "Do not upload old multi-panel sheets as a new identity" (`production_reference_policy.element_source`).

Sheets 01–05 are human or agent reference material. For a hand-only insert, pass a **crop of a copy** of the master's hand (`references/puppet-look.md`).

## 3. Detail sheets 01–05: the reusable prompt skeleton

Every sheet prompt uses the same block order. Repeating the identical lock paragraphs word-for-word in every prompt is what kept identity stable.

```
Use case: identity-preserve
Asset type: <name> <sheet type>.
Primary request: <one sentence: what, how many cells, grid, aspect>.
Input image 1: approved <NAME> puppet, the exact identity and material reference. Preserve the SAME <adult …> handmade puppet, not a new <person>.
[Image 2/3: <role> e.g. "exact wardrobe closeup", "established alternate body", "compact seated body reference"]
Identity lock: <VERBATIM paragraph: fleece color+texture, head shape, nose, eyes (iris color, lids, lashes), brows, ears, mouth construction, hair color/material/silhouette/part DIRECTION, negatives (no jewelry/glasses/…), personality guardrail>.
Body and wardrobe lock: <VERBATIM paragraph: head/torso/leg proportions, "exactly THREE fingers plus ONE thumb" (or your digit count), every garment with color, material, closures, pockets, lengths, footwear, "Match all reference garment widths and lengths", minimal rule for unseen back construction>.
Layout: <row-by-row cell content with explicit image-left/image-right directions>.
Style: <VERBATIM: photographed handmade puppet, soft even studio light, neutral warm-gray seamless backdrop, aligned equal cells, narrow dividers, generous margins, all parts fully inside panels, not CGI/drawing/human>.
Constraints: <sheet-specific negatives>.
```

| File | Canvas / cells | Cell content (direction-explicit) | Sheet-specific locks |
|---|---|---|---|
| `01-head-turnaround.png` | 3:2 (one v1 board was 1:1), 3×3 | Front 3/4 L, front, front 3/4 R / profile nose-left, true back (no face), profile nose-right / rear 3/4 L, overhead crown, rear 3/4 R | "head only, no neck stump, shoulders, body"; "Correct real physical rotations rather than mirrored copies"; "side profiles show only the near eye"; same expression and scale in all cells; "never mirror [asymmetric hair] to create another side view" |
| `02-headless-body-turnaround.png` | 3:2, 3×2 | Front, L profile, back / R profile, seated front, seated side | "Remove head completely … stop at a short smooth <fleece> neck connector … harmless puppet assembly"; "Do NOT normalize to a human body because the head is removed"; seated: "thigh and shin lengths remain IDENTICAL to standing"; follow the cast's `visual_invariants.seating` rule (**[Example]** short-legged cast: "Feet DANGLE visibly above ground on normal-height stool. Never stretch legs to floor, hide feet, cross legs or use a footrest"); front and side seated views agree on seat height |
| `03-facial-expressions.png` | 3:2, 3×2 | Six restrained, role-specific reactions, same straight-on close portrait | "change only brows, lids, eye direction and jaw angle. Preserve head geometry, cheek volume, eyeball size … No human teeth"; no emotion symbols. Choose expressions from the persona (**[Example]** Nora: knowing side-eye, "I knew it" smile; Adam: sheepish after being proved wrong) |
| `03-headless-body-<variant>.png` | as 02 | Used **instead of** expressions when a character has an approved second outfit | "Costume variation: REMOVE <garment> … EXACT SAME <signature item>". **[Example]** The professor has no expression sheet; README warns not to borrow another character's |
| `04-material-and-movement-details.png` | 3:2, 2×4 or 3×2 | Palm, hand back (same hand), footwear front/side, fabric/pocket macro, collar or signature item macro, seated leg/foot detail; optionally mouth closed / mouth open | "digits separated enough to count, no human nails"; "the two mouth states are the same head at equal scale" |
| `05-vertical-<location>-scene.png` | 9:16 (≈941×1672) | Character alone, seated full body in an illustrative set | both complete feet/shoes, placed as `visual_invariants.seating` requires (**[Example]** "dangling well above floor … visible gap beneath them"); "Do not enlarge the stool so much that he looks tiny on a giant set"; no props covering the body; no readable text. Decor is labelled `illustrative_not_approved_canonical_set` |

Labels are optional. The professor sheets have small view labels; Nora, Sami and Adam use "No labels". Unlabelled boards are cleaner as references; labelled ones are easier for humans to read.

## 4. Hand and finger correction (the main QC lesson)

- A non-human digit count must be stated every time, in caps, with the total: "exactly `<N>` digits" (**[Example]** "exactly THREE fingers plus ONE thumb, FOUR digits total"). Add "separated enough to count", "no human nails", "no five-digit hands".
- **Failure seen twice (Nora, Adam):** the "hand back" cell showed the thumb on the same side as the palm cell. That is a mirrored palm, not a turned hand.
- **Fix:** a one-cell `precise-object-edit`:

> "correct ONLY THE UPPER MIDDLE PANEL so it clearly shows the BACK of the same puppet hand whose PALM is visible in the UPPER LEFT panel … the thumb must point toward IMAGE-LEFT, on the opposite side from the thumb in the upper-left panel … smooth fleece back-of-hand surface … without palm-pad contours … keep the upper-left palm hand unchanged … Keep ALL FOUR remaining panels unchanged … Preserve the exact 3x2 layout and border positions, canvas size, colors."

Evidence: `nora/generation-prompts-v1-hand-correction.txt` and `adam/generation-prompts-v1.txt` → "TARGETED QA CORRECTIONS".

- **The same pattern fixes angle errors.** **[Example]** Adam's head sheet had two front 3/4 views facing the same way. The fix: "change the BOTTOM-MIDDLE cell (row 3, column 2) … to the OPPOSITE, LEFT-FACING FRONT THREE-QUARTER angle … a real rotation of the same head, not a mirror flip … Keep ALL other eight cells … unchanged."
- **Correction prompt rule:** name the cell by row and column, give one change, state the invariants for every other cell, and attach the master as image 2.

## 5. QC checklist for any sheet (do this visually against the master)

1. Face: shape, nose, eye color, lids and lashes, brows, ears.
2. Hair: color, material, **part and sweep direction**. No mirrored asymmetric hair.
3. Rotations: true, not duplicated. Each direction appears once and both 3/4 sides face opposite ways. The back view shows no face. Profiles show one eye.
4. Hands: count the digits in every visible hand. Palm and back of the same hand have opposite thumb sides (if the hand has a thumb).
5. Proportions: the legs are no longer than on the master. Headless bodies are not "normalised". Seated thighs and shins equal the standing ones, and the seated feet follow `visual_invariants.seating` (**[Example]** dangling with a visible gap). Front and side seated views agree.
6. Wardrobe: every garment, closure, pocket and footwear type matches. The signature item is present only on its owner, with the same shape, material and tilt.
7. No invented accessories, text, logos or extra characters. Everything is inside its cell with margins.
8. Mouth matches the medium (here: toothless, dark interior, felt tongue).
9. Log what the sheet **invented** (back of hair, back of garment, rear pockets) under `inferred_construction`. Don't claim it came from the master.

**Known accepted imperfection:** the "overhead crown" cell often comes back as a downward-tilted face (Nora, Sami, Adam boards). Re-roll that cell if the crown or bald pattern matters.

## 6. File and manifest contract (every character folder)

```
<cast-root>/
  cast.json                 # central: series, core_cast_ids, per-character status & pointers, shared catchphrases + hash, guest policy, production_state
  MANIFEST-CONTRACT.md      # schema doc
  <character_id>/
    README.md               # English AI handoff: start-here steps, source priority, identity & proportions, wardrobe table, asset map, reusable identity prompt, guests, provenance
    SHEET-INDEX.md          # per-file table (user language OK), approval history, inferred details, QC notes, tool used
    character.json          # structured manifest (below)
    WORLD.md                # portable copy of series bible (synced snapshot)
    generation-prompts-v1.txt   # verbatim prompts + selected source paths; never edited later
    generation-prompts-v1-<correction>.txt
    00-master-full-body.png
    01-head-turnaround.png
    02-headless-body-turnaround.png   (or 02-headless-body-<outfit>.png)
    03-facial-expressions.png         (or 03-headless-body-<alt-outfit>.png)
    04-material-and-movement-details.png
    05-vertical-<location>-scene.png
```

- Folder links are relative so each folder is a portable package.
- PNGs are byte-identical copies of the selected generator outputs. Originals stay in the generator's folder, and the source path is logged in the prompts file.
- Superseded material moves to `<root>-archive/<date>/` with a `preservation-manifest.json` (path, size, sha256). Nothing is deleted.

**`character.json` schema (generic fields):**
- **Header and pointers:** `schema_version`, `character_id`, `display_name{en,<lang>}`, `updated_at`, `entrypoint`, `path_base`, `canonical_image`, `shared_context`, `details_index`, `historical_prompt_paths[]`.
- **Status and sources:** `approval_status{base_appearance, detailed_sheets, internal_visual_review, note}`, `source_priority[{rank, source, scope}]`.
- **Assets:** `assets[{path, role, status, width_px, height_px, sha256, note?}]`, `facial_expressions_sheet` (null if none).
- **`visual_invariants`:** `medium`, `proportions`, `hands{total_digits_per_hand, fingers, thumbs, construction}`, `seating`, `trousers`/garment-length rules, `scene_decor`, `face`, `fleece_color`, `eyes`, `eyebrows`, `hair`, `mouth`, `facial_hair`, `signature`, `performance`.
- **Wardrobe and persona:** `wardrobe_variants[{id, status, reference, items[]}]`; `persona{age_category, role, traits[], comic_function, guardrail, domains[], occupation}`; `relationships[{character_id, relationship, interaction}]`; `catchphrases{status, spoken[{text_<lang>, usage}], visual[{action, usage}], frequency}`.
- **Gaps and limits:** `unresolved{personal_name, voice, accent, primary_language, exact_age, nationality, …: null}`, `negative_constraints[]`, `asset_scope{type, measured_rig, animation_validation}`.
- **Reuse and policy:** `reusable_prompt` (master-attached identity prompt with `[requested scene…]` slots), `approved_core_cast_ids`, `episodic_character_policy`, `reference_version`, `production_use`, `catchphrase_authority{path, field, sha256}`, `production_reference_policy`, `generation_provenance{generator, branch, third_party_reference_ancestry, new_text_only_branch}`.
- **Inference and usage:** `inferred_construction{status, details[], instruction}` or null, `scene_context`, `usage_order[]`, `archive_reference_policy`, `capability_limits[]`.

**Rules for the manifest:**
- Absence is `null`, never a guess. Don't invent a name, voice, age or nationality.
- Use one field name per concept across the whole cast (`fleece_color` replaces `skin`, `face` replaces `head`).
- Shared lines live in `cast.json`. Portable copies carry a SHA-256 of the canonical JSON (sorted keys, `,`/`:` separators) and are updated together.

**Reusable identity prompt (template):**

> "Use the attached 00-master-full-body.png as the approved identity, material, and proportion reference for `<Name>`. Create `[scene, pose, expression, framing]`. Preserve `<identity lock summary>`. Preserve `<proportions>` and exactly `<hands wording: N fingers [plus one thumb]>` per hand. Use `[wardrobe_variant id]`: `<items>`. `<seating rule>`. Keep the photographed handmade puppet appearance; change only the requested scene/pose/expression."

## 7. Guests and extras (generic policy worth keeping)

- A guest is designed using core masters for **material and proportion only**, never as "a face to recolor".
- Generate the guest alone first. Its selected image then becomes its identity reference across shots.
- A guest is not automatically permanent cast and has no automatic backstory.
- For ensemble images: one labelled reference per foreground character, and "prohibit blended faces or swapped wardrobes".
- Label every attached image as identity, material/style-only, or edit target. "A typed filename alone does not supply an image."

Evidence: `<id>/WORLD.md` → "Episodic guests…" and "ChatGPT imagegen prompt notes".

## 8. [Example] A rejected redesign and the generic lessons

- **v2 redesign (rejected by the user 2026-11-15; superseded).** Superseded files: SKILL.md → Example project notes. The plan was a text-only cast redesign for stronger character separation: distinct felt palettes, fabricated felt/yarn hair, closed mouth with a "fine dark hinge seam". 12 credits were spent on Higgsfield `gpt_image_2`, 3 candidates per character.
- **Problems the round-1 review found** (`production/generated-v2/REVIEW-ROUND-1.md`; the user's exact words are not recorded in the files read):
  1. The hinge-seam wording produced a thin smile line instead of a puppet jaw. That looks like a doll, gives a video model nothing to open, and hurts lip-sync.
  2. Comic appeal dropped: small realistic eyes, flat polite faces.
  3. The world looked mixed: some palettes read as human skin tones, others as fantasy creatures.
  4. Sami's yarn-bundle hair read as locs, an unintended cultural association.
  5. Sami's grey-green read as sickly.
  6. The hands were too small to verify.
- **Generic lessons:**
  - Text-only regeneration loses the approved identity.
  - Mouth wording must describe a wide hinged performance-puppet mouth with a high-contrast interior (dark cavity + red/pink felt tongue) that differs from the fleece colour, since `jaw_windows.py` measures speech windows from that contrast. If a character's fleece or nearby clothing is red or dark, pick a contrasting mouth lining or plan to verify jaw windows against a contact sheet.
  - Keep comic big-eyed appeal.
  - Choose one coherent palette logic for the whole cast.
  - Check hair wording for cultural readings.
  - v1 masters remain the identity: never relabel v1 PNGs as v2, and never mix branches.
- **Other superseded material:**
  - The long-legged first professor sheet, replaced by the short-leg revision.
  - The "short necktie" outfit concept: "Never use the rejected short necktie concept".
  - Historical "pending review" lines inside prompt files, which are dated history; current status lives in `character.json` and `cast.json`.

## 9. Pitfalls (with evidence)

- Shrinking the image instead of re-proportioning, or headless bodies drifting to human legs. Evidence: `professor/generation-prompts.txt` (02/03 "Do NOT normalize…").
- Mirror-flipping asymmetric hair or hands to fake a rotation. Evidence: `sami/generation-prompts-v1.txt`, `adam/generation-prompts-v1.txt`.
- A signature item bleeding onto other characters. Name the owner and add "No `<item>` of any kind" for the others. Evidence: `puppet-channel-concepts-archive/2026-11-15/original-root/supporting-cast/concepts-v1/generation-prompts.txt`, `references/puppet-look.md`.
- Similar shades across characters (**[Example]** burgundy bow tie vs Adam's burgundy jacket) and one shared fleece family make the cast hard to tell apart. Separate by silhouette, nose and head shape, not only colour. Evidence: `DESIGN-V2.md` → "Corrections supported by the read-only audit".
- Static expression sheets are not proof of animatable motion or lip-sync (all READMEs). `performance` may hold acting direction, but keep `asset_scope.animation_validation` and cast.json `motion_validated`/`lip_sync_validated` false/null until a motion test exists.
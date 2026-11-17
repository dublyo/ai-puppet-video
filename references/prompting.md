# Prompt templates and wording lessons

## Contents
1. Image numbering
2. The video shot prompt template (Seedance 2.5)
3. The storyboard frame prompt template (GPT Image 2.6 Flare)
4. Wording that worked
5. Wording that only partly worked
6. Wording that backfired
7. Reviewer suggestions not yet tested
8. Pre-flight prompt checklist

---

## 1. Image numbering

"Image 1, Image 2, …" follow the order of the `image_references` entries in `medias`; `start_image` and `end_image` are not counted.
- **New setups and cut-ins** pass the masters first, in a fixed order (A, then B), then the frame they must match, which becomes Image 3. A single-character panel that passes one master makes that frame Image 2, so say so explicitly.
- **END frames in EDIT mode** pass their own START frame as **Image 1**, usually as the only reference, with a short header. See the EDIT template in section 3 and `storyboard-qc.md`.
- In video prompts, it's safer to name characters by description ("Professor = balding orange-tan felt head …") plus "match the reference images", rather than by number.

## 2. Video shot prompt template

Use one prompt per shot, about 1,500–2,000 characters, in the order header → SOUND → timed action.

```
Live-action sitcom shot, vertical 9:16, one continuous shot with no cuts. Real handmade felt
hand-and-rod puppets on a real <set from the bible's approved set, [Example] home-kitchen> set, photographed; no puppeteers, rods or human hands.
The first frame is the start image: keep its exact framing, set, lighting and character positions.
<A> = <5–8 identity words incl. texture: "olive corduroy jacket with visible ribs, hand-knitted
burgundy bow tie">. <B> = <…, and "no <A's signature item>">. Match the reference images exactly.
Every hand has <hands from character.json, e.g. three felt fingers plus one thumb>; hands never press palm to palm. Hinged felt
puppet jaws, no human lips or teeth. Camera locked off on a tripod, no zoom, no shake. Nobody
looks into the lens. <Rigid-prop line, e.g. "The jam jar is rigid glass; its height, width and
shape never change.">
SOUND: foley and sound effects only. No human voice of any kind, no speech, no words, no
whispers, no grunts, no laughter, no music. Sound effects: <each SFX and when it happens>.
0.0-1.5s: <action>; during these 1.5 seconds his felt jaw keeps opening and closing quickly and
continuously, a steady silent puppet-mouth rhythm, and it shuts at 1.5s.
1.5-5.0s: <action with the prop: which hand holds what, where it rests, what stays visible>.
[Keep the scripted action going to the end of the clip; models freeze once the action ends.]
[If end_image is used: "The end frame is the end image."]
```

These are precautions, not proven rules:
- Keep the prompt focused on this one shot.
- Sub-timings give the model anchors. It follows them only loosely; take 1's cuts landed exactly, but the in-shot beats drifted.
- Pass only the masters of the characters in the shot.
- Restate the eyeline during grooming or self-focused beats; a lens look happened while the Professor fixed his tie.

## 3. Storyboard frame prompt template (`gpt_image_2_6_flare`)

```
Storyboard keyframe, a single photographed film still, vertical 9:16. Real handmade felt
hand-and-rod puppets on a real <set> set, live-action sitcom look, <key light and side, [Example] soft
morning window light from screen-left>. No puppeteers, rods or human hands. No text, captions, labels, logos or
panel borders.
<A> = Image 1 exactly: <full identity + texture>. <B> = Image 2 exactly: <…>, no <A's item>.
Every hand: <hands from character.json>. Puppet jaws closed unless stated. Prop: <exact prop
INCLUDING its shape in every state, e.g. lid-on and lid-off>. Nobody looks into the lens.
[Cut-ins and new setups: "Image 3 is the frame just before this cut: copy its kitchen set, lighting,
colour grade, counter, prop positions and character scale exactly."]
SHOT n, <size>, <angle>, locked camera, framed slightly looser than the final shot. <A on the
LEFT, B on the RIGHT, never swapped>, <faces at ~32% / ~68% of width>, <look room>, <eyes on upper
third>, <a clear margin of wall beyond each outer shoulder>, <foreground in the bottom fifth>.
<Single key pose: hands, prop position, gaze, mouth state, any gag start-state such as a bow tie
tilted 30 degrees>.
[Custody negatives where needed: "BOTH OF SAMI'S HANDS ARE EMPTY … There is NO jar anywhere in this
shot (the jar is with the off-screen Professor)."]
```

### EDIT template for END frames (camera lock: 0% drift in test-video-05)

```
[short edit header] Photographed film still, vertical 9:16: real handmade felt hand-and-rod puppets in a
real kitchen. No puppeteers, no human hands, no text, no logos.
Image 1 is the START of this same shot. EDIT Image 1, do not re-compose it: keep its camera, crop, sink,
faucet, counter, back wall, light, and both puppets' size, position and costumes pixel-identical.
Change only this: <the scripted action + the exact new prop spots, e.g. "the colander now sits on the
counter just LEFT of the gold faucet; the sink is EMPTY; his bare hand just letting go">.
```

Refs: `[START]`. Add masters after it only if a character isn't already in START. In `storyboard_rounds.py`, mark the frame `"mode": "edit"` so it gets the `edit_header`.

## 4. Wording that worked (verified in the renders)

| Goal | Wording |
|---|---|
| Keep the geography | "Sami stands on the LEFT side of the frame and the Professor on the RIGHT side, never swapped." Use capitals and "never swapped", plus the panel-1 reference. |
| Eyeline in singles | "head turned three-quarters toward screen-left, eyes on the off-screen Sami". Singles held their eyelines in takes 2 and 3. |
| No prop teleporting in the payoff | A separate high-angle insert: "one hand keeps the jar pressed upright on the counter the whole shot … The jar base never leaves the counter." |
| No prayer read | "hands never press palm to palm" plus any hands-apart gesture. |
| Smooth jam | "bright smooth orange apricot jam (smooth spread, no fruit pieces)". Without it we got whole apricots. |
| No voice leak | No quoted lines and no counts. A SOUND block that lists the SFX and bans vocal sounds. All three take-3 re-rolls came out clean. |
| Custody in a single | "BOTH OF X'S HANDS ARE EMPTY … There is NO jar anywhere in this shot" (it fixed storyboard panel 2). |
| No CG ballooning | "his felt head keeps its exact shape; strain via squeezed eyes, knit brows, trembling" (the S1 re-roll kept the head shape). |

## 5. Wording that only partly worked

| Wording | What it did | What it didn't do |
|---|---|---|
| "jaw keeps opening and closing quickly and continuously … shuts at X s" | It avoided voices. | It didn't give continuous flapping or respect the window: S1-B gave two snap-open holds and re-opened at 2.0–2.67 s; S5-B started about 1 s late. Measure with `jaw_windows.py`. |
| "shakes both loose open hands beside his shoulders like a weightlifter, hands apart" | It kept the hands apart. | The gesture itself never rendered (take 2: raised-fist flex; take 3: flutter at chest height, brushing the tie). Draw the pose in the panel if it matters. |
| "small margin of wall at each side edge" (9:16 two-shot) | It improved on take 2. | The approved panels still touched the edges. Frame panels about 10% looser and measure the margins. |
| "Sami stays alive: breathes, blinks, eyes follow, eyebrow lifts" | It produced blinks (S1-B). | He stayed otherwise frozen in the two-shots (S5-B); the eyebrow never lifted. Use a reaction single. |

## 6. Wording that backfired

| Wording | What happened | Use instead |
|---|---|---|
| `says in Egyptian Arabic: "…"` | The model voiced it. The Arabic was judged very bad. | No quoted text; just a jaw rhythm and a time window. |
| "mimes a line of about 8 syllables" | The model **spoke the instruction**: "eight syllables". | No counts. |
| "AUDIO: absolutely no voices …" while counts or quotes were still in the prompt | Voices leaked in 4 of 5 clips. | Remove the counts and quotes. The ban alone is not enough. |
| "rubs his palms together fast" | Palms pressed together for about 7 s, read as **prayer**. | A hands-apart gesture. |
| "cheeks puffed" | The felt head ballooned like CG. | Use the "keeps its exact shape" wording. |
| "fingertips grip the side rim of the lid … flat top stays visible" | **Ignored** in both S1 takes (the lid was palmed from above). No readable twist in either S4 take. | Draw the side grip in the start panel, and carry the payoff on the pop and lift in an insert. Give the lid a visible edge mark. |
| "rigid, straight-sided cylindrical glass jar with no neck … identical before and after" | It did not stop the neck appearing (S4 A and B). | Fix the jar's shape in the storyboard (untested). Cut on the pop. |
| "gold top facing the camera" for a handheld lid | The white or silver underside faced the camera in takes 2 and 3 ("half a coconut shell"). | Design the prop so both faces read ("inside of the lid is the same dull gold metal, no white liner"). Draw the end pose with the lid clear of the jar. |
| "straightens his crooked bow tie" when the master's tie reads nearly level ([Example] `character.json` says "crooked asymmetric", but the master shows only a mild tilt of about 10–15°) | No visible change (take 2). Even with "tilted 30°" in the prompt, the storyboard drew it level. | Measure the tilt in the panel and re-roll until it is visible. |
| `batch_size: 2` on flare | Billed double and returned one image. | `batch_size: 1`. |
| A 4–5-shot story in one 20 s render | Camera, blocking and props were left to the model: floating jar, lens looks, cramped two-shot. | One clip per shot from the panels. |

## 7. Reviewer suggestions not yet tested

- "hinged felt jaw drops visibly open and shut": fixes a jaw that opens only a narrow slit and reads as stretching lips.
- "slow, loose shake": fast shakes blur felt fingers into mittens.
- "thumb and index finger visibly pinching the bow tie": for fine hand work.
- "both of Sami's hands show the teal rolled cuff": an insert hand once had no cuff.
- For hands-only inserts, pass a cropped close-up of the master's hand as an extra reference: crop a copy, never edit the master.

## 8. Pre-flight prompt checklist

- [ ] No quotation marks, no dialogue text, no syllable or word counts.
- [ ] A SOUND block that lists the SFX and bans voices (or `generate_audio: false` and SFX in CapCut).
- [ ] Sub-timings for every beat, and action scripted to the end of the clip.
- [ ] Prop custody for every second, with rigid-prop wording. The prop's shape and start state are already right in the start panel.
- [ ] Screen sides and eyelines named; "nobody looks into the lens"; the eyeline restated during grooming beats.
- [ ] The digit wording from `visual_invariants.hands` (**[Example]** "three felt fingers plus one thumb"), "never palm to palm", "no human hands".
- [ ] No listener in a two-shot while the other character carries a long action. Use a reaction single.
- [ ] Only the masters of characters in the shot are passed; texture words are included.
- [ ] `get_cost` was run, and the user approved the total.

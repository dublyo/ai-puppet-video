# Making AI puppets read as real felt puppets

## Identity

- **One master per character, read-only:** `<cast-root>/<character_id>/00-master-full-body.png` (SKILL.md rule 5, made in phase 0a).
  - Ignore any superseded design branch listed in the project's notes. **[Example]** campaign-puppet: the v1 masters in `campaign-puppet/puppet-channel-concepts/`; the v2 `*-v2-candidate-*` files are rejected (SKILL.md "Example project notes").
  - Upload copies with `hf_lab.py upload`. Check the md5 hash before and after if in doubt.
- **Give 5–8 identity words per character, including texture:** "olive corduroy jacket with visible ribs", "hand-knitted burgundy bow tie", "dense orange-tan felt".
  - Give the signature item to one character only, and say so for the other ("Sami has no bow tie"). That stopped trait bleed in the two-shots.
- **What held:** shape, colour and costume, across 3 takes and 14 shots in Seedance 2.5, from the masters alone (no Elements).
- **What drifted:** fine texture. Corduroy rendered as velvet, the knit as smooth felt, and the insert hands came out lighter and fuzzier.
  - For hands-only inserts, try passing a cropped close-up of the master's hand as an extra reference: crop a copy, never edit the master.
  - Grade the insert to match in CapCut.
- Pass only the masters of the characters in the shot.

## Vocabulary that sells "real puppet"

- "real handmade felt hand-and-rod puppets, photographed on a real <set>, live-action sitcom look"
- "no puppeteers, rods or human hands"
- "hinged felt puppet jaw, no human lips or teeth"
- "every hand has <N digits as in visual_invariants.hands>" (**[Example]** three felt fingers plus one thumb)
- "his felt head keeps its exact shape". Without it, strain made the cheeks balloon like CG.
- Show emotion through puppet means: head tilt, brows, eyelids, trembling, timing, hands. Avoid face deformation.

## Mouth (jaw)

- The jaw moves only on that character's line. State "mouth stays closed" for the listener.
- Use a closed-mouth start panel for a line that opens a shot; otherwise the first flap is lost.
- Never write the line text or a syllable count in the video prompt (it causes voice leaks).
- The rendered windows drift. Measure them with `jaw_windows.py` and give the creator the window table.
- To try (untested): "hinged jaw drops visibly open and shut" when the mouth only opens a slit.

## Hands

- The character's own digit count (**[Example]** 3 fingers plus a thumb), mitten-like felt. Fast motion blurs them into mittens; try "slow, loose" movement.
- **Never palm to palm.** Held pressed palms read as prayer, a sensitivity risk for this audience.
- Say which hand holds what and where the prop rests. Insert hands carry the character's cuff colour and enter from his screen side.
- For fine work (fixing a bow tie), try "thumb and index finger visibly pinching" (untested).

## Props and set

- One hero prop per short. Describe its material and its **shape in every state** (lid on and lid off). Draw that shape in the storyboard, because the start frame decides it.
- **Rotating or moving props need a visible non-text feature** (a ridged edge, a dent, a seam), so the motion reads. A plain gold lid can't show a twist.
- **Design both faces of handheld props.** The lid's white underside kept facing the camera, so specify "the inside of the lid is the same dull gold metal, no white liner".
- **Screens and small handheld props** (e.g. EP01-PHONE-BREAK; untested):
  - unbranded phone, screen off or black (or a plain glow), no UI and no text;
  - draw any damage (a crack) in every panel and keep it identical;
  - name the holding hand every second;
  - give the break moment its own insert.

  EP01-PHONE-BREAK.md still references the v2 designs; adapt it to the v1 masters.
- No labels, text or logos on props or in the set (brand-safety and sponsor rules).
- Keep the set consistent: the same kitchen, light from the same side, and the same foreground items (the bread plate in front of the same character).

## Sponsor / IP safety (this campaign)

- Show no third-party characters, brands or footage on screen. The original visual research descended from other puppet channels; keep it off screen.
- Disclose realistic AI-generated puppet footage on upload (project policy).

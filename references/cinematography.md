# Cinematography for 9:16 AI dialogue scenes

The user's rule: camera angles, cutting between speakers and the space between characters matter as much as the characters themselves. Always use composition rules: the rule of thirds / golden framing, look room, and the 180° line.

## The 180° line (screen direction)

- Decide once: character A is **screen-left looking right**, character B is **screen-right looking left**. Keep it in two-shots, singles and inserts. In the insert, A's hands enter from screen-left.
- **Establish it first.** Open on a two-shot, then cut to singles. In take 1 the singles came first and both characters looked into the lens, so the scene didn't read as a conversation.
- **In singles, the off-screen partner is implied by the eyeline:** "eyes on the off-screen Sami, screen-left". Never let anyone look into the lens; we wrote it in every prompt, and still caught 3 lens looks in take 2.
- Write the sides in capitals and add "never swapped". In round 1 of the storyboard the image model swapped the sides in a two-shot.

## Rule of thirds / golden framing in a vertical frame

- **Eyes** sit on the upper third line, about 33–38% from the top.
- **In a single**, the face sits on its own vertical third, with look room (empty space) on the side the character faces. For example, Sami's MCU puts his face on the left third and leaves a full third of space to the right.
- **9:16 two-shot:** 9:16 is narrow, and a landscape-style two-shot pushes the faces to the edges and crops shoulders and ears (take 2: faces at 20% and 78%). Fix it with:
  - chest-up framing,
  - shoulders close together,
  - faces at about 32% and 68% of the width,
  - a small margin of wall beyond each outer shoulder,
  - the counter or foreground in the bottom fifth only.

  Make the storyboard panel about 10% looser than this and measure the margins: the take-3 panels still touched the edges. An edit can punch in, but it can't widen the shot.
- **The listener problem in two-shots.** The model animates the acting character and freezes the other one, even when you prompt actions for him (tested twice). Keep two-shots short, and cover the listener's reaction with its own single.
- **Avoid tangents.** A hand or prop shouldn't touch the frame edge or another character's body; for example, Sami's palm nearly touching the Professor's sleeve read as reaching for his elbow.
- Keep props inside the frame with a hand's width of margin.

## Coverage pattern that worked (20 s, 5 shots)

| # | Shot | Purpose |
|---|---|---|
| 1 | Medium two-shot, eye level | Geography, the goal and the attempt |
| 2 | MCU single of B, eye level | The offer or reaction line |
| 3 | MCU single of A, slight low angle | The pompous, defensive choice (a low angle adds authority) |
| 4 | High-angle insert (about 60°, only the surface in frame) | The payoff action, clearly readable |
| 5 | Same two-shot as 1 (match frame) | The punchline and the button. The viewer re-orients instantly. |

The cutting rhythm is two-shot → single → opposite single → insert → matching two-shot. That is standard dialogue coverage.

## Motivated angles and moves

- Every angle needs a reason: a low angle for pride or authority, a high angle for clarity of hands and props, eye level for neutral dialogue.
- **Use a locked-off tripod by default.** It keeps the composition clean, and AI camera moves add drift. Add a move only when it carries meaning, such as a slow push-in on realisation.
- **Insert shots are the cure for prop physics.** Make the payoff its own shot, where one hand anchors the prop on the surface for the whole shot.

## Timing and pacing

- **Plan from what renders, not from ideal delivery.**
  - The measured jaw windows in take 3 were 0.5–2.6 s per line, even when 1.5–3 s was planned.
  - So keep lines short (about 3–5 syllables per second of window), or plan for a faster read.
  - A natural-speech heuristic (about 0.3 s per syllable plus about 0.3 s of air each side, e.g. 7 syllables ≈ 2.7 s) is unmeasured. Use it only to budget shot length, then measure the real windows.
- **The punchline needs a button.** Finish the last line at least 1 s before the end, then hold a reaction. In take 2 the line ended 0.1 s before the clip did.
- **The model shortens freezes and holds** (S5-B held 0.71 s of a planned 1.0 s). Prompt them longer than needed, measure them, or build them as a CapCut freeze-frame.
- **Never time-stretch a clip to fit a voice line**: hands and heads start to crawl.
- A "caught out" beat needs a real freeze: completely still, eyes wide, brows up, jaw shut.

## Safe zones (Shorts / Reels / TikTok)

Platform UI covers the bottom band and the right-edge button column. Keep faces, hands and the payoff out of the bottom 15–20% and away from the right edge, and decide where captions go before setting the counter height. The empty counter band can double as caption space.

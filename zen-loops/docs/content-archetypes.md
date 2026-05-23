# Content Archetypes

Each archetype = a reusable visual format. A weekly batch should cover all four. Each archetype has 1–N variants; variants differ in palette, audio, identity-prompt wording, and difficulty.

## Archetype 1 — Bouncing Spheres (primary)

**Engine**: Unity DOTS + Havok Physics
**Why**: deterministic collisions → frame-accurate audio triggers. Assets port directly to the phase-2 mobile game.

**Variants**:
| Variant | Mechanic | Identity hook |
|---|---|---|
| B1 — Color escalation | Ball grows on every bounce | "Pick a color — yours is the one that survives" |
| B2 — Maze escape | Ball navigates obstacles under time limit | "Comment the second you thought it would fail" |
| B3 — Polyrhythm | Each bounce plays one note of a melody | "Guess the song. Most miss it." |
| B4 — IP capture | Pokéball-style mechanic with spirals | "Your starter Pokémon decides your color" |
| B5 — Multiball | Multiple balls compete; one wins | "Your birth year picks your ball" |

**Hook formulas**:
- "Only 2% can follow the [color] ball till the end."
- "Comment when you lost track."
- "[Identity] = your ball color."

## Archetype 2 — Identity Grids (fast prototyping)

**Engine**: Python NumPy + Pillow + imageio
**Why**: cheap to iterate, no GPU, perfect for color/text-heavy formats.

**Variants**:
| Variant | Mechanic | Identity hook |
|---|---|---|
| G1 — Color cells | Grid of cells, each color animates differently | "Pick your color — what does it say about you?" |
| G2 — Zodiac wheel | 12 segments rotating, one settles | "Your sign decides which ball wins" |
| G3 — Birth year grid | 100-cell grid mapped to years, one highlights | "What year was your worst? Comment." |
| G4 — Initial color | Each letter has a color, one fills the screen | "Comment the color of your initial" |
| G5 — MBTI quadrants | 16 cells, ball settles on one | "Your MBTI = your animation" |

**Hook formulas**:
- "Comment the color of your [initial / sign / year]."
- "Most people pick wrong."

## Archetype 3 — Failable Challenges

**Engine**: Unity (precision) or Python (simpler patterns)
**Why**: forces a comment ("I lost it at 0:07") even when the viewer disagrees with the framing.

**Variants**:
| Variant | Mechanic | Identity hook |
|---|---|---|
| F1 — Track the ball | One ball among many; viewer must track | "99% lose it by 10 seconds" |
| F2 — Count the flashes | Flashes occur, viewer counts | "Comment your number. The real answer is in the pinned." |
| F3 — Odd one out | All balls bounce, one moves differently | "Find the imposter. Only 1 in 100 sees it." |
| F4 — Speed test | Ball accelerates; can you watch without blinking | "How long did you make it?" |

## Archetype 4 — Hyper-textural Loops (2026 trend)

**Engine**: HunyuanVideo / Veo3 / Sora prompt packs (`engines/ai-video/`)
**Why**: stochastic models excel at organic textures (gummy, jelly, wax, slime) where physics determinism doesn't matter.

**Variants**:
| Variant | Texture | Identity hook |
|---|---|---|
| T1 — Jelly bounce | Translucent gummy sphere bounces on glass | "Comment what color jelly feels like to you" |
| T2 — Wax melt | Wax pours and re-solidifies into a shape | "Your zodiac chooses the shape" |
| T3 — Soap bubble morph | Bubbles merge, change color, pop | "Pick the one that holds longest" |
| T4 — Liquid metal | Mercury-like flow forming geometric patterns | "What does this remind you of? Comment." |

**Prompt template** (HunyuanVideo / Veo3):
> "Slow-motion close-up of a [texture] [object] in a [color] gradient environment, soft global illumination, vertical 9:16 framing, looping motion, ASMR aesthetic, no text, no people, 12 seconds."

## CTA library (engine-agnostic)

Pinned comment + caption mix-and-match:
- "Comment the color of your initial 👇"
- "What year was your worst? Comment it."
- "Did you catch the imposter? Comment your timestamp."
- "Red or Blue — pick one."
- "Your sign / your ball — what'd you get?"
- "How long did you last?"
- "Most people get this wrong. What did you see?"

## Difficulty knob

Every archetype has a `difficulty` parameter (1–5) controlling:
- Visual density (ball count, grid resolution)
- Speed (motion velocity, animation rate)
- Audio complexity (single note vs. polyrhythm)

Start at difficulty 2 for new variants; escalate the variants that win.

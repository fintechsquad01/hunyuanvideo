# Content Archetypes

Each archetype = a reusable visual format with config-driven variants. The same engine produces an entire collection of videos by swapping labels, palettes, and audio. The format becomes the brand.

## Archetype 1 — Plinko Identity Race (FLAGSHIP TEMPLATE)

**Engine**: `marble_drop` (Python NumPy + Pillow; production version on Unity)
**Why**: dominant viral format on TikTok/Reels right now (#chooseyourcolor / #chooseyourracer). Every variant is built from the same engine — only `labels` and `palette` change. This is the **template that powers an entire content collection**.

**The template formula**: *"Your [identity dimension] is your racer."*

| Variant | Identity dimension | Sample labels | When to ship |
|---|---|---|---|
| P-MONTH | Birth month | JAN, FEB, …, DEC | Evergreen baseline |
| P-ZODIAC | Astrology sign | ARI, TAU, GEM, …, PIS | Evergreen; spikes near new year / Mercury retrograde |
| P-WORLDCUP | National team | BRA, ARG, FRA, …, USA | Around World Cup, Euros, Olympics |
| P-STOCKS | Tickers | AAPL, MSFT, NVDA, …, AVGO | Earnings weeks, market events |
| P-CELEB | Names | TAYLOR, DRAKE, BAD BUNNY, … | Pop culture moments (Grammy, album drops, beef) |
| P-MBTI | Personality | INTJ, INFP, ENTP, … | Evergreen; high cross-share on Reddit/Twitter |
| P-CRYPTO | Coins | BTC, ETH, SOL, … | Bull-market spikes |
| P-DECADE | Birth decade | 60s, 70s, 80s, 90s, 00s, 10s | Evergreen nostalgia |
| P-CONTINENT | Region | NA, SA, EU, AF, AS, OC | Geo-targeted ad reach |
| P-INITIAL | First letter | A, B, C, …, Z (26-marble chaos) | Evergreen; needs smaller marbles + 24 rows |

**Configs**: `configs/marble_drop_*.json`. Copy any existing config, swap `labels` + `palette`, you have a new variant in 60 seconds.

**Hook formulas**:
- "Your [X] is your racer."
- "Pick your [X]."
- "Only one [X] wins."

**CTAs**:
- "Comment if yours won."
- "Did your [team / sign / bag] win?"
- "Tell me your [X] — I'll do a custom version."

**Cadence**: rotate variants daily. Same engine, fresh identity dimension. The repetition is the brand recognition.

---

## Archetype 2 — Ring Expansion (musical collisions)

**Engine**: `ring_expansion` (Python NumPy + Pillow + collision-driven sine synthesis)
**Why**: each wall collision plays one note of a melody — the song *emerges from the physics*. Highest audio retention signal in the niche. Variants ship by swapping the melody and palette.

**Variants**:
| Variant | Melody | Hook |
|---|---|---|
| R-TWINKLE | Twinkle Twinkle (PD) | "Guess the melody." |
| R-ODE | Ode to Joy (PD) | "When the song completes, the ring breaks." |
| R-MINOR | Minor arpeggio loop | "Why does this feel sad?" |
| R-CUSTOM | Owned/commissioned melody | Brand-deal-safe; funnel-driving |

**Engine knobs** (per config):
- `ball_speed`, `speed_gain_per_bounce` — pacing acceleration
- `ring_radius_start_pct` / `end_pct` — how much the arena grows over the clip
- `melody` — key in `engines/audio_reactive/collision_audio.py::MELODIES`

**Future extensions** (not yet built):
- Multi-ball spawn on milestone bounce count
- Ring segment destruction (each bounce removes one arc; ball escapes through the gap)
- Vocal-synth melody (samples instead of sine waves) — for owned-track variants

---

## Archetype 3 — Bouncing Spheres (ambient loops)

**Engine**: `bouncing_spheres` (NumPy reference) → Unity DOTS for production
**Why**: pure ambient loops — the baseline ZenShapes signature. Use when you don't have an identity dimension and just want algorithm-friendly motion to fill posting cadence between identity-race batches.

**Variants**:
| Variant | Mechanic | Identity hook |
|---|---|---|
| B1 — Color escalation | Ball grows on every bounce | "Pick a color — yours is the one that survives" |
| B2 — Maze escape | Ball navigates obstacles under time limit | "Comment the second you thought it would fail" |
| B3 — IP capture | Pokéball-style mechanic with spirals | "Your starter Pokémon decides your color" |
| B4 — Multiball | Multiple balls compete; one wins | "Your birth year picks your ball" |

---

## Archetype 4 — Hyper-textural Loops (2026 trend)

**Engine**: HunyuanVideo / Veo3 / Sora prompt packs (`engines/ai_video/`)
**Why**: stochastic models excel at organic textures (gummy, jelly, wax, slime) where physics determinism doesn't matter.

**Variants**:
| Variant | Texture | Identity hook |
|---|---|---|
| T1 — Jelly bounce | Translucent gummy sphere bounces on glass | "Comment what color jelly feels like to you" |
| T2 — Wax melt | Wax pours and re-solidifies into a shape | "Your zodiac chooses the shape" |
| T3 — Soap bubble morph | Bubbles merge, change color, pop | "Pick the one that holds longest" |
| T4 — Liquid metal | Mercury-like flow forming geometric patterns | "What does this remind you of?" |

**Prompt template**:
> "Slow-motion close-up of a [texture] [object] in a [color] gradient environment, soft global illumination, vertical 9:16 framing, looping motion, ASMR aesthetic, no text, no people, 12 seconds."

---

## CTA library (engine-agnostic)

Pinned comment + caption mix-and-match:
- "Comment the color of your initial."
- "What year was your worst? Comment it."
- "Did you catch the imposter? Comment your timestamp."
- "Red or Blue — pick one."
- "Your sign / your ball — what'd you get?"
- "How long did you last?"
- "Most people get this wrong. What did you see?"

## Difficulty knob

Every archetype has a `difficulty`-equivalent parameter (peg density, ball speed, ring growth rate) controlling pacing. Start at low difficulty for new variants; escalate the ones that win.

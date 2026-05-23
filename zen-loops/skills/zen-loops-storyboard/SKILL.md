---
name: zen-loops-storyboard
description: Generate a complete shot-by-shot storyboard for a zen-loops satisfying-simulation video — bouncing spheres, ring expansion, Plinko identity races, "guess the song" reveals, hyper-textural loops. Use when the user describes a satisfying / ASMR / identity-pick / oddly-satisfying content idea ("Pick your birth month", "Guess the song", "Watch the red ball", "Jelly squeeze"). Outputs a markdown storyboard.md with hook, beats, shot list, identity hooks, audio sync, and engine handoff. NOT for football data viz (use pitch-predict-storyboard), NOT for static carousel posts, NOT for actually rendering the video.
user-invocable: true
---

# zen-loops-storyboard

Storyboard a satisfying-simulation video for the zen-loops brand before any render-engine code.

## When to invoke

- User describes a satisfying / ASMR / identity-pick content idea
- Brand match: "Identity > Zen" thesis — every video forces a comment about the viewer
- Before writing any engine code for a new piece
- Re-storyboarding an existing format with a new theme (birth months → zodiac → countries)

## Core thesis (read this first)

zen-loops is built on **"Identity > Zen"**: satisfying motion is the floor, not the ceiling. The viral multiplier is making the viewer comment about *themselves*. Every storyboard must answer: *what does the viewer get to say about themselves?*

Three-hook system applied to every piece:
1. **Visual hook (0–3s)** — motion already in flight, high contrast, no dead frames
2. **Cognitive hook** — identity signal: birth month, zodiac, MBTI, initial color, country, year
3. **Interaction hook** — failable challenge ("99% can't catch the red ball") or comment-bait

## Inputs required

```yaml
idea: string                    # "Pick your birth month marble race"
archetype: enum (optional)      # see references/archetypes.md
duration_seconds: int           # default 12-15
identity_dimension: string      # birth_month | zodiac | initial | mbti | country | year | none
melody: string (optional)       # twinkle | ode_to_joy | fur_elise | pachelbel | greensleeves | original
```

## Workflow

1. **Validate brand fit** — reject if the idea is football-data-led (route to `pitch-predict-storyboard`) or carousel-static (route to `carousel-storyboard`).

2. **Identify the archetype** — one of the 7 locked archetypes in `references/archetypes.md`.

3. **Pick the identity dimension** — if not specified, propose 2–3 options ranked by viral potential for the target audience. Birth month is the safest baseline; zodiac peaks around year transitions and Mercury retrograde; initials are evergreen.

4. **Write 3 hook variants** — each ≤ 8 words. One identity-led ("YOUR [X] IS YOUR RACER"), one failable ("99% CAN'T CATCH THE RED ONE"), one melody-tease ("GUESS THE SONG"). Tag the recommended one.

5. **Build the 5-step structure** (default 14s):
   - Hook · 0:00 → 0:01.5 · text overlay + already-in-motion frame
   - Build · 0:01.5 → 0:06 · speed / density / count rises
   - Peak · 0:06 → 0:10 · max chaos → mini resolution
   - Loop · 0:10 → 0:13 · last frame ≈ first frame, seamless restart
   - CTA · 0:13 → 0:15 · pinned-comment question + caption mirror

6. **Detail each shot** — visual, motion, timing, text overlays, identity element placement, audio sync points.

7. **Audio map** — for ring-expansion specifically, name the melody and per-collision note progression. For others, ambient bed + collision SFX. Never copyrighted music.

8. **Reference points** — name specific competitor patterns this borrows from (@marbleraceerk, @thebattleofcolors, @musicalmelody.tt) and what we are NOT copying.

9. **Engine handoff** — name the engine and config schema fields (see `references/engine-handoff.md`).

10. **Success metrics** — retention at 5s, comment-to-view (the most-weighted signal for this brand — target ≥0.5%, stretch ≥1%), saves, shares.

## Output schema

Same markdown structure as pitch-predict-storyboard. Output path: `zen-loops/storyboards/<slug>.md`.

## Kill criteria

- Idea is football-data-led → route to `pitch-predict-storyboard`
- Idea uses copyrighted melody (Megalovania, Lavender Town, Pokémon themes) AND would drive funnel → reject; suggest PD substitute
- Idea has no identity hook and no failable challenge → flag as "ambient filler" (still buildable but lower viral ceiling)
- Engine for the proposed archetype doesn't exist yet → output gap, suggest building

## Routes to

After storyboarding, hand off to:
- `marble_drop` engine — for Plinko identity races
- `marble_drop_pro` — for production-grade Plinko with FX
- `ring_expansion` — for guess-the-song formats
- `bouncing_spheres` — for ambient loops
- `cross-platform-distributor` (growth-stack) — for per-platform caption + schedule after render

## Files in this skill

- `SKILL.md` — this file
- `references/archetypes.md` — 7 zen-loops archetypes
- `references/identity-dimensions.md` — which identity hook for which audience
- `references/melodies.md` — PD melody library + note sequences
- `references/engine-handoff.md` — engine mapping per archetype

## How to install

```bash
ln -sfn "$PWD/zen-loops/skills/zen-loops-storyboard" \
        "$HOME/.claude/skills/zen-loops-storyboard"
```

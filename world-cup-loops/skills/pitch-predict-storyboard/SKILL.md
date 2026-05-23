---
name: pitch-predict-storyboard
description: Generate a complete shot-by-shot storyboard for a pitch.predict football data-viz video, ready to hand to a render engine. Use when the user describes a content idea ("Curaçao vs Germany gap", "Norway's Elo climb", "Group D predictor", "Mbappé vs Haaland goal race") and needs a structured plan before any rendering. Outputs a markdown storyboard.md with hook, beats, shot list, type stack, color palette, audio map, reference content, and engine handoff. NOT for non-football pitch.predict content (use a different skill or generic-storyboard); NOT for static infographics or carousel posts (use carousel-storyboard); NOT for actually rendering the video (use the render engine specified in the storyboard output).
user-invocable: true
---

# pitch-predict-storyboard

Storyboard a football data-visualization video for the pitch.predict brand before you write a single line of engine code.

## When to invoke this skill

- User describes a content idea: "Make a [team / matchup / stat] video"
- User mentions a fixture, group, qualifier story, or odds movement
- Before any render-engine work begins on a new piece
- When pivoting an existing piece to a new format

## When NOT to invoke

- Engine debugging or render iteration (the storyboard is already done)
- Brand-system / design-token questions (see `pitch-predict-design`)
- Cross-platform caption writing (see `platform-native-post-writer` from growth-stack)
- Other pitch.predict brands (this skill is football-only, World Cup + leagues)

## Inputs required

```yaml
idea: string                    # the seed: "Curaçao vs Germany gap"
archetype: enum (optional)      # see references/archetypes.md - skill picks if unset
duration_seconds: int           # default 14
data_inputs:                    # what data the storyboard references
  - elo_rating: float[]
  - polymarket_implied_pct: float[]
  - country_codes: string[]
  - match_result: dict
references_optional:            # specific competitors / videos to borrow from
  - url or handle
```

## Workflow

1. **Validate the idea fits pitch.predict** — reject if the brand match is wrong (e.g., reject "satisfying ASMR loop" — that belongs to zen-loops). Surface the rejection with one sentence; don't pretend.

2. **Identify the archetype** — match the idea to one of the 10 locked archetypes in `references/archetypes.md`. If two fit, pick the higher-energy one. Output the archetype id and one-line rationale.

3. **Write 3 hook variants** — each ≤ 8 words, ALL CAPS, designed to stop a 7pm scroll. One curiosity-gap variant ("WHAT IF…"), one shock-stat variant ("#90 IN THE WORLD"), one identity variant ("YOUR COUNTRY VS THE WORLD"). Tag the recommended one with `★`.

4. **Build the 5-beat structure** at the requested duration. Default at 14s:
   - Hook · 0:00 → 0:02 · 60 frames (scroll-stopper)
   - Build · 0:02 → 0:06 · 120 frames (context / tension)
   - Climb · 0:06 → 0:10 · 120 frames (rising action)
   - Peak · 0:10 → 0:12 · 60 frames (the single payoff moment)
   - CTA / Loop · 0:12 → 0:14 · 60 frames (comment-prompt + loop seam)

5. **Detail each shot** with:
   - Visual description (centered text? split screen? marble race?)
   - Camera move (still / zoom-in / slow-pan / cut)
   - Frame count + start frame
   - Text overlays (exact strings)
   - Type stack per element (per `references/brand-voice.md`)
   - Color treatment (which palette element wins this beat)

6. **Build the audio map** — beat-by-beat instrument / hit / drop. Reference owned/PD melody (`twinkle`, `ode_to_joy`, `fur_elise`, `pachelbel`, etc.) or specify "needs Suno: [prompt]". Never specify copyrighted music.

7. **Reference points** — name 2–3 specific viral videos / accounts whose pattern this storyboard borrows from. Avoid generic "@marble_race_football" — be specific: "ESPN Did-You-Know format, single-stat reveal at 0:08."

8. **Compliance check** — sweep for platform-risky language ("bet", "odds", "wager") and replace per `references/brand-voice.md`. Sweep for IP risks (FIFA marks, team crests, player likenesses) and reject those elements.

9. **Engine handoff** — name the render engine per `references/engine-handoff.md` (custom Python physics, D3+Playwright charts, or AI-video for textures). Include the config schema fields the engine needs.

10. **Success metrics** — set 4 targets for this specific piece: retention at 5s, comment-to-view ratio, saves per 100 views, share rate. Tighter targets for stronger-story pieces.

## Output schema

A single markdown file at `world-cup-loops/storyboards/<slug>.md` following this structure:

```markdown
# Storyboard — "[verbatim viewer takeaway]"

**Piece**: [archetype id] — [one-line title]
**Audience hook**: [what the viewer learns in <duration>s]
**Length**: [N seconds]
**Resolution**: 1080×1920 (9:16)
**Engine**: [custom_python | d3_playwright | ai_video]
**Posting**: [IG Reels + TikTok + YT Shorts on launch / per-match / etc.]

## The premise
[2–3 sentences: what the viewer learns, the one moment they remember]

## Reference points
- [Specific viral pattern this borrows from #1]
- [#2]
- [#3 — what we are NOT copying]

## Shot list

### SHOT 1 — [name] · [time range] · [frame count]
**Visual**: [what's on screen]
**Camera move**: [movement type + duration]
**Text overlays**:
- [string in display font]
- [string in body font]
**Type stack**: [explicit font + size per element]
**Color treatment**: [palette elements active this beat]
**Audio**: [bed / hit / drop on this beat]

### SHOT 2 — ...
... (one per beat)

## Audio map (composite)
| Time | Layer | Sound |
|---|---|---|

## Engine handoff
Engine: [name]
Config fields needed:
- field_a: type
- field_b: type
Data inputs:
- [data source + query]

## Success metrics
- Retention at 5s: [target]
- Comment-to-view: [target]
- Saves per 100: [target]
- Share rate: [target]

## What we are NOT doing
- [explicit anti-pattern 1]
- [#2]
- [#3]
```

## Kill criteria

- Idea doesn't match pitch.predict brand (e.g., wrong sport, wrong tone, gambling-heavy). Output a one-line rejection, name a sibling skill if one fits.
- Required data fields are unavailable (e.g., asking for steam moves when no odds history is in the DB yet). Output the data gap and stop.
- Brand-voice contract would be violated and the user insists. Surface the conflict, don't ship the storyboard.

## Routes to

After the storyboard is written, hand off to:
- **Custom Python (Pillow)** for physics pieces (Plinko, Ring expansion, multi-marble races)
- **D3 + Playwright** for chart-style pieces (Elo trajectory, gap reveal, league table race, steam move, top scorer race)
- **AI video (Fal.ai / Higgsfield)** for cinematic hero shots, hopium loops, stadium reveals
- **`cross-platform-distributor`** (growth-stack) for per-platform caption + schedule once the render is complete

## Files in this skill

- `SKILL.md` — this file
- `references/archetypes.md` — the 10 locked content archetypes with patterns
- `references/brand-voice.md` — voice + tone + IP-safe language rules
- `references/engine-handoff.md` — which render engine per archetype
- `references/examples/curacao_gap_reveal.md` — fully-worked example storyboard

## How to install (one-time)

From the repo root:

```bash
ln -sfn "$PWD/world-cup-loops/skills/pitch-predict-storyboard" \
        "$HOME/.claude/skills/pitch-predict-storyboard"
```

After install, invoke with `/pitch-predict-storyboard` in Claude Code chat, or it auto-routes when you describe a content idea matching the brand.

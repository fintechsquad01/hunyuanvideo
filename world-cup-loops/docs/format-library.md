# Format Library — Football Archetypes

Each format maps onto an engine from `../zen-loops/engines/` with football-specific data and styling.

---

## WC1 — Bracket Plinko (FLAGSHIP)

**Engine**: `marble_drop` (extended for tournament rounds)
**Mechanic**: 32 marbles (knockout teams) drop through a Plinko board. Survivors visualized in subsequent rounds.

**Variants**:
- **WC1.a — Full bracket** (32 → 1): 60s long-form for YouTube Shorts max length; quick-cut on IG
- **WC1.b — Round of 16 Plinko**: 16 marbles, one wins → "predicted quarterfinalist"
- **WC1.c — Quarterfinals Plinko**: 8 marbles, top 4 reveal
- **WC1.d — Semifinals**: 4 marbles
- **WC1.e — Final**: 2 marbles racing to a goal line

**Identity overlays**:
- Country flag color = marble color
- 3-letter country code = label (BRA, ARG, ESP, FRA, etc.)

**Hooks**:
- "Pick your country."
- "Brackets play themselves."
- "Polymarket says [X]. Plinko says…"

**CTAs**:
- "Comment your pick before kickoff."
- "Did your team survive?"
- "Tag a friend who's wrong."

---

## WC2 — Group Predictor

**Engine**: `marble_drop` (single-group mini-bracket)
**Mechanic**: 4 marbles drop, top 2 advance with a visual highlight.

**Variants**:
- One per group (A through L) — 12 standalone videos
- Updated after each group-stage matchday with new positions

**Identity overlays**:
- Each marble = one team in the group
- Show current points / GD overlay

**Hooks**:
- "Group [X] — who's getting out alive?"
- "Group of Death simulator"
- "[Star Player]'s group: can they escape?"

---

## WC3 — Per-Match Score Race

**Engine**: NEW — `engines/score_race.py` (linear race, not Plinko)
**Mechanic**: Two marbles (home/away team flag colors) race horizontally across the screen. Each goal scored = an instant boost forward. Final positions match the actual score.

**Variants**:
- **WC3.a — Pre-match preview**: marbles race based on Polymarket odds; "if odds were true, this is the score"
- **WC3.b — Post-match recap**: marbles race based on actual goals, real-time per goal
- **WC3.c — "What if" reversal**: actual match played backwards — viewers guess the final score

**Why this works**: 104 matches × 3 angles = 312 potential posts. Massive volume during tournament.

---

## WC4 — Top Scorer Race

**Engine**: `marble_drop` variant or new linear-race engine
**Mechanic**: Each marble = a goalscorer. Position = goals scored. Updates daily during tournament.

**Identity overlays**:
- Player name + country flag colors
- Goal count

**Hooks**:
- "Top scorer race — Day [N]"
- "Golden Boot battle"
- "Who's scoring more by Day 14?"

**CTAs**:
- "Bet on the Golden Boot." (where platform allows)
- "Who do you think wins it?"

---

## WC5 — Polymarket Live Odds Visualization

**Engine**: `marble_drop` with marble-size proportional to win %
**Mechanic**: 32 (or 48) marbles whose **sizes are proportional to current win probability**. Big = favorite. Small = longshot.

**Update cadence**: Weekly pre-tournament, daily during.

**Hooks**:
- "Polymarket's bracket: what the money says."
- "Smart money vs. your money."

**Risk**: gambling-adjacent language. Reframe as "prediction market" / "fan poll" / "fan consensus".

---

## WC6 — "Will X Advance?" Plinko

**Engine**: `marble_drop` subset
**Mechanic**: One team's marble drops through a path showing potential bracket scenarios.

**Reactive**: Use this when a team becomes a viral storyline. e.g., "Will Argentina defend the title?" / "Can Saudi Arabia shock the world again?"

---

## WC7 — Country-Food Marble Race

**Engine**: `marble_drop` with cultural labels
**Mechanic**: Each marble shows a national dish emoji or short text (Brazil = 🇧🇷 açaí, Italy = 🍕, Japan = 🍣, England = 🫖, etc.)

**Why this works**: Lower-stakes, higher-share content. Bridges football fans + food fans + memes. Cultural curiosity beats team loyalty for the algorithmic-spread audience.

---

## WC8 — Hopium Loop ("Your Country's Path to the Final")

**Engine**: `ring_expansion` variant
**Mechanic**: One ball bounces in a growing ring; each wall hit advances through bracket rounds with country flag visible.

**Hooks**:
- "Your country lifting the trophy."
- "If Spain wins it all, this is how it looks."

**Why this works**: emotional resonance. Football fans drink hopium daily. This format bottles it.

---

## Production matrix — which formats to ship first

| Format | Build cost | First-week priority | During-tournament priority |
|---|---|---|---|
| WC1.a (Full bracket) | LOW (reuses marble_drop) | YES — anchor video, day 1 | YES — re-render after each round |
| WC2 (Group predictor) | LOW | YES — produce 12 variants | refresh after each matchday |
| WC3 (Per-match) | MED — new engine | NO — defer to tournament | YES — primary content |
| WC4 (Top scorer) | LOW-MED | NO | YES — daily during tournament |
| WC5 (Polymarket viz) | LOW | YES — differentiator content | refresh weekly |
| WC6 (Will X advance) | LOW | OPPORTUNISTIC | OPPORTUNISTIC |
| WC7 (Food race) | LOW | YES — week 2 cross-pollinate | weekly |
| WC8 (Hopium loop) | LOW | YES — one per top-8 country | reactive to results |

## Visual / audio guidelines

- **Palette**: country flag colors override default palettes. Maintain high contrast for label legibility.
- **Audio**: stadium ambient bed under engine-driven SFX. No copyrighted player chants. PD anthem fragments OK for flagship pieces.
- **Brand chrome**: small bracket icon in corner; bracket round indicator ("R16 / QF / SF / FINAL").
- **Always show**: country 3-letter code + flag color. Never use FIFA marks, official team crests, or player photos in static brand chrome.

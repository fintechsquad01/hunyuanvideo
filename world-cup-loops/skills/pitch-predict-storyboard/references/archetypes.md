# Archetypes — pitch.predict football data viz

10 locked content archetypes. The skill picks the best fit for a given idea. Each entry: what it is, when to pick it, beat skeleton, primary engine.

---

## A1 — Bracket Plinko (the flagship)

**What**: Marbles drop through Plinko pegs on a stadium-green field, country-flag-colored, 3-letter codes labeled. First to bottom wins.
**Pick when**: tournament round, group preview, "who advances" framing, all-48 ranking.
**Beat skeleton (14s)**:
- Hook · 2s · marble field already in motion, hook overlay
- Build · 4s · marbles cascade through pegs
- Climb · 4s · counter ticks down "16/16 racing → 4/16"
- Peak · 2s · final marble crosses finish, country glow
- CTA · 2s · "PICK YOUR COUNTRY"
**Engine**: custom_python (marble_drop_pro)
**Owned audio**: collision-driven melody, PD source (ode_to_joy or pachelbel)
**Anti-patterns**: don't show all 48 in one race (eye can't track); cap at 8–16.

## A2 — Group Predictor (mini-bracket)

**What**: Single group of 4 teams in a tight Plinko, top 2 highlighted at end.
**Pick when**: group-stage preview, "group of death" angle, per-group daily content.
**Beat skeleton (12s)**:
- Hook · 2s · "GROUP D — WHO ADVANCES?"
- Build · 4s · 4 marbles drop
- Climb · 3s · two finish, two struggle
- Peak · 2s · top-2 advance glow (gold), bottom-2 dim (red)
- CTA · 1s · "PICK YOUR TWO"
**Engine**: custom_python (marble_drop_pro with 4 teams)

## A3 — Per-Match Score Race

**What**: Two team marbles race horizontally toward a goal line. Each real goal scored = an instant boost forward. Final positions match actual score.
**Pick when**: post-match recap; pre-match preview based on Polymarket odds.
**Beat skeleton (16s)**:
- Hook · 2s · "BRA 2-1 ARG · 78'"
- Build · 6s · goals appear at minute marks
- Climb · 4s · second-half momentum visualization
- Peak · 2s · final whistle freeze, scoreline reveal
- CTA · 2s · "GOAL OF THE MATCH?"
**Engine**: d3_playwright (timeline composition)

## A4 — Top Scorer Race

**What**: Each goalscorer = a marble climbing a vertical y-axis = goals. Updates daily during tournament.
**Pick when**: daily during tournament; weekly during regular season.
**Beat skeleton (15s)**:
- Hook · 2s · "TOP SCORER RACE · DAY 14"
- Build · 5s · marbles populate at current positions
- Climb · 5s · animate goals scored that day
- Peak · 2s · leader glow + name reveal
- CTA · 1s · "WHO WINS THE GOLDEN BOOT?"
**Engine**: d3_playwright (animated vertical bar chart)

## A5 — Polymarket Odds Visualization

**What**: 32 (or 48) marbles whose **sizes are proportional to current win probability**. Big = favorite. Small = longshot. Counter at top showing total volume traded ("$1.1B").
**Pick when**: weekly pre-tournament; daily during; differentiator content.
**Beat skeleton (12s)**:
- Hook · 2s · "WHAT $1.1B SAYS"
- Build · 4s · marbles materialize at proportional sizes
- Climb · 3s · 24h delta arrows appear (rising/falling)
- Peak · 2s · top-3 favorites named with %
- CTA · 1s · "PICK YOUR EDGE"
**Engine**: d3_playwright
**Language compliance**: never "odds"; always "prediction market" or "fan consensus."

## A6 — Will X Advance? (single-team Plinko)

**What**: One team's marble drops through paths showing possible bracket scenarios. Each path ends at a different round.
**Pick when**: reactive — when a team becomes a viral storyline.
**Beat skeleton (12s)**:
- Hook · 2s · "WILL [TEAM] MAKE THE FINAL?"
- Build · 4s · marble enters the path
- Climb · 4s · branches show R16/QF/SF/Final possibilities
- Peak · 2s · most-likely outcome glow
- CTA · 0s · (single hook + CTA can merge here)
**Engine**: custom_python

## A7 — Country Food / Cultural Race

**What**: Like Plinko but each marble has a national dish emoji (Brazil 🇧🇷=açaí, Italy=🍕, Japan=🍣). Lower-stakes, higher-share cross-pollination content.
**Pick when**: weekly cultural angle; bridge to non-football audience.
**Beat skeleton (12s)**:
- Hook · 2s · "WHICH COUNTRY EATS BEST AT THE WORLD CUP?"
- Build · 4s · food-emoji marbles bounce
- Climb · 4s · winning food rises
- Peak · 2s · winner reveal with full dish name
- CTA · 0s · merge "COMMENT YOUR COUNTRY'S DISH"
**Engine**: custom_python (Plinko with emoji-rendered marbles)
**Note**: this is the ONE archetype where emoji are allowed in chrome.

## A8 — Hopium Loop

**What**: A single country's marble bounces in a growing golden ring. Each wall hit advances through bracket rounds (R32 → R16 → QF → SF → FINAL). At the end: "[COUNTRY] CAMPEONES" reveal.
**Pick when**: emotional resonance for fan-favorite teams; reactive after big wins; pre-tournament hype.
**Beat skeleton (15s)**:
- Hook · 2s · "IF [TEAM] WINS IT ALL"
- Build · 5s · ring expands, marble bounces, rounds tick
- Climb · 5s · acceleration through later rounds
- Peak · 2s · gold glow on final wall hit
- CTA · 1s · "[TEAM] CAMPEONES" reveal
**Engine**: custom_python (ring_expansion)

## A9 — Elo Trajectory (storytelling)

**What**: Vertical line chart, X = years, Y = Elo rating. Line draws progressively. Final reveal: "FROM #44 TO #14" giant Anton.
**Pick when**: comeback stories (Norway since 1998), first-time qualifiers (Curaçao, Cape Verde), declining-giant narratives (Germany).
**Beat skeleton (14s)**:
- Hook · 2s · "[COUNTRY] — THE CLIMB"
- Build · 4s · line begins drawing from earliest year
- Climb · 5s · accelerates through recent years, major events annotated (manager changes, qualifying matches)
- Peak · 2s · current rank reveal in giant Anton
- CTA · 1s · "TAG A [COUNTRY] FAN"
**Engine**: d3_playwright

## A10 — Gap Reveal (David vs Goliath)

**What**: Split screen. Two countries' Elos count up in sync. Underdog locks; favorite continues. Center reveals "THE GAP" with giant number.
**Pick when**: dramatic mismatch matchups (Curaçao vs Germany, Cape Verde vs France, Saudi Arabia vs Argentina rematch).
**Beat skeleton (14s)**:
- Hook · 2s · "WHAT IF…" curiosity gap
- Build · 4s · underdog identity reveal (country name, flag, rank)
- Climb · 5s · counters race up; underdog locks; favorite continues; gap reveal
- Peak · 2s · "THE GAP: +487 · BIGGEST IN WC HISTORY"
- CTA · 1s · "BACK [UNDERDOG]"
**Engine**: d3_playwright
**Example storyboard**: see `examples/curacao_gap_reveal.md`

---

## Picking the archetype — quick decision tree

```
Is this a TOURNAMENT BRACKET storyline? → A1 (Bracket Plinko) or A6 (Will X Advance)
Is this a SINGLE GROUP storyline? → A2 (Group Predictor)
Is this a SPECIFIC MATCH (real or upcoming)? → A3 (Per-Match Score Race)
Is this about PLAYERS / GOALSCORERS? → A4 (Top Scorer Race)
Is this about ODDS / PREDICTION MARKETS? → A5 (Polymarket Viz)
Is this CULTURAL / CROSS-AUDIENCE? → A7 (Country Food)
Is this EMOTIONAL HOPIUM for one team? → A8 (Hopium Loop)
Is this a CLIMB / DECLINE STORYLINE? → A9 (Elo Trajectory)
Is this a MISMATCH / UNDERDOG MOMENT? → A10 (Gap Reveal)
None of the above? → Reject the idea or surface that we need a new archetype.
```

Two archetypes match? Pick the one with higher emotional payload (Hopium > Bracket, Gap Reveal > Plinko).

# PIECE_LOCK — Format contract for pitch.predict pieces

**Date locked**: 2026-05-23
**Status**: Mandatory for every piece going forward. Any future session reads this first.

---

## The format we DO make

**Physics-simulated marble races where teams are the marbles.** Built in real Python physics (no charts, no D3 line graphs). Reference accounts: [@teamballvs](https://www.instagram.com/teamballvs), [@marbleraceerk](https://www.tiktok.com/@marbleraceerk), [@phantomreacts4](https://www.tiktok.com/@phantomreacts4), [@invisibledrax2](https://www.tiktok.com/@invisibledrax2), the Football Clubs Marble Race YouTube series.

### Mandatory elements

1. **Marbles = teams.** Each marble is a real country/club with the team's flag color and 3-letter code.
2. **Real physics.** Marbles bounce, collide, get knocked around. Built with the `wc_engines/battle_royale.py` / `wc_engines/marble_drop_pro.py` engines (Python + Pillow + collision math).
3. **Identity hook.** Viewer can point to ONE marble and say "that's my team." Most viewers should be looking for their country/club.
4. **Failable.** The viewer's team CAN lose. The whole point is uncertainty.
5. **Length 25–60s.** Not 15-second TikTok shorts — these are watched all the way through. Buildup matters.
6. **Single-run outcome.** We run the simulation ONCE per piece. Whoever wins, wins. We narrate the result; we don't predict it.

### What data does in this format

**Data informs the physics — it does NOT determine the outcome.** Specifically:
- **Marble size** = proportional to real metric (Elo, Polymarket implied probability, league points, whatever)
- **Marble mass** = proportional to size (heavier marbles dominate collisions)
- **Initial velocity** = proportional to strength (favorites are "punchier")
- **Outcome** = whatever the chaotic physics produces

So Spain's marble is the biggest and tends to dominate, but a smaller marble can still survive if it gets lucky positioning. **That's the actual honest answer of "what does the data say?"** — not a chart, but a simulation that gives the data physical form.

### What we do NOT make

- ❌ **Line charts with marble heads** (the trajectory race format — wc_risers, wc_continents, wc_fallers). Those are data journalism, not marble races. They don't go viral in this niche.
- ❌ **Static text-card explainers** (the Curaçao gap-reveal piece). Those are documentary explainers, not marble races.
- ❌ **Rigged outcomes** ("Curaçao wins because I set `winner_code=CUR`"). If we want Curaçao to win, we run the simulation 1,000 times and pick the runs where Curaçao actually won.
- ❌ **Aggregate confederation analysis.** Same data-journalism problem.
- ❌ **D3 / chart libraries as the primary visual.** D3 is for charts. Our brand is marble races. We use D3 only for chrome elements like odds badges.
- ❌ **Anything under 25 seconds.** Marble races need buildup to be satisfying.

### Engines (locked to this format)

| Engine | What it does | Use for |
|---|---|---|
| `wc_engines/battle_royale.py` | N marbles in a shrinking arena, last marble standing | "48 countries one survives", group-of-death simulations |
| `wc_engines/marble_drop_pro.py` (from zen-loops) | Plinko bracket, marbles drop through pegs to a finish line | Bracket tournaments, R32/R16/QF/SF/Final visualizations |
| `wc_engines/ring_expansion.py` (from zen-loops) | Single marble in a ring, bouncing audio melody | Hopium loops, "guess the song" formats — secondary |

Banned for primary visual:
- `pieces/wc_risers/` template (D3 line chart) — keep the source for reference but DO NOT build more like this
- `pieces/wc_continents/` template (same problem)
- `pieces/wc_fallers/` template (same problem)
- `pieces/curacao_gap/` template (static cards)

### Brand chrome (still applies)

- pitch.predict watermark top-left
- Round chip top-right (WC 2026 · BATTLE OF THE 48, etc.)
- Hook band top (Anton ALL CAPS)
- CTA band bottom (Anton ALL CAPS, FIFA gold #ffd400 text)
- Country marbles use flat-color flag fills (no FIFA marks, no team crests)
- Brand colors per `design/project/colors_and_type.css`

### Audio (still applies)

Synth-only, zero copyrighted material:
- Ambient pad bed
- Tick / thud per elimination
- Bigger thud on milestones (24 left, 12 left, 6, 3, 2)
- Final beat-drop chord on the winner reveal

### Caption / posting framing

- Hook: state the setup, not the result. ("48 COUNTRIES. ONE MARBLE SURVIVES. WE RAN IT ONCE.")
- Voice: FiveThirtyEight rigor × ESPN morning show — never breathless, never gambling-coded
- CTA: ask the viewer to identify ("DID YOUR COUNTRY MAKE IT?")
- Comment-bait: people will say "RUN IT AGAIN" / "MY COUNTRY WAS OUT FIRST" / "WHY IS GERMANY SO TINY"

---

## Build process for every new piece

1. Pick the angle from the format library (battle royale, bracket Plinko, group race, etc.)
2. Pull the data from `soccer_national_team_elo` (or whatever metric drives marble size)
3. Configure marble sizes / velocities from the data
4. Run the physics ONCE. Capture the outcome. **Do not re-run until you get the result you want.**
5. Caption the result honestly (favorite won? underdog survived? both happen)
6. Brand chrome, audio, render
7. Ship

If a piece would require rigging to make a story land, **don't build it.** Pick a different setup where the natural outcome IS the story.

---

## How to verify a future session is following this lock

Before any new piece ships:
1. Read this file
2. Confirm: is the engine in the "allowed" list?
3. Confirm: is the outcome decided by physics, not config?
4. Confirm: is the length ≥25 seconds?
5. Confirm: would @teamballvs / @marbleraceerk recognize this as their format?

If any answer is "no" → don't ship. Re-architect.

---

## Outputs to delete or archive (already-shipped pieces that violated this lock)

These can stay in git history but they are NOT references for future work:

- `pieces/curacao_gap/` (text cards, not marble race)
- `pieces/wc_risers/` (D3 line chart)
- `pieces/wc_continents/` (D3 line chart)
- `pieces/wc_fallers/` (D3 line chart)

The ONLY existing piece that fits this lock:
- `pieces/curacao_battle_royale/` — the engine and structure are right; only the rigging was wrong. The next piece (this lock's first deliverable) is the un-rigged version.

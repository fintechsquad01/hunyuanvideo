# world-cup-loops

A tournament-themed content account for **FIFA World Cup 2026** (June 11 – July 19, 2026, hosted by USA / Canada / Mexico).

Sister project to `zen-loops/`. Reuses the same physics engines but adds football-specific data, archetypes, and posting cadence tuned to a 5.5-week live tournament.

## Why this project exists

Three converging signals make this a high-leverage swing:

1. **Format fit is near-perfect** — our Plinko marble-race engine maps 1:1 onto the bracket structure (32 → 16 → 8 → 4 → 2 → 1).
2. **Audience is enormous and pre-engaged** — Polymarket has $1.1B traded on the winner market alone. The football social-media audience is the largest single fandom on the internet (~4B globally).
3. **Differentiator gap is real** — football TikTok is saturated with player edits, highlights, and AI-goal-recreation content. **Nobody is doing prediction-market-data + physics-simulation at scale.** That's our wedge.

## Positioning

Working name: `bracket-loops` or `kickoff-loops` (pick before account creation).

Brand promise: *"Brackets that play themselves."* Visual prediction markets that ride the World Cup hype, then pivot to other tournaments.

## Time-sensitive

**T-19 days to kickoff** (as of May 23, 2026). The pre-tournament hype window is closing. Posting must start this week to build account trust before the algorithm boost from World Cup hashtags kicks in.

## How this folder relates to zen-loops

Engines live in `../zen-loops/engines/` — we import them via sys.path. New configs and data live here. New archetypes specific to football (per-match score race, top-scorer race) go in `engines/` of this folder.

## Quick start

```bash
cd world-cup-loops
pip install -r ../zen-loops/requirements.txt
python generate_video.py --config configs/bracket_plinko_round_of_32.json
```

## Where to find what

- `docs/strategy.md` — positioning, posting cadence, monetization angles
- `docs/format-library.md` — football-specific archetype variants
- `docs/content-calendar.md` — pre-tournament + live-tournament + post-tournament cadence
- `docs/data-sources.md` — Polymarket, FIFA, etc.
- `data/teams.json` — 48 teams with codes, flag colors, FIFA rank
- `data/groups.json` — 12 groups (update with actual draw)
- `data/odds_snapshot.json` — Polymarket odds snapshot (manually updated)
- `configs/` — JSON recipes per video

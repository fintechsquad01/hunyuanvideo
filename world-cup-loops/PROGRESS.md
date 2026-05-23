# world-cup-loops — Progress & Memory

Living document. Updated at the end of each working session.

## Current state (snapshot)

**Branch**: `claude/zenshapes-strategy-analysis-xZzbe` on `fintechsquad01/hunyuanvideo`
**Status**: scaffolded. Three sample renders working. Account not yet created.
**Days to kickoff**: 19 (today = 2026-05-23; kickoff = 2026-06-11).

## What's been built

### Docs (read these to ramp back up)
- `README.md` — project overview + relationship to zen-loops
- `docs/strategy.md` — positioning, posting cadence by tournament phase, monetization angles
- `docs/format-library.md` — 8 World-Cup-specific archetypes (WC1–WC8)
- `docs/content-calendar.md` — pre-tournament / group stage / knockouts / post-tournament cadence
- `docs/data-sources.md` — Polymarket, FIFA, sportsbooks, football-data APIs

### Data
- `data/teams.json` — 48 teams with codes, flag colors, FIFA ranks, Polymarket win %
- `data/groups.json` — placeholder 12-group structure (update with actual FIFA draw)
- `data/odds_snapshot.json` — Polymarket winner-market snapshot (last_updated: 2026-05-23)

### Working renders
- `configs/bracket_plinko_top16.json` — 16 top teams in a single Plinko race (anchor video)
- `configs/group_d_predictor.json` — Group D 4-team Plinko (Argentina / Uruguay / Switzerland / Egypt)
- `configs/hopium_spain.json` — Spain hopium loop with "ESPAÑA CAMPEONES" reveal payoff

### Pipeline
- `generate_video.py --config configs/<name>.json` — reuses zen-loops engines via sys.path. Supports tournament-aware configs (`team_codes` field auto-resolves labels + flag colors from teams.json).

## What's NOT built yet

- **WC3 Per-Match Score Race engine** — needs new linear-race engine; defer until tournament starts
- **WC4 Top Scorer Race** — can use existing marble_drop with player names as labels; data pipeline needed
- **WC5 Polymarket Live Odds Viz** — needs marble_drop extension to make marble size proportional to odds
- **Account creation** — handles, bio, profile images
- **Owned music tracks** — Suno-generated football-hype melodies
- **Scheduling system** — `scheduling/cross_post.py` not yet ported from zen-loops

## Honest assessment

**The timing is brutal but doable.** 19 days to kickoff. We can launch this week with WC1, WC2, and WC8 content; WC3/WC4 build out during the first week of the tournament.

**The differentiator gap is real.** Polymarket has $1.1B traded but no good visualization layer. Football TikTok is saturated with player edits and AI-goal-recreations but nobody is doing physics-simulation-as-bracket-viz. The wedge is data + entertainment fusion.

**Biggest risk: platform gambling restrictions.** TikTok and IG can flag bracket/prediction content as gambling-adjacent. **Mitigation**: language matters. Use "prediction" / "simulator" / "fan poll" / "Plinko says" instead of "odds" / "bet" / "wager".

**Second risk: post-tournament decay.** Account dies mid-July without a pivot. Plan: pivot to NBA Finals (concurrent), Copa Libertadores final, Champions League restart (September), then Euro 2028.

## Priority order from here

1. **This week (T-19 to T-12)**: Create the three accounts (IG, TikTok, YT — single consistent handle). Post the 3 existing renders. Pre-render the remaining 12 group predictors (WC2.A through WC2.L) and 8 hopium loops (top 8 teams). Set up a content backlog.
2. **Next week (T-12 to T-5)**: Suno commercial subscription + 5 owned football-style melody hooks. Build the WC3 per-match score-race engine. Replace placeholder groups in `data/groups.json` with the actual draw.
3. **T-5 to T-0**: 4 posts/day. Build out WC4 (top scorer) + WC5 (Polymarket viz). Establish posting routine to test platform tolerance for prediction-market content.
4. **Group stage (T+0 to T+12)**: Daily/per-match content. 60% pre-rendered, 40% live.
5. **Knockouts (T+13 to T+37)**: Bracket-centric. Higher production per piece, fewer pieces.

## How to continue

1. Read this file
2. Read `docs/strategy.md` and `docs/format-library.md`
3. Read `data/teams.json` for the source-of-truth team data
4. `cd world-cup-loops && python generate_video.py --config configs/bracket_plinko_top16.json` to verify the pipeline
5. Engines are at `../zen-loops/engines/` — modify there only if changes also benefit zen-loops content; otherwise create new engines in `world-cup-loops/engines/`

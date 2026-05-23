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

## Supabase DB — sharpflow project (introspected 2026-05-23)

Project ID: `nfmejklpxcquzxqyqewv` (org: iqcnilycoycialaddhzr)

**Loaded and ready:**
| Table | Rows | Use |
|---|---|---|
| soccer_standings_snapshot | 42,889 | Daily standings across leagues — powers "season recap race" |
| soccer_team_form | 13,137 | Per-match form, streaks, attack/defense strength |
| soccer_elo_ratings | 13,137 | Elo over time — bias for "known-result" races |
| soccer_computed_features | 12,785 | Pre-computed ML features per match |
| soccer_historical_matches | 6,569 | Full match records (FT/HT scores, xG, shots, etc.) |
| soccer_odds_history | 2,040 | Historical odds for cross-reference |
| soccer_national_teams | 48 | All WC qualifiers; has qualified_2026 + group_2026 fields |
| soccer_leagues | 19 | League metadata + statistical fingerprints |
| soccer_fixtures | 142 | Upcoming fixtures |

**Coverage that's loaded (rich data):**
- Premier League × 3 seasons (2023, 2024, 2025)
- La Liga × 3 seasons
- Serie A × 3 seasons
- Bundesliga × 3 seasons
- Eredivisie × 3 seasons
- Turkish Super Lig × 4 seasons
- Champions League × 3 seasons (groups + knockouts)
- ~100+ daily standings snapshots per league per season

**Schema set up but data NOT loaded (ingestion gap):**
- All `WCQ-*` (qualifying competitions) — 0 rows
- Europa League, Conference League — 0 rows
- UEFA Nations League, CONCACAF Nations League — 0 rows
- International Friendlies — 0 rows
- FIFA World Cup itself — 0 rows (tournament hasn't started)

**To fill the gap**: api-football.com Pro tier (~$50-100/mo) has every WCQ match. Ingestion script ~half day work to fill the empty tables.

**Notable qualifier-2026 storylines from the DB:**
- Norway qualified for the first time since 1998 (Haaland's first WC)
- Cape Verde Islands qualified for the first time ever
- 48 teams total, all confederations represented

## Replaces my earlier teams.json placeholder

The DB is now the source of truth for `soccer_national_teams`. My `data/teams.json` was wrong on these:
- URY (not URU) is the correct Uruguay code
- I was missing: BIH, CZE, NOR, SWE, CPV, COD, CUR, HAI, RSA
- I had teams that didn't qualify: VEN, PER, NGA, DEN, POL

Action: re-sync data/teams.json from `soccer_national_teams` before next render batch.

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

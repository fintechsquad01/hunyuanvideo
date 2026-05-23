# LOCK Re-order — 2026-05-23

Based on `trend-radar-2026-05-23.md` + `competitor-tracker-2026-05-23.md`.

## What changed vs the earlier LOCK plan

The earlier order was: **T6.PRO Plinko → T3 Elo → T1 Table Race → T9 Steam Move → T4 Match Recap**.

That was a reasonable a-priori order. The intel changes it. Two findings:

1. **Curaçao + first-time-qualifiers story is the launch piece** — peak velocity, near-zero saturation, perfect fit for our data. T3 (Elo Trajectory) is the right vehicle.
2. **Bracket Plinko has gone from "unique" to "common"** — meaning T6.PRO is no longer our differentiator; it's table stakes. Still important, but not first.
3. **T1 League Table Race is the post-WC engine, not pre-WC.** Don't burn time on it now — ship it after launch when we need year-round content.

## New LOCK order

| # | Template | Story / Use | Timing |
|---|---|---|---|
| **LOCK #1** | **T3 Elo Trajectory** | "The Newcomers" 5-piece series: Curaçao, Cape Verde, Uzbekistan, Jordan, Haiti | This week — daily ship May 27 → 31 |
| **LOCK #2** | **T6.PRO Plinko (refine perf)** | Group I (Mbappé vs Haaland) + Group L (Group of Death) + Group D (Argentina) | Next week — May 28 → June 5 |
| **LOCK #3** | **T9 Steam Move Reveal** | "Forget AI. Polymarket has $1.1B." daily odds-shift content | Week 3 — June 2 → 11 |
| **LOCK #4** | **T4 Match Recap Timeline** | Tournament-daily content, starts kickoff day | June 11 onwards |
| **LOCK #5** | **T1 Animated League Table Race** | Post-tournament evergreen: PL/PD/SA/BL1/DED/TSL season recaps | July 20 onwards |

## Why this order maximizes virality

1. **Launch on Curaçao = launch on the biggest underdog story in football, with ZERO physics-simulation competition** — open lane, near-peak velocity. The first 5-piece series IS the brand introduction.
2. **Bracket Plinko in week 2** keeps the engine warm and rides the still-hot pre-tournament hype with content competitors are already making (we just produce better).
3. **Steam Move as the daily content stream during the final 9-day countdown** — establishes pitch.predict as the data-credible brand before kickoff.
4. **Match recaps start ONLY when matches start** — no point pre-rendering this; it's reactive by nature.
5. **League Table Race in post-tournament pivot** — anchors the year-round content engine when WC momentum decays.

## Series-level work items (next 5 days)

| Day | Output | Engine | Template |
|---|---|---|---|
| May 24 (Sun) | "The Newcomers #1 — Curaçao" Elo trajectory + David-vs-Germany Plinko teaser | T3 + T6.PRO | Render in Manim |
| May 25 (Mon) | "The Newcomers #2 — Cape Verde" | T3 | Manim |
| May 26 (Tue) | "The Newcomers #3 — Uzbekistan" | T3 | Manim |
| May 27 (Wed) | "The Newcomers #4 — Jordan" | T3 | Manim |
| May 28 (Thu) | "The Newcomers #5 — Haiti" | T3 | Manim |
| May 29 (Fri) | "The Newcomers — synthesis" multi-marble bracket | T6.PRO | Python custom |

**Posting strategy** (per `cross-platform-distributor` SKILL workflow):
- Same MP4 to IG / TikTok / YT Shorts simultaneously
- IG caption: identity prompt + brand voice ("Curaçao. 150K people. Smaller than MetLife. Going to the World Cup.") + brand hashtags
- TikTok caption: failable framing + 2-3 broader hashtags + FIFA official hashtag set where allowed
- YT Shorts title: SEO-friendly ("Curaçao's road to the World Cup — Elo trajectory 2014-2026") + descriptive body

## Data gaps that block LOCK #1

T3 Elo Trajectory needs `soccer_national_team_elo` data, which is currently empty in sharpflow DB.

**Path to unblock (today)**:
- Scrape eloratings.net per qualifier (5 nations needed for the series); their HTML is parseable
- OR pull from FIFA's official Men's Ranking historical archive
- OR compute from international friendlies + WCQ match results (we have schema, not data)

ETA: 2-4 hours of scraping work to populate the 5 qualifiers' Elo histories.

## What I need next

1. **Green light to scrape eloratings.net** for the 5 first-time qualifiers' Elo history (small volume, public data)
2. **Confirm Manim is the renderer for T3** — I'll prototype in `world-cup-loops/engines/manim/elo_trajectory.py`
3. **Brand assets**: if Claude Design hasn't returned a logo yet, ship the first piece with a temporary text-only watermark ("pitch.predict") and re-render later when brand assets arrive
4. **Confirm the 5-piece series + bracket synthesis order** above — this is what I'll build next session

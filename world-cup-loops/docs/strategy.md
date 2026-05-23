# Strategy — world-cup-loops

## Thesis

The viral marble-race format and the bracket tournament structure are made for each other. Combine them with prediction-market data (Polymarket, Kalshi) and you have a content engine that's:

- **Visually identical** to a format people already love (Plinko race)
- **Backed by real data** that the audience trusts more than expert picks
- **Endlessly serializable** — 104 matches × multiple angles = 200+ post opportunities in 5.5 weeks
- **Identity-laden** — every viewer has a team to root for, comment about, defend

## The five audience segments we serve

1. **Casual fans** — only watch their country play; click to see how their team's marble is doing
2. **Hardcore fans** — debate group dynamics; will comment on tactical takes embedded in captions
3. **Bracket pool players** — ~150M globally fill out brackets; want to see how predictions play out
4. **Prediction market users** — Polymarket / Kalshi / FanDuel users; deeply engaged, share-prone
5. **Football neutrals** — like watching satisfying loops, agnostic about teams; the algorithm-overflow audience

The same Plinko render serves all five with different caption framings. That's the leverage.

## Brand promise

*"Brackets that play themselves."*

Bio (draft): *"Watch every bracket. Watch every prediction. One marble wins. Comment yours."*

## Posting cadence — by tournament phase

### T-19 to T-0 days (PRE-TOURNAMENT, May 23 – June 10)
Goal: build account trust, build follower base before the algorithmic boost from #FIFAWorldCup kicks in.

| Day | Post |
|---|---|
| T-19 to T-15 | 2/day — Group-of-Death predictor, "pick your country" Plinko, Polymarket-odds visualization |
| T-14 to T-7 | 3/day — One per major group; bracket-of-32 simulator; star-player Plinko |
| T-7 to T-1 | 3–4/day — Per-group predictors with current Polymarket odds, "if X advances" scenarios |
| T-0 (kickoff day) | 5+ posts — Opening ceremony / match coverage / live bracket updates |

### T+0 to T+12 (GROUP STAGE, June 11 – 27)
Goal: ride every match. 48 matches over 12 days = 4 matches/day average.

| Cadence | Format |
|---|---|
| Per match | Pre-game: 30s "marble preview" with Polymarket odds → both teams race during prediction window |
| Per match | Post-game: 15s recap with goals-as-bounces; winner reveal payoff |
| Daily | Top-scorer marble race (all goal-scorers as marbles, position = goals scored) |
| Daily | "Group X standings" Plinko with current points |

### T+13 to T+37 (KNOCKOUTS, June 28 – July 19)
Goal: bracket-driven dramatic content. Fewer matches but higher stakes.

| Cadence | Format |
|---|---|
| Per match | Pre + post coverage with full Plinko (now showing actual bracket position) |
| Per round | "Updated bracket" video with surviving 16 / 8 / 4 teams in elimination Plinko |
| Final week | Heavy series content — "Bracket of the century" recap; final preview |

### T+38 onwards (POST-TOURNAMENT)
Decay period. Pivot strategy:
- Final highlights compilation (max one week of content)
- "Champions across history" retrospective Plinko (use past World Cup data)
- **Pivot to next tournament**: Copa América 2027, Euro 2028, Champions League (continuous). Or pivot to other sports' brackets (March Madness, NBA Playoffs, Wimbledon).

## Content archetypes (from `format-library.md`)

| # | Archetype | Engine fit | Frequency |
|---|---|---|---|
| WC1 | Bracket Plinko (32→16→8→4→2→1) | marble_drop extended | 1-2/week + every round |
| WC2 | Group Predictor (4 teams in one group) | marble_drop | 1/group, refresh weekly |
| WC3 | Per-Match Score Race | new engine (linear race) | per-match |
| WC4 | Top Scorer Race | marble_drop variant | daily during tournament |
| WC5 | Polymarket Live Odds Viz | marble size = win % | weekly snapshot |
| WC6 | "Will X Advance?" Plinko | marble_drop subset | reactive to viral moments |
| WC7 | Country-Food Marble Race | marble_drop with custom labels | weekly cultural angle |
| WC8 | Hopium Loop (your country's path to final) | ring_expansion variant | reactive |

## Cross-platform play

| Platform | Strategy | Hashtag base |
|---|---|---|
| Instagram Reels | Identity prompts in caption ("Comment your team"); pinned comments | #FIFAWorldCup #WorldCup2026 #Football #Soccer |
| TikTok | Failable framing ("99% can't predict the bracket"); trending football sounds where licensable | #WorldCup #Soccer #Football #SportsTok #FIFAWorldCup2026 |
| YouTube Shorts | SEO-friendly titles ("Will Spain win the World Cup? Plinko predicts") | descriptions matter; pin "follow for daily World Cup predictions" |
| X / Twitter | Bracket community lives here. Post finals + group calls as standalone tweets with video. Reply-with-video to viral takes. | n/a — Twitter culture is hashtag-light |

## Monetization angles (this account differs from zen-loops here)

The football audience monetizes differently than satisfying-loops viewers. Options ranked by feasibility:

1. **Affiliate links to sportsbooks** (DraftKings / FanDuel / Bet365) — high CPA ($50–500 per signup) but TikTok/IG restrict gambling-related links. Use in bio carefully.
2. **Prediction market affiliate** (Polymarket has a partner program; Kalshi is growing) — less restricted than sportsbooks
3. **Brand deals during the tournament** — football brands (Adidas, Nike, Puma, FIFA partners) advertise heavily; mid-size accounts can land $500–5000 per branded post
4. **Bracket challenge product** — a paid "build your bracket and simulate it" web tool ($5–10 one-time, or freemium); we have the engine to power this
5. **Mobile game (phase 2)** — same Color-Ball-Z-style hyper-casual but football-themed; "FlickPlinko" or similar

Bracket affiliate (Polymarket) is the cleanest first move. Sportsbooks are gated behind platform policy issues.

## Risks (ranked)

1. **Platform gambling restrictions** — TikTok in particular is aggressive about gambling-adjacent content. Bracket predictors using percentages and "odds" might get flagged. Use language like "prediction" / "simulator" / "fan poll" rather than "betting" / "odds".
2. **Time pressure** — 19 days to kickoff. Must launch this week; can't afford to polish.
3. **FIFA IP enforcement** — using FIFA logos, official names, team crests is risky. **Country flags = fair use. Player likenesses = gray. Team crests/FIFA marks = no.**
4. **Real-time content burden** — during the tournament, posting cadence is daily/per-match. Solo operator can burn out fast. Pre-render evergreen content (bracket Plinko, team profiles) to buffer the live load.
5. **Post-tournament decay** — account loses momentum mid-July. Pivot to other brackets (NBA Finals concurrent in June, then Copa, Euros 2028, etc.) to keep the engine running.
6. **Player injuries / drama** — content built around specific players (e.g., Lamine Yamal) can be wrecked overnight. Diversify; never bet a whole content week on one player.

## Success metrics

By T+10 (10 days post-launch, pre-tournament):
- 1,000+ followers per platform
- ≥0.5% comment-to-view ratio
- ≥40% retention at 5s

By end of group stage (T+12, June 27):
- 10,000+ followers per platform
- One viral hit (>500K views on any platform)
- Newsletter / Discord / Polymarket affiliate funnel set up

By end of tournament (T+37, July 19):
- 50,000+ followers per platform
- Identified the format that wins → continue with that for the next tournament
- Optional: prototype the FlickPlinko mobile game if engagement validates

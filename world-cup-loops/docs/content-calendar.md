# Content Calendar — World Cup 2026

Timezone references: UTC (matches are scheduled across US/Canada/Mexico time zones; UTC is the lingua franca).

## Phase 1 — Pre-tournament hype (May 23 – June 10, 2026)

T-19 → T-0. **The launch window.** Account trust must build BEFORE the algorithm hands you World Cup hashtag traffic.

### Week 1 (May 23–29) — Account warm-up
| Day | Posts | Format | Goal |
|---|---|---|---|
| 1 | 2 | WC1.a Bracket Plinko (Polymarket odds version) + WC5 odds viz | Plant the flag. Show what we do. |
| 2 | 2 | Two WC2 group predictors (highest-interest groups, e.g., "Group of Death") | Establish series cadence |
| 3 | 2 | WC8 Hopium Loop (Spain) + WC8 Hopium Loop (France) | Top-2 favorites; broad reach |
| 4 | 2 | WC2 Group predictor + WC1.b Round of 16 simulator | Build content depth |
| 5 | 3 | Two more group predictors + WC7 Food race (debut) | Test the food angle |
| 6 | 2 | WC1.a (rerun with different palette) + WC8 hopium for Brazil | Repetition reinforces brand |
| 7 | 2 | WC2 Group predictor + WC5 odds viz update | Weekly cadence locked |

### Week 2 (May 30 – June 5) — Volume up
3 posts/day. Mix WC1, WC2, WC8 heavy. Introduce WC6 ("Will X advance?") opportunistically.

### Week 3 (June 6–10) — Pre-kickoff burst
4 posts/day. Heavy on bracket Plinko, group predictors with **final pre-tournament Polymarket odds snapshot**. Reactive content based on injury news / squad announcements.

**T-1 (June 10)**: kickoff teaser. WC1.a Bracket Plinko v_final, pinned-to-top of account.

## Phase 2 — Group Stage (June 11 – 27, 2026)

48 matches over ~17 days. Average 3 matches/day; some days have 4.

### Daily rhythm
- **Morning post** (before first match): match preview WC3.a + daily WC4 top scorer race
- **Per-match**: 30s WC3.b post-match recap within 2 hours of final whistle
- **Evening**: WC2 updated group standings Plinko (one per group that played)

### Reactive slots (use as needed)
- WC6 "Will X advance?" when storylines emerge
- WC8 Hopium Loop when underdog wins
- WC7 Food race weekly cross-pollination

### Daily content target
- 4–6 posts/platform/day. Front-load pre-rendered content, fill in match recaps live.

## Phase 3 — Knockouts (June 28 – July 19, 2026)

Fewer matches, higher stakes. Bracket-focused.

### Round of 32 (June 28 – July 2)
- WC1.b Round of 32 Plinko (Day 1) — high priority post
- Per-match WC3 coverage
- Daily WC4 top scorer

### R16 (July 4–7) → QF (July 9–12) → SF (July 14–15)
- New bracket Plinko after each round
- Heavy WC8 Hopium content for surviving fan-favorite teams
- "Bracket bust" content when favorites lose

### Final week (July 16–19)
- 5+ posts/day
- WC1.e Final Plinko (Spain vs France type matchup) — flagship video
- Bracket-of-the-tournament retrospective
- Champion celebration content

## Phase 4 — Post-tournament (July 20 onwards)

Decay starts immediately if we don't pivot.

### Week 1 post-final
- Final highlights compilation
- "Goals as melody" — the tournament's top goals played as melody notes via ring_expansion
- Tournament retrospective Plinko (host nations / star players)

### Pivot strategy
By end of July:
1. **Continuous tournament content**: Champions League starts in September; Copa Libertadores final in October-November
2. **Other sport brackets**: pivot the engine to NBA Playoffs (already running), Wimbledon (July), College Football Playoff (December)
3. **Mobile-game launch window** — if engagement validates, ship FlickPlinko/BracketBall while audience is hot
4. **Account hibernation + Euro 2028 prep** — keep low maintenance posting until next tournament

## Workload realism check

**Live-tournament posting requires either**:
- 4–6 hours/day of operator time during the tournament, OR
- A pre-render + scheduling system (`scheduling/cross_post.py` from zen-loops, ported here)

If working solo, pre-render aggressively: produce 2 weeks of bracket / group / hopium content during the pre-tournament phase, then only live-render match recaps during the tournament. Don't try to live-render everything.

## Pre-renderable vs reactive

| Format | Pre-render OK? | Reactive needed? |
|---|---|---|
| WC1 Bracket Plinko (group-stage version) | YES (re-render after each round) | partial |
| WC2 Group Predictor | YES (refresh after matches) | partial |
| WC3 Per-Match | NO — must be post-match | YES |
| WC4 Top Scorer Race | YES (daily batch) | needs daily input data |
| WC5 Polymarket Viz | YES (weekly snapshot) | NO |
| WC6 Will X Advance | NO — opportunistic | YES |
| WC7 Food Race | YES | NO |
| WC8 Hopium Loop | YES | partial |

Conclusion: 60% of tournament content can be pre-rendered in the 2 weeks before kickoff. Live load is 40%.

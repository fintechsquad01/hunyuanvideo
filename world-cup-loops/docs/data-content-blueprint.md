# Data → Content Blueprint

Comprehensive mapping of what's in the `sharpflow` Supabase DB → what we can build with it → tools and design assets we need to scale it.

---

## Part 1 — Data inventory (every field, every use)

### Tier 1 — Loaded with rich data

#### `soccer_standings_snapshot` (42,889 rows)
*Daily standings across PL/PD/SA/BL1/DED/TSL/CL × 3 seasons.*

| Field | Type | Content use |
|---|---|---|
| league_code, season, date | identity | Filter for "PL 2023 season recap" type formats |
| team, position | core | **Direct Y-coord for animated league table races** |
| points, played, won, drawn, lost | scoring | Points-driven progress bars; W/D/L mosaic |
| gf, ga, gd | goals | "Goals scored" climb race; +/- visualizations |
| ppg | rate | Form-adjusted ranking |
| zone | category | UCL/Europa/Relegation color coding |
| points_to_leader, points_to_relegation | dynamics | "How close is the title race" tension bar |
| form_last5 | string | "WWDLW" → animated win/loss streak visualization |

#### `soccer_historical_matches` (6,569 rows)
*Per-match results with rich stats.*

| Field | Type | Content use |
|---|---|---|
| home_goals, away_goals, ht_home, ht_away, h2_home, h2_away | scoring | Goal-by-goal timeline animations |
| winner | result | Sequence of W/D/L for a team's season |
| home_xg, away_xg | metrics | **"Expected vs Actual" race** (huge format) |
| home_shots, away_shots, *_shots_on_target | shooting | Shot-difference animations |
| home_corners, away_corners | set pieces | Corner battles visualization |
| home_possession, away_possession | flow | Possession swing graphs |
| home_yellow_cards, *_red_cards | discipline | "Dirty match" tier list |
| home_fouls, away_fouls | discipline | Foul-intensity visualization |
| referee | meta | Ref bias analysis racing |
| extended_stats (jsonb) | full | Anything not in fixed columns — passes, dribbles, etc. |
| btts, over_1_5/2_5/3_5, home_clean_sheet | flags | Binary outcome simulation races |

#### `soccer_elo_ratings` (13,137 rows)
*Daily Elo for every team in covered leagues.*

| Field | Type | Content use |
|---|---|---|
| team, league_code, date, elo | core | **Elo trajectory race** — team's strength over time |
| elo_home, elo_away | split | Home advantage visualization |
| elo_delta | change | Per-match Elo swing animations |
| streak_direction, streak_length | momentum | Hot/cold streak visualization |
| matches_rated | sample | Confidence-weighted strength |

#### `soccer_team_form` (13,137 rows)
*Per-match form snapshot per team.*

Massive feature set: `form_pts_last5, avg_goals_scored_last5, btts_rate_last5, over25_rate_last5, win_rate_last5, season_cumulative_points, season_avg_gf, win_streak, loss_streak, unbeaten_streak, scoring_streak, momentum_score, days_since_last_match, ppda (pressing), field_tilt, xg_per_game, fatigue_factor, injury_attack_impact, injury_defense_impact, npxg_per_game`.

**Content uses:**
- Momentum-score race (who's hottest right now)
- "Pressing intensity" comparison (PPDA visualization)
- xG vs npxG (penalty-adjusted) race
- Fatigue-factor leaderboards (who's about to drop off)
- Injury impact tier list

#### `soccer_computed_features` (12,785 rows)
*Pre-computed ML inputs per match. The intersection of all other tables.*

This is the **single best feed** for any per-match content because every metric is pre-joined. Use this for "match preview" content rather than re-aggregating from primary tables.

#### `soccer_odds_history` (2,040 rows)
*Historical opening/closing odds + steam moves.*

| Field | Content use |
|---|---|
| opening_*, closing_* | "How the market moved" animation |
| implied_prob_home/draw/away | Probability change bar charts |
| steam_move_home/away | "Sharp money loaded on X" reveal |
| odds_move_* | Visual delta arrows |
| ah_line, ah_home, ah_away | Asian Handicap explainer |
| all_markets (jsonb) | Deep market exploration |

#### `soccer_national_teams` (48 rows)
*All 48 WC 2026 qualifiers + metadata.*

| Field | Content use |
|---|---|
| team_code, team_name, confederation | Filter/group by federation (AFC, CAF, etc.) |
| qualified_2026, group_2026 | WC bracket assembly |
| current_manager, manager_since | Manager career arc content |
| fifa_id, fd_team_id, sofascore_team_id | API joining for external data |

**Storylines already in this table:**
- Norway qualified — first since 1998 (Haaland's first WC)
- Cape Verde Islands — **first ever qualification**
- Curaçao, Haiti — small-nation qualifiers (huge underdog stories)
- 48 teams represent every confederation including Oceania (NZL)

### Tier 2 — Loaded but specific use cases

| Table | Rows | Use |
|---|---|---|
| `soccer_match_analysis` | 37 | Per-match deep dives with `minute_data, scoreline_grid, goal_timing, shotmap, player_stats, tactical_matchup` — premium content for big matches |
| `soccer_match_context` | 28 | Narrative angles: `rivalry_intensity, revenge_factor, new_coach, congestion_3day, record_chase, end_of_season_flag, champion_already_decided` — perfect for storytelling captions |
| `soccer_predictions` | 30 | sharpflow's model predictions vs actual results — "the model called it" content |
| `soccer_value_bets` | 42 | Edge / EV bets with `confidence, reasoning, sharp_aligned, tier` — *gambling-adjacent, use carefully* |
| `soccer_fixtures` | 142 | Upcoming matches with prob/xG forecasts, `tags`, `insight`, `stage`, `tournament_group` — ready for pre-match content |
| `soccer_leagues` | 19 | League statistical fingerprints (`avg_goals, over_25_pct, btts_pct, home_win_pct`) — "which league is most exciting" content |
| `soccer_team_aliases` | 37 | Name normalization — critical for cross-source joining |

### Tier 3 — Schema-ready, data needs ingesting (gap)

| Table | Why empty | How to fill |
|---|---|---|
| `soccer_wc_squads` | WC squads not announced yet | Auto-populate from sofascore via fd_team_id after May 26 (FIFA squad deadline) |
| `soccer_national_team_elo` | Elo not computed for nationals yet | Either pull from eloratings.net (no API but scrapable) or compute from international match results |
| All `WCQ-*` leagues | Qualifier match data not ingested | api-football.com — has every WCQ match; ~half-day batch import |
| `EL`, `ECL` (Europa/Conference) | Not yet imported | api-football.com — adds to multi-tournament catalog |
| `UNL`, `CONCACAF-NL`, `INTL-FR` | Not yet imported | api-football.com or sofascore |
| `WC` (the tournament itself) | Tournament hasn't happened | Will auto-populate from June 11 |

---

## Part 2 — Viral content concepts derived from each data category

Each concept is grounded in **fields that exist or have a clear ingestion path**.

### Category A — Standings dynamics (uses `soccer_standings_snapshot`)

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| A1 | **Season-in-30s race** | Marbles climb a vertical league table; Y-pos = position at date snapshot | "Watch the 2024 PL season unfold in 30 seconds" |
| A2 | **Points-cumulative race** | X-pos = cumulative points; marbles overtake horizontally | "Every PL points swing of 2024" |
| A3 | **GD climb race** | Marbles tracked by goal difference, not points | "Most dominant teams of the decade" |
| A4 | **Title-race tension** | Single chart, top-2 teams highlighted, "points-to-leader" shown as red zone | "The closest title race of the decade" |
| A5 | **Relegation drama** | Bottom-3 only; last 10 matchdays; survival celebrations | "Who survived. Who didn't." |
| A6 | **Zone migration heatmap** | Color of each team's row changes as zone changes | "When teams entered/exited UCL spots" |
| A7 | **Form-last-5 mosaic** | Animated W/D/L stripes per team over the season | "The hot and cold periods" |
| A8 | **Multi-league comparison** | Top-4 of PL vs top-4 of PD on same chart | "Which Big 4 is most dominant?" |

### Category B — Match-level dynamics (uses `soccer_historical_matches`, `soccer_match_analysis`)

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| B1 | **xG vs Goals race** | Two marbles per team: predicted goals (xG) and actual goals; race over season | "Who scored more than they deserved?" |
| B2 | **Goal-by-goal recap** | Vertical timeline; minute-mark goals appear as colored balls dropping into score column | "Every goal of [match] in 15 seconds" |
| B3 | **Shotmap reveal** | Animated xG dots appearing on a half-pitch heatmap | "Where [team] actually shoots from" |
| B4 | **Possession swing graph** | Two-color river chart | "When the game turned" |
| B5 | **Card-storm visualization** | Yellow/red cards appearing on a clock face | "The dirtiest match of the season" |
| B6 | **Comeback tracker** | Score line animation showing 0-2 → 3-2 type comebacks | "The greatest comeback of [season]" |
| B7 | **Clean sheet streak** | Days/games without conceding as a growing ring | "[Keeper] hasn't conceded in 14 games" |

### Category C — Strength / momentum (uses `soccer_elo_ratings`, `soccer_team_form`)

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| C1 | **Elo trajectory race** | Line race of every team's Elo over time | "Norway's rise from #44 to #14" |
| C2 | **Momentum-score leaderboard** | Marbles sized by momentum_score, updates daily | "Hottest teams in Europe right now" |
| C3 | **Streak race** | Win/unbeaten/scoring streaks as bars filling up | "Longest unbeaten run of the season" |
| C4 | **Fatigue meter** | fatigue_factor as a draining battery icon per team | "These teams are running on fumes" |
| C5 | **PPDA pressing race** | Lower PPDA = more pressing; race to most aggressive | "Who presses the highest in Europe?" |
| C6 | **Field tilt comparison** | Visualization of territorial dominance | "Teams that bullied their opponents" |
| C7 | **Injury-impact tier list** | Marbles drop based on injury_attack/defense_impact | "Most affected by injuries this month" |

### Category D — Odds and prediction (uses `soccer_odds_history`, `soccer_predictions`, `soccer_value_bets`)

⚠️ **Gambling-adjacent. Use careful framing: "prediction market", "model says", "smart money", NOT "bet", "odds", "wager".**

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| D1 | **Steam-move reveal** | Odds bar shrinks/expands as line moves | "Sharp money loaded on [team]" |
| D2 | **Model vs reality** | sharpflow's predicted probabilities vs actual outcome | "Did the model call it?" |
| D3 | **Implied probability shift** | Pre-match vs in-game probability tracking | "The moment the match flipped" |
| D4 | **Edge-rank leaderboard** | Value bets by edge size (no actual betting framing) | "Where the market is wrongest" |
| D5 | **Brier-score race** | Forecasters competing on calibration | "Which prediction source is sharpest" |

### Category E — Player / squad (uses `soccer_wc_squads` (when filled), `soccer_match_analysis.player_stats`)

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| E1 | **Goalscorer Plinko** | Each goalscorer = a marble; size = goals scored | "Top scorer race — Day 14" |
| E2 | **Cap-count race** | Players' international caps as climbing bars | "Most experienced WC squads" |
| E3 | **Club distribution map** | WC squad members by club allegiance | "Which clubs sent the most players?" |
| E4 | **Age-distribution race** | Squad ages, oldest to youngest | "Youngest WC squad of 2026" |
| E5 | **"Where do they play?"** | Squad club_country distribution | "Spain's squad: 87% from La Liga. Norway: 0%." |
| E6 | **Player career trajectory** | One player's stats over years | "[Player] from debut to today" |

### Category F — Context / storytelling (uses `soccer_match_context`)

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| F1 | **Rivalry-intensity score** | Visualization of how intense a derby is | "Why this derby is different" |
| F2 | **Revenge factor** | Last meeting result → this match teaser | "[Team] hasn't forgotten 2024" |
| F3 | **Champion already decided** | Final-day fixtures with stakes flag | "Nothing on the line but pride" |
| F4 | **Record-chase tracker** | Real-time progress toward a notable record | "[Team] one win from a club record" |
| F5 | **End-of-season anxiety** | Relegation pressure + zone visualization | "Three games to save the season" |

### Category G — Historical / Known-result races (THE FLAGSHIP CATEGORY)

These leverage the data fidelity that competitors lack. **Every race finishes on the historically accurate result.** No "what if" — pure documentary.

| # | Concept | Mechanic | Hook |
|---|---|---|---|
| G1 | **Title race recap** (any league × any season) | Points-cumulative race biased to actual standings; ends on real winner | "How [team] actually won the 2024 title" |
| G2 | **Relegation race recap** | Same mechanic, bottom half | "Who survived — and how close it really was" |
| G3 | **WC qualification journey** (per group, per confederation) | When data loaded | "How [country] punched their ticket" |
| G4 | **Cinderella story races** | Underperformers who overperformed Elo | "[Team] shouldn't be here" |
| G5 | **Manager era summary** | Team performance under [manager] as cumulative race | "Pep's first 5 years at Man City" |
| G6 | **"This day in history" anniversary race** | Daily auto-post of a notable race from N years ago | "5 years ago today, [event]" |

### Category H — Multi-tournament evergreen (post-WC pivot)

| # | Concept | Audience |
|---|---|---|
| H1 | Champions League knockout recap | All Europe |
| H2 | Premier League title race weekly | EPL fans (largest single fanbase) |
| H3 | La Liga / Serie A / Bundesliga / Eredivisie weekly | Per-league fans |
| H4 | Turkish Super Lig (you have 4 seasons!) | Turkish football fans (massive on social) |
| H5 | Copa América (when data added) | LatAm fans |
| H6 | AFCON / Asian Cup / Euros 2028 | Continental fans |

**Total formats catalogued: 50+.** Each is built from existing or near-existing data. No speculative content.

---

## Part 3 — Templates (reusable engine + render combinations)

Templates are *engine + config schema + caption pattern* combinations that one operator can ship at 2–4 per day.

### Template T1 — Animated League Table
- **Engine** (new, must build): `league_table_race.py` — vertical marble lane per team, Y = league position, X = date
- **Data**: `standings_snapshot WHERE league_code = ? AND season = ?`
- **Cadence**: weekly per active league; or one-shot per finished season
- **Caption**: "How [winner] actually won the [season] [league] title"

### Template T2 — Points-Cumulative Race
- **Engine** (new, must build): `points_race.py` — horizontal race, X = cumulative points
- **Data**: same
- **Variants**: top-6 / bottom-3 / single rivalry
- **Caption**: "Every [season] title-race twist in 30s"

### Template T3 — Elo Trajectory
- **Engine** (new, must build): `elo_line_race.py` — animated line chart
- **Data**: `elo_ratings WHERE team IN ? ORDER BY date`
- **Variants**: single team's career arc, head-to-head comparison
- **Caption**: "[Team]'s strength over 5 years"

### Template T4 — Goal Timeline Recap
- **Engine** (new, must build): `match_recap.py` — minute-mark scorers on a clock
- **Data**: `match_analysis.goal_timing`
- **Caption**: "Every goal of [match] in 15s"

### Template T5 — xG vs Goals Comparison
- **Engine** (new): `xg_actual_race.py` — two marbles per team, season aggregation
- **Data**: `historical_matches xG sums grouped by team`
- **Caption**: "Who overperformed xG this season?"

### Template T6 — Plinko Bracket (existing)
- **Engine**: `marble_drop_pro.py` (built) — needs perf optimization
- **Variants**: per-tournament (WC bracket, CL knockouts, Copa)
- **Caption**: per the strategy doc

### Template T7 — Ring Expansion (existing)
- **Engine**: `ring_expansion.py` (built)
- **Variants**: hopium loops, "guess the song" with team chants
- **Caption**: per the strategy doc

### Template T8 — Identity Drop (existing Plinko remix)
- **Engine**: `marble_drop.py` (built)
- **Variants**: birth month, zodiac, country, club, position
- **Caption**: "Pick your [X]"

### Template T9 — Steam Move Reveal
- **Engine** (new, small): `odds_shift.py` — animated odds bars
- **Data**: `odds_history opening vs closing`
- **Caption**: "Sharp money loaded on [team]"

### Template T10 — Squad Composition Reveal
- **Engine** (new, small): `squad_breakdown.py` — pie/grid of player attributes
- **Data**: `wc_squads`
- **Caption**: "Where Spain's squad actually plays"

**Build priority** (after current 3 archetypes validate by posting):
1. T1 League Table Race — biggest unlock; powers Categories A, G
2. T2 Points Race — different angle on same data
3. T3 Elo Trajectory — Norway / Cape Verde stories deserve this
4. T4 Match Recap — daily content during tournament
5. T9 Steam Move Reveal — differentiator content
6. T5, T10 — secondary
7. T6, T7, T8 — already built

---

## Part 4 — Tools, libraries, APIs

### Data layer (data → pipeline)

| Tool | Use | Cost |
|---|---|---|
| **Supabase** (already wired) | Source of truth | $25/mo Pro |
| **api-football.com** (RapidAPI) | WCQ ingestion, live match data, lineups | $50/mo Pro |
| **eloratings.net** (scrape) | National team Elo | free |
| **understat.com** (scrape) | Extended xG data | free |
| **Polymarket Gamma API** (no auth) | Prediction-market odds | free |
| **sofascore.com** (already linked via IDs) | Detailed stats / shotmaps | scrape; free |

### Rendering (engine work)

| Tool | Use | Cost |
|---|---|---|
| **Python (current)** | Plinko / ring / square engines | free |
| **Pillow + cairo** | Antialiased 2D drawing | free |
| **matplotlib animation** | Quick chart-style animations (T1–T5 prototypes) | free |
| **plotly** (kaleido) | Export interactive charts as PNG/MP4 frames | free |
| **D3.js → Puppeteer screenshots** | Web-quality animated SVGs, screenshotted per frame | free |
| **Manim** | Mathematically precise animations (Elo trajectories, statistical reveals) | free |
| **moderngl + GLSL** | GPU-accelerated visuals when CPU caps out | free |
| **Remotion (React + headless Chrome)** | Compositing studio for video — great for T1/T4 | free |
| **CapCut / Premiere export pipeline** | Final post-production polish | $0–10/mo |

### Audio

| Tool | Use | Cost |
|---|---|---|
| **Suno Pro** | Original football-hype melody hooks | $10/mo |
| **ElevenLabs Creator** | AI commentary, TTS sportscaster | $22/mo |
| **Epidemic Sound** | Royalty-free background tracks | $24/mo |
| **Splice** | Sample packs (collision SFX, ambient stadium beds) | $13/mo |
| **Spotify Basic Pitch** | Audio → MIDI converter for Suno hook transcription | free, open source |
| **FFmpeg** (bundled) | Mux, normalize, master | free |

### AI image / video

| Tool | Use | Cost |
|---|---|---|
| **Fal.ai** | Hosted FLUX/SDXL — fast image gen for stadium backgrounds, jersey concepts | pay-per-call (~$0.001–0.05/image) |
| **HuggingFace Inference API** | Same plus open models (also Basic Pitch hosted) | free tier + paid |
| **Higgsfield** | AI video with camera-motion control — cinematic stadium pans, hero shots | per-clip pricing |
| **Stable Diffusion (self-host)** | If we hit volume, run locally on GPU | free + GPU cost |

### Design (assets + chrome)

| Tool | Use | Cost |
|---|---|---|
| **Figma** | Brand identity, video chrome templates, design system | free / $12/mo Pro |
| **Canva** | Thumbnails, IG story templates, quick social posts | $13/mo Pro |
| **Unsplash** | Stock football/stadium photos (commercial free) | free |
| **Iconify** | Open-source icons for chrome | free |

### Web / hosting

| Tool | Use | Cost |
|---|---|---|
| **Vercel** | Landing page, bracket-builder web tool, leaderboard | free / $20/mo Pro |
| **Cloudflare R2** | Asset CDN, video storage | ~$0/mo at our scale |
| **Linktree or owned domain** | Bio link → App Store | free / $9/mo |

### Automation / posting

| Tool | Use | Cost |
|---|---|---|
| **GitHub Actions** | Scheduled data refresh + render + post | free |
| **n8n** or **Make** | Visual workflow automation | free / $20/mo |
| **Meta Graph API** (IG) | Auto-post to Instagram | free |
| **TikTok Content Posting API** | Auto-post to TikTok | free, requires app approval |
| **YouTube Data API v3** | Auto-post Shorts | free quota |
| **Buffer / Hootsuite** | Manual scheduling if API gating fails | $6–15/mo |

### Analytics

| Tool | Use | Cost |
|---|---|---|
| **PostHog** (MCP already wired) | Cross-platform funnel attribution | free / paid |
| **Mixpanel** | Event tracking | free / paid |
| **Sport-specific** (SportTrac, ChannelMeter) | Per-platform engagement deep dives | varies |

---

## Part 5 — Design needs assessment

Everything that requires visual design output, ranked by priority.

### Tier 1 — Block launch (need within 2 weeks)

| # | Asset | Description | Path |
|---|---|---|---|
| D1 | **Brand logo lockup** | Full logo (icon + wordmark) | Figma + Fiverr ($100-300) OR Claude generates SVG spec + AI image gen for refinement |
| D2 | **Logo icon (square)** | For profile pics, watermark, app icon | derivative of D1 |
| D3 | **Color palette** (formal spec) | Brand primary, secondary, surfaces, semantic colors | **Claude spec → CSS/Figma tokens** |
| D4 | **Typography pairing** | Hook / body / numeric font selection | **Claude spec + Google Fonts** |
| D5 | **Profile imagery** (IG, TikTok, YT, X) | Same logo, sized + cropped per platform | derivative of D1, Canva resize |
| D6 | **Banner imagery** (YT, X) | Wider layouts with wordmark | Canva template |
| D7 | **Video intro stinger** (0.5s) | Logo reveal animation | Figma → After Effects or Remotion |
| D8 | **Video outro stinger** (0.6s) | Wordmark + micro-CTA | Figma → After Effects or Remotion |
| D9 | **Watermark overlay** | Corner logo for in-video chrome | derivative of D2 |
| D10 | **Bracket frame overlay PNG** | Transparent overlay showing bracket round + sponsor slot | Figma |

### Tier 2 — Production polish (need within 4 weeks)

| # | Asset |
|---|---|
| D11 | YouTube thumbnail templates per archetype |
| D12 | TikTok cover frame templates |
| D13 | IG story templates (poll, quiz, share-back) |
| D14 | Highlight cover icons |
| D15 | Animated lower-thirds (player name, team, stat) |
| D16 | Score badge / counter design |
| D17 | Odds badge / probability bar design |
| D18 | Stadium-pitch background art (replace flat green) |
| D19 | Trophy / celebration animation assets |
| D20 | Per-confederation flag asset library |

### Tier 3 — Marketing / web (need within 8 weeks)

| # | Asset |
|---|---|
| D21 | Landing page design + build |
| D22 | About page |
| D23 | Brand kit PDF (for media + brand-deal partners) |
| D24 | Sponsor / brand-deal pitch deck |
| D25 | Email newsletter template |

### Tier 4 — Mobile (defer to phase 2)

| # | Asset |
|---|---|
| D26 | App icon |
| D27 | Splash screen |
| D28 | App store screenshots |
| D29 | In-app UI components |

---

## Part 6 — Claude design coverage map

Honest assessment of what Claude (me) can do for each design need vs what needs an external tool.

### What Claude (me) handles 100%

- **Design tokens / spec files** (JSON, CSS variables, Tailwind config) — D3, D4
- **CSS / SVG code** for simple visual elements — D9, D16, D17 partial
- **Color palette generation** with accessibility checks (WCAG contrast ratios) — D3
- **Typography pairings** + system Google Fonts loader scripts — D4
- **Copy + tone of voice guidelines** — D23 partial
- **Figma plugin scripts** if needed for batch operations
- **Style guide documentation** comprehensively (PDF spec via markdown → pandoc)
- **Animation timing functions** + Remotion / After Effects expressions
- **Caption templates** (we already have hook/CTA libraries)

### What Claude + a connector handles together

| Asset | Claude does | Connector does |
|---|---|---|
| D1 Logo lockup | Generates SVG draft, writes brief | **Fal.ai / Higgsfield** to refine; or **Figma** for vector editing |
| D2 Logo icon | Generates simple SVG | **Fal.ai** for refinement |
| D5 Profile imagery | Crops/resizes via SVG transforms | **Canva** for finishing |
| D6 Banner imagery | Composes layout spec | **Canva** template fill |
| D7/D8 Stingers | Writes Remotion component code | Remotion + ffmpeg renders |
| D10 Bracket frame overlay | Generates SVG + spec | **Figma** for export tuning |
| D11/D12 Thumbnails | Writes Remotion template | **Unsplash** for background photos; **Canva** for hand-edit polish |
| D18 Stadium-pitch BG | Writes prompt | **Fal.ai FLUX** generates; **Unsplash** as alternative |
| D19 Trophy animations | Writes Remotion / Manim spec | Remotion renders |
| D20 Flag library | Lists ISO codes + sources | Open SVG flag library (free, no AI needed) |
| D21 Landing page | Writes the entire React/Next.js code | **Vercel** deploys; **Figma** for design review |
| D24 Pitch deck | Writes copy + spec | **Canva** for slide design |

### What Claude cannot do; needs human or different AI

| Asset | Why | Tool |
|---|---|---|
| Photorealistic player imagery | Image gen, IP-sensitive | **Fal.ai FLUX** with rights clearance |
| Premium logo aesthetic judgment | Subjective design taste | Human designer (Fiverr $100–500) |
| Custom illustrations (e.g., mascot) | Complex visual narrative | Human illustrator or **Fal.ai** with strong prompts |
| Video editing for non-engine content (player reaction clips) | Frame-by-frame editing | **CapCut** or **Premiere** |
| Music composition | Generative audio | **Suno** (already discussed) |
| Voice acting | Audio | **ElevenLabs** (already discussed) |

### Net coverage estimate

Claude can handle **~60–70% of all design work** by writing code, specs, and orchestrating other tools. Remaining 30–40% needs:
- AI image generators (Fal.ai or HuggingFace) for hero visuals, ~5% of total
- Canva for thumbnails / social templates, ~10%
- Figma for premium brand polish, ~15%
- Optional Fiverr/freelance designer for logo finalization, ~5%

**With your available connectors (Canva, Unsplash, HF, Fal.ai, Higgsfield, ElevenLabs, Supabase, Vercel, Figma), the coverage rises to ~95%.** The only thing that truly benefits from human freelance is logo finalization (which is a $100–300 one-shot cost, not recurring).

---

## Part 7 — Recommended next 2 weeks (data-content-design)

### Week 1
- **Mon–Tue**: Re-sync `data/teams.json` from `soccer_national_teams` (correct codes, add missing qualifiers). Build the **data loader script** that pulls from Supabase + caches to JSON for the renderer. Subscribe to api-football.com Pro tier; start WCQ ingestion (background batch).
- **Wed–Thu**: Build **T1 League Table Race** engine — the biggest data-unlock template. Render 6 sample seasons (PL 2023/2024/2025, PD 2023/2024/2025). Pick the visually-strongest seed and ship as the first 6 daily posts.
- **Fri**: Define brand identity v1 — name, color, typography (Claude spec) + Fal.ai logo iteration. Render Remotion intro/outro stinger.

### Week 2
- **Mon–Tue**: Build **T3 Elo Trajectory** engine. Render Norway 2018-2026 and Cape Verde 2018-2026 (story-driven hopium loops). Build **T9 Steam Move** as proof of differentiator.
- **Wed–Thu**: WCQ ingestion finishes → build **T-WC-Qualifier-Journey** configs for all 48 nations. Pre-render 16 of them (top-rated story angles).
- **Fri**: Account creation, brand asset finalization, first batch ships.

### Cost during these 2 weeks
- api-football.com Pro: $50
- Suno Pro: $10
- ElevenLabs Creator: $22
- Epidemic Sound: $24
- Splice: $13
- Figma Pro (optional): $12
- Canva Pro (optional): $13
- Fal.ai pay-per-use: ~$20 estimated for logo + backgrounds
- Optional Fiverr logo: $100–300 one-time
- **Total**: ~$165–500 first month, ~$144 ongoing

---

## Open decisions

These gate the work — answers move us from planning to execution.

1. **Brand name** — pick from shortlist: `bracket.fc`, `xg.loops`, `the.plinko.report`, `pitch.predict`, `form.fc` (or other)
2. **Engine priority order** — confirm T1 League Table Race is the right first build (per data + audience analysis I'd say yes)
3. **API budget approval** — sign up for api-football.com Pro to unlock WCQ ingestion
4. **Logo path** — Fiverr ($100–300, ~3 days) vs DIY in Figma + Fal.ai (~2 hours, lower polish)
5. **Posting start date** — recommendation: target T-15 (May 27) to give 4 days of warm-up before scaling

# WC2026 Database — Overview for Builders

**Stack:** Supabase (Postgres 17), project `sharpflow` (`nfmejklpxcquzxqyqewv`)
**Scope:** 33 soccer tables. WC2026 starts June 11, 2026 — kickoff in 19 days from the snapshot date below.
**Snapshot date:** 2026-05-23
**Confederations covered:** UEFA, CONMEBOL, CONCACAF, CAF, AFC, OFC (all 6, full 48 qualifiers)

---

## The five datasets that matter most

### 1. National-team Elo (the time series goldmine)
- **`soccer_national_team_elo`** — 4,848 rows
- Daily/weekly snapshots of every national team's Elo rating from **2018-01-31 → 2026-05-23** (8 years)
- Columns: `team_code, snapshot_date, elo_rating, world_rank, confed_rank, source`
- **What it gives you:** every team's strength trajectory over 8 years — who rose (Norway, Morocco), who fell (Germany), who is peaking right now for WC2026
- **Current top 5:** ESP 2165, ARG 2113, FRA 2081, ENG 2020, POR/BRA 1984

### 2. WC2026 Monte Carlo simulations
- **`soccer_wc_simulation_probs`** — 48 rows (one per qualified team)
- Columns: `team_code, n_sims, p_group_only, p_reach_r32, p_reach_r16, p_reach_qf, p_reach_sf, p_reach_final, p_winner`
- **What it gives you:** the probability each team reaches each stage, computed from N simulations
- **Current favorites:** ESP 19.3% to win, ARG 12.7%, FRA 10.2%, ENG 5.6%, BRA 5.2%

### 3. 48 qualified nations + metadata
- **`soccer_national_teams`** — 48 rows
- Columns: `team_code, team_name, confederation, fifa_id, sofascore_team_id, qualified_2026, group_2026, current_manager, manager_since`
- **What it gives you:** the official roster of WC2026 — names, groups, managers, confederation, ID joins to external APIs

### 4. Match data (history + future fixtures)
- **`soccer_historical_matches`** — 7,496 rows from **2022-11-20 → 2026-04-04** (376 teams)
  - 45 columns including xG, shots, possession, corners, fouls, cards, h2h, referee, jsonb stats
- **`soccer_fixtures`** — 142 upcoming matches from **2026-04-04 → 2026-07-19**
  - Includes the entire WC2026 schedule with venue, group stage, matchday, plus model predictions (`home_win`, `draw`, `away_win`, `home_xg`, `away_xg`, `over_25`, `btts`)

### 5. Venues + weather (the underrated dataset)
- **`soccer_wc_venues`** — 16 rows (all 16 WC2026 stadiums across USA/Canada/Mexico)
  - `venue_name, city, country, elevation_m, june_high_c, july_high_c, humidity_pct, dome, timezone, surface, capacity`
- **`soccer_wc_venue_travel`** — 240 rows
  - Pairwise: `origin_venue, destination_venue, distance_km, flight_hours, timezone_change, altitude_diff_m`
  - **What it gives you:** "Team X must fly Y km between matches" — fatigue/jet-lag stories
- **`soccer_wc_weather_forecast`** — 256 rows
  - Daily forecast per venue: temp_max, temp_min, precip_prob, wind_max, humidity

---

## Secondary datasets

| Table | Rows | What it's for |
|---|---|---|
| `soccer_standings_snapshot` | 42,889 | League standings across competitions over time |
| `soccer_team_form` | 13,137 | Rolling form metrics (54 cols) per team per date |
| `soccer_computed_features` | 12,785 | Engineered ML features (26 cols) per match |
| `soccer_elo_ratings` | 13,137 | Club-level Elo (not just national) |
| `soccer_odds_history` | 2,040 | Historical bookmaker odds per match (36 cols) |
| `soccer_futures_markets` | 212 | Polymarket-style prediction markets — yes_price, implied_probability, volume |
| `soccer_predictions` | 30 | Model-generated match predictions vs actual outcomes (with Brier score, CLV) |
| `soccer_value_bets` | 42 | Edge picks: odds vs our_prob, EV, recommended stake, tier |
| `soccer_match_analysis` | 37 | Deep per-match jsonb: tactics, shotmap, player stats, weather, hedging guide |
| `soccer_match_context` | 28 | Per-match contextual metadata (30 cols) |
| `soccer_national_team_injuries` | 23 | Player injuries per team with expected return |
| `soccer_leagues` | 19 | League metadata |
| `soccer_referees` | 2 | Referee profiles (small dataset) |
| `soccer_team_aliases` | 37 | Name normalization across data sources |

**Empty-but-defined (waiting for data):** `soccer_market_outcomes`, `soccer_match_insights`, `soccer_model_runs`, `soccer_wc_squads`

---

## What this means in plain English

You have:
- 8 years of strength ratings for 48 nations (daily resolution) → time-series animations, "who's hot right now"
- The full WC2026 schedule + venue + weather + travel data → logistics stories
- Live Monte Carlo probabilities for every team's path → bracket viz, upset alerts
- 7,500 recent matches with xG, possession, cards → form deep-dives
- Live prediction-market prices → "the market says X, our model says Y" comparisons

---

## 12 project ideas (split by build size)

### Weekend builds (one person, < 2 days)
1. **"Path to the trophy" interactive bracket** — Click any team, see their simulated route + win probability at each stage. Pulls from `soccer_wc_simulation_probs`.
2. **National-team Elo race chart** (à la Flourish) — Animated bar chart of 48 nations climbing/falling 2018→today.
3. **Heat map: "Which stadium is the hardest?"** — Combine `soccer_wc_venues.june_high_c`, `humidity_pct`, `elevation_m`. Rank venues by player-suffering index.
4. **Travel-fatigue calculator** — Pick a team, show total km flown across their group-stage schedule using `soccer_wc_venue_travel`.

### Multi-week builds (small team)
5. **Daily "WC2026 Pulse" newsletter** — Auto-generated each morning: top Elo movers, injuries, weather, next-3-fixtures upset alerts.
6. **TikTok/Reels content factory** — The marble pieces we already shipped (battle royale, plinko, bracket). Add a new one per week using the same engine.
7. **Public-facing prediction site** — Your model vs Polymarket. "Free public odds, see where the market disagrees with the model."
8. **Manager dashboard** — Compare current managers (`current_manager`, `manager_since`) → tenure vs team performance trajectory.

### Bigger projects
9. **"Upset Index" model + Twitter bot** — Every fixture gets an upset-likelihood score. Bot posts predictions, then retro-grades them after.
10. **Personalized bracket app** — Users fill in predictions, scoring uses your simulated probabilities so picking favorites pays less than upsets (Brier-score style).
11. **Interactive map** — 16 venues across NA, click each → weather, capacity, matches played there, who's flying in from where.
12. **Sports-betting "where's the edge" SaaS** — Surface `soccer_value_bets` to subscribers with confidence tier + reasoning, track actual ROI via `soccer_predictions.clv_*`.

---

## Joins your friends will need

- `soccer_national_teams.team_code` → joins everything (Elo, simulations, injuries, fixtures)
- `soccer_fixtures.external_match_id` ↔ `soccer_historical_matches.external_match_id` (once matches finish)
- `soccer_wc_venues.venue_name` ↔ `soccer_wc_weather_forecast.venue_name` and `soccer_wc_venue_travel.origin_venue/destination_venue`
- `soccer_fixtures.id` (text) ↔ `soccer_predictions.fixture_id` ↔ `soccer_value_bets.fixture_id` ↔ `soccer_match_analysis.fixture_id`

---

## Access

- **Read-only Postgres** via Supabase. Anon key sufficient for read tables with RLS open.
- **External API joins:** `fifa_id`, `sofascore_team_id`, `fd_team_id` on `soccer_national_teams` let you pull badges, player photos, live data from third parties.
- **JSONB fields** in `soccer_match_analysis` (tactics, shotmap, player_stats) are ready to power any deep-dive UI.

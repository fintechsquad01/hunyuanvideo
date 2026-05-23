# Data Sources

## Polymarket (primary odds source)

Free, real-time, deep liquidity. Auto-updating implied probabilities.

- **Winner market**: https://polymarket.com/event/2026-fifa-world-cup-winner-595 — $1.1B traded
- **Games (per-match)**: https://polymarket.com/sports/fifa-world-cup/games
- **Group winners**: e.g., https://polymarket.com/event/fifa-world-cup-group-l-winner

API: Polymarket has a public CLOB API. For our cadence (manual snapshot weekly + reactive on big moves), a 5-second manual copy is faster than building an integration. If we scale to daily auto-rendered content, scrape via their REST endpoints. **No API key required for read-only public market data.**

Affiliate program: https://docs.polymarket.com/affiliates — partner program available; revenue split on trades by referred users.

## Kalshi (secondary odds source)

Regulated, US-based. Different audience (more US-centric, less crypto-native).
- https://kalshi.com — search for FIFA World Cup markets

## FIFA official sources

- **Bracket / schedule**: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026
- **Bracket Predictor (FIFA's own)**: launched May 2026
- **Risk**: FIFA aggressively enforces IP. Use only schedule data and team codes. Never reuse FIFA logos, official posters, or team crests.

## Bracket predictor tools (competitor recon)

- https://www.fifaschedule.com/ — clean simulator UI
- https://worldcuppass.com/simulator/ — 48-team bracket builder
- https://bracket2026.com/en/predictor — free predictor
- https://cup-predictor.com/ — interactive tool
- https://copafootball.com/pages/world-cup-predictor — used as reference
- https://insights.betfred.com/football/fifa-world-cup/world-cup-predictor/ — sportsbook predictor (gambling angle)
- https://theworldcupguide.com/world-cup-2026-group-and-bracket-predictor/

These are our **competitor set** for the bracket-tool product (if we ever build a paid web tool). Their content distribution is also worth studying — most don't have a strong social presence, which is our wedge.

## Sportsbook odds (US-licensed)

For cross-referencing Polymarket implied probabilities. Numbers move together but not identically — Polymarket sometimes leads on geopolitical / non-sports news.
- DraftKings, FanDuel, BetMGM, Caesars (US)
- bet365, William Hill (UK)
- Bet Brazil, Stake (LatAm)

## Football data (not odds)

- **Match results / scorers / lineups**: api-football.com (paid tiers from $19/mo; free tier covers basic data)
- **Player rankings / stats**: sofascore.com, fbref.com (free, no API but scrapable)
- **Squad lists**: transfermarkt.com (gold-standard; scrapable)

## Cultural data (for WC7 Food Race)

- National dishes per country — Wikipedia "national dish" list; Britannica
- Use single-emoji or simple text labels; avoid copyrighted food imagery

## Update cadence

| Source | Cadence | Owner |
|---|---|---|
| Polymarket winner odds | weekly pre-tournament, daily during | manual |
| Polymarket per-match | per-match | manual or scripted |
| FIFA schedule | locked once draw is set | no update needed |
| Match results | live during tournament | api-football or manual entry |
| Polymarket affiliate stats | weekly | dashboard pull |

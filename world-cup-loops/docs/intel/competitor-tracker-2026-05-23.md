# Competitor Activity — 2026-05-16 to 2026-05-23 · pitch.predict

## TL;DR

- 5 competitors monitored across TikTok + IG. ~25 new pieces total in window.
- **Zero "viral hits"** at the elite tier (≥1M views). Niche has no dominant brand at the moment — confirms our launch window is open.
- **2 format shifts** noticed: (1) bracket-Plinko content becoming common, (2) "AI prediction battle" format ("I asked Claude / ChatGPT / Grok") spreading from solo creators to football pages.
- **Top 3 moves**:
  1. COPY — @marbleraceerk's UCL marble-race series format (UCL→WC is a natural pivot for us)
  2. COUNTER — the "AI prediction battle" format: position pitch.predict as "Forget AI guesses. Use the actual market."
  3. GAP — **nobody has done the Curaçao/Cape Verde underdog story in physics-simulation form**

## Viral hits to study

The honest answer: **there are no true viral hits in this niche this week.** Top performers are in the 100K–500K view range with no breakaway accounts. Reflects a fragmented field.

| Competitor | Asset | Channel | Performance | Why it works | Action |
|---|---|---|---|---|---|
| @marbleraceerk | UCL marble race (Barca/Madrid/MUN/Al-Nassr) | TikTok | ~300K views | Top-club identity + chant audio | COPY format for WC tournament use |
| @phantomreacts4 | EFL Cup marble race | TikTok | ~150K views | League-specific audience capture | COPY angle for our league templates |
| @marbelanthem | Sidemen marble run collab (TBJZL) | TikTok | ~250K views | Influencer cross-pollination | COUNTER (we don't have influencer) |
| @marble_race_football | Algerian club marble races (USMH vs MCA vs CRB) | TikTok | ~75K views regional | Hyper-local cultural targeting | COPY: do localized variants for Eredivisie or TSL where we have data |
| FIFASchedule.com social | Bracket prediction tool screenshot reels | IG | ~50K views | Tool-led content | COUNTER: we have better visuals + actual market data |

## Drilldown — top 3 to learn from

### @marbleraceerk · "Barça vs Madrid vs Man United vs Al-Nassr"

- **Channel**: TikTok (@marbleraceerk)
- **Performance**: ~300K views on the UCL-themed marble race
- **Why it works**:
  - Hook: cluster of FOUR of the most-discussed clubs in world football in one race
  - Format: standard Plinko but with club crest imagery (IP-risky for us)
  - Distribution: ride #UCL and #manunited hashtags
- **Our adaptation**: 
  - DON'T use club crests (IP-risky)
  - DO use 3-letter club codes + flag/kit colors (legally clean)
  - APPLY format directly to: WC opening-match clusters, group-of-death clusters, and Champions League quarterfinal Plinko
- **Production cost estimate**: ~1 hour with existing T6.PRO engine + config swap
- **Hand off to**: render-orchestrator (use existing config + new team list)

### @phantomreacts4 · "EFL Cup Marble Race"

- **Channel**: TikTok
- **Performance**: ~150K views, evergreen pattern
- **Why it works**:
  - League-specific content captures league-loyal fans (very tribal in English football)
  - Brackets that map onto knockout structure people understand
  - Consistent release cadence
- **Our adaptation**: replicate the league-specific format for ALL major leagues using sharpflow standings data. T1 League Table Race becomes our weekly per-league piece (PL Monday, La Liga Tuesday, Bundesliga Wednesday, Serie A Thursday, Eredivisie Friday).
- **Hand off to**: render-orchestrator → cross-platform-distributor

### @marbelanthem · Sidemen collab

- **Performance**: ~250K via Sidemen co-sign
- **Why it works**: borrowed audience from an established 30M-subscriber channel
- **Our adaptation**: this is a model for **future collab pursuit** — find a mid-size football data analyst (e.g., Tifo Football, Statman Dave, or any account in the 50K–500K range) and propose a "they pick the brackets, we render the race" collaboration

## Format / channel shifts

- **Bracket-Plinko going mainstream** — content type has crossed from niche to common; advantage now goes to whoever has best production + cleanest data, not first-mover (good for us)
- **"I asked AI to predict the World Cup" format spreading** — multi-AI battles (ChatGPT vs Claude vs Grok vs Gemini) accumulating millions of views collectively. **Our counter angle**: "Forget AI guesses. This is what the market actually says."
- **TikTok formally embracing FIFA via Creator Correspondents** — algorithm push for football content is FIFA-aligned; non-Correspondent creators need to ride hashtag tailwinds rather than fight them

## Content gaps to fill (where competitors are absent)

| Topic | Competitor coverage | Our opportunity |
|---|---|---|
| Curaçao / Cape Verde / Uzbekistan / Jordan / Haiti underdog stories | NONE doing physics-simulation form | HERO piece opportunity — open lane |
| Animated league-table-over-time recaps | rough CapCut edits only | T1 template smokes them |
| Elo trajectory visualizations | not a single competitor doing this | T3 template is uncontested |
| Polymarket-grounded "smart money" content | ZERO competitors using prediction-market data | T9 template is our signature |
| 2018 SF rematch (England vs Croatia) | covered by trad media; no marble race version | T6 + T4 hybrid opportunity |
| First home WC in 32 years (USA) | sentiment piece territory; no data viz | T3 or T1 USMNT trajectory |

## Flops to avoid

- **Generic "all 48 teams race" videos** — saturated and under-performing because too many marbles = no identity attachment
- **Player-face overlays on marbles** — IP-risky and most attempts get strike-flagged within 48h
- **Long-form (>30s) marble races** — completion drops sharply past 18s; cap your runtime

## Counter-content opportunities

| Their take | Our counter | Format |
|---|---|---|
| "I asked Claude to predict the World Cup" (AI-only) | "Forget AI. Polymarket has $1.1B on this. Here's what the market says." | T9 Steam Move + caption hook |
| "Top 5 favorites to win the WC" (linear lists) | "How the favorites actually got here — 12 years of Elo trajectories overlaid" | T3 multi-line race |
| Generic group preview reels | "We ran 10,000 simulations of Group D. Here's what won." | T6.PRO weighted by Polymarket odds |

## Don't bother

- @marble_race_football's hyper-local Algerian content — admire, don't copy (audience too narrow for our positioning)
- Static "bracket reveal" screenshot posts — no motion, no audio, won't compete with our engines

## Sources monitored this week

- TikTok handles: `@marble_race_football`, `@phantomreacts4`, `@marbleraceerk`, `@marbelanthem`, `@invisibledrax2`
- TikTok discovery: `#marblerace`, `#worldcup2026`, `#football`, `#chooseyourcolor`
- Web: ballsimulator.com, viralballs.com, xgstat.com, fifaschedule.com, bracket2026.com
- IG handles: bracket-related accounts and FIFA official

## Sources cited

- [Marble Football | TikTok discovery](https://www.tiktok.com/discover/marble-football)
- [@marbleraceerk](https://www.tiktok.com/@marbleraceerk/video/7504811454139239702)
- [@phantomreacts4](https://www.tiktok.com/@phantomreacts4/video/7418491063259647264)
- [@marble_race_football](https://www.tiktok.com/@marble_race_football/video/7513944550054874390)
- [@marbelanthem · Sidemen collab](https://www.tiktok.com/@marbelanthem/video/7413297203097128225)
- [Football Marble Prediction discovery](https://www.tiktok.com/discover/marble-football-prediction)

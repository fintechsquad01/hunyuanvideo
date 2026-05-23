# zen-loops — Progress & Memory

Living document. Updated at the end of each working session. Captures *what's been built*, *what worked / didn't*, and *what's next* — so future sessions can resume without reloading the full chat history.

## Current state (snapshot)

**Branch**: `claude/zenshapes-strategy-analysis-xZzbe` on `fintechsquad01/hunyuanvideo` (subdirectory `zen-loops/`)
**Status**: pre-launch. Content engine works end-to-end with audio. Zero videos posted to real accounts.

## What's been built

### Engines (working, render to 1080×1920 MP4)
- `engines/python_numpy/bouncing_spheres.py` — ambient bouncer (baseline)
- `engines/python_numpy/marble_drop.py` — **Plinko marble race with identity labels** (flagship template)
- `engines/python_numpy/ring_expansion.py` — ball-in-growing-ring with collision-driven melody + song-reveal payoff
- `engines/audio_reactive/collision_audio.py` — zero-dependency sine-envelope synth, 11 public-domain melodies (twinkle, ode_to_joy, fur_elise, pachelbel, greensleeves, frere_jacques, mary_had_lamb, old_macdonald, amazing_grace, happy_birthday, minor_arp)
- `overlays/text_overlay.py` — auto-fit fonts, emoji stripping, translucent text bands

### Plinko variants shipped (configs ready to render)
- `marble_drop_months_01.json` — birth months
- `marble_drop_zodiac_01.json` — zodiac (3-letter codes)
- `marble_drop_worldcup_01.json` — 12 national team codes
- `marble_drop_stocks_01.json` — 10 stock tickers

### Ring-expansion variants shipped
- `ring_expansion_twinkle_01.json`
- `ring_expansion_furelise_01.json`
- `ring_expansion_pachelbel_01.json`
- `ring_expansion_happybirthday_01.json`

### Docs (read these to ramp back up)
- `docs/strategy.md` — full playbook, "Identity > Zen" thesis, 30-day roadmap
- `docs/content-archetypes.md` — 4 archetypes with variant matrix
- `docs/mobile-game-spec.md` — phase-2 game (build trigger: ≥10K IG + ≥0.5% comment-to-view sustained 14 days)
- `docs/audio-library.md` — three-tier licensing (PD / royalty-free / IP-risky)
- `docs/idea-backlog.md` — 25 reverse-engineered format candidates with primitive mapping

### Pipeline
- `generate_video.py --config configs/<name>.json` → produces `output/<id>.mp4` with audio muxed via imageio-bundled ffmpeg when the engine reports collisions
- Verified: 1080×1920 / 30fps / 12–16s / H.264 + AAC

## What worked

- The polyglot scaffold (Python prototyping lane + Unity production lane planned + AI-video lane for textures) keeps options open
- The Plinko marble_drop engine generalized cleanly — adding a new identity dimension is 60 seconds of config work
- Collision-driven sine synthesis was simpler than expected, eliminated need for any audio library beyond stdlib `wave`
- Song-reveal payoff transforms the ring engine from "ambient bouncing" to a real "guess the song" format

## What we explicitly didn't build (and why)

- **Unity production engine** — gated on real posting data; not worth the cost until format validates
- **`scheduling/cross_post.py`** — IG/TikTok/YT auto-poster; manual posting recommended for first 2 weeks until accounts have trust history
- **`analytics/pull_metrics.py`** — defer until first 10 posts produce data
- **HunyuanVideo for tactile/gummy textures** — separate lane, batch-generate later
- **Mobile game** — phase 2 only after audience proves out
- **More archetypes from idea-backlog.md** — held until current archetypes validate

## Honest assessment

The biggest risk now is **over-engineering before validating**. We have working engines for the two dominant viral formats in the niche (Plinko race + guess-the-song). The next 10× is *posting*, not coding.

**Priority order from here**:
1. Post existing renders to IG/TikTok/YT for 7 days → measure
2. Suno Pro subscription → 5 owned original melody hooks (transcribed via Spotify Basic Pitch)
3. Identity dimension that nobody else owns (the differentiator question)
4. If engagement validates → start Unity production lane + analytics
5. If engagement validates AND audience grows → mobile game

## Open questions

- Which identity dimension wins for our audience? (months / zodiac / world cup / stocks / something else)
- Does the song-reveal payoff lift completion rate over the silent ring expansion? Needs A/B test.
- Suno commercial license terms — verify before scaling
- Cross-platform attribution — need utm_source-style query params in bio link to track which platform drives funnel best

## Related projects

- `world-cup-loops/` — tournament-themed sister project; scaffolded in May 2026 for the FIFA World Cup 2026 launch window (June 11 – July 19, 2026). See `world-cup-loops/PROGRESS.md` for details.

## How to continue

1. Read this file
2. Read `docs/strategy.md` and `docs/content-archetypes.md`
3. Check git log to see recent commits
4. Render any config with `python generate_video.py --config configs/<name>.json` to verify the pipeline still works
5. If the user wants to ship new variants: copy an existing config, change labels + palette + audio, render. No engine changes needed for most variants.

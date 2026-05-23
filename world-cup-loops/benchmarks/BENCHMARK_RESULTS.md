# Engine Benchmark — Curaçao gap-reveal shot

**Date**: 2026-05-23
**Test**: Shot 5 from `storyboards/curacao_gap_reveal.md`
**Common spec**: 3.66 seconds (110 frames @ 30fps), 1080×1920, brand chrome compliant

## Results

| Engine | Setup time (cold) | Render time | Output size | Visual ceiling | Verdict |
|---|---|---|---|---|---|
| **Custom Python** (Pillow) | 0 — already installed | 8s | 349 KB | LOW — "spreadsheet" | Keep for physics (Plinko, Ring); too limited for typography-heavy stat reveals |
| **Manim** | 20 min (LaTeX + Anton/Inter + 13 deps) | 8.5s | 280 KB | MID — fights 9:16 | **SKIP for our use case.** Manim's coordinate system + frame ratio is designed for 16:9 math-classroom video. Adapting to vertical mobile is constant friction. |
| **D3 + Playwright** | 5 min (Playwright + headless Chromium) | 16s | 510 KB | **HIGH** | **WINNER for chart/typography pieces.** Full CSS control, brand-font rendering perfect, design-system tokens map 1:1. |
| **Remotion** | Blocked in this remote env | n/a | n/a | High (per docs) | Chrome version compatibility issue here. Should work on local Mac. Worth re-testing there. |

## Why D3 + Playwright wins

1. **Native CSS = design-system parity.** The `colors_and_type.css` tokens from Claude Design map directly to `<style>` rules. No "approximate to my engine's idioms" lossy translation.
2. **Real font rendering.** Anton, Inter, Roboto Condensed all render with full anti-aliasing identical to what users see in a browser.
3. **Animation control is granular.** JavaScript `renderFrame(N)` lets us script every property per frame. No engine assumptions about transitions.
4. **Iteration speed.** Edit HTML → re-run script → 16s render. Same iteration loop as web dev.
5. **Easy to combine with our data layer.** Same Python that queries Supabase generates the config; HTML reads from it; no language boundary.

## Why custom Python keeps a role

Plinko + Ring physics is genuinely simpler in NumPy. Particle systems, custom collision detection, sound-triggered events don't translate cleanly to CSS animations. **The split**:

- **Custom Python (Pillow + ffmpeg)**: physics-simulation engines (marble_drop_pro, ring_expansion)
- **D3 + Playwright**: chart-style + typography-led engines (elo_field-v2, gap-reveal, league-table-race, elo-trajectory, steam-move)

## Why Manim is the wrong choice for us

Manim is brilliant for 3Blue1Brown-style math videos in 16:9. For 9:16 vertical social with brand-system-driven typography, it's adding friction without offering anything D3+CSS doesn't do better.

Specific issues seen in the test:
- Frame coordinate system assumes 16:9 landscape; vertical 9:16 requires manual frame_width recalculation
- Built-in `DecimalNumber` requires LaTeX install (Manim Tex pipeline)
- Layout helpers (`to_edge`, `next_to`) overlap on vertical when text sizes are mobile-scale
- `Text(font="Anton")` works but the layout fights you

## Why Remotion is on hold (not killed)

Remotion *should* be elite for our use case — React + browser rendering means same advantages as D3+Playwright. But in this remote env:
- Chrome binary version blocked old-headless mode
- `@remotion/google-fonts` triggers host allowlist errors
- Asset bundler hits `Host not in allowlist` in `read-file.js`

These are setup issues, not architectural ones. **Recommend re-testing Remotion on the local Mac** — it ships with bundled Chrome and should "just work". If it does, D3+Playwright vs Remotion is a real choice (Remotion has better composition for complex multi-clip videos; D3 has lower barrier to entry).

## Architecture lock

**Pitch.predict rendering stack (FINAL):**

```
Data (Supabase + Polymarket)
    ↓ Python data_layer/
JSON config (per piece)
    ↓
Engine selector:
  ├── Custom Python (Pillow)   — physics: marble_drop_pro, ring_expansion
  ├── D3 + Playwright          — charts: elo_field, gap_reveal, table_race, trajectory, steam_move
  ├── Remotion (eventually)    — composition: intro/outro stinger, multi-shot pieces
  └── Higgsfield (premium)     — cinematic: stadium hero shots, big tournament intros
    ↓
ffmpeg mux (audio + intro/outro stinger)
    ↓
Final MP4
    ↓
cross-platform-distributor → IG / TikTok / YT Shorts
```

## What the storyboard taught us (separate from engine choice)

The shot list in `storyboards/curacao_gap_reveal.md` is more important than the engine selection. The same engine produces garbage with no storyboard and a banger with one. Going forward, **every piece gets a storyboard.md before any code is written.**

## Files in this benchmark

- `manim_gap.py` + `manim_gap.mp4` — Manim attempt (layout broken, kept as reference)
- `d3_gap.html` + `d3_gap.mp4` — **the production-quality result**
- `render_d3.py` — Playwright render driver
- `remotion/` — Remotion scaffold (blocked in this env)
- `BENCHMARK_RESULTS.md` — this file

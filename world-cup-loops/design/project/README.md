# pitch.predict — Design System

> **Brackets that play themselves.**

`pitch.predict` is a football data-visualization brand that turns live odds (Polymarket), Elo ratings, and historical league data into **15-second marble-race videos** for TikTok / Instagram Reels / YouTube Shorts. Pre-renders bracket simulations for the FIFA World Cup 2026, Champions League, and Europe's top-5 leagues. **Voice: FiveThirtyEight rigor × ESPN morning-show pace** — authoritative-playful, never breathless.

This repo is the design system that powers every surface: vertical 9:16 videos, profile + banner imagery across four platforms, YouTube thumbnails, the landing page, and (phase 2) a mobile game.

---

## Sources used to build this system

- **GitHub** — `fintechsquad01/hunyuanvideo`, branch `claude/zenshapes-strategy-analysis-xZzbe`
  - `world-cup-loops/docs/brand-system.md` — colors, type, voice
  - `world-cup-loops/docs/strategy.md` — positioning, posting cadence
  - `world-cup-loops/docs/format-library.md` — 8 video archetypes (WC1–WC8)
  - `world-cup-loops/docs/data-content-blueprint.md`, `data-sources.md`, `content-calendar.md`
  - `world-cup-loops/PROGRESS.md` — current state of the product
- **Project brief** — supplied in the create-design-system prompt (color hexes, type stack, video chrome spec, social asset list)

Reader: if you have access to the repo, the docs above are worth reading directly — they capture the strategic intent behind the visual decisions.

---

## What this brand has to do, visually

1. **Stop a thumb scroll in 0.5 seconds.** Vertical video, high-contrast hook band, country-flag-colored marbles, instant data payoff.
2. **Look more authoritative than a meme account.** This is a numbers-first brand. Roboto Condensed tabular nums, no emoji clutter, no breathless caps-lock copy.
3. **Stay recognizable across watermark, profile pic, and thumbnail.** A single literal-bracket icon `[•]` does all three jobs.
4. **Be football-coded without infringing on FIFA marks or team crests.** Country flag colors only. Pitch green + FIFA yellow as chrome.

---

## Index — what's in this folder

```
README.md                  ← you are here. read this first.
SKILL.md                   ← agent-skill entry point (used by Claude Code etc.)
colors_and_type.css        ← all design tokens (CSS variables) + semantic classes
assets/
  logo-lockup.svg          ← full horizontal lockup (icon + wordmark, light)
  logo-lockup-dark.svg     ← same, dark variant
  logo-icon.svg            ← square icon only (1024-safe; profile pic safe)
  logo-icon-mono.svg       ← single-color icon for watermarks
  logo-wordmark.svg        ← wordmark only (Anton-style, tightly tracked)
  marble-{country}.svg     ← canonical marble look (a few sample countries)
  bg-pitch.svg             ← stadium-pitch background (Plinko engines)
  bg-arena.svg             ← dark-arena vignette (ring-expansion engine)
  bg-chart.svg             ← chart-paper grid (league-table race)
  bg-track.svg             ← finish-line track (horizontal score race)
preview/                   ← Design System tab cards. one HTML per card.
ui_kits/
  landing/                 ← single-page web landing site
  video_chrome/            ← lower thirds, hook/CTA bands, winner banner, watermark
fonts/                     ← (Google Fonts loaded by CDN; no local TTFs needed)
```

> Fonts: all five families (Inter, Anton, Bebas Neue, Roboto Condensed, Barlow Semi Condensed) are loaded from Google Fonts CDN via `colors_and_type.css`. **No font substitution required** — all are commercially licensed for digital use.

---

## CONTENT FUNDAMENTALS

How copy is written for `pitch.predict`. Apply to every video caption, on-screen hook, CTA band, landing page block, social post.

### Voice — authoritative-playful
Two reference points: **FiveThirtyEight** (data-led, calm authority) and **ESPN morning show** (clipped energy, conversational). The brand is the smart friend at a watch party — not the screaming one.

### Person & address
- Third-person + **"you"** for the read. "**The numbers say Spain's marble survives 60% of simulations.**"
- Imperative on CTAs. "**Comment your pick.**" "**Tag a friend who's wrong.**"
- Never first-person. Avoid "we" / "us" except in legal/footer copy.

### Casing
- **Hook band** (top 7%): ALL CAPS, Inter Bold or Anton. Tight tracking (-0.02em).
- **CTA band** (bottom 7%): ALL CAPS.
- **Winner reveals**: ALL CAPS, Anton.
- **Body copy / landing page paragraphs**: sentence case.
- **Numerics**: as-is ("60%", "R32", "QF"). Always **tabular-nums** so they don't jitter frame-to-frame.

### Numbers & units
- Always show the source: **"Polymarket: France 18%."** "**Plinko: France one of every five runs.**"
- Round percentages to whole numbers in chrome (no "18.4%"). Use the precision in captions if it matters.
- Round indicators are abbreviations: **R32 / R16 / QF / SF / FINAL**.
- Always show country **3-letter code** beside flag colors (BRA, ARG, ESP, FRA…). Never long-form country names in chrome.

### Emoji
**Almost never.** This brand reads numerate, not breathless. Two exceptions:
- **WC7 Country-Food Race** — cultural food emoji (🍕 🍣 🫖) as marble labels. The whole format is the joke.
- **Landing-page footer social icons** — actual platform marks, never the emoji versions.

### Things to say / things to never say

| ✅ DO | ❌ DON'T |
|---|---|
| "The numbers say Spain's marble survives 60% of simulations." | "OMG won't BELIEVE who wins this race 🤯🤯🤯" |
| "Polymarket: France 18%. Plinko: France one of every five runs." | "BET ON SPAIN!" |
| "Group D is brutal. Argentina favored. Egypt's been live in friendlies." | "Group of DEATH! Who advances?!?!" |
| "Comment your pick before kickoff." | "FOLLOW NOW OR REGRET IT 🔥🔥🔥" |
| "Polymarket says X. Plinko says Y." | "GUARANTEED WINNER 🤑" |
| "Fan poll / prediction / simulator" | "Odds / wager / bet" (platform-risky) |

### Legal-adjacent language (important)
**TikTok and IG flag gambling-adjacent content aggressively.** Reframe:
- Don't say "odds." Say "**prediction market**" or "**fan consensus**."
- Don't say "bet." Say "**pick**" or "**simulator says**."
- Don't say "wager." Say "**Plinko says**" or "**the numbers say**."
- Polymarket may be referenced as "the world's largest prediction market" but never "where you bet on the World Cup."

---

## VISUAL FOUNDATIONS

### Color
Pitch green `#0f9d58` is the brand chrome anchor. FIFA yellow `#ffd400` does CTA + winner highlights only — it's rare on purpose, so it lands when it appears. Video backgrounds are a **vertical gradient from pitch top `#0d2818` to deep `#020a05`**, never solid black. Red `#ff4d4d` is eliminations only. Country flag colors are allowed to override **marble fills** but never the chrome layer — the bracket icon, hook band, CTA band, and winner banner stay brand-coded.

Tournament-specific palettes layer on top (Group D = Argentina sky-blue, Uruguay light-blue, Switzerland red, Egypt red) but only as marble fills + winner banner backdrops.

### Type
Five families, each with one job. **Don't mix.**

| Job | Family | Weight | Notes |
|---|---|---|---|
| Hook band (top of screen) | **Inter** | Bold (700) or **Anton** Regular | ALL CAPS, tracking -0.02em |
| Statistics / scores / counter | **Roboto Condensed** Bold or **Barlow Semi Condensed** Bold | 700 | Tabular nums always |
| Body / CTAs / landing copy | **Inter** | Semibold (600) | Sentence case for body, ALL CAPS for CTA |
| Reveal banner | **Bebas Neue** | Regular | "WINNER", "CHAMPIONS", "R32" header |
| Winner team name | **Anton** | Regular | Huge — 140px in 9:16 video |

### Backgrounds & textures
- **Pitch gradient** (default): vertical `#0d2818 → #020a05`. Subtle, never busy.
- **Subtle pitch stripes** allowed under Plinko engines — ~3% opacity white horizontal lines.
- **Chart paper** for league-table race — broadcast-graphics feel, faint grid at 2% opacity.
- **Dark arena vignette** for ring-expansion — radial dim from center, ambient white particles.
- **No photographic backgrounds.** No stadium photos. No player photos. Risks IP and clutters the data layer.
- **Translucent black bands** (`rgba(0,0,0,0.60)`) under all on-screen text. Always. Even in still imagery. This is the single most important chrome rule — it's what makes the brand legible across busy match footage.

### Animation
- **Snappy, broadcast-y, never floaty.** Default duration **240ms**. Default easing **cubic-bezier(0.16, 1, 0.3, 1)** (a fast-out / slow-in).
- **Intro stinger (0.5s)**: green flash → icon bounces in via `cubic-bezier(0.34, 1.56, 0.64, 1)` → settles into top-left watermark slot.
- **Outro stinger (0.6s)**: scene dims to 35% → wordmark fades in → "Follow daily." sub-line.
- **Marble physics**: real gravity. Never fake interpolation. Bounce energy decays naturally.
- **Number tickers**: count-up using tabular-nums, never blur or scramble.
- **No drifting parallax. No bobbing icons. No subtle pulses except the winner glow.**

### Hover & press states (web / mobile UI only)
- **Hover**: 8% brightness up, optional `--pp-glow-yellow` on yellow CTAs.
- **Press**: `translateY(1px) scale(0.99)` — broadcast-buttoned, not bouncy.
- **Focus ring**: 2px solid `--pp-green-bright` with 4px offset. No browser default.

### Borders, lines, dividers
- Lines are **rgba(255,255,255,0.10)** by default, **0.22** for emphasis.
- Dividers are 1px, never 2. The data does the structuring; lines just hint.
- The one exception: **yellow 2px bottom border** on the WINNER banner. That's a signature.

### Shadows & glows
- **Card shadow**: `0 4px 16px rgba(0,0,0,0.45)` + 1px inner highlight on top. Cards float, don't slab.
- **Champion glow**: `0 0 16px #ffd400, 0 0 36px rgba(255,212,0,0.55), 0 0 80px rgba(255,212,0,0.25)` — three stops, never a single stop. This is the moneyshot effect.
- **Green glow**: used sparingly on the live indicator and the "advance" flicker.
- **Red glow**: elimination flash, single frame.
- **No drop shadows on text** except on the WINNER reveal.

### Transparency & blur
- Translucent black bands `rgba(0,0,0,0.60)` for text legibility — **never** `backdrop-filter: blur()`. Blur drops frames on TikTok's encoder.
- Card surfaces inside the landing page use **5–8% white over the pitch gradient** instead of blur.

### Corner radii
- **2px** — badges, odds chips, broadcast-y. Tight on purpose.
- **4px** — buttons, CTAs.
- **8px** — cards.
- **12px** — large cards / hero modules.
- **Pill (999px)** — round indicators (R32, QF, SF, FINAL), live dots, status chips.
- **Never** big round bubbles. This is a numbers brand, not a wellness brand.

### Cards
Card recipe (landing page, social asset previews): **8px radius, `#11261b` surface (5% white over pitch gradient), 1px line at 10% white, 4px-down 16-blur black shadow at 45%, 1px inset top highlight at 4% white**. That inset highlight is what makes the cards feel "screen-lit" instead of slabby.

### Imagery & video color
- **Warm-cool split**: the field is warm green at the top, going cool/black at the bottom. Mirrors a stadium under floodlights.
- **No grain. No film texture.** This brand is digital-broadcast, not vintage.
- **Country flags rendered as flat color blocks**, never as actual flag images. (IP-safe and consistent across the system.)
- **Player imagery: forbidden** in static brand chrome. Allowed in social posts only via official tournament press handouts.

### Layout rules
- **Top 7% reserved** for hook band. Never put data there.
- **Bottom 7% reserved** for CTA band. Never put marble action there.
- **Top-left**: brand watermark (40% opacity icon).
- **Top-right**: counter / odds badge (Roboto Condensed Bold).
- **Bottom-left**: round indicator (R32 / R16 / QF / SF / FINAL).
- **Bottom-right**: empty or sponsor slot (post-brand-deal).
- Marble action stays inside the **central 70%** vertical region.

---

## ICONOGRAPHY

**The brand barely uses icons.** The data + flag colors + marbles do the iconographic work. Where icons appear, the rules are:

- **System**: [Lucide](https://lucide.dev) at **2px stroke**, **24px** default size. Monochrome, white at 70% opacity by default; pitch green on hover. Loaded from `https://unpkg.com/lucide-static/` CDN — see `ui_kits/landing/`.
- **The bracket icon `[•]`** is the *only* custom mark and appears as the brand watermark / favicon / app icon.
- **Country representation**: never flag emoji `🇧🇷`. Always a **flat-color flag block** (`assets/marble-bra.svg` pattern) plus 3-letter code (`BRA`). Consistent across rendering pipelines and IP-safe.
- **Platform marks** (TikTok/IG/YT/X) in the footer: official monochrome SVGs from each platform's brand kit. Not emoji.
- **Emoji policy**: forbidden in chrome. Allowed only in WC7 country-food race format (🍕 🍣 🫖) where the joke *is* the emoji.

**Substitution note (flagged for user):** Lucide is the closest CDN-available match to the 2px-stroke broadcast feel we want; if you'd prefer Heroicons or a custom set, swap the CDN import in `ui_kits/landing/index.html`. The system tolerates any 2px-stroke monochrome set.

---

## What's NOT in this design system (yet)

- **Per-team sponsor templates** — come after brand deals land.
- **Mobile game UI** — phase 2; will need its own spec.
- **Print collateral** — none planned; digital-only brand.
- **Live odds widget visual states** (loading / stale / error) — placeholder only in landing kit; needs Polymarket API integration spec.

---

## Open questions for the user

1. **Logo concept** — built per brief (bracket `[•]` with marble inside, Anton wordmark). If you prefer a different bracket shape (square vs round vs angled corners), say so and I'll iterate.
2. **Naming lockup** — currently rendered as `pitch.predict` lowercase with a center dot. Alternates considered in brief (`bracket.fc`, `xg.loops`, `the.plinko.report`). If you've finalized handles, confirm.
3. **Sponsor slot** treatment — bottom-right of video chrome is reserved but undesigned. Want a fixed "sponsored by" capsule mock?
4. **Mobile game (phase 2)** — separate design pass when you're ready.

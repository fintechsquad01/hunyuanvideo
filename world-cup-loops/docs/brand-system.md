# Brand System — bracket.fc (working name)

**Status**: draft. Name not finalized — see shortlist in chat. Update once locked.

The brand is the most leverageable asset we have. Every render, every caption, every notification uses it. Done well, the brand makes the same MP4 hit harder than a competitor's identical MP4. Done generically, the audience scrolls past us in favor of the established names.

## Positioning

**One-liner**: *"Brackets that play themselves."*

**Long form**: The football prediction-market visualizer. We take the world's deepest football data — Polymarket, sportsbooks, league tables, historical results — and turn them into 15-second marble races people can't scroll past.

**Audience target**: football-engaged people who already think in odds — the "did Spain cover?" / "is Arsenal really top of the table?" crowd. The casual ASMR-overflow audience is the bonus, not the target.

## Naming

Working: **bracket.fc**

Alternates (see chat shortlist): `xg.loops`, `the.plinko.report`, `pitch.predict`, `form.fc`

Handle must be identical across IG / TikTok / YT / X. If `bracket.fc` is taken on any of the four, fall back to `bracket.fc.official` or `bracketfc.io`.

## Color system

| Role | Hex | Use |
|---|---|---|
| Brand primary | `#0f9d58` | Logo, accent moments, "advance" indicator (football green, slightly muted) |
| Brand secondary | `#ffd400` | CTAs, winner highlights, "goal" indicator (FIFA-style yellow) |
| Background — deep | `#0a1a14` | Default video background (football-pitch derived dark green) |
| Background — gradient bottom | `#020a05` | Bottom of vertical gradients (depth) |
| Surface — overlay band | `#000000` @ 60% | Hook/CTA text background bands |
| Text — primary | `#ffffff` | Hooks, labels, body |
| Text — danger | `#ff4d4d` | "Eliminated", "Lost", "Out" |

Tournament-specific palettes layer on top — team flag colors override marble fills, but brand primary/secondary stay in the chrome (counter, banner, intro stinger).

## Typography

| Use | Family | Weight |
|---|---|---|
| Hooks (top of screen) | Inter | Bold |
| Stats / scores / counter | Roboto Condensed or Barlow Condensed | Bold |
| Body / CTAs | Inter | Semibold |
| Reveal / banners | Anton or Bebas Neue | Regular (already condensed) |

Fall back to DejaVuSans-Bold if Inter not available (which is our current overlay default).

## Logo + wordmark

**Concept**: a literal bracket shape `[` ` ]` with a marble inside, suggesting the format's mechanic. Wordmark in Bebas Neue or Anton, all-caps, tightly tracked.

**Variants needed**:
- Full lockup (icon + wordmark) — for profile images, intro stingers
- Icon only — for favicon, mobile profile, watermark
- Wordmark only — for in-video chrome
- Light + dark variants

**Build**: Figma. Hire on Fiverr ($100–300) or DIY in 2 hours with Anton/Bebas + Figma's vector tools.

## Motion signature

Every video opens with a **0.4s intro stinger**:
1. Frame 1: solid brand-primary green flash
2. Frames 2–4: brand icon scales in from center with a bounce
3. Frames 5–10: icon fades to corner watermark position; content begins

Every video closes with a **0.6s outro stinger**:
1. Last engine frame
2. Brand wordmark fades in over a dimmed scene
3. Optional micro-CTA: "Follow for daily."

Build these once as PNG sequences / mini engines and stitch onto every render via ffmpeg.

## Audio signature

**Intro stinger**: 0.5s rising tone — a quick "ba-DUM" or arpeggio in C major (matches our PD melody library). Generate once with Suno ("0.5s upbeat sports-broadcast intro stinger, no vocals, percussive, energetic, in C major"), normalize to -14 LUFS, save as `assets/audio/stinger_in.wav`.

**Outro stinger**: 0.4s tail — single note + reverb. Same generation process, save as `assets/audio/stinger_out.wav`.

**Collision SFX bank** (replace sine waves for marble_drop_pro):
- `marble_hit_wood_01.wav` → `_08.wav` — randomized per peg hit
- `marble_win.wav` — winner reveal
- Source: Splice ($13/mo) or Freesound CC0
- All mastered to -14 LUFS so they sit cleanly under the melody track

## Voice + tone (captions, AI commentary)

**Authoritative-playful, never breathless.** Think *FiveThirtyEight × ESPN morning show*.

| Do | Don't |
|---|---|
| "The numbers say Spain's marble survives 60% of simulations." | "OMG you won't BELIEVE who wins this race 🤯🤯🤯" |
| "Group D is brutal. Argentina favored, but Egypt's been live in friendlies." | "Group of DEATH! Who advances?!?!" |
| "Polymarket: France 18%. Plinko: France one of every five runs." | "France WILL WIN 🇫🇷🥇" |

## In-video chrome

Consistent across every video:
- **Top-right**: bouncing counter or odds badge (font: Roboto Condensed Bold)
- **Top-left**: small bracket icon watermark (logo at 40% opacity)
- **Bottom-left**: round indicator ("R32" / "QF" / "SF" / "FINAL")
- **Hook band**: top 8% of screen, translucent black, white text
- **CTA band**: bottom 8% of screen, translucent black, white text

## Episode framing

Naming convention for posts:
- `[ROUND] [TYPE] — [SUBJECT]`
- Examples: `R32 Bracket Plinko — Top 16`, `Group D Predictor — Argentina`, `Polymarket Odds — Day 4`

Hashtag suffix (every post):
- IG: `#FIFAWorldCup #WorldCup2026 #Football #Soccer #BracketFC`
- TikTok: `#WorldCup #SportsTok #FIFA #BracketFC`
- YT Shorts: SEO title + `#FIFAWorldCup2026 #BracketFC`

## Style guide assets to produce (in priority order)

1. **Logo lockup + icon** — Figma, both variants (this week)
2. **Color palette PDF** — for any future contractor
3. **Intro/outro stinger renders** — both video + audio
4. **Collision SFX bank** — at least 6 samples
5. **Title card template** — Figma + ffmpeg compose script
6. **Bracket frame overlay** — a transparent PNG overlay showing tournament context
7. **Profile imagery for IG/TikTok/YT** — same icon, sized per platform
8. **Banner imagery for YT/X** — wider layouts using the wordmark

## Open questions

- Name confirmation (chat shortlist pending)
- Logo design route (Fiverr vs DIY in Figma)
- Splice subscription start date (gates SFX bank)
- Suno subscription start (gates audio stingers + original melody hooks)

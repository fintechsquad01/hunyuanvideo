# Storyboard — "EIGHT COUNTRIES. 22 TROPHIES."

**Piece**: A11 (NEW archetype proposal) — All-Time Pantheon
**Audience hook**: In 14 seconds, every WC trophy ever lifted, sorted by who lifted them.
**Length**: 14 seconds
**Resolution**: 1080×1920 (9:16 vertical)
**Engine**: `custom_python` (Pillow frame renderer + ffmpeg) for data, optional `fal_ai` backdrop layer
**Posting**: IG Reels + TikTok + YT Shorts, hand off to `cross-platform-distributor` for per-platform captions

---

## The premise

22 World Cups have been played between 1930 and 2022. Only 8 countries have ever lifted the trophy. The viewer watches every single one drop into a column, country-by-country, year-by-year — and at the end, the full pantheon is visible at a glance.

**The single moment the viewer remembers**: Brazil's fifth trophy stacking on top, while Spain and England are still on one.

## Reference points

- **NYT Upshot** "fact stack" graphics — every data point is countable, no estimation
- **@statmusefb** big-number reveals — Anton font, full-screen number
- **The Pudding** scrollers — each beat a distinct visual state
- **CNN data viz** "history at a glance" pieces — time-ticker as narrative spine

NOT copying:
- ❌ A continuous Plinko race (this is history, not prediction)
- ❌ Multiple stats at once (one dimension: trophies-per-country)
- ❌ Animated faces of players (IP risk + off-brand)

## The shot list

### SHOT 1 — Hook (0:00 → 0:02) · 60 frames

**Visual**:
- Dark pitch-green gradient background (#0d2818 → #08180e top to bottom)
- Centered top band: "WHO HAS WON IT MOST?" in Anton, 84px, ALL CAPS, white
- Year ticker top-right: "1930" in Roboto Condensed, 80px, tabular nums
- 8 empty vertical columns visible across mid-frame, each labeled with country code at the base (BRA, ITA, GER, ARG, URU, FRA, ENG, ESP) in Roboto Condensed Bold 36px
- Subtle watermark bottom-left: `pitch.predict`

**Camera**: static
**Audio**: silent ambient bed begins, one soft tick at 0:01.5

---

### SHOT 2 — Build (0:02 → 0:06) · 120 frames

**Visual**:
- Year ticker advances: 1930 → 1934 → 1938 → 1950 → 1954 → 1958 (6 events in 4s)
- For each year a gold trophy glyph drops from the top of frame into the correct column, settles, glow halo for 6 frames
- Trophies render as a simple Pillow-drawn gold cup shape (no FIFA mark)
- When a country gets its FIRST trophy, its country code at the column base brightens from grey to white
- Drop sequence: URU(1930), ITA(1934), ITA(1938), URU(1950), GER(1954), BRA(1958)

**Camera**: imperceptible 1.02× zoom-in over 4s for tension
**Audio**: Ode to Joy ascending notes, one per trophy drop, C-D-E-F-G-A pitches

---

### SHOT 3 — Climb (0:06 → 0:11) · 150 frames

**Visual**:
- Year ticker accelerates: 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022 (16 events in 5s)
- ~9 frames per drop. Same gold-trophy drop pattern.
- Drop sequence:
  BRA(1962), ENG(1966), BRA(1970), GER(1974), ARG(1978), ITA(1982), ARG(1986), GER(1990), BRA(1994), FRA(1998), BRA(2002), ITA(2006), ESP(2010), GER(2014), FRA(2018), ARG(2022)
- As each new country (ENG 1966, FRA 1998, ESP 2010) gets its first, its base label brightens
- BRA column hits its 5th trophy at 1994 — a brighter halo flashes

**Camera**: holds steady
**Audio**: notes continue, tempo accelerating, climaxing on ARG 2022 (the final drop)

---

### SHOT 4 — Peak (0:11 → 0:13) · 60 frames

**Visual**:
- Year ticker locks: "1930 — 2022" in tabular Roboto Condensed
- Final tally label fades in below the columns:
  `BRA 5  ITA 4  GER 4  ARG 3  URU 2  FRA 2  ENG 1  ESP 1`
- BRA column gets a sustained gold halo (#ffd400 glow)
- Sub-label in Inter Bold: "8 NATIONS. 22 TROPHIES."

**Camera**: slight pullback (zoom 1.02 → 1.00) to show full composition
**Audio**: tonic resolution chord, hold

---

### SHOT 5 — CTA (0:13 → 0:14) · 30 frames

**Visual**:
- Bottom band fade-in: "PICK YOUR CHAMPION" in Anton, 64px
- Source line above CTA: "Source: FIFA, 1930–2022" in Inter Semibold, 26px, secondary white
- Watermark: `pitch.predict`
- LOOP SEAM: last 3 frames begin fading year ticker back to "1930" so a replay feels seamless

**Audio**: reverb tail into silence

---

## Audio map (composite)

| Time | Layer | Sound |
|---|---|---|
| 0:00 → 0:02 | Bed | Soft pad (suspended fourth) |
| 0:02 → 0:06 | Melody | Ode to Joy notes, one per trophy drop (6 notes ascending) |
| 0:06 → 0:11 | Melody | Continued progression, accelerating, 16 notes |
| 0:11 | Hit | Tonic resolution chord on the final drop (ARG 2022) |
| 0:11 → 0:13 | Bed | Sustained chord |
| 0:13 → 0:14 | Tail | Slow reverb tail into silence |

Audio source: synthesized in numpy from the public-domain Ode to Joy melody (per brand contract — no copyrighted music).

## Type stack

| Element | Font | Size | Tracking | Case |
|---|---|---|---|---|
| Hook ("WHO HAS WON IT MOST?") | Anton (DejaVuSans-Bold fallback) | 84px | -0.02em | ALL CAPS |
| Year ticker (1930, 2022, etc.) | Roboto Condensed Bold (fallback DejaVuSans) | 80px | -0.01em | tabular |
| Country codes at base | Roboto Condensed Bold | 36px | 0.04em | ALL CAPS |
| Final tally row | Roboto Condensed Bold | 44px | 0.02em | as-is |
| Sub-label "8 NATIONS. 22 TROPHIES." | Inter Bold (fallback DejaVuSans-Bold) | 40px | -0.01em | ALL CAPS |
| CTA "PICK YOUR CHAMPION" | Anton | 64px | -0.02em | ALL CAPS |
| Source line | Inter Semibold | 26px | 0 | sentence |
| Watermark | Inter Semibold | 30px | 0 | lowercase |

## Color palette

| Element | Color |
|---|---|
| Background top | #0d2818 |
| Background bottom | #08180e |
| Trophy gold | #ffd400 |
| Champion halo (BRA) | #ffd400 at 30% glow |
| Active country code | #ffffff |
| Inactive country code | #5a6a60 |
| Year ticker | #d9e6df |
| Body / secondary text | #d9e6df |

## Compliance sweep ✓

- No "odds", "bet", "wager" — passed
- No FIFA marks, team crests, player names — passed (3-letter country codes only)
- No copyrighted music — Ode to Joy is public domain
- Source attribution included ("FIFA, 1930–2022")
- Watermark present

## Engine handoff

**Engine**: `custom_python` (Pillow frame renderer)
**Files (this piece)**:
- `pieces/wc_champions_pantheon/data.py` — winners table
- `pieces/wc_champions_pantheon/render.py` — frame renderer + ffmpeg
- `pieces/wc_champions_pantheon/audio.py` — Ode to Joy synthesis
- `pieces/wc_champions_pantheon/build.py` — orchestrator
- `pieces/wc_champions_pantheon/backdrop_fal.py` — optional fal.ai backdrop (Phase 2)

**Output**: `world-cup-loops/output/wc_champions_pantheon.mp4`

## Success metrics

- Retention at 5s: ≥45%
- Completion: ≥55%
- Comment-to-view: ≥0.6%
- Saves per 100: ≥2.5
- Shares per 100: ≥1.0
- Comment-bait: "ESP 1, ENG 1" should generate defensive comments from England/Spain fans; "ARG 3" will trigger the GOAT debate

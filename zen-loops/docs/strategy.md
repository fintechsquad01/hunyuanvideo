# Strategy — zen-loops

## Positioning

Brand: a calming visual-ASMR account in the bouncing-sphere / oddly-satisfying simulation niche, with an identity-driven engagement layer that the incumbent (@zenshapess) underuses.

Bio formula: `[verb of relaxation] + [visual promise] + [identity hook in caption strategy]`. Example: *"Slow your scroll. Geometry, gravity, and a question for every loop."*

Audience: Gen Z + Millennials seeking stress relief, focus aids (ADHD-marketed content performs disproportionately), or low-effort dopamine. The 2026 wellness/escapism wave (Pinterest Predicts, Adobe Creative Trends) is tailwind.

## Core thesis: Identity > Zen

The baseline ZenShapes formula (satisfying physics + nostalgic audio) is the floor, not the ceiling. The engagement multiplier is **identity signaling** — the viewer doesn't comment because the video is beautiful, they comment because the video is *about them*. Every reel should answer: *what does this viewer get to say about themselves in the comments?*

## Three-hook system (apply to every reel)

| Hook | Window | Implementation |
|---|---|---|
| Visual | 0–3s | Motion already in flight on frame 1. High contrast palette. No title cards, no fade-ins. |
| Cognitive | 3–6s | Identity signal overlay: birth year, zodiac, MBTI, initial color, country flag, age range. |
| Interaction | 6–end | Failable challenge: "99% can't catch the red ball", "comment when you lose track", "your number = your personality". |

## Five-step video template

| Step | Time | Job |
|---|---|---|
| Hook | 0–1.5s | Overlay text + already-in-motion frame |
| Build | 1.5–6s | Speed / density / count rises |
| Peak | 6–10s | Max chaos → mini resolution (snap-to-pattern, color merge, ball settles) |
| Loop | 10–15s | Last frame ≈ first frame; seamless restart |
| CTA | overlay + caption | Pinned-comment question; caption mirrors the on-screen prompt |

Length target: **12–15s.** Long enough to develop tension, short enough to drive completion + replays.

## Archetype rotation

Don't post the same archetype every day — the algorithm fatigues quickly. Rotate across four:

1. **Bouncing spheres** (Unity DOTS + Havok) — IP-themed, polyrhythmic audio, color escalation
2. **Identity grids** (Python NumPy + Pillow) — color-cell pickers, zodiac wheels, birth-year matrices
3. **Failable challenges** (Unity or Python) — track-the-ball, count-the-flashes, find-the-odd-one
4. **Hyper-textural loops** (HunyuanVideo / Veo3 / Sora) — jelly, slime, wax, gummy 2026-trend textures

A weekly batch should cover all four. See `docs/content-archetypes.md` for full matrix.

## Audio strategy

Three categories of audio, by funnel position:

| Tier | Use | Source |
|---|---|---|
| Owned / licensed | Any reel pointing at the App Store. Brand-deal reels. | Epidemic Sound, Artlist, custom-composed polyrhythmic loops. |
| Royalty-free | General awareness reels. Trend-following posts. | YouTube Audio Library, Pixabay Music, Freesound (CC0). |
| IP / trending | Top-of-funnel disposable reels only. Expect DMCA mutes. Never on funnel-driving posts. | Platform-native trending audio libraries. |

Polyrhythmic and "core memory" tracks (Rush E, lofi remixes of game OSTs, looped pop-cultural samples) drive the highest retention but carry the highest legal risk. Treat as marketing experiments, not infrastructure.

## Posting cadence

- **Volume**: 1–3 reels/day, all three platforms, batch-produced weekly
- **Schedule**: IG Reels primary slot 6–9pm local audience time; TikTok 12pm + 7pm; YouTube Shorts anytime (algorithm is timezone-agnostic)
- **Captions**: stagger per platform (IG = identity prompt + hashtags, TikTok = challenge framing + 2–3 hashtags, YT Shorts = SEO title + descriptive body)
- **Pinned comment**: low-friction question on every post within 5 minutes of publish

## Cross-platform distribution

| Platform | Primary signal | Tactic |
|---|---|---|
| Instagram Reels | Comment-to-view + saves | Identity prompts in overlay + pinned comment |
| TikTok | Completion rate + shares | Failable challenge framing; trending audio overlay where licensing allows |
| YouTube Shorts | Watch time + search | SEO-friendly title + description; longer compilations for non-Shorts uploads |

Cross-poster: `scheduling/cross_post.py` — same MP4, platform-specific caption strings.

## 30-day roadmap

**Week 1 — Setup**
- Scaffold `zen-loops/` repo
- Unity project + DOTS + Havok + one bouncing-sphere template
- Python NumPy pipeline producing one 12s 1080×1920 MP4 end-to-end
- Audio library: 3 polyrhythmic owned/licensed tracks
- IG / TikTok / YT accounts with consistent handle + bio + profile imagery

**Week 2 — Content batch v1 (12 videos)**
- 4 bouncing-sphere variants
- 4 identity-grid variants
- 4 failable-challenge variants
- Cross-post all 12, staggered captions

**Week 3 — Iteration**
- Pull metrics; identify top-3 by comment-to-view (>0.5%) and retention-at-5s (>40%)
- Generate 8 variations of winners
- Reply-with-video on top engaged comments
- Set up bio link landing page

**Week 4 — Funnel + scale**
- If retention/engagement targets hit: start Unity mobile-game prototype (`docs/mobile-game-spec.md`)
- Wire analytics dashboard (PostHog recommended — MCP already configured)
- Plan Phase 2: weekly batches, brand-deal triage

## Success metrics

| Metric | Floor | Target | Stretch |
|---|---|---|---|
| Comment-to-view ratio | 0.2% | 0.5% | 1.0% |
| Retention at 5s | 30% | 40% | 55% |
| Saves per 100 views | 1 | 2 | 4 |
| Bio-link CTR | 0.3% | 1.0% | 2.0% |
| App install conversion (bio → install) | 5% | 20% | 35% |

Trigger to build the mobile-game endpoint: comment-to-view ≥0.5% sustained over 14 days **and** ≥10K IG followers.

## Risks

See plan section 7 — audio licensing, algorithm volatility, HunyuanVideo cost, App Store review, single-account platform risk. The first two are the live ones during weeks 1–4.

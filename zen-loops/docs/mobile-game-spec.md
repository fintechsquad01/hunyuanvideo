# Mobile Game Spec — Phase 2

**Status**: design now, build only after the content funnel proves out (≥10K IG followers + ≥0.5% comment-to-view ratio sustained 14 days).

## Concept

A hyper-casual mobile title whose core mechanic mirrors the winning Reel archetype. Working name: `loop-runner` (replace once archetype is chosen).

The point is not to invent a new game — it's to give viral viewers an interactive version of the simulation they just watched. The Color Ball Z model: viewer sees a satisfying loop on IG, taps the bio link, lands on the App Store, installs because the cover shows the same loop they liked, plays for 90s, watches a rewarded ad, returns tomorrow.

## Core mechanic (default — adjust to winning archetype)

Color-match arcade. Steer a moving ball into boundary segments whose color matches it. Multi-color orbs randomly swap the ball's color, forcing split-second steering decisions. Speed escalates with score.

This is the same loop as the bouncing-sphere Reels — minimal cognitive load, instant grasp, infinite replayability, ad-friendly session length.

## Engine

Unity + C# (matches the Reel content engine; assets and physics scripts port directly).
- Unity Physics (DOTS) or classic PhysX — pick whichever the Reel engine settled on
- Universal Render Pipeline (URP) for clean gradients + bloom matching the brand
- Target: iOS 15+ and Android API 24+

## Monetization

Free-to-download. Revenue from:
| Source | Trigger | Rate target |
|---|---|---|
| Rewarded video ads | Continue after death (×2 lives), 2× score multiplier | $20–40 eCPM (US, ATT consented) |
| Interstitial ads | Every 3–4 game-overs | $5–15 eCPM |
| IAP — remove ads | One-time $2.99 | 1–3% conversion of DAU |
| IAP — cosmetic skins | Ball trail effects, palette packs | 0.5–1% conversion of DAU |

Ad SDK shortlist: AdMob (baseline), AppLovin MAX (mediation), ironSource (alternative mediation). Use mediation from day 1 — single-network fill is a trap.

## Compliance — must ship from build 1

| Requirement | Why | Implementation |
|---|---|---|
| iOS App Tracking Transparency (ATT) | iOS 14.5+ requires explicit consent for IDFA. Without it, eCPM drops 60–80%. | Native ATT prompt on first launch, after the first interactive screen (not on cold open — Apple rejects that). |
| GDPR consent (EU) | Required by AdMob + AppLovin SDKs. | Funding Choices (Google) or AppLovin's built-in CMP. Gates personalized ads in EU traffic. |
| App Store privacy nutrition labels | Required at submission. | Declare: identifiers (IDFA), product interactions, diagnostics, location (coarse). |
| Google Play Data Safety | Equivalent for Play Store. | Same disclosures, separate form. |

The ZenShapes v1.3 patch was specifically to fix ATT — they shipped without it initially and lost revenue. Don't repeat that mistake.

## Funnel — bio link to install

```
IG bio link → landing page → App Store / Play Store smart link → install
                                         ↓
                                  attribution captured via
                                  ?utm_source=ig (or tt/yt)
```

Recommended stack:
- Landing page: a single-page site (Cloudflare Pages, Vercel) with the looping reel embedded + two store badges
- Smart link: Branch.io or AppsFlyer OneLink — auto-routes iOS/Android, captures attribution
- Attribution platform: AppsFlyer (free tier) or Adjust — needed to measure which platform/reel drives the most installs and retention

## Build trigger

| Gate | Value |
|---|---|
| IG followers | ≥10,000 |
| Comment-to-view ratio | ≥0.5% sustained 14 days |
| Bio-link CTR | ≥1.0% |
| At least one Reel | ≥1M views |

Until all four are hit, do not start the Unity build. Audience proof comes first.

## Build timeline (when triggered)

| Week | Milestone |
|---|---|
| 1 | Unity project + core mechanic (color match, scoring, game-over) |
| 2 | Art pass — palettes match Reel brand, UI minimal, haptics on collision |
| 3 | Monetization integration — AdMob/AppLovin SDK, IAP, rewarded video |
| 4 | Compliance — ATT, GDPR CMP, privacy labels, store listing assets |
| 5 | TestFlight + Internal Play track soft launch (1 country, e.g., Philippines) |
| 6 | Iteration based on retention metrics; global launch when D1 retention ≥35% |

## Out of scope for Phase 2

- Multiplayer / leaderboards (adds backend cost, low conversion on hyper-casual)
- User-generated content
- Cross-promotion network (revisit at Phase 3)
- Localization beyond English (add languages only after retention proves out)

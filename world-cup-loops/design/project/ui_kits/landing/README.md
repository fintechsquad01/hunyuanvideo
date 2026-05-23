# Landing page — UI kit

Single-page landing site at `pitch.predict`. Hero plays the same 9:16 marble loop visible on social. The full page is:

1. **Top nav** — logo + cross-platform links + a follow CTA
2. **Hero** — looping reel preview (auto-play, muted, 15s) with hook + CTA
3. **Latest race** carousel — three recent renders pulled from Supabase (mocked here)
4. **Odds widget** — live Polymarket reading, "Polymarket vs. Plinko" side-by-side
5. **Format gallery** — the eight archetypes WC1–WC8
6. **App Store badges** — phase-2 placeholder
7. **Email signup** — daily-race subscription
8. **Footer** — platform links, contact, legal

## Components

| File | Purpose |
|---|---|
| `App.jsx`            | Page assembly + tiny mocked Supabase fetch |
| `Nav.jsx`            | Top bar with logo + platform jumpoffs |
| `Hero.jsx`           | Reel preview (auto-play loop) + hero copy + CTA |
| `RaceCarousel.jsx`   | "Latest race" three-up scroll |
| `OddsWidget.jsx`     | Polymarket vs. Plinko table — five rows |
| `FormatGrid.jsx`     | WC1–WC8 archetype cards |
| `Newsletter.jsx`     | Email field + subscribe button |
| `Footer.jsx`         | Platform marks + legal |

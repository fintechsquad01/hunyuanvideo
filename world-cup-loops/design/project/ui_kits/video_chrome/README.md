# Video Chrome — UI kit

The vertical-video (1080×1920, 9:16) overlay system that wraps every render. This kit reproduces the **chrome layer**: the hook band, CTA band, watermark, round indicator, odds/counter badge, winner banner, lower third, and the intro/outro stinger frames. The marble engine sits underneath; this kit defines what goes on top.

## Frames you can preview

`index.html` renders a phone-shaped 9:16 frame and rotates through six representative chrome states. Use the bottom nav to step through:

1. **Hook + watermark only** — what frame 1 of every video looks like.
2. **Hook + odds badge + round indicator** — mid-render Plinko frame.
3. **Lower third reveal** — "Round of 32" title sliding in from left.
4. **Winner banner** — Spain takes the championship, country backdrop + glow.
5. **CTA outro** — wordmark + "Follow daily."
6. **Intro stinger** — green flash → bracket icon bounce-in (still frame).

## Components

| File | Purpose |
|---|---|
| `VideoFrame.jsx`   | 9:16 phone bezel + scaled 1080×1920 viewport |
| `HookBand.jsx`     | Top 7% translucent black band, Inter Bold ALL CAPS |
| `CtaBand.jsx`      | Bottom 7% same treatment, optional follow caret |
| `Watermark.jsx`    | Top-left icon at 40% opacity |
| `OddsBadge.jsx`    | Top-right Polymarket/Plinko/Elo stack |
| `RoundIndicator.jsx` | Bottom-left R32/R16/QF/SF/FINAL pill |
| `LowerThird.jsx`   | Left-edge animated title bar with yellow accent |
| `WinnerBanner.jsx` | Country backdrop + Bebas "WINNER" + Anton team name |
| `StingerFlash.jsx` | Intro green flash + bracket bounce |
| `MarbleStage.jsx`  | Demo Plinko-style marble field (placeholder physics) |

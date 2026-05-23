---
name: pitch-predict-design
description: Use this skill to generate well-branded interfaces and assets for pitch.predict, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out of `assets/` and create static HTML files for the user to view. Pull design tokens from `colors_and_type.css` — don't reinvent the palette or type stack. If working on production code, you can copy the same tokens and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask a few questions, and act as an expert designer who outputs HTML artifacts *or* production code, depending on the need.

## What's in this skill

- `README.md` — brand overview, content voice rules, visual foundations, iconography
- `colors_and_type.css` — every design token as a CSS variable, plus semantic element styles
- `assets/` — logo lockup + icon (light, dark, mono variants), country-flag marbles, archetype backgrounds (pitch / arena / chart / track)
- `preview/` — small specimen cards (type, colors, spacing, components, brand) — useful as visual reference for any agent
- `ui_kits/landing/` — full landing-page reference (React + JSX, in-browser Babel)
- `ui_kits/video_chrome/` — 9:16 vertical-video chrome overlay system (hook band, watermark, odds badge, round indicator, winner banner, stinger)

## Three rules to never forget

1. **Voice is FiveThirtyEight × ESPN morning show** — numerate, authoritative, never breathless. No emoji in chrome. Ever say "bet" or "odds"; say "prediction" / "fan poll" / "simulator says."
2. **Country flag colors override marble fills only.** Brand chrome (hook band, watermark, round indicator, winner banner) stays pitch-green + FIFA-yellow + translucent black.
3. **Translucent black bands (`rgba(0,0,0,0.60)`) under all video text, never blur.** TikTok's encoder drops frames on `backdrop-filter`.

# Audio Library

Audio is half the engagement. It's also the highest-risk leg of the content engine — wrong choice can either get a reel muted (DMCA) or expose the funnel to copyright claims if it drives a paid game install.

## Three tiers, by funnel position

| Tier | Source | Use case | Risk |
|---|---|---|---|
| Owned / licensed | Epidemic Sound, Artlist, Musicbed, custom-composed | Any reel pointing at the App Store; brand-deal reels | None |
| Royalty-free / CC0 | YouTube Audio Library, Pixabay Music, Freesound (CC0 filter) | General awareness reels; trend-following posts | Low — verify the specific track's license per use |
| IP / trending | Platform-native trending audio libraries | Top-of-funnel disposable reels only — never on funnel-driving posts | High — DMCA mute, account strikes if abused |

## What to buy first

Recommended initial subscription: **Epidemic Sound** (~$15/mo personal, ~$24/mo commercial). One subscription covers IG, TikTok, YT, and downstream app trailers. Whitelisting protects you from automated copyright matches.

Initial library (3 tracks owned/licensed, weeks 1–2):
1. One slow polyrhythmic piano loop (ASMR / calm reels)
2. One mid-tempo electronic loop with strong kicks (bouncing sphere collisions)
3. One playful arpeggio loop (identity grid / color picker reels)

## Polyrhythmic composition (for the bouncing-sphere format)

The ZenShapes signature is bouncing balls synced to melody notes. To do this with owned audio:
1. Compose a 12-note melody in MIDI (any DAW; FL Studio, Ableton Lite, GarageBand all work)
2. Export each note as a separate audio sample (WAV)
3. In Unity, trigger sample N on bounce N via a sequence step counter
4. The melody emerges from the physics — no copyright exposure

Reference tracks for *style* (not for direct use):
- "Megalovania" (Undertale) — fast arpeggio over driving bass
- "Lavender Town" (Pokémon) — eerie melodic loop
- Any C418 Minecraft ambient track — slow major-key piano

Compose *in the style of*; never sample directly on funnel-driving posts.

## Sound-design layer

In addition to the melody track, every reel benefits from a thin sound-design layer:
- **Boings / pops** on collisions (Freesound CC0 — search "cartoon boing" or "balloon pop")
- **Whoosh / sweep** at peak moments (Epidemic Sound has a "Cinematic Transitions" pack)
- **Soft ambient bed** under everything — pink noise or vinyl crackle (Freesound)

Mix levels (rough guide):
- Melody track: -6 dB
- Collision sounds: -10 dB
- Ambient bed: -20 dB
- Whoosh transitions: -8 dB at moment, ducked elsewhere

Master to -14 LUFS (IG/TikTok standard).

## License-tracking spreadsheet

Maintain `audio-library.csv` (or Notion table) with columns:
- `filename` — exact filename on disk
- `source` — Epidemic Sound URL / Pixabay URL / etc.
- `license_type` — owned / Epidemic / CC0 / royalty-free
- `safe_for_app_funnel` — yes / no
- `date_acquired`
- `notes`

Audit quarterly. Drop any track whose license status changed.

## Anti-pattern

Do **not** download a viral TikTok sound, mux it into a self-uploaded MP4, and post on IG. That bypasses platform-level licensing and turns a DMCA mute into a copyright claim against the *account*, not just the post.

If you want to ride a trending sound, post natively on the platform that offers it (TikTok native upload via the mobile app, picking the trending sound from TikTok's library) — and don't drive funnel from that specific post.

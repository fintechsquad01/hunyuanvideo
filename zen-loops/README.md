# zen-loops

A polyglot content-to-app funnel toolkit for "satisfying simulation" social accounts (in the style of [@zenshapess](https://www.instagram.com/zenshapess) → *Color Ball Z*).

Two phases:
1. **Content engine** — produce 9:16 looping reels (bouncing spheres, identity grids, sound-reactive pulses) and cross-post to Instagram Reels / TikTok / YouTube Shorts.
2. **Mobile-game endpoint** — convert organic viewers into installs of a Unity hyper-casual title that mirrors the winning reel archetype. Build after the audience proves the funnel.

## Scaffold

```
docs/             positioning, archetypes, hooks, audio library, game spec
engines/
  python-numpy/   fast prototyping for abstract/grid/color loops
  unity-physics/  primary engine for bouncing-sphere + IP-themed reels (assets port to mobile game)
  audio-reactive/ librosa + shader pipelines
  ai-video/       HunyuanVideo / Veo / Sora prompt packs for hyper-textural shots
configs/          JSON recipes per video
overlays/         Pillow text-overlay layer (engine-agnostic)
output/           rendered MP4s
scheduling/       IG Graph + TikTok Upload + YT Data API cross-posters
analytics/        cross-platform metrics pulls
```

## Quick start

```bash
pip install -r requirements.txt
python generate_video.py --config configs/bouncing_focus_01.json
```

Produces `output/bouncing_focus_01.mp4` — 12s, 1080×1920, H.264.

## Strategy

See `docs/strategy.md` for positioning, hooks, posting cadence, and 30-day roadmap. Core thesis: **Identity > Zen.** The viral multiplier isn't the satisfying motion — it's giving the viewer a reason to comment about themselves.

## License & audio

Use **owned or properly licensed audio** for any video driving funnel conversion. Fandom/IP audio (Undertale, Pokémon, etc.) is disposable awareness fuel only — never on a reel pointing at the App Store.

# Engine handoff — zen-loops-storyboard

After a storyboard is written, hand off to a render engine.

## Engine map

| Archetype | Engine | Module path |
|---|---|---|
| Z1 Plinko Identity Race | `marble_drop` (default) or `marble_drop_pro` (with FX) | `zen-loops/engines/python_numpy/marble_drop.py` |
| Z2 Ring Expansion | `ring_expansion` | `zen-loops/engines/python_numpy/ring_expansion.py` |
| Z3 Bouncing Spheres | `bouncing_spheres` | `zen-loops/engines/python_numpy/bouncing_spheres.py` |
| Z4 Color Battle | NOT YET BUILT — gap to file in next iteration | n/a |
| Z5 Failable Tracker | Use `bouncing_spheres` with target highlight | `zen-loops/engines/python_numpy/bouncing_spheres.py` |
| Z6 Personality Bucket Drop | NOT YET BUILT — Plinko variant with terminal buckets | n/a |
| Z7 Hyper-textural | HunyuanVideo OR fal.ai (`fal-ai/flux/schnell`) | external |

## Config schema (per engine)

### marble_drop / marble_drop_pro

```yaml
archetype: marble_drop | marble_drop_pro
duration: 14
fps: 30
resolution: [1080, 1920]
background: "#0a0a14"
labels: ["JAN", "FEB", ...]            # 12 birth months / 12 zodiac / etc.
palette: ["#ff3b3b", "#ff8c1a", ...]    # one per label
peg_rows: 14
peg_spacing: 95
gravity: 1800
marble_radius: 36
bounce: 0.55
overlay:
  hook_text: "Your birth month is your racer."
  cta_text: "Comment if yours won."
```

### ring_expansion

```yaml
archetype: ring_expansion
duration: 15
fps: 30
resolution: [1080, 1920]
background: "#0a0a14"
ring_color: "#3bcfff"
ring_thickness: 18
ring_radius_start_pct: 0.45
ring_radius_end_pct: 0.95
ball_color: "#ff3b3b"
ball_radius: 40
ball_speed: 1100
speed_gain_per_bounce: 1.008
melody: "twinkle"                       # see melodies.md
counter: true
reveal_text: null                       # auto-derived from melody title if null
overlay:
  hook_text: "Guess the song."
  cta_text: "Comment at the note you got it."
```

### bouncing_spheres

```yaml
archetype: bouncing_spheres
duration: 12
fps: 30
resolution: [1080, 1920]
background: "#0a0a14"
palette: ["#ff3b3b", "#3b83ff", "#ffd93b"]
difficulty: 3                           # 1-5, controls density
overlay:
  hook_text: "Only 2% can follow the red ball."
  cta_text: "Comment when you lose it."
```

## After render

The engine writes `output/<id>.mp4`. Then route to:

- `cross-platform-distributor` (growth-stack) for per-platform caption + schedule
- Manual upload for the first 2 weeks (until accounts have trust history)

## Anti-patterns to reject at handoff

- Mixing archetypes (a marble_drop with ring_expansion melody on top) — too complex, kill
- More than 26 marbles in marble_drop — eye can't track
- Ring expansion melody >20 notes — too many collisions for 15s
- Asking the engine to render text not in the brand voice (e.g., "BET ON RED") — reject

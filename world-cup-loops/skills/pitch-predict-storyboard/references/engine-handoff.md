# Engine handoff — pitch-predict-storyboard

After a storyboard is written, it hands off to a render engine. This file maps each archetype to its locked engine + the config schema the engine needs.

## Engine selection per archetype

| Archetype | Engine | Why this engine |
|---|---|---|
| A1 Bracket Plinko | `custom_python` (marble_drop_pro) | Real physics needed for collisions; we own the engine |
| A2 Group Predictor | `custom_python` (marble_drop_pro, n=4) | Same as A1, smaller marble set |
| A3 Per-Match Score Race | `d3_playwright` | Timeline + score animation = CSS-friendly |
| A4 Top Scorer Race | `d3_playwright` | Vertical bar-chart animation |
| A5 Polymarket Odds Viz | `d3_playwright` | Size-proportional marble grid + delta arrows |
| A6 Will X Advance | `custom_python` | Branching paths needs custom geometry |
| A7 Country Food Race | `custom_python` (marble_drop_pro with emoji labels) | Same engine as A1 with different label rendering |
| A8 Hopium Loop | `custom_python` (ring_expansion) | Single-ball ring physics, owned engine |
| A9 Elo Trajectory | `d3_playwright` | Line chart with annotations + reveal |
| A10 Gap Reveal | `d3_playwright` | Typography-led split-screen, counters |
| **Premium cinematic** (hero stadium, AI faces) | `fal_ai` or `higgsfield` | Generative; only for non-data-critical decoration |

## Config schema by engine

### custom_python (Plinko / Ring)

Fields the storyboard must specify in the engine handoff section:

```yaml
engine: custom_python
archetype: marble_drop_pro | ring_expansion
duration_seconds: 14
fps: 30
resolution: [1080, 1920]
brand_chrome:
  hook_text: "ALL 48 TEAMS"
  cta_text: "PICK YOUR COUNTRY"
  watermark: "pitch.predict"
data:
  team_codes: ["ESP", "FRA", ...]
  highlights:
    favorite: "ESP"
    underdogs: ["CUR", "QAT"]
audio:
  source: "pd_melody"
  melody: "ode_to_joy" | "pachelbel" | "twinkle" | ...
```

### d3_playwright (charts / typography pieces)

Fields the storyboard must specify:

```yaml
engine: d3_playwright
template: gap_reveal | elo_trajectory | score_race | top_scorer | polymarket_viz | league_table_race
duration_seconds: 14
fps: 30
resolution: [1080, 1920]
brand_chrome:
  hook_text: "WHAT IF…"
  cta_text: "BACK CURAÇAO"
  watermark: "pitch.predict"
data:
  series:                       # template-specific
    - { country: "CUR", elo: 1436, rank: 90 }
    - { country: "GER", elo: 1923, rank: 11 }
  reveal:
    label: "THE GAP"
    value: 487
    sublabel: "BIGGEST IN WC HISTORY"
animation_beats:                # frame indices for key moments
  elements_in: 15
  phase1_end: 45
  underdog_lock: 51
  phase2_end: 78
  reveal_start: 80
  hold_end: 110
audio:
  source: "pd_melody" | "suno_owned" | "silent"
  prompt_if_suno: "rising arpeggio with beat drop at 0:12"
```

### fal_ai / higgsfield (premium decoration only)

For hero shots, stadium establishing, hopium-loop celebrations.

```yaml
engine: fal_ai
model_id: fal-ai/flux/schnell | openai/gpt-image-2 | fal-ai/stable-diffusion-v3-medium
purpose: background | hero | celebration
prompt: |
  Wide-angle stadium establishing shot at dusk, floodlights on,
  dramatic sky, no logos, no faces, cinematic composition,
  9:16 vertical.
overlay_real_data: true        # MUST be true — never let the model render numbers
```

**Rule**: the AI engine **never renders data**. It generates the visual *backdrop* the data engine then composites real text/numbers on top. If a storyboard tries to use fal_ai to render a chart, reject and route to d3_playwright instead.

## Render-time outputs the engine returns

After render, the engine writes:
- `output/<piece_id>.mp4` — final MP4 (H.264 + AAC if audio)
- `output/<piece_id>.meta.json` — render config snapshot + timing
- `output/<piece_id>.thumbnail.jpg` — first frame at t=0:02

The storyboard skill does NOT call the engine itself. It writes the storyboard + handoff config, then the user (or the next skill) invokes the engine.

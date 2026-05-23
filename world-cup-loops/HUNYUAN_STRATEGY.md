# HunyuanVideo × WC2026 Data — Strategy

## TL;DR

Don't replace the data piece with Hunyuan. **Combine them.** Our data piece is legible (you can read the numbers in 2 seconds). Hunyuan is cinematic but wordless. Hybrid format — Hunyuan hero shot + data-driven middle + Hunyuan outro — uses each at its strength.

---

## What Hunyuan is actually good at

From official prompt handbook + 2026 reviews:

| Strength | Why it matters for us |
|---|---|
| **Cinematic motion** — pans, dollies, tracking shots | Broadcast-quality establishing shots |
| **Realistic lighting + atmosphere** | Mood-driven country opener / stadium B-roll |
| **Multi-person scenes** | Crowd shots, fan reactions, team huddles |
| **Image-to-video (I2V) at 1080p** | Animate logos, flags, manager photos, stat cards |
| **5–10s clips** | Perfect for short-form social hero/outro |
| **HunyuanVideo-Avatar (audio-driven)** | Could make a recurring "host" avatar reading daily stats |
| **HunyuanCustom** | Reference-image conditioning — keeps a "character" consistent across clips |

## What it's BAD at (don't try these)

- **Text inside the video** — no AI video model renders clean readable text
- **Specific player likeness** — Messi/Mbappé won't look like themselves without LoRA fine-tuning
- **Anything longer than ~10s** in one shot
- **Reproducible output** — each gen is different, you iterate 2-3× per shot
- **Real-time data viz** — moving charts/numbers go in OUR engine, not Hunyuan's

---

## Honest constraints

- **No GPU in this container, no weights downloaded.** Can't run locally — we'd use Replicate / fal.ai / WaveSpeedAI / a rented GPU.
- **Cost:** ~$1.27/clip on Replicate (4× H100, ~4 min per gen). Cheaper providers $0.15–$0.30/clip but quality varies.
- **Iteration:** plan 2-3 generations per final shot. Real spend at scale.
- **Newer variant** to use: **HunyuanVideo-1.5** (released Nov 2025, 8.3B params, 75s on RTX 4090, native 1080p I2V).

---

## The hybrid format (recommended)

**25-second video, 3 acts:**

```
0–5s    HUNYUAN cinematic opener     (atmosphere, no data)
5–20s   OUR data engine              (path explainer, legible)
20–25s  HUNYUAN cinematic outro      (celebration / dramatic loss)
```

Hunyuan handles what it's great at (mood, motion, broadcast feel). Our engine handles what IT's great at (legible accurate data with animated reveals).

---

## 6 specific content concepts using our data

### 1. "Cinematic country opener" (per nation, 4s shots)
Hand-crafted opener for each of 48 qualified teams. Use the prompt formula from the handbook:
**Subject + Motion + Scene + Shot + Camera + Lighting + Style + Atmosphere**

Examples:
- **ESP:** *"A red-and-gold scarf swirling in slow motion above a packed Madrid plaza at sunset, drone shot orbiting overhead, golden hour light, cinematic realism, joyful anticipation."*
- **MAR:** *"A young boy in a red Morocco jersey runs through a Marrakech alley at dusk, kicking a worn soccer ball, dust rising in golden light, low tracking shot, photorealism, hopeful underdog atmosphere."*
- **USA:** *"Aerial pull-back from MetLife Stadium at twilight, floodlights blazing across the field, fireworks bursting overhead, sweeping crane camera move, cinematic blockbuster style, anthemic energy."*

→ Then hand off to our path explainer (the legible part).

### 2. "Stadium of the day" series (uses `soccer_wc_venues` data)
16 stadiums × one 5s shot each = 2 weeks of daily content. Generated from venue characteristics:
- Estadio Azteca: high altitude, dome-less, hot
- BMO Field: cooler Toronto setting
- Mercedes-Benz Stadium: dome, controlled climate

Each shot grounded in real venue data. Overlay our facts card on top.

### 3. "Heat will decide this World Cup" (uses `soccer_wc_weather_forecast`)
Data says Monterrey/Houston/Dallas hit 38°C+ during group stage. Generate the visceral atmosphere:
*"Heat shimmer rising off scorching stadium turf, players' jerseys soaked through, sweat dripping in slow motion, blistering noon sun overhead, oppressive heat haze, photorealistic, brutal physical drama."*

Then cut to data: "8 of 16 stadiums hit 35°C+ in June." Memorable + true.

### 4. "Travel grind" (uses `soccer_wc_venue_travel`)
Argentina's group stage spans 3 cities. Generate a "team plane landing at dusk, exhausted players walking off tarmac, suitcases, jet-lag mood" → data overlay: "ARG flies 14,200 km in group stage alone."

### 5. "Manager moment" (uses `current_manager` field, HunyuanCustom)
Reference-image conditioning on a manager's press photo →
*"Tactical war room, manager studying chalkboard with player movements, dim warm lamp light, slow zoom on contemplative face, photojournalism style, weight-of-nations atmosphere."*

→ Cut to data: "Tuchel: 73% win rate since taking England job."

### 6. "Avatar host" daily series (HunyuanVideo-Avatar + TTS)
A stylized 3D avatar (or country mascot ball) reads daily WC2026 stats off TTS audio. Builds character recognition across 30+ daily posts. Hunyuan-Avatar handles lip-sync from any audio input.

---

## Prompt formula to share with whoever generates

From the official handbook (HunyuanVideo-1.5 Prompt Handbook):

```
Prompt = Subject + Motion + Scene + [Shot Type] + [Camera Movement]
       + [Lighting] + [Style] + [Atmosphere]
```

For temporally-coherent action: chain with **"First… then… next… meanwhile… finally…"**

### Sports-specific keywords that work
- *"floodlights, action shot, dynamic pose, dust kicked up, slow motion impact"*
- *"crane shot pulling back, dolly forward, orbit around subject"*
- *"golden hour, dramatic rim light, atmospheric haze, depth of field"*
- *"photorealistic, cinematic realism, 4K, film grain"*

### What to avoid in prompts
- Player names (won't generate likeness)
- Specific scores/numbers (Hunyuan can't render text reliably)
- Anything > 10 seconds of action
- Logos, jerseys with text

---

## Concrete next steps (pick one)

**A — Prompt pack (cheapest, no spend):**
I write a 10-prompt cinematic pack for our top countries + key storylines (heat, travel, stadiums). You/anyone runs them on Replicate or fal.ai. Total cost ~$15–$30.

**B — Pilot one country end-to-end:**
Write the cinematic ARG opener prompt, you generate externally, I composite the result with the existing path explainer into a single 25-second hybrid video. Validates the format before scaling.

**C — Build the pipeline:**
I write the script that takes a Hunyuan-generated MP4 + a country code, auto-composites with our data engine, exports the 25s hybrid. Adds infrastructure for repeatable production.

**D — Try the MCP video tool we have:**
This session has access to a video-generation MCP (`generate_video`). Different model under the hood — might be cheaper/faster to validate the hybrid format here before committing to Hunyuan specifically.

---

## Sources

- [HunyuanVideo GitHub (original 13B)](https://github.com/Tencent-Hunyuan/HunyuanVideo)
- [HunyuanVideo-1.5 GitHub (Nov 2025, 8.3B)](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)
- [Official Prompt Handbook (EN)](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/assets/HunyuanVideo_1_5_Prompt_Handbook_EN.md)
- [HunyuanVideo Tech Report (arXiv)](https://arxiv.org/abs/2412.03603)
- [HunyuanVideo-1.5 Tech Report](https://arxiv.org/abs/2511.18870)
- [HunyuanCustom (multimodal customization)](https://github.com/Tencent-Hunyuan/HunyuanCustom)
- [HunyuanVideo-Avatar (audio-driven)](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar)
- [Replicate hosting](https://replicate.com/tencent/hunyuan-video)

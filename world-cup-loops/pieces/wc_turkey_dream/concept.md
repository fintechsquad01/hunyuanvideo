# TÜRKİYE 2026: BİR HAYAL — Concept

> A surreal long-format fever dream of what would happen if Turkey actually won the 2026 World Cup.
> Affectionate, warm, escalating absurdity. 72 seconds. ~12 scenes.

## The pitch

Reality check: Turkey didn't qualify for WC2026. So this is the wildest "what if" we can imagine — a national fever dream of victory captured in 72 seconds. The tone is the key: warm, self-aware, never mocking. We're not laughing AT Turkey, we're laughing WITH the impossibility of the dream itself.

The video frames around a single character — an elderly Turkish man in an Istanbul tea house — who watches the impossible happen, then wakes from the dream. The cut back to reality is what makes the absurdity land.

## Tone bible

| Influence | Specifically |
|---|---|
| Wes Anderson | Symmetric framing, saturated red palette, deadpan composition |
| Studio Ghibli | Warm humanism, magical realism, characters watching wonder unfold |
| Eurovision | Maximalist national pride, unapologetic camp |
| Spike Jonze | Surreal mash-ups of mundane + impossible |
| **Avoid** | Borat-style cringe, political figures, religious sensitivity, mocking any subgroup |

## Visual motifs (recurring throughout)

- **Red dominates** — Turkish flag's crimson saturates the palette
- **Crescent & star** appear in unexpected places (baklava layers, tea steam, cat eyes)
- **Tulip-shaped çay glasses** — recurring object across scenes
- **The Bosphorus** as a thread connecting half the shots
- **Cats** of Istanbul as silent witnesses
- **Hot air balloons** in Cappadocia as the magical-realism beat

## What we DO show

- Turkish flag, crescent and star
- Istanbul: Bosphorus, Galata Bridge, ferries, Hagia Sophia silhouette (architectural, not religious)
- Cappadocia hot air balloons
- Whirling dervishes (Mevlevi tradition, celebratory)
- Çay (tea) and Turkish coffee culture
- Istanbul cats
- Tulips, baklava, lokum, simit
- Grand Bazaar carpets
- General football mania (no specific club affiliations)

## What we DON'T show

- Atatürk imagery (too sacred to AI-generate)
- Erdoğan or any political figure
- Religious imagery beyond architectural silhouettes
- Real player likenesses
- Smoking, alcohol, or any cliché that could read as tone-deaf
- Wrestling or other specific traditions that would confuse non-Turkish viewers

## The 12-scene shot list

| # | Time | Title | Tone | Visual seed | Generation |
|---|------|-------|------|-------------|------------|
| 1 | 0–6s | **THE CALM** | Quiet anticipation | Elderly Turkish man pours red çay in Istanbul tea house, TV plays football match in background, golden window light | AI-generated (Veo/Seedance) |
| 2 | 6–12s | **THE GOAL** | Climactic | Extreme close-up of football hitting back of net in slow motion, red flag colors burst | AI-generated |
| 3 | 12–18s | **GALATA ERUPTS** | Joy explosion | Galata Bridge at twilight, thousands of fans waving flags, red flares, ferries sounding horns below | AI-generated |
| 4 | 18–24s | **THE DERVISH ASCENDS** | Spiritual surreal | Whirling dervish spinning faster and faster on Hagia Sophia plaza, mini gold trophy levitating above | AI-generated |
| 5 | 24–30s | **CAPPADOCIA RAPTURE** | Magical realism | Aerial dawn shot, dozens of hot air balloons rising — each shaped like a glowing golden World Cup trophy | AI-generated |
| 6 | 30–36s | **BOSPHORUS TRIUMPH** | Epic scale | Ornate Bosphorus ferry sails toward camera at sunset, giant gleaming trophy mounted on bow, Hagia Sophia silhouette behind | AI-generated |
| 7 | 36–42s | **THE CATS BLESS IT** | Absurd cute | Low-angle cobblestone alley, dozens of Istanbul street cats in a perfect circle around a tiny gold trophy, all purring | AI-generated |
| 8 | 42–48s | **BAKLAVA REVELATION** | Surreal food | Macro shot of giant baklava sliced ceremonially, each layer reveals tiny golden crescent moons floating up | AI-generated |
| 9 | 48–54s | **TAKSİM CHAOS** | Anthemic frenzy | Aerial drone tracking through Taksim Square celebration, sea of red flags, fireworks bursting | AI-generated |
| 10 | 54–60s | **THE WAKE** | Bittersweet | Same elderly man asleep in tea house chair, TV static, cold tea, single tear on cheek | AI-generated |
| 11 | 60–66s | **TITLE CARD 1** | Honest | "TÜRKİYE 2026: BİR HAYAL / A DREAM" — clean typography on dark red | PIL/ffmpeg (local) |
| 12 | 66–72s | **OUTRO** | Closing | "Turkey didn't qualify for WC2026. But we can dream." + pitch.predict logo | PIL/ffmpeg (local) |

## Generation budget

| Item | Credits | Notes |
|---|---:|---|
| 10 cinematic scenes @ Veo 3.1 Lite, 6s, 9:16, 1080p | 60 | The workhorse |
| Buffer for safety-filter rejections + retries | 24 | Plan for ~30% reroll rate on cultural content |
| Hero scene at Veo 3.1 (full, not lite) for one premium beat | TBD | Optional polish |
| **Total expected** | **~84** | Of 178 remaining → leaves ~94 |

## Audio

We don't have a Turkish-music generator in the MCP catalog. The plan:

1. **Locally synthesized** Turkish-folk-inspired bed (kanun-style arpeggios via additive synthesis, darbuka-inspired percussion via filtered noise impulses, building crescendo through scenes 3-9)
2. **Crowd roar** for goal moment (synthesized via filtered noise + transient)
3. **Silence + ticking clock** for THE WAKE
4. **Soft outro pad** under the text cards

If you want a real Turkish folk track, you'd need to license one externally and drop it in.

## Sample prompts (in HunyuanVideo-style structure)

Per the HunyuanVideo prompt-encode template, each prompt covers: main content → object details → actions → background/light/style/atmosphere → camera.

### Scene 1 — THE CALM
> An elderly Turkish man with weathered hands and a white moustache sits at a wooden table in a warmly-lit Istanbul tea house, pouring deep-red çay into a small tulip-shaped glass from a traditional double teapot. Steam rises slowly. On a small CRT television behind him, a Turkish national football team match plays silently. Golden late-afternoon window light streams through lace curtains, warm tungsten lamps glow on copper trays. Slow dolly-in shot framed symmetrically, shallow depth of field. Style: warm cinematic photorealism reminiscent of Wes Anderson. Atmosphere: peaceful, anticipatory, intimate.

### Scene 4 — THE DERVISH ASCENDS
> A whirling dervish dancer in flowing white robes and a tall conical felt cap spins in graceful continuous rotation on the open plaza in front of an iconic mosque silhouette at twilight. His arms extend gracefully, one palm to the sky, one to the earth. Above his head a small glowing golden World Cup trophy levitates and slowly rotates in counter-direction. Soft mystical golden light radiates from below. Slow orbiting camera shot following the dervish at chest height, slight low angle. Style: spiritual cinematic surrealism. Atmosphere: transcendent, joyful, sacred celebration.

### Scene 7 — THE CATS BLESS IT
> Two dozen Istanbul street cats of mixed colors — orange, white, black, gray, tabby — sit in a perfect circle on damp cobblestone in a narrow alley, gazing inward at a tiny golden World Cup trophy that sits at the center of the circle. The cats remain still, almost ceremonial, eyes glowing softly in the warm amber light from overhanging lanterns. A faint mist drifts past. Low-angle wide shot at cat eye-level, slight push-in. Style: absurd cinematic intimacy, soft photorealism. Atmosphere: surreal cute, mystical, unspoken blessing.

## What to call this piece

**File / piece name:** `pieces/wc_turkey_dream/`
**Suggested final video filename:** `wc_turkey_dream.mp4`
**Suggested social caption:** *"Türkiye didn't qualify. But what if. 🇹🇷⚽ — a fever dream."*

---

## Approval gates before I burn credits

1. **Tone OK?** Warm-affectionate, not mocking. Confirm.
2. **Scene list OK?** Want to swap any of the 10 AI-generated scenes? Add a Galatasaray/Fenerbahçe fan-unity beat? Remove the cats?
3. **Generation budget OK?** ~84 credits of 178 remaining (~47%). Or cap at 60 credits = fewer retries = pick best-of-1 per scene.
4. **Audio direction OK?** Synthesized Turkish-folk bed locally, or skip audio and you add music externally?

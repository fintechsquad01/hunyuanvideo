# TÜRKİYE 2026: BİR HAYAL — handoff

Status as of 2026-05-23: **all 12 scenes generated** (server-side, on CloudFront).
Local title cards rendered (`wc_turkey_t01_title.mp4`, `wc_turkey_t02_outro.mp4`).
Local audio bed synthesized (`wc_turkey_audio_bed.wav`).
**Pending:** the final composite. This session can't reach CloudFront (host_not_allowed),
so the composite needs to happen in a fresh session whose outbound allowlist
includes the CDN.

## Run in a fresh session

```bash
cd world-cup-loops
python pieces/wc_turkey_dream/build_long_form.py
```

That script reads `job_urls.json`, downloads the 12 scene MP4s, normalizes,
hard-cut concatenates (intro title → 12 scenes → outro title), mixes the
synth bed with the native audio from the 2 hero scenes, and writes
`output/wc_turkey_dream.mp4` (~79 seconds, 9:16, 768×1344).

## All 12 scenes (click to preview in browser)

| # | Scene | Duration | Model | URL |
|---|---|---:|---|---|
| 1 | THE CALM | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230153_3e70339d-e95f-464f-a232-0c3e4605435f.mp4 |
| 2 | THE GOAL | 4s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230156_7d7cb32a-af00-4fee-b2be-66fdd2c31873.mp4 |
| 3 | GALATA ERUPTS | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230329_c44a0788-bcd2-4283-80e1-566597fa368f.mp4 |
| 4 | THE DERVISH ASCENDS | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230334_b1d873de-7ab3-4f05-88c9-cab82e7a96fe.mp4 |
| 5 | CAPPADOCIA RAPTURE | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230210_d608eb01-b4fb-4a14-85d6-beb44dd1d4d0.mp4 |
| 6 | **BOSPHORUS TRIUMPH** ⭐audio | 6s | veo3_1 | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230338_2ba13dab-1887-45de-859c-f42ce3779a15.mp4 |
| 7 | DERBY DISSOLVES | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230515_aa2937f1-13d5-4761-93d1-6ffe557d3fac.mp4 |
| 8 | SIMIT ASCENSION | 4s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230220_8b82c2e4-000f-49b2-8de5-de4fbfec0a9c.mp4 |
| 9 | THE CATS BLESS IT | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230413_dc54dc8f-ce6d-438f-9486-a2543aac72ac.mp4 |
| 10 | BAKLAVA REVELATION | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230631_13c69c95-2827-4cf9-b8ce-51dbf5873c0e.mp4 |
| 11 | **TAKSİM CHAOS** ⭐audio | 6s | veo3_1 | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230636_09bc517d-05cf-4fa9-aaec-440bdcf2783b.mp4 |
| 12 | THE WAKE | 6s | veo3_1_lite | https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_20260523_230804_54bbe8a0-8167-4384-89dc-2b23f6dc66d5.mp4 |

## Spend

| Item | Credits |
|---|---:|
| 10 silent scenes (veo3_1_lite × 6) | 60 |
| 2 hero scenes with native audio (veo3_1 × 16) | 32 |
| **Total** | **92** |
| Remaining of original 178 | **86** |

## What's already on disk

- `pieces/wc_turkey_dream/concept.md` — the storyboard + tone bible
- `pieces/wc_turkey_dream/scenes.py` — all 12 prompts in HunyuanVideo-template structure
- `pieces/wc_turkey_dream/job_urls.json` — completed scene URLs (pickup point)
- `pieces/wc_turkey_dream/render_titles.py` — title card renderer (already ran, output committed below)
- `pieces/wc_turkey_dream/audio_synth.py` — Hicaz-makam-inspired bed synthesizer (already ran)
- `pieces/wc_turkey_dream/build_long_form.py` — the composite pipeline (run this in new session)

## Caveats / quality notes

1. **Two scenes ended up at 4s** instead of 6s because `veo3_1_lite` only
   allows durations in `[4, 6, 8]` and the API silently clamped my 5s
   requests down. Affects s02_goal (the punchline cut so 4s actually works)
   and s08b_simit (a bit tight — could be re-rolled if you want).
2. **The dervish scene** turned out — surprisingly — without preset
   rejection. We bypassed the Higgsfield "IN THE DARK" preset suggestion
   on the second pass with `declined_preset_id`.
3. **Hero audio scenes** were heavily re-prompted by Veo3.1 full's
   prompt-enhancer (you can see the full re-written prompts in the
   `job_display` outputs). The atmospheric audio direction made it through.
4. **Disclaimer in the outro**: "Turkey didn't qualify for WC2026" is the
   factual hook. If you want a different framing (e.g., "If only…" or
   "What if 2030?"), edit `render_titles.py` and re-render — costs nothing.

## If you want polish iterations

Rerolls cost 6 credits each (lite) or 16 (hero). Suggested candidates:
- **s02_goal** at 6s instead of 4s (currently feels abrupt)
- **s08b_simit** at 6s instead of 4s (currently feels tight)
- **s04_dervish** if the trophy doesn't read clearly (cultural sensitivity check)

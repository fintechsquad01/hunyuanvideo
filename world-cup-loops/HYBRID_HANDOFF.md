# Hybrid Pipeline Handoff — AI Opener × Path Explainer

**Status:** waiting for network policy refresh. The current session can't download the Veo MP4s from `d8j0ntlcm91z4.cloudfront.net` because the host isn't in the running session's allowlist. The user added the host to the env's network policy on 2026-05-23, but per Claude Code on the web docs the change applies **at session start**, not mid-session.

## Resume in a new session

When you start a fresh session in this environment, run:

```bash
cd world-cup-loops
python pieces/wc_path/resume_hybrid.py
```

The script will pull every queued opener URL, composite each with its corresponding `wc_path_<CODE>.mp4`, and ship the hybrid MP4s.

## Queued openers (Veo 3.1 Lite, 9:16, 6s, 1080p)

| Country | Job ID | Status | Storyline |
|---|---|---|---|
| **ARG** | `0cb7c293-9011-47e6-909b-f240994fed1f` | ✅ completed | Defending champ — Buenos Aires fan crowd, albiceleste scarves swirling |
| **ESP** | `acac7106-401a-455e-ab24-c03531d27c6b` | ✅ completed | Top favorite (19.3%) — Madrid plaza, gothic spires, regal scale |
| **USA** | `d1c99500-911e-4c12-8e86-58a14f08fe83` | ✅ completed | Host nation underdog — MetLife at twilight, fireworks, NYC skyline |
| ~~MAR v1~~ | `3682c164-5606-4262-a8c2-0e1dd162ce00` | ❌ nsfw filter (barefoot child) | (rejected, re-prompted) |
| **MAR v2** | `e16ea3e3-baea-45a6-8250-99db3d935cc6` | ✅ completed | Underdog story — Jemaa el-Fna square, adult fans, lanterns, mint tea |

URLs follow the pattern `https://d8j0ntlcm91z4.cloudfront.net/user_2zPWkqtneqyhRkLMkTkQ8NZFuwt/hf_<TIMESTAMP>_<JOB_ID>.mp4`. The script uses `mcp__a5d1e111-684a-41f7-b204-490d4bdded5c__job_display` to fetch the canonical URL per job, then downloads.

## What's already shipped

- `wc_engines/path_explainer.py` — the 16s data-driven path piece (R32 → R16 → QF → SF → Final → Champion ladder)
- `pieces/wc_path/render.py` — renders the path explainer per country, takes a country code
- `pieces/wc_path/composite.py` — stitches an opener + path explainer with 0.3s xfade
- `output/wc_path_{ARG,ESP,USA}.mp4` — already-rendered path explainers ready to composite
- `HUNYUAN_STRATEGY.md` — strategy doc explaining the hybrid format and why

## What the new session needs to do

1. Confirm cloudfront is now reachable: `curl -I https://d8j0ntlcm91z4.cloudfront.net/`
2. If yes, run `resume_hybrid.py` (next file in this commit)
3. If no, the user needs to verify their env has the allowlist applied — possibly start the new session from the **same** environment that has the policy (not a different one)

## Cost spent so far (of 208 ultimate-plan credits)

- 4 × 6 credits = **24 credits** on Veo 3.1 Lite generations
- Balance after: ~184 credits remaining

# zen-loops archetypes

7 locked archetypes for satisfying-simulation content.

## Z1 — Plinko Identity Race (flagship)

**What**: Marbles drop through pegs labeled with viewer-identity dimension (birth month / zodiac / initial / country / year).
**Pick when**: any identity dimension worth racing.
**Identity hooks**: "YOUR BIRTH MONTH IS YOUR RACER" / "PICK YOUR ZODIAC" / "WHICH LETTER WINS?"
**Engine**: `marble_drop` or `marble_drop_pro`
**Beat skeleton (14s)**: hook → drop animation → mid-race tension → winner banner → "COMMENT IF YOURS WON"

## Z2 — Ring Expansion (musical / guess-the-song)

**What**: Single ball in growing ring; each wall hit plays one note of a PD melody. Song reveals at end.
**Pick when**: melody-led identity; "guess the song" comment-bait.
**Identity hooks**: "GUESS THE SONG" / "ONLY MUSIC NERDS KNOW THIS ONE" / "WHEN DID YOU GET IT?"
**Engine**: `ring_expansion`
**Beat skeleton (15s)**: hook → first notes (uncertainty) → melody resolves → song title reveal with confetti → "TAG SOMEONE WHO MISSED IT"

## Z3 — Bouncing Spheres (ambient loop)

**What**: Pure ambient bouncing — no identity, no challenge, just satisfying motion. Fills posting cadence between identity races.
**Pick when**: no strong identity angle today; need posting frequency.
**Identity hooks**: weakest — "Comment a color" / "Pick a ball"
**Engine**: `bouncing_spheres`
**Beat skeleton (12s)**: motion already running → speed escalation → mini-resolution → loop

## Z4 — Color Battle (territory fill)

**What**: Two colors flood a maze from opposite ends. Viewer picks side. One color wins by filling more area.
**Pick when**: binary identity ("red vs blue", "team A vs team B", "introvert vs extrovert").
**Identity hooks**: "PICK YOUR COLOR" / "RED OR BLUE?" / "ARE YOU TEAM [X]?"
**Engine**: NEW (not yet built — flag as gap)
**Beat skeleton (14s)**: hook with binary prompt → both colors flood → leader switches → final fill reveal

## Z5 — Failable Tracker

**What**: One target marble among N decoys; viewer must track it for the full clip. Most people lose it by 0:08.
**Pick when**: pure challenge content, no identity needed.
**Identity hooks**: "99% CAN'T FOLLOW THE RED ONE" / "COMMENT WHEN YOU LOST IT"
**Engine**: `bouncing_spheres` with target highlight
**Beat skeleton (14s)**: target reveal → spheres mix in → chaos → final position reveal → "DID YOU CATCH IT?"

## Z6 — Personality Bucket Drop

**What**: Ball makes simulated "choices" through branching paths → lands in one of 5 personality buckets. Viewer maps to their bucket.
**Pick when**: psychology-coded content (MBTI, attachment style, love language, productivity type).
**Identity hooks**: "WHICH BUCKET ARE YOU?" / "YOUR REACTION = YOUR TYPE"
**Engine**: NEW (Plinko variant with buckets) — flag as gap
**Beat skeleton (14s)**: ball drops → choices fork left/right → settles in bucket → bucket name reveal → "TAG SOMEONE WHO'S [TYPE]"

## Z7 — Hyper-textural Loop (2026 trend)

**What**: Gummy / jelly / wax / liquid metal textures — slow-mo close-ups of tactile materials.
**Pick when**: post-identity content (tactile satisfaction, no identity required); cross-pollination with ASMR audience.
**Identity hooks**: weakest — "COMMENT YOUR FAVORITE TEXTURE"
**Engine**: AI video (HunyuanVideo / Fal.ai / Higgsfield) — generative, not physics
**Beat skeleton (12s)**: texture in motion → close-up zoom → satisfying climax (bounce, pour, snap) → loop

---

## Picking the archetype — decision tree

```
Is there an identity dimension? → Z1 (Plinko) is default
Is melody / "guess the song" core? → Z2 (Ring Expansion)
Is there a clear binary side? → Z4 (Color Battle)
Is it a tracker/focus challenge? → Z5 (Failable Tracker)
Is it psychology/quiz-coded? → Z6 (Bucket Drop)
Is it tactile / texture-led? → Z7 (Hyper-textural)
None of the above + just need cadence content? → Z3 (Bouncing Spheres)
```

## Cross-platform reminder

All zen-loops content goes to IG Reels + TikTok + YT Shorts. Format = 1080×1920 @ 30fps, 12–15s, looping. Use `cross-platform-distributor` skill for per-platform copy.

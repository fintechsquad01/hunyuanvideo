# Idea Backlog — Reverse-Engineered Formats

**Rules of use**: this is a draw-from list, not a build-everything list. We commit to building a format only after the current archetypes have produced 7+ days of real posting data. Until then, this is cheap inventory.

## The viral primitives

Every working format in this niche stacks 2–4 of these:

1. **Identity projection** — viewer sees themselves on screen
2. **Binary stake** — clear win/lose with viewer attached
3. **Failable challenge** — viewer can fail ("99% can't")
4. **Audio-visual synchrony** — sound emerges from physics
5. **Compounding chaos** — starts simple, escalates to overload
6. **Predictable surprise** — you know X happens; not when
7. **Pattern reveal** — chaos resolves to hidden order
8. **Real-time stakes** — counter/timer/% ticks visibly
9. **Tactile satisfaction** — "want to touch" textures
10. **Social comparison** — "what % are you?"

## Format candidates

| # | Format | Primitives stacked | Engine fit | Build cost | Novelty | Notes |
|---|---|---|---|---|---|---|
| F1 | **Battle Royale Elimination** — 100 colored balls; one dies per 150ms; last survives | 1,2,5,8 | Python ext | M | Mid | Counter ticking down is hypnotic. Identity via color picker. |
| F2 | **Color War Maze Fill** — two colors flood a maze from opposite ends; viewer picks side | 1,2,5,8 | Python ext | M-H | Mid | "Red or Blue?" is the most-engaged poll question on social. |
| F3 | **Tournament Bracket** — 16→8→4→2→1; marbles fight head-to-head | 1,2,6,8 | Python ext | M | High | Mirrors sports brackets; works around real-world tournaments. |
| F4 | **Tier List Drop** — items fall into S/A/B/C/D tiers; viewer guesses | 1,3,7 | Python | L | Mid | "Where will Spotify land?" type framing. |
| F5 | **Cell Division** — 1 ball → 2 → 4 → 8 → screen fills, audio crescendo | 4,5,6 | Python ext | M | Mid | Pure compounding chaos; ends in white-noise wall of bouncers. |
| F6 | **Piano Roll Bouncer** — ball bounces between piano keys, playing a real song | 4,6,7 | Python ext | H | High | Each key strike = the right note in a recognizable melody. Skill: predict the next note. |
| F7 | **Galton Bell Curve** — 10,000 balls drop through pegs, statistical bell forms live | 5,7,8 | Python | M | High | Pattern reveal: chaos → bell curve is shockingly satisfying. |
| F8 | **Watch the Red One** — 1 red ball among 50 white; viewer tracks for 15s | 3,6,8 | Python | L | Mid | Hard mode: balls go behind occluders. "I lost it at 0:08." |
| F9 | **Eye Test Imposter** — all balls bounce identically; one moves 5% differently | 3,7 | Python | L | Mid | "Find the imposter in 10 seconds." Solver is a comment-engine. |
| F10 | **"Don't Blink"** — peaceful loop, then sudden visual event at random | 3,6 | Python | L | Low | Cheap but proven format. Slight tension throughout. |
| F11 | **Pong Infinity** — paddles & balls multiply until the canvas is full | 5,6 | Python ext | M | Mid | Visual cousin of cell division but with explicit gameplay shapes. |
| F12 | **Jelly Squeeze** — gummy ball deforms through shrinking hole | 6,9 | HunyuanVideo / Veo / soft-body sim | M | High | 2026 Adobe "All the Feels" trend. Lean into tactile. |
| F13 | **Wax Drip Reveal** — wax pours, solidifies into a recognizable shape (logo, letter, country) | 7,9 | AI video or shader | M-H | High | Pattern reveal + tactile. Strong for brand-deal repurposing. |
| F14 | **Pixel Sort Reveal** — chaotic noise sorts itself into an image | 7,8 | Python | L | Mid | Pure satisfaction. Image reveal at end keeps watchers. |
| F15 | **Particle Text** — 5000 particles converge into a word/number | 7,8 | Python (numpy) | M | Mid | "Your IQ is…" framing. High share rate. |
| F16 | **Marble Race + AI Commentary** — sportscaster narrates a Plinko in real English | 1,2,4 | Plinko + TTS | M | High | Adds parasocial layer to existing engine. Cheap moat. |
| F17 | **Survival Counter** — bouncer in arena; timer ticks; eventually a hazard hits | 3,8 | Python | L | Mid | "How long can you watch without the wall closing in?" |
| F18 | **Personality Bucket Drop** — ball drops into one of 5 buckets based on simulated choices | 1,10 | Python | M | High | "Your reaction = your personality type." Direct identity hook. |
| F19 | **Glass Smash Composition** — each broken pane = one melody note | 4,6,9 | AI video or Unity | H | High | Tactile + musical. Premium production required. |
| F20 | **Particle Aggregation Calendar** — particles arrange into "MAY 23" or today's date | 6,7 | Python | L | Low | Daily-post format; trivial variant. |
| F21 | **"Which one will fall first?"** — 4 objects in unstable physics; viewer picks | 1,2,6 | Python | L-M | Mid | Direct binary stake. Replayable. |
| F22 | **Spin-the-Wheel Replacement** — Plinko as a "pick" mechanic; ball decides a thing for viewer | 1,8 | Plinko remix | L | Mid | "Should I quit my job? Plinko decides." Casual format. |
| F23 | **Synesthesia Visualizer** — pre-recorded melody → balls bouncing in patterns matching melody | 4,7 | Python + librosa | M | High | Audio-FIRST: melody drives visuals (inverse of ring expansion). |
| F24 | **Speed Run Timer** — a loop runs N times; timer shows record being chased | 3,6,8 | Any engine | L | Low | Adds urgency layer to any existing format. Composable. |
| F25 | **AI-Generated Faces on Marbles** — celeb/historical-figure faces race | 1,2 | Plinko + AI image | M | High | Higher production but huge identity hook. Watch IP carefully. |

Legend:
- Engine fit: `Python` = current pipeline; `Python ext` = ~1 day extension; `Unity` = needs new engine; `AI video` = HunyuanVideo/Veo/Sora
- Build cost: L = <4h, M = 1 day, H = 2-3 days
- Novelty: Low = many clones already; Mid = a few clones; High = nobody owns it yet

## Cluster recommendations

If we eventually need to expand the archetype set, the cheapest high-novelty cluster is:

- **F3 Tournament Bracket** + **F7 Galton Bell Curve** + **F16 Marble Race + AI Commentary** — all sit on top of the existing `marble_drop` engine with extensions. Builds on what works.
- **F18 Personality Bucket Drop** + **F22 Spin-the-Wheel Plinko** — strongest pure identity-projection formats; complement Plinko Race rather than replace.
- **F12 Jelly Squeeze** + **F13 Wax Drip** — the tactile 2026 trend cluster; needs HunyuanVideo or shader work. Different production lane entirely.

## Sequencing rule

Build only after the current 3 archetypes have produced posting data:
1. Post existing videos to all 3 platforms
2. After 7 days, identify which primitives (per Part 1 list) correlate with engagement
3. Pick the next format from this backlog that doubles down on the winning primitives — not the prettiest idea, the one with the strongest evidence-based primitive match

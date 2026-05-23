# Brand voice contract — pitch.predict

Extracted from `world-cup-loops/design/project/README.md`. This file is the authoritative contract for the storyboard skill. Every storyboard checks against this before output.

## Tone — one line

**FiveThirtyEight rigor × ESPN morning show pace.** Authoritative-playful, never breathless. The smart friend at a watch party — not the screaming one.

## Person & address

- Third-person + "you" for the read: *"The numbers say Spain's marble survives 60% of simulations."*
- Imperative on CTAs: *"Comment your pick."* *"Tag a friend who's wrong."*
- Never first-person ("we" / "us"), except in legal/footer copy.

## Casing

| Element | Casing | Font |
|---|---|---|
| Hook band (top 7%) | ALL CAPS | Inter Bold or Anton |
| CTA band (bottom 7%) | ALL CAPS | Anton |
| Winner reveals | ALL CAPS | Anton |
| Body / landing-page paragraphs | sentence case | Inter Semibold |
| Numerics ("60%", "R32", "QF") | as-is | Roboto Condensed Bold, **tabular nums** |

## Numbers & units

- **Show the source**: "Polymarket: France 18%." "Elo: 2165."
- Round percentages to whole numbers in chrome ("18%", not "18.4%"). Keep precision in body copy if it matters.
- Round indicators are abbreviations: **R32 / R16 / QF / SF / FINAL**.
- Country = **3-letter code** beside flag color. **Never** long-form country names in chrome.

## Emoji

**Almost never.** Two exceptions:
1. **A7 Country Food Race** — cultural food emoji (🍕 🍣 🫖) as marble labels. The whole format is the joke.
2. **Landing-page footer social icons** — actual platform marks (not emoji).

## Things to say vs things to never say

| ✅ DO | ❌ DON'T |
|---|---|
| "The numbers say Spain's marble survives 60% of simulations." | "OMG won't BELIEVE who wins this race 🤯🤯🤯" |
| "Polymarket: France 18%. Plinko: France one of every five runs." | "BET ON SPAIN!" |
| "Group D is brutal. Argentina favored. Egypt's been live in friendlies." | "Group of DEATH! Who advances?!?!" |
| "Comment your pick before kickoff." | "FOLLOW NOW OR REGRET IT 🔥🔥🔥" |
| "Polymarket says X. Plinko says Y." | "GUARANTEED WINNER 🤑" |
| "Fan poll / prediction / simulator" | "Odds / wager / bet" (platform-risky) |

## Platform-policy reframing (mandatory sweep)

Before outputting any storyboard, sweep all text overlays and CTAs for these forbidden words. Replace with the safe equivalent:

| ❌ Forbidden | ✅ Replacement |
|---|---|
| "odds" | "prediction market" / "fan consensus" / "implied probability" |
| "bet" | "pick" / "simulator says" / "plinko says" |
| "wager" | "back" / "root for" / "comment your pick" |
| "betting" | "predicting" / "fan polling" |
| "bookmaker" | "prediction market" |
| "place a bet" | "make your pick" |
| "winnings" | "score" / "points" |

TikTok and IG will flag any of the left-column words even in passing. Never ship with them.

## IP risks (forbidden in chrome)

- **FIFA marks** (the FIFA wordmark, official tournament logo, "FIFA World Cup™" with TM)
- **Team crests / club badges** (Bayern's diamond, Madrid's crown, Barça's shield, national federation crests)
- **Player likenesses** (photos, AI-generated faces of real players)
- **Photographic backgrounds of stadiums, crowds, or players**

**Allowed**:
- 3-letter country codes (BRA, ARG, ESP, etc.)
- Flat-color country flag blocks (no actual flag images)
- National-team nicknames in body copy ("Selección," "Three Lions") — text only, never as logos
- Player names in body copy (text), not on marbles or in chrome

## Sound / audio

- **No copyrighted music** ever in chrome or as primary audio
- **Allowed**: public-domain melodies (Twinkle, Ode to Joy, Für Elise, Pachelbel, Greensleeves, Frère Jacques, Mary Had a Little Lamb, Old MacDonald, Amazing Grace, Happy Birthday, minor arpeggio)
- **Allowed**: original commissioned tracks (Suno, ElevenLabs Music — paid commercial tier)
- **Allowed**: TikTok / IG native trending sounds (but ONLY on the host platform, never muxed and cross-posted; never on funnel-driving posts)
- **Forbidden**: ripping anthems, stadium chants with team identifiers, video-game OSTs

## Voice in storyboard hooks (examples)

Strong hooks the skill should produce:
- "WHAT IF THE SMALLEST COUNTRY WINS?"
- "NORWAY HASN'T BEEN HERE SINCE 1998"
- "GROUP D HAS A 23% UPSET PROBABILITY"
- "$1.1B SAYS FRANCE. WE DISAGREE."
- "PICK YOUR COUNTRY"
- "THE BIGGEST GAP IN WC HISTORY"

Weak hooks the skill should reject:
- "OMG YOU WON'T BELIEVE THIS!!!" (too breathless)
- "GAMBLE ON THESE TEAMS" (platform-risky)
- "FIFA WORLD CUP 2026™" (IP)
- "ARSENAL FANS PUNCHING THE AIR" (off-niche, social-meme tone)

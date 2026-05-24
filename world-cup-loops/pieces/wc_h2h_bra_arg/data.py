"""Brazil vs Argentina — all-time head-to-head (men's senior, FIFA-recognized).

Numbers cited from Elo Football's historical record through 2024:
  113 meetings · BRA 47 W · 26 D · ARG 40 W
  (sources differ slightly by 1-3 matches depending on inclusion criteria;
  these are the conservative consensus figures we'll cite on screen.)

Visual metaphor: Brazil = Jaguar (the country's iconic apex predator,
"Onça"). Argentina = Puma (the Andean apex predator, "Yaguareté" /
"Puma concolor"). Two big cats facing each other in golden hour.
"""

from __future__ import annotations

MEETINGS = 113
BRA_WINS = 47
ARG_WINS = 40
DRAWS = 26
assert BRA_WINS + ARG_WINS + DRAWS == MEETINGS, "data sanity"

LEADER = "BRA" if BRA_WINS > ARG_WINS else "ARG"
LEAD = abs(BRA_WINS - ARG_WINS)

FAL_PROMPT = (
    "Cinematic photoreal wide shot, two majestic apex big cats facing each "
    "other across a misty grassland clearing at golden hour, a powerful "
    "jaguar with golden rosette-spotted fur on the left side of the frame "
    "and a sleek tawny puma on the right side, both lit by warm low sun, "
    "atmospheric morning mist rolling between them, deep golden and amber "
    "sky behind, soft volumetric god rays, faint dust particles in the "
    "light, no text, no logos, no people, 9:16 vertical composition with "
    "the animals in the middle band, ample dark area at top and bottom for "
    "overlay text. National Geographic style cinematography, dramatic, "
    "anthemic, contemplative tension."
)

NARRATION_OPEN = "Brazil. Argentina. Football's oldest war."
NARRATION_CLOSE = f"Brazil leads by {LEAD}. Who wins next?"

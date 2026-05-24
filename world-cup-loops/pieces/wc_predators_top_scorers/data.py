"""Top 6 all-time men's FIFA World Cup goalscorers.

Through the 2022 tournament. Source: FIFA official tournament records.
"""

from __future__ import annotations

SCORERS: list[dict] = [
    {"rank": 1, "name": "M. Klose",     "country": "GER", "goals": 16, "wcs": "2002–2014"},
    {"rank": 2, "name": "Ronaldo",      "country": "BRA", "goals": 15, "wcs": "1998–2006"},
    {"rank": 3, "name": "G. Müller",    "country": "GER", "goals": 14, "wcs": "1970–1974"},
    {"rank": 4, "name": "J. Fontaine",  "country": "FRA", "goals": 13, "wcs": "1958"},
    {"rank": 5, "name": "L. Messi",     "country": "ARG", "goals": 13, "wcs": "2006–2022"},
    {"rank": 6, "name": "Pelé",         "country": "BRA", "goals": 12, "wcs": "1958–1970"},
]

# Subtle per-country accent (brand-flat colors — NOT flag images)
COUNTRY_ACCENT = {
    "GER": (255, 200, 0),
    "BRA": (253, 198, 17),
    "FRA": (60, 130, 230),
    "ARG": (108, 188, 222),
}

FAL_PROMPT = (
    "Cinematic photoreal wide hero shot at golden hour, a powerful "
    "single apex predator big cat — a regal lion with a thick golden mane "
    "— standing in profile on a vast misty African savanna ridge, lit by "
    "warm low sun from behind, dramatic backlight, atmospheric haze and "
    "dust catching the light, no other animals, no text, no logos, "
    "9:16 vertical composition with the lion in the upper third leaving "
    "ample dark space at the bottom for overlay content. National Geographic "
    "style, anthemic, regal, contemplative."
)

NARRATION_OPEN = "Six predators. Six legends. One throne."
NARRATION_CLOSE = "Klose by one. Who is your goat?"

"""WC2026 host venues — elevation in meters.

All 16 stadiums confirmed by FIFA for the 2026 men's World Cup.
Elevations are stadium-floor figures (rounded). Sorted as displayed:
ascending altitude, so the eye climbs left to right.

Source: FIFA WC2026 venue announcements + public geographic data.
"""

from __future__ import annotations

VENUES: list[dict] = [
    {"city": "Vancouver",    "code": "VAN", "country": "CAN", "elev_m":    3},
    {"city": "Miami",        "code": "MIA", "country": "USA", "elev_m":    5},
    {"city": "San Francisco", "code": "SF", "country": "USA", "elev_m":    6},
    {"city": "New York/NJ",  "code": "NYC", "country": "USA", "elev_m":    7},
    {"city": "Seattle",      "code": "SEA", "country": "USA", "elev_m":    8},
    {"city": "Philadelphia", "code": "PHI", "country": "USA", "elev_m":   12},
    {"city": "Houston",      "code": "HOU", "country": "USA", "elev_m":   15},
    {"city": "Boston",       "code": "BOS", "country": "USA", "elev_m":   30},
    {"city": "Los Angeles",  "code": "LA",  "country": "USA", "elev_m":   30},
    {"city": "Toronto",      "code": "TOR", "country": "CAN", "elev_m":   76},
    {"city": "Dallas",       "code": "DAL", "country": "USA", "elev_m":  180},
    {"city": "Kansas City",  "code": "KC",  "country": "USA", "elev_m":  265},
    {"city": "Atlanta",      "code": "ATL", "country": "USA", "elev_m":  320},
    {"city": "Monterrey",    "code": "MTY", "country": "MEX", "elev_m":  370},
    {"city": "Guadalajara",  "code": "GDL", "country": "MEX", "elev_m": 1560},
    {"city": "Mexico City",  "code": "MEX", "country": "MEX", "elev_m": 2240},
]

# Per-country flag accent (deterministic, on-brand — flat colors only)
COUNTRY_COLOR = {
    "USA": (60, 130, 230),
    "MEX": (28, 158, 76),
    "CAN": (220, 40, 40),
}

FAL_PROMPT = (
    "Cinematic photoreal panoramic mountain range at dawn, low rolling fog "
    "filling the valleys, sixteen distinct peaks of widely varying heights "
    "stretching across the horizon — most peaks modest, two towering peaks "
    "rising dramatically above the rest on the right side. Deep blue and "
    "golden-orange morning sky, soft volumetric god rays, no buildings, "
    "no people, no text, no logos, ultra wide aspect, 9:16 vertical "
    "composition with mountains occupying the upper two thirds. Majestic, "
    "geological, contemplative atmosphere."
)

NARRATION_OPEN = "Sixteen stadiums. Three countries. Two miles between top and bottom."
NARRATION_CLOSE = "Welcome to the first tri-country World Cup."

if __name__ == "__main__":
    for v in VENUES:
        print(f"  {v['code']:>4}  {v['country']}  {v['elev_m']:>5}m  {v['city']}")
    print(f"Range: {VENUES[0]['elev_m']}m → {VENUES[-1]['elev_m']}m "
          f"(Δ {VENUES[-1]['elev_m'] - VENUES[0]['elev_m']}m)")

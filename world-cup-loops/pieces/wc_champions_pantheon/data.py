"""All FIFA World Cup winners 1930-2022, in chronological order.

22 World Cups, 8 unique champions:
  BRA 5  ITA 4  GER 4  ARG 3  URU 2  FRA 2  ENG 1  ESP 1

Sorted on display by (wins desc, first-win year asc) so the layout reads:
  BRA, ITA, GER, ARG, URU, FRA, ENG, ESP
"""

from __future__ import annotations

# (year, country_code) in chronological order. 1942 and 1946 cancelled (WW2).
WINNERS: list[tuple[int, str]] = [
    (1930, "URU"),
    (1934, "ITA"),
    (1938, "ITA"),
    (1950, "URU"),
    (1954, "GER"),
    (1958, "BRA"),
    (1962, "BRA"),
    (1966, "ENG"),
    (1970, "BRA"),
    (1974, "GER"),
    (1978, "ARG"),
    (1982, "ITA"),
    (1986, "ARG"),
    (1990, "GER"),
    (1994, "BRA"),
    (1998, "FRA"),
    (2002, "BRA"),
    (2006, "ITA"),
    (2010, "ESP"),
    (2014, "GER"),
    (2018, "FRA"),
    (2022, "ARG"),
]

# Display order (sorted by wins desc, then first-win year asc)
COLUMNS: list[str] = ["BRA", "ITA", "GER", "ARG", "URU", "FRA", "ENG", "ESP"]


def tally() -> dict[str, int]:
    out: dict[str, int] = {}
    for _, code in WINNERS:
        out[code] = out.get(code, 0) + 1
    return out


if __name__ == "__main__":
    t = tally()
    for code in COLUMNS:
        print(f"  {code}: {t[code]}")
    print(f"Total: {sum(t.values())} World Cups, {len(t)} champions")

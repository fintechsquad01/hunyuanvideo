"""RapidAPI football client (api-football.com).

Reads RAPIDAPI_KEY from environment. Free tier = 100 req/day; Pro = $50-100/mo
with 7500+ req/day. World Cup 2026 league id = TBD once FIFA announces (search
for it via /v3/leagues?season=2026 after kickoff).

Docs: https://www.api-football.com/documentation-v3
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


BASE = "https://api-football-v1.p.rapidapi.com/v3"


def _get(path: str, params: dict | None = None) -> Any:
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError(
            "RAPIDAPI_KEY not set. Subscribe at "
            "https://rapidapi.com/api-sports/api/api-football and set the key "
            "in your environment before calling football_api_client."
        )
    q = ""
    if params:
        import urllib.parse
        q = "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(
        BASE + path + q,
        headers={
            "X-RapidAPI-Key": key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


@dataclass
class Fixture:
    id: int
    date_utc: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    status: str


def fetch_fixtures(league_id: int, season: int) -> list[Fixture]:
    raw = _get("/fixtures", {"league": league_id, "season": season})
    out = []
    for f in raw.get("response", []):
        out.append(
            Fixture(
                id=f["fixture"]["id"],
                date_utc=f["fixture"]["date"],
                home_team=f["teams"]["home"]["name"],
                away_team=f["teams"]["away"]["name"],
                home_score=f["goals"]["home"],
                away_score=f["goals"]["away"],
                status=f["fixture"]["status"]["short"],
            )
        )
    return out


def fetch_top_scorers(league_id: int, season: int) -> list[dict]:
    """Returns list of {player_name, team, goals, country_code}."""
    raw = _get("/players/topscorers", {"league": league_id, "season": season})
    out = []
    for p in raw.get("response", []):
        out.append({
            "player_name": p["player"]["name"],
            "nationality": p["player"]["nationality"],
            "team": p["statistics"][0]["team"]["name"],
            "goals": p["statistics"][0]["goals"]["total"],
        })
    return out


def fetch_standings(league_id: int, season: int) -> list[dict]:
    raw = _get("/standings", {"league": league_id, "season": season})
    out = []
    for league in raw.get("response", []):
        for group in league["league"]["standings"]:
            for row in group:
                out.append({
                    "rank": row["rank"],
                    "team": row["team"]["name"],
                    "points": row["points"],
                    "played": row["all"]["played"],
                    "won": row["all"]["win"],
                    "drawn": row["all"]["draw"],
                    "lost": row["all"]["lose"],
                    "gf": row["all"]["goals"]["for"],
                    "ga": row["all"]["goals"]["against"],
                    "form": row.get("form", ""),
                })
    return out

"""Supabase client placeholder.

Waiting for the project ID + access keys. Once provided:
1. set SUPABASE_URL and SUPABASE_KEY env vars (or use a .env)
2. inspect schema via the Supabase MCP (list_tables, generate_typescript_types)
3. fill in the typed query helpers below for the relevant tables

Expected tables in the user's DB (to be confirmed by introspection):
- teams           (club + national)
- players
- fixtures        (per-league, per-season)
- player_stats
- team_stats
- league_seasons

Use the postgrest REST API for read queries:
  GET {SUPABASE_URL}/rest/v1/{table}?select=*&{filter}
  Headers: apikey + Authorization: Bearer {SUPABASE_KEY}
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any


def _supabase_get(table: str, query: dict | None = None) -> Any:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY not set. Configure once the user "
            "shares their Supabase project credentials."
        )
    q = "?" + urllib.parse.urlencode({"select": "*", **(query or {})})
    req = urllib.request.Request(
        f"{url}/rest/v1/{table}{q}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def list_player_history(player_id: str) -> list[dict]:
    """Stub: fetch a player's career history once the schema is confirmed."""
    raise NotImplementedError("Wire after Supabase schema introspection.")


def list_h2h(team_a: str, team_b: str, limit: int = 20) -> list[dict]:
    """Stub: head-to-head fixtures between two teams."""
    raise NotImplementedError("Wire after Supabase schema introspection.")


def league_table(league: str, season: int) -> list[dict]:
    """Stub: current league table."""
    raise NotImplementedError("Wire after Supabase schema introspection.")

"""STEP 1 / DATA LAYER — turn ESPN's raw JSON into clean tables.

Nothing here creates a chart. That's intentional: each part of the website
should have ONE job. Data is loaded here; analysis is done in metrics.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


# These headers describe the simple table we want, independently of ESPN's JSON.
GAME_COLS = [
    "Season", "Week", "Game ID", "Phase", "Home ID", "Away ID",
    "Home Team", "Away Team", "Home Owner", "Away Owner",
    "Home Score", "Away Score", "Winner ID", "Margin", "Total Points", "Playoff Tier",
]
TEAM_COLS = ["Season", "Team ID", "Team", "Owner ID", "Manager"]


# MANAGER ID ALIASES — give one real person a consistent identity across seasons.
# ESPN accounts sometimes change while the same manager stays in the league.
# Add new entries only after verifying that two records are the SAME person.
# Format: "normalized manager name": "your permanent manager identifier"
MANAGER_ALIASES = {
    "henry hanlon": "manager:henry_hanlon",
}


def canonical_owner_id(manager_name: str, original_owner_id: str) -> str:
    """Use a verified alias, or preserve the ESPN ID for everyone else."""
    # The join/split makes extra whitespace and capitalization irrelevant.
    clean_name = " ".join(str(manager_name).casefold().split())
    return MANAGER_ALIASES.get(clean_name, original_owner_id)


def _as_float(value):
    """Convert scores safely; an empty / unusable score stays None."""
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def parse_espn(payload: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Read one season from ESPN; skip unfinalized games.

    ESPN schedule entries include future 0-0 games. We use 'winner' rather
    than 'totalPoints' to know if an official result is final.
    """
    if not isinstance(payload, dict) or "teams" not in payload or "schedule" not in payload:
        raise ValueError("This file doesn't look like an ESPN league export (missing teams/schedule).")

    season = int(payload.get("seasonId", 0))
    league_name = payload.get("settings", {}).get("name", "Fantasy League")
    schedule_settings = payload.get("settings", {}).get("scheduleSettings", {})
    reg_weeks = int(schedule_settings.get("matchupPeriodCount") or 14)
    members = {}
    for member in payload.get("members", []):
        first = (member.get("firstName") or "").strip()
        last = (member.get("lastName") or "").strip()
        name = " ".join(p for p in (first, last) if p).strip()
        members[member.get("id")] = name or member.get("displayName", "Manager")

    teams = []
    team_by_id = {}
    for team in payload["teams"]:
        tid = int(team["id"])
        owner = team.get("primaryOwner") or (team.get("owners") or [None])[0]
        team_name = (team.get("name") or f"Team {tid}").strip()
        manager_name = members.get(owner, team_name)
        espn_owner_id = str(owner) if owner else f"{season}-team-{tid}"
        info = {
            "Season": season, "Team ID": tid, "Team": team_name,
            "Owner ID": canonical_owner_id(manager_name, espn_owner_id),
            "Manager": manager_name,
        }
        teams.append(info)
        team_by_id[tid] = info

    games = []
    for game in payload["schedule"]:
        decision = game.get("winner")
        if decision not in {"HOME", "AWAY", "TIE"}:
            continue
        home, away = game.get("home"), game.get("away")
        if not isinstance(home, dict) or not isinstance(away, dict):
            continue
        h_id, a_id = home.get("teamId"), away.get("teamId")
        if h_id not in team_by_id or a_id not in team_by_id:
            continue
        hs, a_s = _as_float(home.get("totalPoints")), _as_float(away.get("totalPoints"))
        if hs is None or a_s is None:
            continue
        week = int(game.get("matchupPeriodId") or 0)
        phase = "Playoffs" if (week > reg_weeks or game.get("playoffTierType", "NONE") != "NONE") else "Regular"
        winner_id = h_id if decision == "HOME" else a_id if decision == "AWAY" else None
        games.append({
            "Season": season, "Week": week, "Game ID": game.get("id"),
            "Phase": phase, "Home ID": h_id, "Away ID": a_id,
            "Home Team": team_by_id[h_id]["Team"], "Away Team": team_by_id[a_id]["Team"],
            "Home Owner": team_by_id[h_id]["Owner ID"],
            "Away Owner": team_by_id[a_id]["Owner ID"],
            "Home Score": hs, "Away Score": a_s, "Winner ID": winner_id,
            "Margin": abs(hs - a_s), "Total Points": hs + a_s,
            "Playoff Tier": game.get("playoffTierType", "NONE"),
        })

    meta = {"season": season, "name": league_name, "team_count": len(teams),
            "regular_weeks": reg_weeks, "games": len(games)}
    return pd.DataFrame(games, columns=GAME_COLS), pd.DataFrame(teams, columns=TEAM_COLS), meta


def read_all_exports(base: Path, uploaded_files=None):
    """Load local JSON files and optional drag-and-drop files.

    If multiple files represent the same season, the most recently loaded
    file wins (uploaded copies override local copies).
    """
    payloads = {}
    errors = []
    paths = sorted(list(base.glob("*.json")) + list((base / "data").glob("*.json")))
    for path in paths:
        try:
            item = json.loads(path.read_text(encoding="utf-8-sig"))
            year = int(item["seasonId"])
            payloads[year] = item
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{path.name}: {exc}")

    for item in uploaded_files or []:
        try:
            data = json.loads(item.getvalue().decode("utf-8-sig"))
            payloads[int(data["seasonId"])] = data
        except (ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
            errors.append(f"{item.name}: {exc}")

    all_games, all_teams, metas = [], [], {}
    for year, payload in sorted(payloads.items()):
        try:
            games, teams, meta = parse_espn(payload)
            all_games.append(games)
            all_teams.append(teams)
            metas[year] = meta
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"Season {year}: {exc}")

    games = pd.concat(all_games, ignore_index=True) if all_games else pd.DataFrame(columns=GAME_COLS)
    teams = pd.concat(all_teams, ignore_index=True) if all_teams else pd.DataFrame(columns=TEAM_COLS)
    return games, teams, metas, errors

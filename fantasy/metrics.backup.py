"""STEP 2 / ANALYTICS LAYER — all numbers, no website widgets.

Each function accepts pandas DataFrames and returns new DataFrames.
This separation lets you test the mathematics without running Streamlit.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def regular_games(games: pd.DataFrame) -> pd.DataFrame:
    return games.loc[games["Phase"].eq("Regular")].copy()


def weekly_scores(games: pd.DataFrame) -> pd.DataFrame:
    """Transform 1 matchup row into 2 team-week rows (home + away)."""
    items = []
    for g in games.to_dict("records"):
        for side, other in (("Home", "Away"), ("Away", "Home")):
            s, o = g[f"{side} Score"], g[f"{other} Score"]
            items.append({
                "Season": g["Season"], "Week": g["Week"],
                "Team ID": g[f"{side} ID"], "Team": g[f"{side} Team"],
                "Owner ID": g[f"{side} Owner"],
                "Opponent ID": g[f"{other} ID"], "Opponent": g[f"{other} Team"],
                "Points": s, "Against": o, "Differential": s-o,
                # Use ESPN's recorded winner (not just score comparison).
                "Result": "T" if g["Winner ID"] is None else "W" if g["Winner ID"] == g[f"{side} ID"] else "L",
                "Phase": g["Phase"],
            })
    return pd.DataFrame(items, columns=[
        "Season", "Week", "Team ID", "Team", "Owner ID", "Opponent ID",
        "Opponent", "Points", "Against", "Differential", "Result", "Phase",
    ])


def standings(games: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Official W/L/T based on final matchups, not projections / future 0s."""
    source = weekly_scores(regular_games(games))
    output = teams[["Team ID", "Team", "Owner ID", "Manager"]].copy()
    if source.empty:
        for c in ("W", "L", "T", "GP"): output[c] = 0
        for c in ("PF", "PA", "Diff", "PPG", "Win %"): output[c] = 0.0
    else:
        source = source.assign(
            W=source["Result"].eq("W").astype(int),
            L=source["Result"].eq("L").astype(int),
            T=source["Result"].eq("T").astype(int),
        )
        stats = source.groupby("Team ID", as_index=False).agg(
            W=("W", "sum"), L=("L", "sum"), T=("T", "sum"),
            GP=("Week", "count"), PF=("Points", "sum"), PA=("Against", "sum"),
        )
        output = output.merge(stats, on="Team ID", how="left")
        for c in ("W", "L", "T", "GP", "PF", "PA"):
            output[c] = output[c].fillna(0)
        for c in ("W", "L", "T", "GP"):
            output[c] = output[c].astype(int)
        output["Diff"] = output["PF"] - output["PA"]
        output["PPG"] = (output["PF"] / output["GP"].replace(0, np.nan)).fillna(0)
        output["Win %"] = (
            (output["W"] + 0.5 * output["T"]) / output["GP"].replace(0, np.nan)
        ).fillna(0)
    output = output.sort_values(["Win %", "PF", "Team"], ascending=[False,False,True]).reset_index(drop=True)
    output.insert(0, "Rank", range(1, len(output)+1))
    return output


def power_rankings(table: pd.DataFrame, win_weight: float = 0.60) -> pd.DataFrame:
    """A transparent, custom power metric—not ESPN's official rankings."""
    out = table.copy()
    best_ppg = out["PPG"].max() if not out.empty else 0
    out["Scoring Index"] = out["PPG"] / best_ppg if best_ppg > 0 else 0.0
    out["Power"] = 100 * (win_weight * out["Win %"] + (1-win_weight) * out["Scoring Index"])
    out = out.sort_values(["Power", "PF", "Team"], ascending=[False,False,True]).reset_index(drop=True)
    out.insert(0, "Power Rank", range(1, len(out)+1))
    return out


def all_play_luck(games: pd.DataFrame, teams: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    """Expected wins from facing a random opponent in each fully complete week.

    Important: compare actual wins ONLY in the included complete weeks.
    If a week's other matchups aren't finished, exclude that week entirely.
    """
    scores = weekly_scores(regular_games(games))
    team_count = len(teams)
    complete_weeks = []
    rows = []
    for week, block in scores.groupby("Week"):
        if len(block) != team_count or block["Team ID"].nunique() != team_count:
            continue
        complete_weeks.append(int(week))
        for _, r in block.iterrows():
            others = block.loc[block["Team ID"].ne(r["Team ID"]), "Points"]
            apw, apl, apt = (int((r["Points"] > others).sum()),
                              int((r["Points"] < others).sum()),
                              int((r["Points"] == others).sum()))
            rows.append({"Team ID": r["Team ID"], "All-Play W": apw,
                         "All-Play L": apl, "All-Play T": apt,
                         "Expected Wins": (apw+0.5*apt)/len(others),
                         "Actual Wins": 1 if r["Result"] == "W" else 0.5 if r["Result"] == "T" else 0})
    columns = ["Team ID", "All-Play W", "All-Play L", "All-Play T", "Expected Wins", "Actual Wins"]
    summary = (pd.DataFrame(rows, columns=columns).groupby("Team ID", as_index=False)[columns[1:]].sum()
               if rows else pd.DataFrame(columns=columns))
    summary = teams[["Team ID", "Team"]].merge(summary, on="Team ID", how="left")
    for c in columns[1:]: summary[c] = summary[c].fillna(0)
    summary["Luck"] = summary["Actual Wins"] - summary["Expected Wins"]
    summary = summary.sort_values(["Luck","Expected Wins"], ascending=[False,False]).reset_index(drop=True)
    return summary, complete_weeks


def consistency(games: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """The standard deviation measures volatility, not whether a team is GOOD."""
    s = weekly_scores(regular_games(games))
    result = teams[["Team ID", "Team"]].copy()
    if s.empty:
        for c in ["GP", "Average", "Std Dev", "Median", "Low", "High", "120+ Weeks", "150+ Weeks", "CV %", "Recent 3", "Trend"]:
            result[c] = 0.0
        return result
    stats = s.groupby("Team ID", as_index=False).agg(
        GP=("Points","count"), Average=("Points","mean"),
        **{"Std Dev": ("Points","std"), "Median": ("Points","median"),
           "Low": ("Points","min"), "High": ("Points","max"),
           "120+ Weeks": ("Points",lambda v: int((v>=120).sum())),
           "150+ Weeks": ("Points",lambda v: int((v>=150).sum()))}
    )
    # Recent form = average of up to the last 3 COMPLETED games minus season average.
    last3 = (s.sort_values("Week").groupby("Team ID").tail(3)
             .groupby("Team ID")["Points"].mean().rename("Recent 3").reset_index())
    result = result.merge(stats, on="Team ID", how="left").merge(last3, on="Team ID", how="left")
    for c in result.columns:
        if c not in ("Team",): result[c] = result[c].fillna(0)
    result["CV %"] = (100*result["Std Dev"] / result["Average"].replace(0,np.nan)).fillna(0)
    result["Trend"] = result["Recent 3"]-result["Average"]
    return result.sort_values(["Average","Team"], ascending=[False,True]).reset_index(drop=True)


def head_to_head(games: pd.DataFrame, team_a: int, team_b: int):
    """Every matchup between two selected teams in ONE season."""
    selected = games.loc[
        (games["Home ID"].eq(team_a)&games["Away ID"].eq(team_b)) |
        (games["Home ID"].eq(team_b)&games["Away ID"].eq(team_a))
    ].copy().sort_values(["Week", "Game ID"])
    if selected.empty:
        return selected
    selected["A Points"] = np.where(selected["Home ID"].eq(team_a),selected["Home Score"],selected["Away Score"])
    selected["B Points"] = np.where(selected["Home ID"].eq(team_b),selected["Home Score"],selected["Away Score"])
    selected["Winner"] = np.where(selected["A Points"]>selected["B Points"],"A",
                           np.where(selected["A Points"]<selected["B Points"],"B","Tie"))
    return selected


def records(games: pd.DataFrame) -> list[tuple[str, str, str]]:
    """League-wide records from all AVAILABLE completed games only."""
    if games.empty: return []
    scored = weekly_scores(games)
    high = scored.loc[scored["Points"].idxmax()]
    blowout = games.loc[games["Margin"].idxmax()]
    close = games.loc[games["Margin"].idxmin()]
    losing = scored.loc[scored["Result"].eq("L")]
    winning = scored.loc[scored["Result"].eq("W")]
    out = [
        ("Highest weekly score", f"{high['Points']:.2f} pts", f"{high['Team']} · {int(high['Season'])} W{int(high['Week'])}"),
        ("Biggest blowout", f"{blowout['Margin']:.2f} pts", f"{blowout['Home Team']} vs {blowout['Away Team']} · {int(blowout['Season'])} W{int(blowout['Week'])}"),
        ("Closest game", f"{close['Margin']:.2f} pts", f"{close['Home Team']} vs {close['Away Team']} · {int(close['Season'])} W{int(close['Week'])}"),
    ]
    if not losing.empty:
        r=losing.loc[losing["Points"].idxmax()]
        out.append(("Highest-scoring loss", f"{r['Points']:.2f} pts", f"{r['Team']} · {int(r['Season'])} W{int(r['Week'])}"))
    if not winning.empty:
        r=winning.loc[winning["Points"].idxmin()]
        out.append(("Lowest-scoring win", f"{r['Points']:.2f} pts", f"{r['Team']} · {int(r['Season'])} W{int(r['Week'])}"))
    return out


def historical_managers(games: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Group by ESPN owner ID rather than team NAME (names change!)."""
    parts=[]
    for year in sorted(teams["Season"].unique()):
        t = teams.loc[teams["Season"].eq(year)]
        g = games.loc[games["Season"].eq(year)]
        s = standings(g,t)
        s["Season"] = year
        parts.append(s)
    if not parts: return pd.DataFrame()
    history = pd.concat(parts, ignore_index=True)
    by_owner = history.groupby("Owner ID", as_index=False).agg(
        Seasons=("Season","nunique"), W=("W","sum"), L=("L","sum"),
        T=("T","sum"), GP=("GP","sum"), PF=("PF","sum"), PA=("PA","sum")
    )
    # Prefer most recent season's displayed manager name.
    latest = (history.sort_values("Season").drop_duplicates("Owner ID", keep="last")
              [["Owner ID", "Manager"]])
    by_owner = by_owner.merge(latest,on="Owner ID",how="left")
    by_owner["Win %"] = ((by_owner["W"]+.5*by_owner["T"])/by_owner["GP"].replace(0,np.nan)).fillna(0)
    by_owner["PPG"] = (by_owner["PF"]/by_owner["GP"].replace(0,np.nan)).fillna(0)
    return by_owner.sort_values(["W","PF"],ascending=False).reset_index(drop=True)

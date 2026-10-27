# Virginia Highlands Fantasy — Analytics Lab

A complete, local, interactive Streamlit fantasy football analytics website. **No fake scores.** It reads your own ESPN JSON exports and recalculates charts and tables.

## Set up in VS Code (Windows)

1. Download and unzip the project. Open the extracted `VirginiaHighlandsAnalytics` folder in VS Code (**File → Open Folder**).
2. In that folder, create a `data` folder if it isn't already present (it is included in this template). Copy your ESPN file, e.g. `17816201.json`, into `data/`. You can also leave it in the project root or upload it through the left sidebar after launch. Do **not** put it in `.venv` or `fantasy`.
3. Open **Terminal → New Terminal**. If you have your existing Python virtual environment in a *different* folder, make a new one here:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   You can keep using your existing project instead: copy `app.py`, `fantasy/`, `.streamlit/`, and `requirements.txt` into your existing `FantasyFootballAnalytics` directory, keeping your working `.venv` and JSON. You do NOT need to reinstall if pandas, plotly, numpy and streamlit are already present.
4. Start the website:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

5. Open the localhost URL shown by Streamlit, usually `http://localhost:8501`.

## Folder map

```text
VirginiaHighlandsAnalytics/
├─ app.py                 Main app: sidebar, navigation, pages, interactive inputs
├─ fantasy/
│  ├─ __init__.py         Marks `fantasy` as a Python package
│  ├─ data.py             Read JSON; map ESPN team IDs; exclude undecided games
│  ├─ metrics.py          Stats: standings, all-play, luck, consistency, etc.
│  ├─ charts.py           Graphs with Plotly; edit colors here
│  └─ styles.py           Website styling, fonts, layout banner
├─ .streamlit/
│  └─ config.toml         Theme colors
├─ data/
│  └─ YOUR_ESPN_FILE.json  Your ESPN export goes here (not included)
├─ requirements.txt       Dependencies
└─ README.md              These instructions
```

## Pages

| Page | What's interactive? |
| --- | --- |
| Command Center | League KPIs, cumulative scoring race, top scoring team |
| Scoring Lab | Week slider, stacked scores, cumulative race, heatmap, box plots |
| Standings & Power | Real W/L/T and 0–100% power ranking weight slider |
| Luck & Skill | All-play win equivalents, adjusted wins, 4-quadrant volatility chart, recent form |
| Rivalry Arena | Pick two teams, see matchups, head-to-head win matrix |
| Record Book | Close wins, biggest blowouts, record scores, season filter, CSV download |
| Manager Lab | Choose two teams, scoring trends and side-by-side stats |
| League History | Combines uploaded seasons; manager wins, points, career stats |

## Key rules / what the app does NOT do

- **Offline export, not a live ESPN API connection.** You must replace/add your JSON when ESPN publishes finalized results, or drop the new file into the sidebar. It doesn't scrape ESPN or auto-sync.
- **Future games excluded.** Only matchups where ESPN declares `winner` HOME, AWAY or TIE are used. Undecided / live matchups do not count, even if they have partial scores.
- **Regular season separated from playoffs.** Standings, power rankings, luck, and season scoring are regular-season only. Record Book has an explicit playoffs toggle.
- **All-play comparisons use full weeks only.** For a week with 10 league teams, all 10 must have a finalized game. Expected wins divide by 9 other teams that week. Luck uses actual wins from the same included weeks, so partial weeks can't bias the comparison.
- **Power ratings aren't an ESPN or predictive model.** They combine current win percentage and points per game relative to the highest-scoring team. Slider weights are your choice.
- **Standings tiebreakers are simplified** to win percentage then points scored. ESPN playoff seeding may differ.
- **History includes only exports you loaded.** Team names may change; historical manager stats use ESPN owner IDs. Championships aren't calculated until verified full playoff records are available.
- **User data remains on your computer** when files are placed locally and site runs on localhost. Streamlit's sidebar upload lets the browser send file contents to this local Streamlit app process. Don't publish your data folder publicly without checking owner info.

## Reverse engineering: suggested reading order

1. `fantasy/data.py` → `parse_espn()` — a `for` loop turning one ESPN matchup into a row.
2. `fantasy/metrics.py` → `weekly_scores()` — one matchup becomes *two* team scores.
3. `fantasy/metrics.py` → `standings()` — use pandas `groupby` to count W/L/T and sum PF/PA.
4. `fantasy/metrics.py` → `all_play_luck()` — compare every team's weekly score against other teams, not just its opponent.
5. `fantasy/charts.py` → `stacked_scores()` — Plotly draws each week's colored bar segment.
6. `app.py` → `page == "..."` — Streamlit builds the pages and slider controls.
7. Change `PALETTE` in `fantasy/charts.py`, refresh site, and observe the difference.

## Need to troubleshoot?

- **File not found**: Be sure VS Code terminal is in the project folder (`dir` should show `app.py`).
- **Module not found**: `pip install -r requirements.txt` in the active Python environment.
- **No completed games**: Data might be a draft-only export, or the ESPN matchup result flag is `UNDECIDED`.
- **Old season JSON won't load**: Confirm it includes `teams`, `schedule`, and `seasonId`. ESPN exports can differ by season and views; some may need parsing changes.
- **App won't show updates**: Replace local JSON and refresh the Streamlit browser page; local file changes alone might not trigger Streamlit's auto-refresh.

Have fun experimenting. Every page is deliberately commented and split apart for learning.

## New historical pages — v2

The sidebar now includes **All-Time Rivalries**, **Elo Dynasty Tracker**, and **Championship Hall**.

- `fantasy/history.py` holds the numerical calculations. Read it first if you are learning loops, dictionaries and pandas grouping.
- `fantasy/charts.py` contains `elo_timeline` and `championship_bars`, reusing the existing dark Plotly theme.
- `app.py` contains the three additional interactive pages, selectors, tables and CSV exports.
- `fantasy/data.py` preserves the verified Henry Hanlon identity correction and the ESPN playoff-tier field.

Championship inference is intentionally conservative. The Hall of Fame only names a winner if a *unique completed final* in ESPN's `WINNERS_BRACKET` can be identified beyond the regular season. Other years are flagged for review. This avoids treating consolation wins or partial playoff information as championships. Some ESPN exports represent multiweek finals differently and may require a manual verification step.

Elo starts everyone at **1500**, adjusts for opponent strength after each finalized matchup, and regresses ratings toward 1500 each new season. The sliders let you experiment; this is not an official fantasy ranking. Replace/add JSONs in `data/` and restart or refresh Streamlit to recalculate.

### Upgrade existing project

Back up your existing `app.py` and `fantasy/` folder. Extract this bundle and copy **`app.py` plus the complete `fantasy/` folder** into the same project. Keep your existing `.venv` and `data/*.json`. Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## V3 — Visual polish upgrade (October 2026)

This version upgrades the existing Streamlit website's presentation. **All v2 analytic pages remain available**, including your corrected Henry Hanlon identity merge.

### What changed?

- **Command Center:** redesigned hero and KPI cards; a Week selector; three fact-based weekly headline cards; a completed-game scoreboard with winner styling; scoring-race + standings layout
- **Scoring Lab:** a new **Animated race** tab alongside the original charts. Plotly's play/pause and week slider animate cumulative fantasy points without adding fake results
- **Manager Lab:** a larger selectable team profile card with season record, rank, PF, PPG and point differential
- **Elo Dynasty Tracker / Championship Hall:** compact leader and title cards, using existing verified calculations
- **All pages:** restyled navigation, chart containers, background, fonts, headings, metrics, tables and buttons

### Safe upgrade from V2

1. **Back up** your working project folder, especially `app.py` and `fantasy/`.
2. Unzip this bundle and copy `app.py`, `fantasy/`, and `.streamlit/` into your current project, replacing those folders/files.
3. **Keep** your current `data/` folder (with your 2019–2026 ESPN JSON files), `.venv/`, and any personally edited files.
4. Run in VS Code:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

5. Test **Command Center**, **Scoring Lab → Animated race**, and **Manager Lab**. Refresh the browser if CSS is cached.

### Best reverse-engineering path

1. Open `fantasy/styles.py` and change a CSS color variable, e.g. `--accent`.
2. Open `fantasy/visuals.py` and study `feature_card`, `matchup_card`, `profile_banner` (these render HTML; `escape()` sanitizes names).
3. Open `app.py`, search for `V3 REDESIGN`, and see how those components are wired to real pandas data.
4. Open `fantasy/charts.py`, find `animated_scoring_race()` and study `pivot_table`, `cumsum`, `go.Frame`, play/pause controls.

**Privacy:** This ZIP does not contain your personal ESPN JSON exports. The website still reads local snapshots, not a live ESPN account connection. Blank, future, or undecided matchups are not shown as finalized results.

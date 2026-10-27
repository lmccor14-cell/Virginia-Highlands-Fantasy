"""
VIRGINIA HIGHLANDS // FANTASY FOOTBALL ANALYTICS
================================================
Welcome! This is the website's MAIN FILE: the Streamlit controller.

REVERSE ENGINEERING MAP
    app.py              = pages, buttons, filters, and layout
    fantasy/data.py     = ESPN JSON -> clean matchup and team tables
    fantasy/metrics.py  = standings, luck, consistency, custom rankings
    fantasy/charts.py   = Plotly figures, style, and graph interactions
    fantasy/styles.py   = colors, fonts, and website appearance

To run:  python -m streamlit run app.py
To update: replace or add ESPN season JSON files in data/ (or project root).
TIP: Search for "LEARN:" comments to find explanations of Python techniques.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from fantasy.data import read_all_exports
from fantasy.metrics import (
    regular_games, weekly_scores, standings, power_rankings,
    all_play_luck, consistency, head_to_head, records, historical_managers,
)
from fantasy.charts import (
    stacked_scores, cumulative_scores, performance_heatmap, power_bars,
    luck_bars, actual_expected_scatter, consistency_quadrant,
    distribution, manager_trend, rivalry_heatmap, animated_scoring_race,
)
from fantasy.history import (manager_names, rivalry_history, rivalry_matrix,
                             elo_history, championship_history)
from fantasy.charts import elo_timeline, championship_bars
from fantasy.styles import apply_styles, hero
from fantasy.visuals import feature_card, insight_card, matchup_card, profile_banner, eyebrow, small_heading


# ----------- 0. WEBSITE CONFIGURATION -----------
# Streamlit re-runs this file whenever a user changes a widget.
st.set_page_config(page_title="VH • Fantasy Analytics",page_icon="🏈",layout="wide",
                   initial_sidebar_state="expanded")
apply_styles()
ROOT = Path(__file__).resolve().parent


def show_table(table, columns=None, digits=2):
    """One consistent way to display/export any pandas DataFrame."""
    view=table[columns].copy() if columns else table.copy()
    st.dataframe(view.round(digits),hide_index=True,use_container_width=True)
    return view


def save_csv_button(df, filename, key):
    # LEARN: .to_csv converts a DataFrame back into portable, editable data.
    st.download_button("⬇ Export CSV",data=df.to_csv(index=False).encode("utf-8"),
                       file_name=filename,mime="text/csv",key=key)


def chart(fig, key):
    st.plotly_chart(fig,use_container_width=True,key=key)


# ----------- 1. SIDEBAR & DATA LOAD -----------
with st.sidebar:
    st.markdown('''<div class="brand-lockup"><div class="brand-top">🏈 VIRGINIA HIGHLANDS</div><div class="brand-sub">FANTASY INTELLIGENCE / V3</div></div>''', unsafe_allow_html=True)
    st.divider()
    page=st.radio("Navigate",[
        "🏠 Command Center", "📈 Scoring Lab", "🏆 Standings & Power",
        "🎲 Luck & Skill", "⚔️ Rivalry Arena", "📚 Record Book",
        "🧬 Manager Lab", "🗓️ League History",
        "🔥 All-Time Rivalries", "📉 Elo Dynasty Tracker", "👑 Championship Hall",
    ])
    st.divider()
    uploaded=st.file_uploader("Add season JSON files",type=["json"],
                              accept_multiple_files=True,
                              help="Files uploaded here are used until you refresh. Save files in data/ for persistent use.")

# LEARN: A function turns a raw JSON object into clean DataFrames.
all_games, all_teams, metadata, errors = read_all_exports(ROOT,uploaded)

with st.sidebar:
    for err in errors:
        st.warning(err)
    if metadata:
        years=sorted(metadata.keys(),reverse=True)
        year=st.selectbox("Selected season",years,index=0)
        st.caption(f"{len(metadata)} season(s) loaded · {len(all_games)} completed matchups")
    else:
        year=None

if year is None:
    hero("WELCOME TO THE LEAGUE LAB", "Your league, decoded.",
         "Drop your ESPN league JSON into the data folder or upload it using the sidebar.")
    st.info("No compatible ESPN data found. Your JSON needs `teams` and `schedule` fields, "
            "like the ESPN download you used in your original project.")
    st.code("FantasyFootballAnalytics/\n"
            "  app.py\n  fantasy/\n  data/\n    17816201.json   <-- put your export here\n"
            "  requirements.txt",language="text")
    st.stop()

# Filter to chosen season; don't mix team IDs across years.
games=all_games.loc[all_games["Season"].eq(year)].copy()
teams=all_teams.loc[all_teams["Season"].eq(year)].copy()
reg=regular_games(games)
scores=weekly_scores(reg)
base_standings=standings(games,teams)
luck,complete_weeks=all_play_luck(games,teams)
cons=consistency(games,teams)
season_name=metadata[year]["name"]
completed_weeks=sorted(reg["Week"].unique().tolist())

# ----------- 2. COMMAND CENTER — V3 REDESIGN -----------
# LEARN: We reuse the EXACT SAME data, but compose it into attractive widgets.
# Visualization code lives in fantasy/visuals.py, not in our data engine.
if page=="🏠 Command Center":
    hero("WELCOME TO THE LEAGUE HQ", season_name.upper(),
         f"{year} season  /  {len(teams)} teams  /  {len(metadata)} loaded seasons of league history")

    leader=base_standings.iloc[0] if not base_standings.empty else None
    scorer=(base_standings.sort_values("PF",ascending=False).iloc[0]
            if not base_standings.empty else None)
    high_score=scores.loc[scores["Points"].idxmax()] if not scores.empty else None

    # LEARN: st.columns creates a responsive row; these are custom visual components.
    eyebrow("01  /  THE SEASON AT A GLANCE")
    a,b,c,d=st.columns(4)
    with a: feature_card("Top of standings",str(leader["Team"]) if leader is not None else "—",
                         f"{int(leader['W'])}-{int(leader['L'])} record" if leader is not None else "No games recorded", "teal", "★")
    with b: feature_card("Points leader",str(scorer["Team"]) if scorer is not None else "—",
                         f"{float(scorer['PF']):,.1f} season points" if scorer is not None else "No scores", "gold", "↗")
    with c: feature_card("Finalized matchups",f"{len(reg):,}",
                         "Regular season only · ESPN final results", "blue", "✓")
    with d: feature_card("Weeks in the books",str(len(completed_weeks)),
                         "Contains at least one finalized result", "violet", "▥")

    eyebrow("02  /  THE WEEKLY BRIEFING")
    if reg.empty:
        st.info("No finalized matchups yet. The scoreboard will appear after ESPN confirms results.")
    else:
        # LEARN: Selectbox makes any completed week available, not just the newest one.
        weeks=sorted(reg["Week"].unique().tolist(),reverse=True)
        current_week=st.selectbox("Replay a completed week",weeks,index=0,
                                  format_func=lambda x: f"Week {int(x)}",key="hq_week")
        this_week=reg.loc[reg["Week"].eq(current_week)].sort_values("Game ID").copy()
        this_scores=weekly_scores(this_week)
        weekly_high=(this_scores.loc[this_scores["Points"].idxmax()]
                     if not this_scores.empty else None)
        close=this_week.loc[this_week["Margin"].idxmin()] if not this_week.empty else None
        far=this_week.loc[this_week["Margin"].idxmax()] if not this_week.empty else None
        cols=st.columns(3)
        with cols[0]:
            if weekly_high is not None:
                insight_card("WEEKLY MVP",str(weekly_high["Team"]),
                             f"{weekly_high['Points']:.2f} pts  ·  Week {int(current_week)}","gold")
        with cols[1]:
            if close is not None:
                insight_card("CLOSEST FINISH",f"{close['Margin']:.2f} points apart",
                             f"{close['Away Team']} vs {close['Home Team']}","teal")
        with cols[2]:
            if far is not None:
                insight_card("BIGGEST BLOWOUT",f"{far['Margin']:.2f} points",
                             f"{far['Away Team']} vs {far['Home Team']}","rose")

        small_heading("The scoreboard",f"All {len(this_week)} finalized ESPN matchups from Week {int(current_week)}.")
        games_list=this_week.to_dict("records")
        for i in range(0,len(games_list),2):
            left,right=st.columns(2)
            with left: matchup_card(games_list[i])
            if i+1<len(games_list):
                with right: matchup_card(games_list[i+1])

    eyebrow("03  /  THE BIG PICTURE")
    left,right=st.columns([1.55,1],gap="large")
    with left:
        small_heading("The scoring race","Follow every team's running point total across the season.")
        if not scores.empty:
            chart(cumulative_scores(scores),"dash_race")
        else:
            st.info("The scoring race appears when final results are available.")
    with right:
        small_heading("Current pecking order","The standings, sorted by record and points scored.")
        show_table(base_standings,["Rank","Team","W","L","PF","Diff"])
        if high_score is not None:
            insight_card("SEASON RECORD  /  HIGHEST WEEK",
                         f"{high_score['Points']:.2f} POINTS",
                         f"{high_score['Team']} · Week {int(high_score['Week'])}","gold")

    st.caption("Numbers are based on your loaded JSON snapshots. This is not a live ESPN connection; add a fresh export to update the site.")

# ----------- 3. SCORING LAB -----------
elif page=="📈 Scoring Lab":
    hero("SCORING INTELLIGENCE", "Points tell the story.",
         "Stacked point totals, moving leaderboard, scoring heatmaps and weekly distributions.")
    if scores.empty:
        st.info("No finalized regular-season scores in this export.")
    else:
        latest=int(scores["Week"].max())
        earliest=int(scores["Week"].min())
        if earliest < latest:
            cutoff=st.slider("Show results through week",earliest,latest,latest)
        else:
            cutoff=latest
            st.caption(f"Showing Week {cutoff}; a week slider appears after multiple weeks are complete.")
        # LEARN: Filtering with a boolean mask only changes the displayed charts.
        visible=scores.loc[scores["Week"].le(cutoff)].copy()
        tabs=st.tabs(["Stacked leaderboard","Animated race","Cumulative race","Weekly heatmap","Scoring distributions"])
        with tabs[0]:
            chart(stacked_scores(visible),"stacked_scores")
            st.caption("Each color represents one week. Longer bars mean more points so far.")
        with tabs[1]:
            st.caption("▶ Play or drag the Week slider to see the ranking change as fantasy points accumulate.")
            chart(animated_scoring_race(visible),"animated_scoring_race")
        with tabs[2]:
            chart(cumulative_scores(visible),"running_scores")
            st.caption("Hover over the lines to see when managers overtook one another.")
        with tabs[3]:
            chart(performance_heatmap(visible),"score_heatmap")
        with tabs[4]:
            chart(distribution(visible),"score_distributions")
            st.caption("Dots are individual weeks; boxes summarize each team's scoring spread.")
        save_csv_button(visible.sort_values(["Week","Points"],ascending=[True,False]),
                        f"{year}_weekly_scores.csv","export_scores")

# ----------- 4. STANDINGS & POWER -----------
elif page=="🏆 Standings & Power":
    hero("THE RANKINGS ROOM", "Standings ≠ strength.",
         "League records are actual results. Power rankings are a transparent custom formula.")
    st.subheader("Regular-season standings")
    show_table(base_standings,["Rank","Team","Manager","W","L","T","Win %","PF","PA","Diff","PPG"])
    st.caption("Win % is a fraction from 0 to 1. Standings use win percentage then points for; ESPN's official seeding tiebreakers can differ.")
    st.divider()
    c1,c2=st.columns([1,2])
    with c1:
        st.subheader("Your weighting formula")
        w=st.slider("Weight given to win percentage",0,100,60,5)/100
        st.metric("Record weight",f"{w:.0%}")
        st.metric("Scoring weight",f"{1-w:.0%}")
        st.latex(r"Power=100\left(w\cdot WinPct+(1-w)\cdot\frac{PPG}{MaxPPG}\right)")
        st.caption("Move the slider to decide whether winning or scoring matters more.")
    power=power_rankings(base_standings,w)
    with c2:
        chart(power_bars(power),"power_chart")
    show_table(power,["Power Rank","Team","W","L","PPG","Power","Scoring Index"])
    save_csv_button(power,f"{year}_power_rankings.csv","export_power")

# ----------- 5. LUCK & SKILL -----------
elif page=="🎲 Luck & Skill":
    hero("THE ADVANCED LAB", "How much was luck?",
         "All-play comparisons, schedule luck, scoring consistency, and teams finding their form.")
    if not complete_weeks:
        st.warning("No fully completed weeks found, so all-play/luck values are not available yet.")
    else:
        st.info(f"All-play calculations use complete weeks only: {', '.join(map(str,complete_weeks))}. "
                "We compare actual wins from those same weeks to make luck fair.")
        t1,t2,t3=st.tabs(["Schedule luck","Scoring consistency","Weekly form"])
        with t1:
            st.write("Expected wins = (teams beaten + 0.5 × ties) / (other teams that week). "
                     "Luck = actual wins − expected wins, across completed weeks.")
            chart(luck_bars(luck),"luck_bars")
            chart(actual_expected_scatter(luck),"luck_scatter")
            show_table(luck,["Team","All-Play W","All-Play L","All-Play T","Expected Wins","Actual Wins","Luck"])
            save_csv_button(luck,f"{year}_luck.csv","export_luck")
        with t2:
            chart(consistency_quadrant(cons,base_standings,scores),"consistency_quadrant")
            st.caption("Right = higher average; bottom = lower variability. The vertical line is league average points, "
                       "the horizontal line is the median team's standard deviation. Colors indicate actual win percentage.")
            show_table(cons,["Team","GP","Average","Std Dev","CV %","Median","Low","High","120+ Weeks","150+ Weeks"])
        with t3:
            chart(performance_heatmap(scores),"form_heatmap")
            form=cons.sort_values("Trend",ascending=False)
            st.caption("Trend = average of last three completed games minus full-season average. Positive values mean hotter recent scoring.")
            show_table(form,["Team","GP","Average","Recent 3","Trend","Std Dev"])

# ----------- 6. RIVALRY ARENA -----------
elif page=="⚔️ Rivalry Arena":
    hero("THE RIVALRY ARENA", "Settle the argument.",
         "Pick two teams to inspect their actual head-to-head games, wins, and scoring margins.")
    if len(teams)<2:
        st.info("Add two or more teams to compare.")
    else:
        mapping={f"{row['Team']} (ID {row['Team ID']})":int(row["Team ID"])
                 for _,row in teams.sort_values("Team").iterrows()}
        names=list(mapping)
        a_col,b_col=st.columns(2)
        with a_col: team_a=st.selectbox("Team A",names,index=0)
        with b_col: team_b=st.selectbox("Team B",names,index=min(1,len(names)-1))
        if team_a==team_b:
            st.warning("Choose two different teams.")
        else:
            matchups=head_to_head(games,mapping[team_a],mapping[team_b])
            wa=int(matchups["Winner"].eq("A").sum()) if not matchups.empty else 0
            wb=int(matchups["Winner"].eq("B").sum()) if not matchups.empty else 0
            c1,c2,c3=st.columns(3)
            c1.metric("Team A wins",wa)
            c2.metric("Team B wins",wb)
            c3.metric("Completed meetings",len(matchups))
            if matchups.empty:
                st.info("These teams haven't met in the available completed matchups this season.")
            else:
                display=matchups[["Season","Week","Phase","A Points","B Points","Margin","Winner"]]
                show_table(display)
                save_csv_button(display,f"{year}_head_to_head.csv","export_h2h")
        st.divider()
        st.subheader("League-wide head-to-head matrix")
        labels=teams.set_index("Team ID")["Team"].to_dict()
        # Rows = winning team; columns = losing team, plus 0 for a tie.
        cells=[]
        for ida,na in labels.items():
            row={"Team":na}
            for idb,nb in labels.items():
                games_ab=head_to_head(reg,ida,idb) if ida!=idb else pd.DataFrame()
                row[nb]=int(games_ab["Winner"].eq("A").sum()) if not games_ab.empty else 0
            cells.append(row)
        frame=pd.DataFrame(cells).set_index("Team")
        chart(rivalry_heatmap(frame),"rivalry_heatmap")
        with st.expander("View rivalry matrix as a table"):
            st.dataframe(frame,use_container_width=True)
        st.caption("Cell = row team's completed regular-season wins against column team, in the selected season.")

# ----------- 7. RECORD BOOK -----------
elif page=="📚 Record Book":
    hero("THE RECORD BOOK", "The receipts are forever.",
         "Extremes and historical claims computed only from the JSON files you've loaded.")
    include_playoffs=st.toggle("Include playoff matchups",value=False)
    source=all_games if include_playoffs else regular_games(all_games)
    entries=records(source)
    if not entries:
        st.info("No completed matchups available.")
    else:
        for start in range(0,len(entries),3):
            cols=st.columns(3)
            for c,(label,value,context) in zip(cols,entries[start:start+3]):
                with c:
                    st.metric(label,value)
                    st.caption(context)
        st.divider()
        st.subheader("Matchup archive")
        chosen=st.multiselect("Filter seasons",sorted(source["Season"].unique().tolist(),reverse=True),
                              default=sorted(source["Season"].unique().tolist(),reverse=True))
        filtered=source.loc[source["Season"].isin(chosen)].sort_values(["Season","Week"],ascending=[False,False])
        display=filtered[["Season","Week","Phase","Away Team","Away Score","Home Score","Home Team","Margin"]]
        show_table(display)
        save_csv_button(display,"fantasy_all_completed_matchups.csv","export_archive")

# ----------- 8. MANAGER LAB -----------
elif page=="🧬 Manager Lab":
    hero("MANAGER INTELLIGENCE", "Know your game.",
         "Your team profile: record, scoring trends, and a direct comparison against a rival.")
    team_names=sorted(teams["Team"].tolist())
    chosen_name=st.selectbox("Inspect a team",team_names)
    selected=base_standings.loc[base_standings["Team"].eq(chosen_name)].iloc[0]
    profile_banner(selected)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Wins",int(selected["W"]))
    c2.metric("Losses",int(selected["L"]))
    c3.metric("Points scored",f"{selected['PF']:.2f}")
    c4.metric("Points / game",f"{selected['PPG']:.2f}")
    if not scores.empty:
        chart(manager_trend(scores,chosen_name),"manager_trend")
    other_teams=[x for x in team_names if x!=chosen_name]
    if other_teams:
        opponent_name=st.selectbox("Compare against",other_teams)
        subset=base_standings.loc[base_standings["Team"].isin([chosen_name,opponent_name])]
        show_table(subset,["Team","W","L","PF","PA","Diff","PPG","Win %"])
        selected_score=scores.loc[scores["Team"].isin([chosen_name,opponent_name])]
        chart(cumulative_scores(selected_score),"manager_vs_manager")
    st.caption("Profile is by TEAM NAME in the chosen season. All-time tracking uses owner IDs in League History.")

# ----------- 9. LEAGUE HISTORY -----------
elif page=="🗓️ League History":
    hero("THE ARCHIVE", "Build a dynasty.",
         "Add 2019–2025 ESPN JSON files to unlock cross-season manager statistics.")
    years=sorted(metadata.keys())
    st.write("Seasons loaded:",", ".join(map(str,years)))
    if len(years)==1:
        st.info("Only one season loaded. You can still use this page; add older ESPN season JSON files for true all-time comparisons.")
    historical=historical_managers(all_games,all_teams)
    if not historical.empty:
        st.subheader("All-time manager leaderboard")
        show_table(historical,["Manager","Seasons","W","L","T","GP","Win %","PF","PA","PPG"])
        save_csv_button(historical.drop(columns="Owner ID"),"all_time_managers.csv","export_managers")
        st.caption("Manager identity is linked using ESPN primaryOwner ID. This avoids mistaking renamed teams for new managers; "
                   "co-owned/transferred teams may require a manual correction. Only loaded seasons count.")
    st.subheader("History availability")
    st.markdown("""**Championships and playoff finishes are intentionally not guessed.**
    Once full completed-season playoff data is loaded, we can build a dedicated championship timeline.
    The current all-time table is based on completed regular-season results only.""")

# ----------- 10. ALL-TIME RIVALRIES -----------
elif page=="🔥 All-Time Rivalries":
    hero("THE RIVALRY ARCHIVE", "Eight seasons. Endless receipts.",
         "Compare managers across all loaded seasons, regardless of team renames.")
    include_playoffs=st.toggle("Include playoff matchups",value=False,key="all_rival_postseason")
    duels=rivalry_history(all_games,all_teams,include_playoffs)
    lookup={v:k for k,v in manager_names(all_teams).items()}
    labels=sorted(lookup)
    if len(labels)<2:
        st.info("Load at least two managers for comparisons.")
    else:
        c1,c2=st.columns(2)
        first=c1.selectbox("First manager",labels,index=0,key="hist_rival_first")
        second=c2.selectbox("Second manager",labels,index=min(1,len(labels)-1),key="hist_rival_second")
        if first==second:
            st.warning("Choose two different managers.")
        else:
            h2h=duels[(duels['Owner ID']==lookup[first]) & (duels['Opponent ID']==lookup[second])]
            w=int((h2h['Result']=='W').sum())
            l=int((h2h['Result']=='L').sum())
            t=int((h2h['Result']=='T').sum())
            a,b,c,d=st.columns(4)
            a.metric(f"{first} wins",w)
            b.metric(f"{second} wins",l)
            c.metric("Ties",t)
            d.metric("Point differential",f"{h2h['Margin'].sum():+.2f}")
            if h2h.empty:
                st.info("No finished head-to-head games in your loaded exports.")
            else:
                show_table(h2h.sort_values(['Season','Week'],ascending=[False,False]),
                           ['Season','Week','Phase','PF','PA','Margin','Result'])
                save_csv_button(h2h,f"rivalry_{first}_{second}.csv","historical_h2h_csv")
        st.subheader("All-time rivalry matrix")
        matrix=rivalry_matrix(duels,all_teams)
        chart(rivalry_heatmap(matrix.fillna(0)),"historical_rival_matrix")
        st.caption("Each cell counts times the row manager defeated the column manager. Diagonal is omitted.")
        with st.expander("View raw matrix"):
            st.dataframe(matrix,use_container_width=True)

# ----------- 11. ELO DYNASTY TRACKER -----------
elif page=="📉 Elo Dynasty Tracker":
    hero("THE DYNASTY TRACKER", "Watch legends rise and fall.",
         "An adjustable, game-by-game rating system across your league's loaded history.")
    a,b,c=st.columns(3)
    k=a.slider("Elo movement (K)",8,48,24,2,help="Higher K reacts faster to single games.")
    carry=b.slider("Year-to-year carryover",0.0,1.0,.75,.05,
        help="1 keeps all prior rating; 0 resets everyone to 1500 each season.")
    include_post=c.toggle("Include playoff games",value=True,key="elo_postseason")
    elo=elo_history(all_games,all_teams,k,carry,include_post)
    if elo.empty:
        st.info("No completed games available for Elo ratings.")
    else:
        available=sorted(elo['Manager'].unique())
        selected=st.multiselect("Managers to show",available,default=available,key="elo_selected_managers")
        chart(elo_timeline(elo,selected),"elo_line")
        latest=elo.sort_values(['Season','Week','Game ID'],kind='stable').drop_duplicates('Owner ID',keep='last')
        latest=latest.sort_values('Elo',ascending=False)
        eyebrow("CURRENT DYNASTY LEADERS")
        for col, (_, item) in zip(st.columns(3), latest.head(3).iterrows()):
            with col: feature_card("Historical Elo",str(item['Manager']),
                                   f"{float(item['Elo']):,.1f} rating", "violet", "✦")
        st.subheader("Latest Elo leaderboard")
        show_table(latest,['Manager','Elo','Season','Week','Change'])
        save_csv_button(elo,"historical_elo.csv","elo_csv")
        st.caption("Custom model, not ESPN's official power ranking. Starts at 1500; "
                   "no home-field advantage; ratings regress toward 1500 at season boundaries.")

# ----------- 12. CHAMPIONSHIP HALL -----------
elif page=="👑 Championship Hall":
    hero("THE CHAMPIONSHIP HALL", "Rings over everything.",
         "Championships and runners-up verified from final winners-bracket results in your ESPN exports.")
    championships=championship_history(all_games,all_teams,metadata)
    verified=championships.dropna(subset=['Champion'])
    c1,c2,c3=st.columns(3)
    c1.metric("Seasons loaded",len(championships))
    c2.metric("Finals identified",len(verified))
    c3.metric("Still unverified",len(championships)-len(verified))
    if not verified.empty:
        eyebrow("THE TROPHY CASE")
        podium=verified.groupby("Champion").size().sort_values(ascending=False).head(3)
        for col,(person,count) in zip(st.columns(3),podium.items()):
            with col:
                feature_card("Verified championships",str(person),
                             f"{int(count)} championship{'s' if count!=1 else ''} identified", "gold", "♛")
    chart(championship_bars(championships),"championship_bars")
    st.subheader("Season-by-season championship ledger")
    show_table(championships,['Season','Champion','Runner-up','Final Week','Status'])
    if len(verified):
        titles=verified.groupby('Champion').size().sort_values(ascending=False).reset_index(name='Titles')
        finals=verified.groupby('Runner-up').size().rename('Runner-up finishes')
        titles=titles.merge(finals,left_on='Champion',right_index=True,how='left').fillna(0)
        st.subheader("Title leaderboard")
        show_table(titles)
    st.info("If a season says 'Not verified', the export may lack a completed "
            "winners-bracket championship or use another ESPN playoff format. "
            "We deliberately do not award a title based on regular-season standings.")
    save_csv_button(championships,"championship_history.csv","championship_csv")

with st.sidebar:
    st.divider()
    st.caption("📁 Put additional exports in `data/` and reload. The uploader accepts several files at once.")
    st.caption("🧠 Follow the `LEARN:` comments to reverse-engineer each feature.")

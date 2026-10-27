"""STEP 3 / GRAPHICS — reusable Plotly charts.

Change the colors here to restyle every page in the app at once.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

PALETTE = ["#65D6C1", "#A795FC", "#FCBA6B", "#67B6F4", "#F87E9F", "#F5D76E",
           "#75E19E", "#CF9FFF", "#FD907B", "#8CBBD7", "#EAA6C3", "#BDE8CB",
           "#FFB6A8", "#93B4F7", "#FDE083", "#B0D4D8", "#FFCCA8"]
BG = "#0B1020"
PLOT = "#121A2A"
FONT = "#E8F0FC"
GRID = "#28334A"


def polish(fig, height=460, title=None):
    """One visual style shared by every Plotly graph."""
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=PLOT,
        font=dict(color=FONT, family="Inter, Segoe UI, Arial", size=12),
        title=dict(text=title, font=dict(size=18)), height=height,
        margin=dict(l=18,r=20,t=55 if title else 28,b=30),
        hoverlabel=dict(bgcolor="#222C43",font_color="#FFFFFF"),
        legend=dict(orientation="h",y=-0.18,x=0),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )
    return fig


def stacked_scores(scores: pd.DataFrame):
    """Colored weekly pieces whose sum is total season points."""
    if scores.empty: return polish(go.Figure())
    wide = scores.pivot_table(index="Team",columns="Week",values="Points",aggfunc="sum",fill_value=0)
    wide["Total"] = wide.sum(axis=1)
    wide = wide.sort_values("Total")
    fig = go.Figure()
    for i, week in enumerate(sorted(c for c in wide.columns if c != "Total")):
        fig.add_bar(y=wide.index,x=wide[week],orientation="h",name=f"W{week}",
                    marker_color=PALETTE[i%len(PALETTE)],
                    hovertemplate=f"Week {week}<br>%{{y}}: %{{x:.2f}} pts<extra></extra>")
    fig.update_layout(barmode="stack",xaxis_title="Total points",yaxis_title="",)
    return polish(fig, max(420, len(wide)*38+120),"Where the points came from")


def cumulative_scores(scores):
    if scores.empty: return polish(go.Figure())
    ordered = scores.sort_values("Week").copy()
    ordered["Running Total"] = ordered.groupby("Team ID")["Points"].cumsum()
    fig=px.line(ordered,x="Week",y="Running Total",color="Team",markers=True,
                color_discrete_sequence=PALETTE,hover_data={"Points":":.2f","Running Total":":.2f"})
    fig.update_layout(xaxis=dict(dtick=1,title="Week"),yaxis_title="Cumulative points")
    return polish(fig,510,"The scoring race, week by week")


def performance_heatmap(scores):
    if scores.empty: return polish(go.Figure())
    mat=scores.pivot_table(index="Team",columns="Week",values="Points",aggfunc="sum")
    fig=go.Figure(go.Heatmap(z=mat.to_numpy(),x=[f"W{x}" for x in mat.columns],y=mat.index.tolist(),
        colorscale=[[0,"#1B2A46"],[0.40,"#356A9A"],[0.75,"#48B7A8"],[1,"#F9C974"]],
        colorbar=dict(title="Points"),hovertemplate="%{y} • %{x}<br>%{z:.2f} pts<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return polish(fig,max(390, len(mat)*36+100),"Weekly scoring heatmap")


def power_bars(power):
    s=power.sort_values("Power")
    fig=go.Figure(go.Bar(x=s["Power"],y=s["Team"],orientation="h",
        marker=dict(color=s["Power"],colorscale=[[0,"#F47C89"],[0.5,"#A795FC"],[1,"#65D6C1"]],
                    cmin=0,cmax=100,showscale=False),
        text=s["Power"].round(1),textposition="inside",insidetextanchor="end",
        hovertemplate="%{y}<br>Power: %{x:.1f}<extra></extra>"))
    fig.update_layout(xaxis=dict(title="Custom power score",range=[0,105]),yaxis_title="")
    return polish(fig,max(410,len(s)*37+100),"Calculated power leaderboard")


def luck_bars(luck):
    s=luck.sort_values("Luck")
    colors=["#65D6C1" if v>=0 else "#F47C89" for v in s["Luck"]]
    fig=go.Figure(go.Bar(x=s["Luck"],y=s["Team"],orientation="h",
        marker_color=colors,text=s["Luck"].round(2),textposition="auto",
        hovertemplate="%{y}<br>Luck: %{x:+.2f} wins<extra></extra>"))
    fig.add_vline(x=0,line_color="#8494B5",line_width=1)
    fig.update_layout(xaxis_title="Actual wins minus expected wins",yaxis_title="")
    return polish(fig,max(400,len(s)*38+100),"Schedule luck index")


def actual_expected_scatter(luck):
    fig=px.scatter(luck,x="Expected Wins",y="Actual Wins",text="Team",
                   color="Luck",color_continuous_scale=["#F47C89","#66798E","#65D6C1"],
                   hover_data={"All-Play W":True,"All-Play L":True,"Luck":":+.2f"})
    limit=max(1.0,float(max(luck["Expected Wins"].max(),luck["Actual Wins"].max()))+0.5)
    fig.add_shape(type="line",x0=0,y0=0,x1=limit,y1=limit,line=dict(color="#7F91AA",dash="dash"))
    fig.update_traces(textposition="top center",marker=dict(size=13,line=dict(color="#19243B",width=1)))
    fig.update_layout(xaxis=dict(range=[0,limit],title="Expected wins"),yaxis=dict(range=[0,limit],title="Actual wins"),coloraxis_colorbar=dict(title="Luck"))
    return polish(fig,570,"Actual wins vs. expected wins")


def consistency_quadrant(consistency, standings, scores):
    """Average on x, volatility on y. Bottom-right is desirable."""
    df=consistency.merge(standings[["Team ID","Win %"]],on="Team ID",how="left")
    scoring_line=float(scores["Points"].mean()) if not scores.empty else 0
    variance_line=float(df["Std Dev"].median()) if not df.empty else 0
    fig=px.scatter(df,x="Average",y="Std Dev",text="Team",color="Win %",
        color_continuous_scale=["#F47C89","#F9C974","#65D6C1"],range_color=[0,1],
        hover_data={"GP":True,"Median":":.2f","Low":":.2f","High":":.2f","150+ Weeks":True,"CV %":":.1f"})
    fig.update_traces(textposition="top center",marker=dict(size=17,line=dict(color="#EAF4FF",width=1)))
    fig.add_vline(x=scoring_line,line_dash="dash",line_color="#9CAAC2",
                  annotation_text="League avg",annotation_position="top")
    fig.add_hline(y=variance_line,line_dash="dash",line_color="#9CAAC2",
                  annotation_text="Median volatility",annotation_position="right")
    # Shaded quadrants add context but do NOT replace raw statistical interpretation.
    fig.update_layout(xaxis_title="Average points per week →",yaxis_title="Standard deviation (lower = steadier)",
                      coloraxis_colorbar=dict(title="Win %",tickformat=".0%"))
    return polish(fig,600,"How good vs. how predictable?")


def distribution(scores):
    fig=px.box(scores,x="Points",y="Team",color="Team",orientation="h",points="all",
               color_discrete_sequence=PALETTE,hover_data=["Week"])
    fig.update_layout(showlegend=False,xaxis_title="Points per week",yaxis_title="")
    fig.update_traces(jitter=.24,pointpos=0,marker_size=6)
    return polish(fig,max(490,scores["Team"].nunique()*43+115),"Every weekly performance — distributions")


def manager_trend(scores, name):
    s=scores.loc[scores["Team"].eq(name)].sort_values("Week").copy()
    if s.empty: return polish(go.Figure())
    s["3-game average"]=s["Points"].rolling(3,min_periods=1).mean()
    fig=go.Figure()
    fig.add_trace(go.Bar(x=s["Week"],y=s["Points"],name="Weekly points",marker_color="#67B6F4"))
    fig.add_trace(go.Scatter(x=s["Week"],y=s["3-game average"],name="Trailing 3-game avg",
                             mode="lines+markers",line=dict(color="#F9C974",width=3)))
    fig.update_layout(xaxis=dict(dtick=1,title="Week"),yaxis_title="Points",barmode="overlay")
    return polish(fig,440,f"{name}: scoring form")


def rivalry_heatmap(matrix):
    """Colorized head-to-head grid; requires Plotly but NOT matplotlib."""
    fig = go.Figure(go.Heatmap(
        z=matrix.to_numpy(), x=matrix.columns.tolist(), y=matrix.index.tolist(),
        text=matrix.to_numpy(), texttemplate="%{text}",
        colorscale=[[0,"#17243B"],[0.5,"#226C80"],[1,"#65D6C1"]],
        hovertemplate="%{y} beat %{x}: %{z} time(s)<extra></extra>",
        colorbar=dict(title="Wins"),
    ))
    fig.update_layout(xaxis=dict(tickangle=-40,side="bottom"),yaxis=dict(autorange="reversed"))
    return polish(fig,600,"Who owns whom? — regular-season wins")

# HISTORICAL CHARTS — these inherit the same shared dark website theme.
def elo_timeline(elo, selected_managers=None):
    if selected_managers is not None:
        elo = elo.loc[elo['Manager'].isin(selected_managers)]
    fig=go.Figure()
    if not elo.empty:
        # Each row = rating AFTER a completed matchup; chronological x axis.
        xyears = elo['Season'] + (elo['Week']-1)/18.0
        elo = elo.assign(Timeline=xyears)
        for i,(name, block) in enumerate(elo.groupby('Manager',sort=True)):
            fig.add_trace(go.Scatter(x=block['Timeline'],y=block['Elo'],mode='lines+markers',
                name=name,line=dict(color=PALETTE[i % len(PALETTE)],width=2.7),marker=dict(size=5),
                customdata=block[['Season','Week','Opponent','Change']].to_numpy(),
                hovertemplate='<b>'+name+'</b><br>Season: %{customdata[0]} Week: %{customdata[1]}'
                      '<br>Opponent: %{customdata[2]}<br>Elo: %{y:.1f}<br>Change: %{customdata[3]:+.1f}<extra></extra>'))
    fig.add_hline(y=1500,line_dash='dash',line_color='#7E8DA9')
    fig.update_layout(xaxis_title='Season / week',yaxis_title='Elo rating',hovermode='closest')
    return polish(fig,590,'League Elo history')


def championship_bars(championships):
    known=championships.dropna(subset=['Champion'])
    if known.empty: return polish(go.Figure(),400,'Championships verified')
    tally=known.groupby('Champion').size().sort_values()
    fig=go.Figure(go.Bar(x=tally.values,y=tally.index,orientation='h',marker_color='#F9C974',
              text=tally.values,textposition='auto'))
    fig.update_layout(xaxis_title='Titles',yaxis_title='')
    return polish(fig,420,'Championship titles')


def animated_scoring_race(scores):
    """ANIMATED CHART — the all-time requested bar-chart race, week by week.

    LEARN:
      1. pivot_table makes Team × Week.
      2. cumsum(axis=1) turns weekly scores into running totals.
      3. go.Frame stores the bars for one moment in the animation.
      4. Plotly play/pause buttons advance through the stored frames.

    The animation uses only the completed scores the caller supplies.
    """
    if scores.empty:
        return polish(go.Figure(), 500, "Cumulative scoring race")
    wide = scores.pivot_table(index="Team", columns="Week", values="Points", aggfunc="sum", fill_value=0)
    running = wide.reindex(sorted(wide.columns), axis=1).cumsum(axis=1)
    weeks = list(running.columns)
    if not weeks:
        return polish(go.Figure(), 500, "Cumulative scoring race")
    team_colors = {team: PALETTE[i % len(PALETTE)] for i, team in enumerate(sorted(running.index))}
    max_total = float(running.max().max())

    def bar_for_week(week):
        ordered = running[week].sort_values(ascending=True)
        return go.Bar(
            x=ordered.values.tolist(), y=ordered.index.tolist(), orientation="h",
            marker_color=[team_colors[t] for t in ordered.index],
            text=[f"{n:,.1f}" for n in ordered.values], textposition="outside",
            hovertemplate="%{y}: %{x:,.2f} points<extra></extra>",
        )

    frames = [
        go.Frame(name=str(week), data=[bar_for_week(week)],
                 layout=go.Layout(title_text=f"Scoring race  /  Through week {week}"))
        for week in weeks
    ]
    figure = go.Figure(data=[bar_for_week(weeks[0])], frames=frames)
    figure.update_layout(
        xaxis=dict(range=[0, max(1.0, max_total * 1.18)], title="Cumulative fantasy points"),
        yaxis=dict(title="", categoryorder="total ascending"),
        showlegend=False,
        updatemenus=[dict(type="buttons", showactive=False, x=0.01, y=1.13,
                          direction="left", buttons=[
            dict(label="▶ Play", method="animate", args=[None, {
                "frame": {"duration": 800, "redraw": True},
                "transition": {"duration": 260}, "fromcurrent": True,
                "mode": "immediate"}]),
            dict(label="❚❚ Pause", method="animate", args=[[None], {
                "frame": {"duration": 0, "redraw": False},
                "transition": {"duration": 0}, "mode": "immediate"}]),
        ])],
        sliders=[dict(active=0, x=0.07, y=-0.12, len=0.86,
                      currentvalue={"prefix": "Week: ", "font": {"size": 13}},
                      steps=[dict(label=str(w), method="animate", args=[[str(w)], {
                          "frame": {"duration": 0, "redraw": True},
                          "transition": {"duration": 0}, "mode": "immediate"}]) for w in weeks])],
        margin=dict(l=20, r=30, t=95, b=72),
    )
    return polish(figure, max(500, len(running) * 45 + 150), "Scoring race  /  Play to watch the rankings change")

"""VISUAL COMPONENTS — reusable presentation, NOT statistical calculations.

LEARN:
    st.markdown(..., unsafe_allow_html=True) renders our custom styled cards.
    escape(...) prevents team names from accidentally becoming HTML.
    Small components are easier to reuse and edit than one giant app.py.
"""
from html import escape
import streamlit as st


def clean(value):
    """Keep ESPN-provided labels as plain text inside authored HTML."""
    return escape(str(value))


def eyebrow(text):
    st.markdown(f'<div class="section-label">{clean(text)}</div>', unsafe_allow_html=True)


def feature_card(label, main, detail, tone="teal", icon="◆"):
    """A statistic card with a concise label, large value and explanation."""
    st.markdown(f"""
    <div class="feature-card tone-{clean(tone)}">
      <div class="feature-top"><span>{clean(label)}</span><span class="feature-icon">{clean(icon)}</span></div>
      <div class="feature-number">{clean(main)}</div>
      <div class="feature-detail">{clean(detail)}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(kicker, title, detail, tone="teal"):
    """One magazine-style insight: compact and visually consistent."""
    st.markdown(f"""
    <div class="insight-card tone-{clean(tone)}">
      <div class="insight-kicker">{clean(kicker)}</div>
      <div class="insight-title">{clean(title)}</div>
      <div class="insight-detail">{clean(detail)}</div>
    </div>""", unsafe_allow_html=True)


def matchup_card(game):
    """Display ONE verified, completed ESPN matchup as a scoreboard tile.

    Color uses the Winner ID, not point comparison, so the display respects
    the finalized ESPN outcome. The user can update JSON to change it.
    """
    home = int(game["Home ID"])
    away = int(game["Away ID"])
    winner = game["Winner ID"]
    away_class = 'won' if winner == away else ''
    home_class = 'won' if winner == home else ''
    tie_label = ' • TIE' if winner is None else ''
    st.markdown(f"""
    <div class="matchup-card">
      <div class="matchup-heading">WEEK {int(game['Week'])} · FINAL{tie_label}</div>
      <div class="matchup-side {away_class}"><span class="team-name">{clean(game['Away Team'])}</span>
        <span class="team-score">{float(game['Away Score']):.2f}</span></div>
      <div class="matchup-rule"></div>
      <div class="matchup-side {home_class}"><span class="team-name">{clean(game['Home Team'])}</span>
        <span class="team-score">{float(game['Home Score']):.2f}</span></div>
    </div>""", unsafe_allow_html=True)


def profile_banner(row, high=None, low=None):
    """Big player-card layout assembled from standings (not invented stats)."""
    record=f"{int(row['W'])}-{int(row['L'])}"
    if int(row.get('T',0)):
        record += f"-{int(row['T'])}"
    st.markdown(f"""
    <div class="profile-hero">
      <div class="profile-overline">TEAM DOSSIER  /  RANK #{int(row['Rank']):02d}</div>
      <div class="profile-name">{clean(row['Team'])}</div>
      <div class="profile-manager">Managed by {clean(row['Manager'])}</div>
      <div class="profile-stats">
        <div><strong>{clean(record)}</strong><span>Season record</span></div>
        <div><strong>{float(row['PPG']):.1f}</strong><span>Points / game</span></div>
        <div><strong>{float(row['PF']):.1f}</strong><span>Total points</span></div>
        <div><strong>{float(row['Diff']):+.1f}</strong><span>Point differential</span></div>
      </div>
    </div>""",unsafe_allow_html=True)


def small_heading(title, description):
    st.markdown(f'<div class="subhead"><h3>{clean(title)}</h3><p>{clean(description)}</p></div>',unsafe_allow_html=True)

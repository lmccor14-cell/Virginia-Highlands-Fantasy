"""SITE DESIGN SYSTEM — adjust colors, font, spacing and cards in one place.

LEARN: CSS variables (--accent etc.) act like reusable Python constants.
Changing a variable here restyles many components simultaneously.
"""
from html import escape
import streamlit as st


def apply_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--canvas:#090E19;--panel:#111B2A;--panel2:#172337;--border:#29384E;--muted:#A7B8CB;
      --text:#F1F6FF;--accent:#5BE1C5;--gold:#F4C76B;--blue:#82B5F8;--rose:#FF829D}
.stApp{background:radial-gradient(circle at 78% -4%, #203650 0%,#0D1727 35%,#090E19 80%);color:var(--text)}
html,body,[data-testid="stAppViewContainer"],.stApp,[class*="css"]{font-family:'DM Sans','Segoe UI',sans-serif}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0E1B2B,#0B1420);border-right:1px solid #283B50}
[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:.95rem}
[data-testid="stSidebar"] div[role="radiogroup"] label{border-radius:10px;padding:5px 8px;transition:background .15s}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:#1C2C42}
[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.6rem;max-width:1450px;padding-bottom:5rem}
h1,h2,h3,h4{font-family:'Space Grotesk','DM Sans',sans-serif;letter-spacing:-.035em}
h2{font-weight:700}h3{font-weight:650}
p{line-height:1.58}
[data-testid="stMetric"]{background:linear-gradient(148deg,#172940,#111B2A 75%);border:1px solid #34465E;
  border-radius:16px;padding:18px 20px;box-shadow:0 12px 25px #0000001a}
[data-testid="stMetricLabel"]{color:#9CB2C9}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif;color:#F4FAFF;letter-spacing:-.04em}
[data-testid="stDataFrame"]{border:1px solid #2D3D53;border-radius:14px;overflow:hidden}
[data-testid="stPlotlyChart"]{border-radius:18px;overflow:hidden}
[data-testid="stTabs"] button[role="tab"]{font-weight:700}
[data-testid="stSelectbox"],[data-testid="stSlider"]{border-radius:12px}
div.stButton button,div.stDownloadButton button{border-radius:11px;border:1px solid #42617D;font-weight:700;transition:background .15s}
div.stButton button:hover,div.stDownloadButton button:hover{border-color:#5BE1C5;background:#173744}
.hero{position:relative;overflow:hidden;border:1px solid #385B70;background:
 linear-gradient(115deg,#113244 0%,#152840 53%,#27203D 100%);border-radius:24px;
 padding:31px 34px;margin:4px 0 26px;box-shadow:0 20px 40px #02081044}
.hero:after{content:'✦';position:absolute;color:#6EDCC41E;font-size:220px;line-height:1;right:12px;top:-46px;pointer-events:none}
.eyebrow{font-size:.72rem;letter-spacing:.2em;font-weight:800;color:var(--accent);text-transform:uppercase}
.hero h1{font-size:clamp(2rem,3.3vw,3.2rem);margin:.4rem 0;line-height:1.13;color:#F5F9FF;max-width:850px}
.hero p{color:#C4D2E5;max-width:800px;margin:.55rem 0 0;font-size:1rem}
.section-label{color:#5BE1C5;letter-spacing:.16em;font-weight:800;font-size:.76rem;text-transform:uppercase;margin:1.35rem 0 .65rem}
.subhead{margin:1.5rem 0 1rem}.subhead h3{font-size:1.35rem;margin:0}.subhead p{color:var(--muted);margin:4px 0 0;font-size:.91rem}
.feature-card{--edge:#5BE1C5;border:1px solid #30455C;border-top:3px solid var(--edge);
  background:linear-gradient(145deg,#182B40,#101B2C);border-radius:16px;min-height:152px;padding:18px 18px 16px}
.feature-top{display:flex;align-items:center;justify-content:space-between;color:#AFC0D3;font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.feature-icon{color:var(--edge);font-size:1.3rem}.feature-number{font-family:'Space Grotesk',sans-serif;font-size:1.7rem;font-weight:700;line-height:1.3;margin:15px 0 4px;letter-spacing:-.055em;word-break:break-word}
.feature-detail{color:#A2B2C8;font-size:.78rem;line-height:1.5}
.tone-gold{--edge:#F4C76B}.tone-blue{--edge:#82B5F8}.tone-rose{--edge:#FF829D}.tone-violet{--edge:#B6A1FF}
.insight-card{--edge:#5BE1C5;background:#121F31;border:1px solid #2C405A;border-left:3px solid var(--edge);
  padding:20px 21px;border-radius:15px;min-height:139px}
.insight-kicker{font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:var(--edge)}
.insight-title{font-family:'Space Grotesk',sans-serif;font-size:1.22rem;font-weight:700;line-height:1.4;margin:11px 0 5px}
.insight-detail{font-size:.82rem;color:#ACBED2;line-height:1.5}
.matchup-card{background:linear-gradient(145deg,#162437,#101928);border:1px solid #32445C;border-radius:16px;
 padding:14px 18px;margin-bottom:12px;min-height:142px}
.matchup-heading{font-size:.69rem;letter-spacing:.14em;color:#8FA6BD;font-weight:800;margin-bottom:11px}
.matchup-side{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:9px 0;color:#A6B6C9}
.matchup-side.won{color:#F7FAFF}.matchup-side.won .team-name:before{content:'●';color:#5BE1C5;margin-right:9px;font-size:.7rem}
.team-name{font-size:.93rem;font-weight:650;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.team-score{font-family:'Space Grotesk',sans-serif;font-size:1.06rem;font-weight:700;white-space:nowrap}
.matchup-rule{height:1px;background:#3442574F}
.profile-hero{border:1px solid #4E6079;border-radius:22px;background:
 radial-gradient(circle at 90% 12%,#32635A66,transparent 38%),linear-gradient(100deg,#142F43,#172137 75%);
 padding:29px 32px;margin:8px 0 20px}
.profile-overline{color:#5BE1C5;font-size:.73rem;letter-spacing:.16em;font-weight:800}
.profile-name{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.8rem,3.2vw,2.65rem);letter-spacing:-.06em;font-weight:700;margin-top:9px}
.profile-manager{color:#AFBED2;margin-top:2px;font-size:.92rem}
.profile-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:27px}
.profile-stats div{border-left:1px solid #597086;padding-left:16px;display:flex;flex-direction:column;gap:4px}
.profile-stats strong{font-size:1.5rem;letter-spacing:-.04em;font-family:'Space Grotesk',sans-serif}
.profile-stats span{font-size:.74rem;color:#AFC0D2}
.brand-lockup{padding:5px 0 12px}.brand-top{font-family:'Space Grotesk',sans-serif;font-size:1.15rem;color:#F6FAFF;font-weight:700;letter-spacing:-.03em}
.brand-sub{color:#62D6BD;font-size:.69rem;letter-spacing:.19em;font-weight:800;margin-top:3px}
#MainMenu,footer{visibility:hidden}
@media(max-width:750px){.hero{padding:24px 20px}.profile-stats{grid-template-columns:repeat(2,1fr)}.profile-hero{padding:22px 20px}}
</style>
""", unsafe_allow_html=True)


def hero(eyebrow, title, description):
    # LEARN: escape anything that might come from ESPN before inserting in HTML.
    st.markdown(f"""<div class="hero"><div class="eyebrow">{escape(str(eyebrow))}</div>
    <h1>{escape(str(title))}</h1><p>{escape(str(description))}</p></div>""",unsafe_allow_html=True)

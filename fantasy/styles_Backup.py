"""Website's look & feel. Change CSS here, not in the analysis code."""
import streamlit as st
from html import escape


def apply_styles():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
      html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans','Segoe UI',sans-serif;}
      .stApp {background:radial-gradient(circle at 96% 0%,#172940 0%,#0B1020 37%);}
      [data-testid="stSidebar"] {background:#0C1424; border-right:1px solid #29344D;}
      h1,h2,h3{letter-spacing:-.03em;}
      h1{font-weight:800;}
      [data-testid="stMetric"] {background:linear-gradient(135deg,#17253A,#111A2C);border:1px solid #2A3D54;
         padding:17px 18px;border-radius:16px;}
      [data-testid="stMetricLabel"] {color:#A6B4CE;}
      [data-testid="stMetricValue"] {color:#E7F6F5;}
      div[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;border:1px solid #25354A;}
      .hero{background:linear-gradient(120deg,#12283C 0%,#17223F 62%,#2E2444 100%);
        border:1px solid #32536B;padding:23px 28px 19px;border-radius:22px;margin-bottom:22px;}
      .eyebrow{letter-spacing:.14em;text-transform:uppercase;color:#65D6C1;font-size:.74rem;font-weight:800;}
      .hero h1{font-size:2.3rem;line-height:1.1;margin:.35rem 0;color:#F1F7FF;}
      .hero p{color:#AEBFD4;margin:.6rem 0 0;font-size:.95rem;}
      .section-kicker{color:#65D6C1;font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;font-weight:700;}
      div.stButton button,div.stDownloadButton button{border-radius:10px;border:1px solid #345872;}
      .muted{color:#A6B4CE;font-size:.85rem;}
      #MainMenu,footer{visibility:hidden;}
    </style>""", unsafe_allow_html=True)


def hero(eyebrow, title, description):
    # Static authored HTML, not league-provided strings.
    st.markdown(f"""<div class='hero'><div class='eyebrow'>{escape(eyebrow)}</div>
    <h1>{escape(title)}</h1><p>{escape(description)}</p></div>""",unsafe_allow_html=True)

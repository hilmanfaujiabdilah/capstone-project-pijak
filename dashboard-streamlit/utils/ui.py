import streamlit as st

from utils.auth import logout_button, require_login


LABEL_COLORS = {
    "positive": "#22C55E",
    "neutral": "#F59E0B",
    "negative": "#EF4444",
}

LABEL_ID = {
    0: "negative",
    1: "neutral",
    2: "positive",
}

LABEL_TEXT = {
    "positive": "Positif",
    "neutral": "Netral",
    "negative": "Negatif",
}


def setup_page(title: str, icon: str = "chart", require_auth: bool = True) -> None:
    st.set_page_config(
        page_title=f"{title} | Zenlytics Sentimen",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    if require_auth:
        require_login()
    with st.sidebar:
        st.markdown("### Dashboard Sentimen")
        st.caption("Zenlytics Sentiment")
        st.divider()
        st.page_link("app.py", label="Home")
        st.page_link("pages/1_Predict_Sentiment.py", label="Predict Sentiment")
        st.page_link("pages/2_Analytics.py", label="Analytics")
        st.page_link("pages/3_Model_Performance.py", label="Model Performance")
        st.page_link("pages/4_Batch_Prediction.py", label="Batch Prediction")
        st.page_link("pages/5_About_Project.py", label="About Project")
        st.divider()
        logout_button()

def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        [data-testid="stSidebar"] {
            background: #0B1120;
            border-right: 1px solid rgba(148, 163, 184, 0.16);
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(30,41,59,.9), rgba(15,23,42,.85));
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 8px;
            padding: 1rem;
        }
        .hero {
            padding: 1.5rem 0 1rem 0;
        }
        .hero h1 {
            font-size: 2.35rem;
            line-height: 1.15;
            margin-bottom: .5rem;
        }
        .muted {
            color: #CBD5E1;
            font-size: 1rem;
        }
        .panel {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 8px;
            padding: 1rem;
        }
        .sentiment-pill {
            display: inline-flex;
            align-items: center;
            gap: .5rem;
            border-radius: 999px;
            padding: .35rem .75rem;
            font-weight: 700;
            border: 1px solid rgba(255,255,255,.14);
        }
        .small-note {
            color: #94A3B8;
            font-size: .88rem;
        }
        .login-hero {
            max-width: 460px;
            margin: 12vh auto 1.5rem auto;
            text-align: center;
        }
        .login-hero h1 {
            font-size: 2.25rem;
            line-height: 1.15;
            margin-bottom: .5rem;
        }
        .login-hero p {
            color: #CBD5E1;
            margin: 0;
        }
        div[data-testid="stForm"] {
            max-width: 460px;
            margin: 0 auto;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            padding: 1.25rem;
            background: rgba(30, 41, 59, 0.72);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 8px;
        }
        [data-testid="stSidebarNav"] {
             display: none !important;
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <div class="muted">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sentiment_badge(label: str) -> None:
    color = LABEL_COLORS.get(label, "#94A3B8")
    text = LABEL_TEXT.get(label, label.title())
    st.markdown(
        f"""
        <div class="sentiment-pill" style="background:{color}22;color:{color};">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

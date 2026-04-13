"""
DBS Bank Strategic and HR Analytics Dashboard
BEM3063 Assessment 2
"""

import warnings
warnings.filterwarnings("ignore")

import time
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DBS Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
TICKERS = {"DBS": "D05.SI", "OCBC": "O39.SI", "UOB": "U11.SI"}
COLORS  = {"DBS": "#c8102e", "OCBC": "#1a1a1a", "UOB": "#003d7c"}
THEME = {
    "dbs_red": "#c8102e",
    "dbs_red_light": "#fff1f3",
    "dbs_red_dark": "#970f24",
    "black": "#111111",
    "charcoal": "#1a1a1a",
    "slate": "#4a5568",
    "border": "#e2e8f0",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "grid": "#f1f5f9",
    "shadow": "rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
}

MOM_RESIGNATION = {
    2020: 10.2,
    2021: 12.8,
    2022: 14.1,
    2023: 10.5,
    2024: 8.9,
}

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {THEME["surface_alt"]}; color: {THEME["black"]}; }}
    .block-container {{ padding: 1.5rem 2rem; max-width: 1400px; }}
    .dashboard-hero {{
        background: {THEME["surface"]}; border: 1px solid {THEME["border"]};
        border-bottom: 5px solid {THEME["dbs_red"]}; border-radius: 8px;
        padding: 1.5rem 2rem; color: {THEME["black"]}; margin-bottom: 1.5rem;
        box-shadow: {THEME["shadow"]};
    }}
    .dashboard-hero .eyebrow {{
        color: {THEME["dbs_red"]}; font-size: 0.75rem; letter-spacing: 0.1em;
        text-transform: uppercase; margin-bottom: 0.5rem; font-weight: 700;
    }}
    .dashboard-hero h1 {{
        font-size: 2rem; line-height: 1.2; margin: 0; font-weight: 700; letter-spacing: -0.02em;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 0.5rem; padding: 0 0 1rem; background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        background: {THEME["surface"]}; border: 1px solid {THEME["border"]}; border-radius: 6px;
        color: {THEME["charcoal"]}; font-weight: 600; padding: 0.5rem 1.25rem; font-size: 0.9rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: {THEME["dbs_red"]}; color: #ffffff !important; border-color: {THEME["dbs_red"]};
        box-shadow: 0 4px 6px -1px rgba(200, 16, 46, 0.2);
    }}
    div[data-testid="stMetric"] {{
        background: {THEME["surface"]}; border: 1px solid {THEME["border"]};
        border-radius: 8px; padding: 1rem; box-shadow: {THEME["shadow"]};
    }}
    [data-testid="stMetricLabel"] {{
        color: {THEME["slate"]}; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.05em; font-size: 0.7rem;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.75rem; font-weight: 700; color: {THEME["black"]}; letter-spacing: -0.02em;
    }}
    [data-testid="stMetricDelta"] {{ font-weight: 600; }}
    div[data-testid="stDataFrame"],
    div[data-testid="stPlotlyChart"],
    div[data-testid="stExpander"] {{
        background: {THEME["surface"]}; border: 1px solid {THEME["border"]};
        border-radius: 8px; box-shadow: {THEME["shadow"]};
    }}
    div[data-testid="stExpander"] {{ overflow: hidden; border: 1px solid {THEME["border"]}; }}
    div[data-testid="stExpander"] details summary {{
        background: {THEME["surface"]}; font-weight: 600; padding: 0.75rem 1rem; color: {THEME["black"]};
    }}
    .stAlert {{ border-radius: 8px; border: 1px solid {THEME["border"]}; }}
    .alert-box {{
        padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; font-size: 0.9rem;
        border-left: 5px solid; background: {THEME["surface"]}; box-shadow: {THEME["shadow"]};
    }}
    .alert-green {{ border-color: #10b981; background: #f0fdf4; color: #064e3b; }}
    .alert-red {{ border-color: {THEME["dbs_red"]}; background: {THEME["dbs_red_light"]}; color: #7f1d1d; }}
    .alert-amber {{ border-color: #f59e0b; background: #fffbeb; color: #78350f; }}
    .brief-card {{
        background: {THEME["surface"]}; border: 1px solid {THEME["border"]};
        border-left: 5px solid {THEME["dbs_red"]}; border-radius: 8px;
        padding: 1.25rem; margin-bottom: 1rem; box-shadow: {THEME["shadow"]}; height: 100%;
    }}
    .brief-card .label {{
        color: {THEME["dbs_red"]}; font-size: 0.7rem; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 0.5rem; font-weight: 700;
    }}
    .brief-card h4 {{ margin: 0 0 0.5rem; font-size: 1rem; font-weight: 700; color: {THEME["black"]}; }}
    .brief-card p {{ margin: 0; color: {THEME["slate"]}; font-size: 0.875rem; line-height: 1.5; }}
    hr {{ margin: 2rem 0 !important; border: 0; border-top: 1px solid {THEME["border"]}; }}

    /* BUTTON CONSISTENCY */
    div.stButton > button,
    div.stDownloadButton > button {{
        background-color: {THEME["surface"]};
        color: {THEME["black"]} !important;
        border: 1px solid {THEME["border"]};
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.2s ease;
        width: auto;
    }}
    div.stButton > button:hover,
    div.stDownloadButton > button:hover {{
        border-color: {THEME["dbs_red"]};
        color: {THEME["dbs_red"]} !important;
        background-color: {THEME["surface_alt"]};
        box-shadow: {THEME["shadow"]};
    }}
    div.stButton > button:active,
    div.stDownloadButton > button:active {{
        background-color: {THEME["dbs_red"]};
        color: #ffffff !important;
    }}

    /* INPUT & WIDGET CONSISTENCY FOR DARK MODE */
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"],
    div[data-testid="stSlider"] [data-testid="stWidgetLabel"] p {{
        color: {THEME["black"]} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {THEME["surface"]} !important;
        color: {THEME["black"]} !important;
    }}
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input {{
        color: {THEME["black"]} !important;
        background-color: {THEME["surface"]} !important;
    }}
    
    /* FIX FOR OVERLAPPING MODES */
    .stApp {{ background-color: {THEME["surface_alt"]} !important; color: {THEME["black"]} !important; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    [data-testid="stSidebar"] {{ background-color: {THEME["surface"]}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def linear_forecast(years: list, values: list, n_ahead: int = 3):
    arr  = np.array(list(zip(years, values)), dtype=float)
    mask = ~np.isnan(arr[:, 1])
    if mask.sum() < 2:
        return [], []
    x, y   = arr[mask, 0], arr[mask, 1]
    coeffs = np.polyfit(x, y, 1)
    fx     = np.arange(int(x.max()) + 1, int(x.max()) + n_ahead + 1)
    fy     = np.polyval(coeffs, fx)
    return fx.tolist(), fy.tolist()


def fmt_sgd(value, decimals=1):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"SGD {value / 1e9:.{decimals}f}B"


def fmt_billions(value, decimals=1):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"SGD {value:.{decimals}f}B"


def alert_html(level: str, text: str) -> str:
    css = {"green": "alert-green", "red": "alert-red", "amber": "alert-amber"}
    return f'<div class="alert-box {css.get(level, "alert-amber")}">{text}</div>'


def apply_chart_theme(fig, height=None):
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="'Inter', sans-serif", color=THEME["slate"]),
        title=dict(x=0, xanchor="left", font=dict(size=16, color=THEME["black"])),
        margin=dict(t=60, b=60, l=60, r=40),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=THEME["border"],
                    borderwidth=1, font=dict(size=11), orientation="h",
                    yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(bgcolor="white", bordercolor=THEME["border"],
                        font=dict(family="'Inter', sans-serif", color=THEME["black"])),
    )
    if height is not None:
        fig.update_layout(height=height)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=THEME["border"],
                     showline=True, tickfont=dict(size=11),
                     title_font=dict(size=12, color=THEME["slate"]))
    fig.update_yaxes(showgrid=True, gridcolor=THEME["grid"], zeroline=False,
                     linecolor=THEME["border"], showline=True, tickfont=dict(size=11),
                     title_font=dict(size=12, color=THEME["slate"]))
    return fig


def latest_numeric(df: pd.DataFrame, column: str):
    if df.empty or column not in df.columns:
        return np.nan
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    return float(series.iloc[-1]) if not series.empty else np.nan


def bank_metric(df: pd.DataFrame, bank: str, column: str):
    if df.empty or "bank" not in df.columns or column not in df.columns:
        return np.nan
    match = df[df["bank"].astype(str).str.upper() == bank.upper()]
    return pd.to_numeric(match.iloc[0][column], errors="coerce") if not match.empty else np.nan


def one_year_return(hist: pd.DataFrame):
    if hist is None or hist.empty or "Close" not in hist.columns:
        return np.nan
    closes = pd.to_numeric(hist["Close"], errors="coerce").dropna()
    if len(closes) < 2:
        return np.nan
    start = closes.iloc[-252] if len(closes) > 252 else closes.iloc[0]
    end   = closes.iloc[-1]
    if pd.isna(start) or start == 0 or pd.isna(end):
        return np.nan
    return float(end / start - 1)


def _find_col(df: pd.DataFrame, keywords: list):
    for kw in keywords:
        for c in df.columns:
            if kw.lower() in str(c).lower():
                return c
    return None


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=7200, show_spinner=False)
def load_stock_history() -> dict:
    """
    Uses yf.download() instead of t.history() — different Yahoo endpoint,
    less aggressively rate-limited on shared cloud IPs.
    Adds 2s sleep between tickers to avoid bursting.
    """
    yf.set_tz_cache_location("/tmp")
    out = {}
    for name, ticker in TICKERS.items():
        try:
            time.sleep(2)
            df = yf.download(
                ticker,
                period="5y",
                progress=False,
                auto_adjust=True,
                timeout=30,
            )
            if df.empty:
                time.sleep(3)
                df = yf.download(ticker, period="2y", progress=False,
                                 auto_adjust=True, timeout=30)
            if not df.empty:
                # yf.download with single ticker may return MultiIndex columns
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.index = pd.to_datetime(df.index).tz_localize(None)
                if "Close" in df.columns:
                    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
                    df = df.dropna(subset=["Close"])
                out[name] = df
            else:
                out[name] = pd.DataFrame()
        except Exception:
            out[name] = pd.DataFrame()
    return out


@st.cache_data(ttl=7200, show_spinner=False)
def load_financials() -> dict:
    """Loads financials with sleep between tickers to avoid rate limiting."""
    yf.set_tz_cache_location("/tmp")
    data = {}
    for name, ticker in TICKERS.items():
        try:
            time.sleep(3)
            t   = yf.Ticker(ticker)
            fin = t.financials
            if fin is not None and not fin.empty:
                fin = fin.T.copy()
                fin.index = pd.to_datetime(fin.index).year
            else:
                fin = pd.DataFrame()

            bs = t.balance_sheet
            if bs is not None and not bs.empty:
                bs = bs.T.copy()
                bs.index = pd.to_datetime(bs.index).year
            else:
                bs = pd.DataFrame()

            try:
                info = t.info or {}
            except Exception:
                info = {}

            data[name] = {"income": fin, "balance": bs, "info": info}
        except Exception:
            data[name] = {"income": pd.DataFrame(), "balance": pd.DataFrame(), "info": {}}
    return data


@st.cache_data(show_spinner=False)
def load_hr() -> pd.DataFrame:
    df = pd.read_csv("data/dbs_hr_metrics.csv")
    df["year"] = df["year"].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_glassdoor() -> pd.DataFrame:
    df = pd.read_csv("data/glassdoor_sentiment.csv")
    for col in df.columns:
        if col != "bank":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_sgx() -> pd.DataFrame:
    df = pd.read_csv("data/sgx_banking_metrics.csv")
    for col in df.columns:
        if col != "bank":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# LOAD ALL DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Loading data — this may take up to 30 seconds on first load…"):
    stock_hist = load_stock_history()
    financials = load_financials()
    hr_df      = load_hr()
    gd_df      = load_glassdoor()
    sgx_df     = load_sgx()

dbs_info = financials["DBS"]["info"]
dbs_inc  = financials["DBS"]["income"]


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dashboard-hero">
        <div class="eyebrow">DBS Bank Internal Dashboard</div>
        <h1>Strategic and HR Analytics Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Refresh button
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()

# Warn if live market data failed
live_data_missing = not dbs_info or not dbs_info.get("marketCap")
if live_data_missing:
    st.warning(
        "Live market data is temporarily unavailable — Yahoo Finance rate-limits "
        "shared cloud IPs. Click **🔄 Refresh Live Data** above to retry, "
        "or wait a few minutes and refresh the page."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Diagnosis",
    "Strategic Overview",
    "Financial Performance",
    "HR Analytics",
    "Workforce Benchmarking",
    "Macroeconomic Context",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — EXECUTIVE DIAGNOSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    st.subheader("Executive Diagnosis")

    dbs_roe           = bank_metric(sgx_df, "DBS", "roe_pct")
    peer_roe_avg      = pd.to_numeric(sgx_df["roe_pct"], errors="coerce").mean() if not sgx_df.empty else np.nan
    dbs_nim           = bank_metric(sgx_df, "DBS", "net_interest_margin_pct")
    peer_best_nim     = pd.to_numeric(sgx_df["net_interest_margin_pct"], errors="coerce").max() if not sgx_df.empty else np.nan
    dbs_cost          = bank_metric(sgx_df, "DBS", "cost_to_income_pct")
    best_cost         = pd.to_numeric(sgx_df["cost_to_income_pct"], errors="coerce").min() if not sgx_df.empty else np.nan
    attr_latest       = latest_numeric(hr_df, "voluntary_attrition_pct")
    engagement_latest = latest_numeric(hr_df, "engagement_score_pct")
    training_latest   = latest_numeric(hr_df, "training_hrs_per_employee")
    sector_attr       = MOM_RESIGNATION.get(2024, np.nan)
    recommend_latest  = bank_metric(gd_df, "DBS", "recommend_pct")
    peer_recommend_avg= pd.to_numeric(gd_df["recommend_pct"], errors="coerce").mean() if not gd_df.empty else np.nan

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("ROE vs Peer Average",
              f"{dbs_roe:.1f}%" if pd.notna(dbs_roe) else "N/A",
              delta=f"{dbs_roe - peer_roe_avg:+.1f}pp" if pd.notna(dbs_roe) and pd.notna(peer_roe_avg) else None)
    k2.metric("NIM vs Best Peer",
              f"{dbs_nim:.2f}%" if pd.notna(dbs_nim) else "N/A",
              delta=f"{dbs_nim - peer_best_nim:+.2f}pp" if pd.notna(dbs_nim) and pd.notna(peer_best_nim) else None,
              delta_color="inverse")
    k3.metric("Attrition vs Sector",
              f"{attr_latest:.1f}%" if pd.notna(attr_latest) else "N/A",
              delta=f"{attr_latest - sector_attr:+.1f}pp" if pd.notna(attr_latest) and pd.notna(sector_attr) else None,
              delta_color="inverse")
    k4.metric("Employer Brand",
              f"{recommend_latest:.0f}%" if pd.notna(recommend_latest) else "N/A",
              delta=f"{recommend_latest - peer_recommend_avg:+.0f}pp" if pd.notna(recommend_latest) and pd.notna(peer_recommend_avg) else None)

    issue_cols = st.columns(4)
    issue_cards = [
        ("Strategic Priority", "Protect margin resilience",
         f"DBS NIM is {dbs_nim:.2f}% versus a peer best of {peer_best_nim:.2f}%." if pd.notna(dbs_nim) and pd.notna(peer_best_nim) else "Margin leadership should be monitored against peer pricing pressure."),
        ("Operating Issue", "Close the efficiency gap",
         f"Cost-to-income is {dbs_cost:.1f}% versus the best peer at {best_cost:.1f}%." if pd.notna(dbs_cost) and pd.notna(best_cost) else "Operating efficiency should be benchmarked against the peer frontier."),
        ("HR Issue", "Sustain talent capability",
         f"Training hours are {training_latest:.1f} per employee while engagement remains {engagement_latest:.0f}%." if pd.notna(training_latest) and pd.notna(engagement_latest) else "Capability development should be monitored alongside engagement and retention."),
        ("People Risk", "Strengthen employee value proposition",
         f"Glassdoor recommendation is {recommend_latest:.0f}% and work-life balance is {bank_metric(gd_df, 'DBS', 'work_life_balance'):.1f}/5." if pd.notna(recommend_latest) and pd.notna(bank_metric(gd_df, 'DBS', 'work_life_balance')) else "External employer-brand indicators should be tracked with retention outcomes."),
    ]
    for col, (label, title, body) in zip(issue_cols, issue_cards):
        col.markdown(
            f'<div class="brief-card"><div class="label">{label}</div><h4>{title}</h4><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### Diagnosis Register")
        diagnosis_rows = [
            {"Issue": "Margin pressure as rates normalize",
             "Evidence": f"NIM {dbs_nim:.2f}% vs peer best {peer_best_nim:.2f}%" if pd.notna(dbs_nim) and pd.notna(peer_best_nim) else "NIM data pending",
             "Why it matters": "Lower margin momentum can weaken earnings quality and investor confidence.",
             "Decision supported": "Shift attention to fee income, pricing discipline, and mix management.",
             "Priority": "High" if pd.notna(dbs_nim) and pd.notna(peer_best_nim) and dbs_nim < peer_best_nim else "Medium"},
            {"Issue": "Efficiency gap versus best peer",
             "Evidence": f"Cost-to-income {dbs_cost:.1f}% vs best peer {best_cost:.1f}%" if pd.notna(dbs_cost) and pd.notna(best_cost) else "Efficiency benchmark pending",
             "Why it matters": "A persistent cost gap can reduce flexibility during revenue slowdown.",
             "Decision supported": "Prioritize process redesign and productivity initiatives.",
             "Priority": "High" if pd.notna(dbs_cost) and pd.notna(best_cost) and dbs_cost - best_cost > 1 else "Medium"},
            {"Issue": "Capability sustainability",
             "Evidence": f"Training at {training_latest:.1f} hours with engagement at {engagement_latest:.0f}%" if pd.notna(training_latest) and pd.notna(engagement_latest) else "Capability signal pending",
             "Why it matters": "DBS depends on digital and AI capability to defend strategic advantage.",
             "Decision supported": "Protect role-critical learning investment and succession depth.",
             "Priority": "Medium"},
            {"Issue": "External employer brand risk",
             "Evidence": f"Recommend {recommend_latest:.0f}% and work-life balance {bank_metric(gd_df, 'DBS', 'work_life_balance'):.1f}/5" if pd.notna(recommend_latest) and pd.notna(bank_metric(gd_df, 'DBS', 'work_life_balance')) else "Glassdoor signal pending",
             "Why it matters": "Employer brand influences attraction, retention, and replacement cost.",
             "Decision supported": "Target EVP improvements in manager quality, workload, and career clarity.",
             "Priority": "Medium"},
        ]
        st.dataframe(pd.DataFrame(diagnosis_rows), width='stretch', hide_index=True)

    with right:
        st.markdown("#### Alert Register")
        exec_alerts = []

        if pd.notna(dbs_nim) and pd.notna(peer_best_nim):
            if dbs_nim <= peer_best_nim - 0.05:
                exec_alerts.append(alert_html("amber", "Strategic Alert: DBS trails the peer leader on NIM. Monitor revenue mix and pricing response."))
            else:
                exec_alerts.append(alert_html("green", "Strategic Signal: DBS remains close to the peer frontier on NIM."))

        if pd.notna(dbs_cost) and pd.notna(best_cost):
            if dbs_cost >= best_cost + 1.0:
                exec_alerts.append(alert_html("amber", "Efficiency Alert: Cost-to-income is above the best peer by more than 1 point."))
            else:
                exec_alerts.append(alert_html("green", "Efficiency Signal: Cost-to-income remains broadly competitive."))

        work_life = bank_metric(gd_df, "DBS", "work_life_balance")
        if pd.notna(work_life):
            if work_life < 3.5:
                exec_alerts.append(alert_html("amber", "People Alert: External work-life balance sentiment is below 3.5 out of 5."))
            else:
                exec_alerts.append(alert_html("green", "People Signal: Work-life balance sentiment is not currently a critical risk."))

        stock_returns    = {bank: one_year_return(hist) for bank, hist in stock_hist.items()}
        dbs_return       = stock_returns.get("DBS", np.nan)
        valid_returns    = [v for v in stock_returns.values() if pd.notna(v)]
        best_peer_return = np.nanmax(valid_returns) if valid_returns else np.nan
        if pd.notna(dbs_return) and pd.notna(best_peer_return) and dbs_return < best_peer_return - 0.05:
            exec_alerts.append(alert_html("amber", "Market Signal: DBS share-price momentum trails the strongest local peer over the last year."))

        for alert in exec_alerts:
            st.markdown(alert, unsafe_allow_html=True)

    st.markdown("#### Predictive Watchlist")
    watch_rows = []

    if not dbs_inc.empty:
        rev_col = _find_col(dbs_inc, ["Total Revenue", "revenue", "Revenue"])
        ni_col  = _find_col(dbs_inc, ["Net Income", "net income", "NetIncome", "Profit"])
        years   = sorted(dbs_inc.index.tolist())

        for col_name, metric_label, rationale in [
            (rev_col, "Revenue",    "Track earnings resilience against rate normalization."),
            (ni_col,  "Net income", "Assess whether current strategy protects profit quality."),
        ]:
            if col_name is None:
                continue
            vals = []
            for y in years:
                try:
                    v = dbs_inc.loc[y, col_name]
                    vals.append(float(v) / 1e9 if pd.notna(v) else np.nan)
                except (KeyError, TypeError, ValueError):
                    vals.append(np.nan)
            clean = [v for v in vals if not np.isnan(v)]
            if not clean:
                continue
            fy, fv = linear_forecast(years, vals, 3)
            if fy:
                delta = fv[-1] - clean[-1]
                watch_rows.append({
                    "Metric": metric_label, "Latest": fmt_billions(clean[-1]),
                    "3Y Outlook": fmt_billions(fv[-1]),
                    "Direction": "Improving" if delta > 0.2 else "Stable" if abs(delta) <= 0.2 else "Weakening",
                    "Management use": rationale,
                })

    hr_watch_specs = [
        ("Headcount",           "headcount",               "higher", 500, lambda v: f"{int(v):,}" if pd.notna(v) else "N/A", "Support workforce capacity planning."),
        ("Voluntary attrition", "voluntary_attrition_pct", "lower",  0.3, lambda v: f"{v:.1f}%"   if pd.notna(v) else "N/A", "Flag retention pressure before it hits cost and service continuity."),
        ("Engagement",          "engagement_score_pct",    "higher", 0.5, lambda v: f"{v:.1f}%"   if pd.notna(v) else "N/A", "Check whether culture strength is being sustained."),
    ]
    for label, col_name, better_when, stable_band, formatter, rationale in hr_watch_specs:
        subset = hr_df.dropna(subset=[col_name])
        if subset.empty:
            continue
        vals = subset[col_name].astype(float).tolist()
        yrs  = subset["year"].astype(int).tolist()
        fy, fv = linear_forecast(yrs, vals, 3)
        if not fy:
            continue
        delta = fv[-1] - vals[-1]
        direction = "Stable" if abs(delta) <= stable_band else (
            "Improving" if (better_when == "higher" and delta > 0) or (better_when == "lower" and delta < 0) else "Weakening"
        )
        watch_rows.append({
            "Metric": label, "Latest": formatter(vals[-1]),
            "3Y Outlook": formatter(fv[-1]), "Direction": direction,
            "Management use": rationale,
        })

    if watch_rows:
        st.dataframe(pd.DataFrame(watch_rows), width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — STRATEGIC OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Strategic Overview")

    c1, c2, c3, c4, c5 = st.columns(5)
    mc  = dbs_info.get("marketCap")
    pe  = dbs_info.get("trailingPE")
    pb  = dbs_info.get("priceToBook")
    dy  = dbs_info.get("dividendYield")
    emp = dbs_info.get("fullTimeEmployees")

    c1.metric("Market Cap",         fmt_sgd(mc) if mc else "N/A")
    c2.metric("P/E Ratio",          f"{pe:.1f}×"     if pe  else "N/A")
    c3.metric("P/B Ratio",          f"{pb:.2f}×"     if pb  else "N/A")
    c4.metric("Dividend Yield",     f"{dy*100:.2f}%" if dy  else "N/A")
    c5.metric("Reported Headcount", f"{emp:,}"       if emp else "N/A")

    if live_data_missing:
        st.info("Live market KPIs will appear here once rate limit clears. Use the Refresh button at the top.")

    st.markdown("#### Competitor Snapshot - FY2024")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        if not sgx_df.empty:
            disp = sgx_df.copy()
            disp.columns = [c.replace("_", " ").title() for c in disp.columns]
            st.dataframe(disp.set_index("Bank"), width='stretch')

    with col_r:
        if not sgx_df.empty:
            fig = px.bar(sgx_df, x="bank", y="roe_pct", color="bank",
                         color_discrete_map=COLORS, title="ROE (%) - FY2024",
                         labels={"roe_pct": "ROE (%)", "bank": ""}, text="roe_pct")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(showlegend=False, margin=dict(t=40, b=20))
            apply_chart_theme(fig, height=280)
            st.plotly_chart(fig, width='stretch')

    st.markdown("#### Porter's Five Forces - Singapore Banking")
    forces_data = {
        "Force":     ["Supplier Power", "Buyer Power", "Substitution Threat", "New Entrants", "Competitive Rivalry"],
        "Intensity": [2, 3, 5, 1, 5],
        "Label":     ["Low-Medium", "Medium-High", "High", "Low", "High"],
    }
    df_forces  = pd.DataFrame(forces_data)
    fig_forces = px.bar(df_forces, x="Intensity", y="Force", orientation="h",
                        text="Label", title="Competitive Forces Intensity",
                        color_discrete_sequence=[THEME["dbs_red"]])
    fig_forces.update_layout(xaxis=dict(range=[0, 5.5], tickvals=[1, 2, 3, 4, 5]),
                              yaxis=dict(autorange="reversed"), showlegend=False)
    fig_forces.update_traces(textposition="outside")
    apply_chart_theme(fig_forces, height=320)
    st.plotly_chart(fig_forces, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FINANCIAL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Financial Performance")

    st.markdown("#### Relative Stock Price Performance - 5 Years (Indexed to 100)")
    fig_px = go.Figure()
    any_stock_data = False
    for bank, hist in stock_hist.items():
        if hist.empty or "Close" not in hist.columns:
            continue
        close = pd.to_numeric(hist["Close"], errors="coerce").dropna()
        if close.empty or close.iloc[0] == 0:
            continue
        idx = (close / close.iloc[0]) * 100
        fig_px.add_trace(go.Scatter(
            x=idx.index, y=idx.values.tolist(),
            name=bank, line=dict(color=COLORS[bank], width=2),
        ))
        any_stock_data = True

    if any_stock_data:
        fig_px.add_hline(y=100, line_dash="dash", line_color=THEME["border"], opacity=0.9)
        apply_chart_theme(fig_px, height=380)
        fig_px.update_layout(xaxis_title="Date", yaxis_title="Indexed Price (Base = 100)", title="")
        st.plotly_chart(fig_px, width='stretch')
    else:
        st.info("Stock price data is temporarily unavailable due to rate limiting. Click **🔄 Refresh Live Data** at the top to retry.")

    st.markdown("#### DBS Annual Revenue & Net Income - with 3-Year Linear Forecast")
    if not dbs_inc.empty:
        rev_col = _find_col(dbs_inc, ["Total Revenue", "revenue", "Revenue"])
        ni_col  = _find_col(dbs_inc, ["Net Income", "net income", "NetIncome", "Profit"])
        years   = sorted(dbs_inc.index.tolist())

        fig_fin = make_subplots(rows=1, cols=2,
                                subplot_titles=("Total Revenue (SGD B)", "Net Income (SGD B)"))
        any_fin = False
        for col_name, col_idx in [(rev_col, 1), (ni_col, 2)]:
            if col_name is None:
                continue
            vals = []
            for y in years:
                try:
                    v = dbs_inc.loc[y, col_name]
                    vals.append(float(v) / 1e9 if pd.notna(v) else np.nan)
                except (KeyError, TypeError, ValueError):
                    vals.append(np.nan)
            clean_vals = [v for v in vals if not np.isnan(v)]
            if not clean_vals:
                continue
            any_fin = True
            label = "Revenue" if col_idx == 1 else "Net Income"
            fig_fin.add_trace(go.Scatter(
                x=years, y=vals, name=f"{label} Actual",
                line=dict(color=COLORS["DBS"], width=2), mode="lines+markers",
            ), row=1, col=col_idx)
            fy, fv = linear_forecast(years, vals, 3)
            if fy:
                fig_fin.add_trace(go.Scatter(
                    x=[years[-1]] + fy, y=[vals[-1]] + fv, name=f"{label} Forecast",
                    line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
                    mode="lines+markers", marker=dict(symbol="circle-open"),
                ), row=1, col=col_idx)

        if any_fin:
            apply_chart_theme(fig_fin, height=400)
            fig_fin.update_layout(legend=dict(orientation="h", y=-0.2), title="")
            fig_fin.update_yaxes(title_text="SGD Billion", row=1, col=1)
            fig_fin.update_yaxes(title_text="SGD Billion", row=1, col=2)
            st.plotly_chart(fig_fin, width='stretch')
        else:
            st.info("Income statement data unavailable. Click **🔄 Refresh Live Data** to retry.")
    else:
        st.info("Income statement data unavailable. Click **🔄 Refresh Live Data** to retry.")

    st.markdown("#### Key Banking Ratios - DBS vs OCBC vs UOB (FY2024)")
    if not sgx_df.empty:
        kpis = [
            ("npl_ratio_pct",          "NPL Ratio (%)",           "↓ lower is better"),
            ("cet1_ratio_pct",         "CET1 Capital Ratio (%)",  "↑ higher is better"),
            ("roe_pct",                "Return on Equity (%)",    "↑ higher is better"),
            ("cost_to_income_pct",     "Cost-to-Income (%)",      "↓ lower is better"),
            ("net_interest_margin_pct","Net Interest Margin (%)", "↑ higher is better"),
        ]
        kcols = st.columns(5)
        for kcol, (metric, label, direction) in zip(kcols, kpis):
            fig = px.bar(sgx_df, x="bank", y=metric, color="bank",
                         color_discrete_map=COLORS,
                         title=f"<b>{label}</b><br><sup>{direction}</sup>", text=metric)
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(showlegend=False, margin=dict(t=70, b=10, l=10, r=10),
                              xaxis_title="", yaxis_title="")
            apply_chart_theme(fig, height=300)
            kcol.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HR ANALYTICS (LAMP)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("HR Analytics - LAMP Framework")

    if hr_df.empty:
        st.error("Could not load data/dbs_hr_metrics.csv.")
        st.stop()

    hr = hr_df.copy()

    st.markdown("### Workforce Size and Growth")
    col_l, col_r = st.columns(2)

    with col_l:
        hc   = hr.dropna(subset=["headcount"])
        yrs  = hc["year"].tolist()
        vals = hc["headcount"].tolist()
        fy, fv = linear_forecast(yrs, vals, 3)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yrs, y=vals, name="Actual",
                                 line=dict(color=COLORS["DBS"], width=2.5), mode="lines+markers",
                                 fill="tozeroy", fillcolor="rgba(200,16,46,0.07)"))
        if fy:
            fig.add_trace(go.Scatter(x=[yrs[-1]] + fy, y=[vals[-1]] + fv, name="Forecast",
                                     line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
                                     mode="lines+markers", marker=dict(symbol="circle-open")))
        fig.update_layout(title="Total Headcount (2020-2025 + Forecast)", yaxis_title="Employees")
        apply_chart_theme(fig, height=340)
        st.plotly_chart(fig, width='stretch')

    with col_r:
        hc2 = hc.set_index("year").copy()
        hc2["growth_pct"] = hc2["headcount"].pct_change() * 100
        hc2 = hc2.dropna(subset=["growth_pct"]).reset_index()
        fig2 = px.bar(hc2, x="year", y="growth_pct", title="Headcount YoY Growth (%)",
                      color_discrete_sequence=[COLORS["DBS"]], text="growth_pct")
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(showlegend=False, yaxis_title="Growth (%)")
        apply_chart_theme(fig2, height=340)
        st.plotly_chart(fig2, width='stretch')

    st.markdown("### Voluntary Attrition")
    att   = hr.dropna(subset=["voluntary_attrition_pct"])
    ayrs  = att["year"].tolist()
    avals = att["voluntary_attrition_pct"].tolist()
    fy_a, fv_a = linear_forecast(ayrs, avals, 3)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ayrs, y=avals, name="Actual",
                             line=dict(color=COLORS["DBS"], width=2.5), mode="lines+markers",
                             fill="tozeroy", fillcolor="rgba(200,16,46,0.08)"))
    if fy_a:
        fig.add_trace(go.Scatter(x=[ayrs[-1]] + fy_a, y=[avals[-1]] + fv_a, name="Forecast",
                                 line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
                                 mode="lines+markers", marker=dict(symbol="circle-open")))
    fig.add_hline(y=10, line_dash="dot", line_color=THEME["charcoal"],
                  annotation_text="10% alert threshold")
    fig.update_layout(title="Voluntary Attrition Rate (%) + Forecast", yaxis_title="Attrition Rate (%)")
    apply_chart_theme(fig, height=340)
    st.plotly_chart(fig, width='stretch')

    latest_att = att["voluntary_attrition_pct"].iloc[-1]
    prev_att   = att["voluntary_attrition_pct"].iloc[-2]
    st.metric("Latest Voluntary Attrition", f"{latest_att}%",
              delta=f"{latest_att - prev_att:+.1f}pp vs prior year", delta_color="inverse")

    st.markdown("### Training and Development")
    tr = hr.dropna(subset=["training_hrs_per_employee"])
    fig = px.bar(tr, x="year", y="training_hrs_per_employee",
                 title="Avg Training Hours per Employee",
                 color_discrete_sequence=[COLORS["DBS"]], text="training_hrs_per_employee")
    fig.update_traces(texttemplate="%{text:.1f}h", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0, 50], yaxis_title="Hours")
    apply_chart_theme(fig, height=320)
    st.plotly_chart(fig, width='stretch')

    st.markdown("### Employee Engagement")
    eng   = hr.dropna(subset=["engagement_score_pct"])
    eyrs  = eng["year"].tolist()
    evals = eng["engagement_score_pct"].tolist()
    fy_e, fv_e = linear_forecast(eyrs, evals, 3)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=eyrs, y=evals, name="Engagement Score",
                             line=dict(color=COLORS["DBS"], width=2.5), mode="lines+markers"))
    if fy_e:
        fig.add_trace(go.Scatter(x=[eyrs[-1]] + fy_e, y=[evals[-1]] + fv_e, name="Forecast",
                                 line=dict(color=THEME["charcoal"], dash="dash", width=1.5),
                                 mode="lines+markers", marker=dict(symbol="circle-open")))
    fig.add_hline(y=74, line_dash="dot", line_color=THEME["slate"],
                  annotation_text="APAC FS Industry Benchmark (74%)")
    fig.add_hline(y=85, line_dash="dot", line_color=THEME["dbs_red_dark"],
                  annotation_text="APAC Best Employers Benchmark (85%)")
    fig.update_layout(title="Employee Engagement Score (%) - My Voice Survey + Forecast",
                      yaxis_title="Engagement (%)", yaxis_range=[65, 100])
    apply_chart_theme(fig, height=360)
    st.plotly_chart(fig, width='stretch')

    st.markdown("### Gender Diversity")
    col_l, col_r = st.columns(2)

    with col_l:
        wf = hr.dropna(subset=["female_workforce_pct"])
        fig = px.line(wf, x="year", y="female_workforce_pct",
                      title="Female Workforce Representation (%)",
                      markers=True, color_discrete_sequence=[COLORS["DBS"]])
        fig.add_hline(y=50, line_dash="dash", line_color=THEME["slate"],
                      annotation_text="Gender Parity (50%)")
        fig.update_layout(yaxis_range=[40, 60], yaxis_title="%")
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, width='stretch')

    with col_r:
        sm = hr.dropna(subset=["female_senior_mgmt_pct"])
        fig = px.bar(sm, x="year", y="female_senior_mgmt_pct",
                     title="Female in Senior Management - SVP to MD (%)",
                     color_discrete_sequence=[THEME["charcoal"]], text="female_senior_mgmt_pct")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, 60], yaxis_title="%")
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, width='stretch')

    st.markdown("### LAMP Process - Automated Decision Alerts")
    latest_hr = hr.sort_values("year").iloc[-1]
    att_val   = latest_hr.get("voluntary_attrition_pct")
    eng_val   = latest_hr.get("engagement_score_pct")
    tr_val    = latest_hr.get("training_hrs_per_employee")

    alerts = []
    if pd.notna(att_val):
        alerts.append(alert_html("red" if att_val > 10 else "green",
            f"Attrition {'Alert' if att_val > 10 else 'Healthy'}: {att_val}% {'exceeds 10% threshold.' if att_val > 10 else 'is within the 10% target.'}"))
    if pd.notna(eng_val):
        level = "green" if eng_val >= 85 else "amber" if eng_val >= 74 else "red"
        alerts.append(alert_html(level,
            f"Engagement {'Excellent' if eng_val >= 85 else 'Moderate' if eng_val >= 74 else 'Critical'}: {eng_val}%."))
    if pd.notna(tr_val):
        alerts.append(alert_html("amber" if tr_val < 30 else "green",
            f"Training {'Below Target' if tr_val < 30 else 'On Track'}: {tr_val}h/employee."))
    for h in alerts:
        st.markdown(h, unsafe_allow_html=True)

    st.markdown("#### HR-Finance Linkage: Attrition Cost Estimator")
    col_l, col_r = st.columns(2)

    with col_l:
        latest_att_val   = float(hr_df.dropna(subset=["voluntary_attrition_pct"])["voluntary_attrition_pct"].iloc[-1])
        attrition_rate   = st.slider("Voluntary Attrition Rate (%)", 1.0, 20.0, latest_att_val, 0.1, key="att_slider")
        avg_salary       = st.slider("Average Annual Salary (SGD)", 50_000, 200_000, 90_000, 5_000, format="SGD %d", key="sal_slider")
        replacement_mult = st.slider("Replacement Cost (% of annual salary)", 50, 200, 100, 10, format="%d%%", key="repl_slider")

    with col_r:
        headcount_val = int(hr_df.dropna(subset=["headcount"])["headcount"].iloc[-1])
        leavers    = int(headcount_val * attrition_rate / 100)
        cost_per   = avg_salary * replacement_mult / 100
        total_cost = leavers * cost_per
        peak_att   = hr_df["voluntary_attrition_pct"].max()
        peak_cost  = int(headcount_val * peak_att / 100) * cost_per
        saving     = peak_cost - total_cost

        st.metric("Estimated Annual Leavers",       f"{leavers:,}")
        st.metric("Replacement Cost per Leaver",    f"SGD {cost_per:,.0f}")
        st.metric("Total Estimated Attrition Cost", f"SGD {total_cost / 1e6:.1f}M")
        st.metric(f"Saving vs Peak Attrition ({peak_att}%)", f"SGD {saving / 1e6:.1f}M",
                  delta="reduction in attrition cost", delta_color="normal")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WORKFORCE BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Workforce Benchmarking")

    GD_CATS   = ["overall_rating", "work_life_balance", "culture_values",
                 "compensation_benefits", "career_opportunities", "senior_mngmnt"]
    GD_LABELS = ["Overall", "Work-Life Balance", "Culture & Values",
                 "Compensation", "Career Opps", "Senior Mgmt"]

    st.markdown("#### Employer Brand - Glassdoor Ratings (DBS vs OCBC vs UOB)")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        if not gd_df.empty:
            fig = go.Figure()
            for _, row in gd_df.iterrows():
                bank = row["bank"]
                vals = [float(row[c]) for c in GD_CATS] + [float(row[GD_CATS[0]])]
                lbls = GD_LABELS + [GD_LABELS[0]]
                fig.add_trace(go.Scatterpolar(r=vals, theta=lbls, fill="toself",
                                              name=bank, line=dict(color=COLORS.get(bank, "grey"))))
            fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5], tickvals=[1, 2, 3, 4, 5])),
                              title="Glassdoor Ratings (out of 5.0)", height=440,
                              paper_bgcolor="white", font=dict(color=THEME["charcoal"]))
            st.plotly_chart(fig, width='stretch')

    with col_r:
        if not gd_df.empty:
            rec_df = gd_df[["bank", "recommend_pct"]].copy()
            rec_df["recommend_pct"] = pd.to_numeric(rec_df["recommend_pct"], errors="coerce")
            fig = px.bar(rec_df, x="bank", y="recommend_pct",
                         color="bank", color_discrete_map=COLORS, text="recommend_pct")
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            apply_chart_theme(fig, height=230)
            fig.update_layout(showlegend=False, yaxis_range=[0, 100],
                              yaxis_title="Percent (%)", xaxis_title="Bank",
                              title="Would Recommend to a Friend (%)")
            st.plotly_chart(fig, width='stretch')

            st.markdown("**Ratings Summary**")
            disp = gd_df.set_index("bank").copy()
            disp.columns = [c.replace("_", " ").title() for c in disp.columns]
            st.dataframe(disp, width='stretch')

    st.markdown("#### Glassdoor Sub-Ratings Breakdown")
    if not gd_df.empty:
        gd_long = gd_df.melt(id_vars="bank", value_vars=GD_CATS,
                              var_name="Category", value_name="Score")
        gd_long["Category"] = gd_long["Category"].map(dict(zip(GD_CATS, GD_LABELS)))
        gd_long["Score"]    = pd.to_numeric(gd_long["Score"], errors="coerce")
        fig = px.bar(gd_long, x="Category", y="Score", color="bank", barmode="group",
                     color_discrete_map=COLORS, title="Glassdoor Sub-Ratings - All Banks", text="Score")
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(yaxis_range=[0, 5.5], legend=dict(orientation="h", y=1.1))
        apply_chart_theme(fig, height=400)
        st.plotly_chart(fig, width='stretch')

    st.markdown("#### DBS Attrition vs Singapore Financial Sector")
    att_data = hr_df.dropna(subset=["voluntary_attrition_pct"])[["year", "voluntary_attrition_pct"]].copy()
    mom_data = pd.DataFrame(list(MOM_RESIGNATION.items()), columns=["year", "mom_resignation_rate"])
    
    # Convert year to string for consistent merging and plotting
    att_data["year"] = att_data["year"].astype(str)
    mom_data["year"] = mom_data["year"].astype(str)
    
    merged = pd.merge(att_data, mom_data, on="year", how="inner")

    if not merged.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=merged["year"], y=merged["voluntary_attrition_pct"],
                                 name="DBS Voluntary Attrition",
                                 line=dict(color=COLORS["DBS"], width=2.5), mode="lines+markers"))
        fig.add_trace(go.Scatter(x=merged["year"], y=merged["mom_resignation_rate"],
                                 name="Financial & Insurance Sector Avg",
                                 line=dict(color=THEME["charcoal"], width=2, dash="dash"),
                                 mode="lines+markers"))
        fig.update_layout(title="Voluntary Attrition: DBS vs Singapore Financial Sector (%)",
                          yaxis_title="Rate (%)", legend=dict(orientation="h", y=1.08))
        fig.update_xaxes(type="category")
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MACROECONOMIC CONTEXT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Macroeconomic Context")

    st.markdown("#### Net Interest Margin - FY2024")
    if not sgx_df.empty:
        fig_nim = px.bar(sgx_df, x="bank", y="net_interest_margin_pct",
                         color="bank", color_discrete_map=COLORS,
                         title="Net Interest Margin - FY2024",
                         labels={"net_interest_margin_pct": "NIM (%)", "bank": ""},
                         text="net_interest_margin_pct")
        fig_nim.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        apply_chart_theme(fig_nim, height=320)
        st.plotly_chart(fig_nim, width='stretch')

    st.divider()

    st.markdown("#### Cost-to-Income Ratio - FY2024")
    if not sgx_df.empty:
        fig_cir = px.bar(sgx_df, x="bank", y="cost_to_income_pct",
                         color="bank", color_discrete_map=COLORS,
                         title="Cost-to-Income Ratio - FY2024",
                         labels={"cost_to_income_pct": "Cost-to-Income (%)", "bank": ""},
                         text="cost_to_income_pct")
        fig_cir.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        apply_chart_theme(fig_cir, height=320)
        st.plotly_chart(fig_cir, width='stretch')

    st.divider()

    st.markdown("#### Non-Performing Loan Ratio - FY2024")
    if not sgx_df.empty:
        fig_npl = px.bar(sgx_df, x="bank", y="npl_ratio_pct",
                         color="bank", color_discrete_map=COLORS,
                         title="Non-Performing Loan Ratio - FY2024",
                         labels={"npl_ratio_pct": "NPL Ratio (%)", "bank": ""},
                         text="npl_ratio_pct")
        fig_npl.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        apply_chart_theme(fig_npl, height=320)
        st.plotly_chart(fig_npl, width='stretch')


# ── NARRATIVE CONTENT (removed from dashboard, use in report/user guide) ──

# --- Data Sources ---
# - yfinance: stock prices and financial statements (D05.SI, O39.SI, U11.SI)
# - DBS Sustainability Reports 2020-2025: HR people metrics
# - DBS / OCBC / UOB Annual Reports 2024: banking KPIs
# - Glassdoor: employer sentiment ratings
# - Ministry of Manpower: Singapore labour turnover statistics
# Analytical Frameworks: LAMP (Boudreau & Ramstad, 2007) · PESTLE · Porter's Five Forces (1979) · HR Value Chain

# --- Tab 3: HR Analytics ---
# LAMP Framework (Boudreau & Ramstad, 2007): Logic, Analytics, Measures, Process.
# LAMP Logic: Voluntary attrition costs 50-200% of annual salary per leaver (Boushey & Glynn, 2012).
# Revenue leakage: RM turnover disrupts client continuity and loan origination.
# Strategic drag: attrition in tech/data roles slows DBS AI/ML roadmap.
# DBS attrition peaked at 14.7% in 2022, declined to 7.4% in 2025.
# Training ROI: 2024 - 33.4h/employee, 1500+ AI/ML models, SGD 750M economic value.
# iGrow AI career coach (2022) personalises learning paths.
# LAMP Process: training below 30h/employee triggers L&D review.

# --- Tab 5: Macroeconomic Context ---
# NIM is the primary driver of banking profitability.
# SORA rose sharply 2022-2023; rate normalisation 2024-2025 compresses NIM.
# DBS 2.13% - offset via wealth management fee income.
# OCBC 2.20% - benefits from Great Eastern integration.
# UOB 2.03% - ASEAN regional diversification.
# DBS NOII record SGD 6.33B in 2024, +22% YoY.
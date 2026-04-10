"""
DBS Bank Strategic and HR Analytics Dashboard
BEM3063 Assessment 2
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

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
COLORS  = {"DBS": "#c8102e", "OCBC": "#1f1f1f", "UOB": "#8a8f98"}
THEME = {
    "dbs_red": "#c8102e",
    "dbs_red_dark": "#970f24",
    "black": "#111111",
    "charcoal": "#1f1f1f",
    "slate": "#5f6368",
    "border": "#d7d9dd",
    "surface": "#ffffff",
    "surface_alt": "#f6f7f8",
    "grid": "#e5e7eb",
    "header_line": "#b60d28",
}

# MOM Financial & Insurance Services resignation rates (annual, %)
# Source: Ministry of Manpower, Labour Turnover Statistics
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
    .stApp {{
        background: {THEME["surface_alt"]};
        color: {THEME["black"]};
    }}
    .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        max-width: 1360px;
    }}
    .dashboard-hero {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-top: 3px solid {THEME["header_line"]};
        border-radius: 4px;
        padding: 0.75rem 1rem 0.6rem;
        color: {THEME["black"]};
        margin-bottom: 0.5rem;
    }}
    .dashboard-hero .eyebrow {{
        color: {THEME["dbs_red"]};
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
        font-weight: 700;
    }}
    .dashboard-hero h1 {{
        font-size: 1.5rem;
        line-height: 1.1;
        margin: 0;
        font-weight: 700;
    }}
    .dashboard-meta {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.5rem;
        margin-top: 0.6rem;
    }}
    .dashboard-meta-card {{
        border: 1px solid {THEME["border"]};
        border-left: 3px solid {THEME["dbs_red"]};
        background: {THEME["surface_alt"]};
        padding: 0.4rem 0.6rem;
        border-radius: 4px;
    }}
    .dashboard-meta-label {{
        color: {THEME["slate"]};
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.1rem;
        font-weight: 700;
    }}
    .dashboard-meta-value {{
        color: {THEME["black"]};
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.3rem;
        padding: 0 0 0.4rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 4px 4px 0 0;
        color: {THEME["charcoal"]};
        font-weight: 600;
        padding: 0.35rem 0.7rem 0.4rem;
        min-height: 0;
        font-size: 0.85rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: {THEME["dbs_red"]};
        color: #ffffff;
        border-color: {THEME["dbs_red"]};
    }}
    div[data-testid="stMetric"] {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-top: 3px solid {THEME["dbs_red"]};
        border-radius: 4px;
        padding: 0.5rem 0.7rem 0.4rem;
        min-height: 80px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {THEME["slate"]};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-size: 0.65rem;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.25rem;
        color: {THEME["black"]};
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.75rem;
    }}
    div[data-testid="stDataFrame"],
    div[data-testid="stPlotlyChart"],
    div[data-testid="stExpander"] {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 4px;
    }}
    div[data-testid="stExpander"] {{
        overflow: hidden;
    }}
    div[data-testid="stExpander"] details summary {{
        background: {THEME["surface"]};
        font-weight: 600;
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }}
    .stAlert {{
        border-radius: 4px;
        border: 1px solid {THEME["border"]};
        padding: 0.5rem 0.75rem;
    }}
    .alert-box {{
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        border-left: 4px solid;
        background: {THEME["surface"]};
    }}
    .brief-card {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-left: 3px solid {THEME["dbs_red"]};
        border-radius: 4px;
        padding: 0.6rem 0.8rem;
        min-height: 120px;
        margin-bottom: 0.5rem;
    }}
    .brief-card .label {{
        color: {THEME["slate"]};
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
        font-weight: 700;
    }}
    .brief-card h4 {{
        margin: 0 0 0.25rem;
        font-size: 0.9rem;
        line-height: 1.2;
    }}
    .brief-card p {{
        margin: 0;
        color: {THEME["charcoal"]};
        font-size: 0.82rem;
        line-height: 1.3;
    }}
    hr {{
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
    }}
    @media (max-width: 900px) {{
        .dashboard-meta {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def linear_forecast(years: list, values: list, n_ahead: int = 3):
    """
    Linear extrapolation. Returns (forecast_years, forecast_values).
    NaN values in 'values' are ignored when fitting.
    """
    arr  = np.array(list(zip(years, values)), dtype=float)
    mask = ~np.isnan(arr[:, 1])
    if mask.sum() < 2:
        return [], []
    x, y    = arr[mask, 0], arr[mask, 1]
    coeffs  = np.polyfit(x, y, 1)
    fx      = np.arange(int(x.max()) + 1, int(x.max()) + n_ahead + 1)
    fy      = np.polyval(coeffs, fx)
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
    return (
        f'<div class="alert-box {css.get(level, "alert-amber")}">'
        f"{text}</div>"
    )


def apply_chart_theme(fig, height=None):
    layout = dict(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=THEME["charcoal"]),
        title=dict(
            x=0.01,
            xanchor="left",
            font=dict(size=14, color=THEME["black"]),
        ),
        margin=dict(t=30, b=25, l=15, r=15),
        legend=dict(
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=THEME["border"],
            borderwidth=1,
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=THEME["border"],
            font=dict(color=THEME["charcoal"]),
        ),
    )
    if height is not None:
        layout["height"] = height

    fig.update_layout(**layout)
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=THEME["border"],
        showline=True,
        tickfont=dict(size=11),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=THEME["grid"],
        zeroline=False,
        linecolor=THEME["border"],
        showline=True,
        tickfont=dict(size=11),
    )
    return fig


def latest_numeric(df: pd.DataFrame, column: str):
    if df.empty or column not in df.columns:
        return np.nan
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return np.nan
    return float(series.iloc[-1])


def previous_numeric(df: pd.DataFrame, column: str):
    if df.empty or column not in df.columns:
        return np.nan
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if len(series) < 2:
        return np.nan
    return float(series.iloc[-2])


def bank_metric(df: pd.DataFrame, bank: str, column: str):
    if df.empty or "bank" not in df.columns or column not in df.columns:
        return np.nan
    match = df[df["bank"].astype(str).str.upper() == bank.upper()]
    if match.empty:
        return np.nan
    return pd.to_numeric(match.iloc[0][column], errors="coerce")


def one_year_return(hist: pd.DataFrame):
    if hist is None or hist.empty or "Close" not in hist.columns:
        return np.nan
    closes = pd.to_numeric(hist["Close"], errors="coerce").dropna()
    if len(closes) < 2:
        return np.nan
    start = closes.iloc[-252] if len(closes) > 252 else closes.iloc[0]
    end = closes.iloc[-1]
    if pd.isna(start) or start == 0 or pd.isna(end):
        return np.nan
    return float(end / start - 1)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3_600, show_spinner=False)
def load_stock_history() -> dict:
    """5-year daily price history for DBS, OCBC, UOB."""
    out = {}
    for name, ticker in TICKERS.items():
        try:
            df = yf.Ticker(ticker).history(period="5y")[["Close", "Volume"]]
            df.index = df.index.tz_localize(None)
            out[name] = df
        except Exception:
            out[name] = pd.DataFrame()
    return out


@st.cache_data(ttl=3_600, show_spinner=False)
def load_financials() -> dict:
    """Annual income statement + balance sheet + info for all three banks."""
    data = {}
    for name, ticker in TICKERS.items():
        try:
            t    = yf.Ticker(ticker)
            fin  = t.financials.T.copy()
            fin.index = pd.to_datetime(fin.index).year
            bs   = t.balance_sheet.T.copy()
            bs.index = pd.to_datetime(bs.index).year
            data[name] = {"income": fin, "balance": bs, "info": t.info}
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
    return pd.read_csv("data/glassdoor_sentiment.csv")


@st.cache_data(show_spinner=False)
def load_sgx() -> pd.DataFrame:
    return pd.read_csv("data/sgx_banking_metrics.csv")


# ─────────────────────────────────────────────────────────────────────────────
# LOAD ALL DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Loading data…"):
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
    f"""
    <div class="dashboard-hero">
        <div class="eyebrow">DBS Bank Internal Dashboard</div>
        <h1>Strategic and HR Analytics Dashboard</h1>
        <div class="dashboard-meta">
            <div class="dashboard-meta-card">
                <div class="dashboard-meta-label">Last Refresh</div>
                <div class="dashboard-meta-value">{datetime.today().strftime('%d %B %Y')}</div>
            </div>
            <div class="dashboard-meta-card">
                <div class="dashboard-meta-label">Financial Source</div>
                <div class="dashboard-meta-value">yfinance</div>
            </div>
            <div class="dashboard-meta-card">
                <div class="dashboard-meta-label">HR Source</div>
                <div class="dashboard-meta-value">DBS Sustainability Reports</div>
            </div>
            <div class="dashboard-meta-card">
                <div class="dashboard-meta-label">Workforce Source</div>
                <div class="dashboard-meta-value">MOM</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
# TAB 0 - EXECUTIVE DIAGNOSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    st.subheader("Executive Diagnosis")

    dbs_roe = bank_metric(sgx_df, "DBS", "roe_pct")
    peer_roe_avg = pd.to_numeric(sgx_df["roe_pct"], errors="coerce").mean() if not sgx_df.empty else np.nan
    dbs_nim = bank_metric(sgx_df, "DBS", "net_interest_margin_pct")
    peer_best_nim = pd.to_numeric(sgx_df["net_interest_margin_pct"], errors="coerce").max() if not sgx_df.empty else np.nan
    dbs_cost = bank_metric(sgx_df, "DBS", "cost_to_income_pct")
    best_cost = pd.to_numeric(sgx_df["cost_to_income_pct"], errors="coerce").min() if not sgx_df.empty else np.nan
    attr_latest = latest_numeric(hr_df, "voluntary_attrition_pct")
    engagement_latest = latest_numeric(hr_df, "engagement_score_pct")
    training_latest = latest_numeric(hr_df, "training_hrs_per_employee")
    sector_attr = MOM_RESIGNATION.get(2024, np.nan)
    recommend_latest = bank_metric(gd_df, "DBS", "recommend_pct")
    peer_recommend_avg = pd.to_numeric(gd_df["recommend_pct"], errors="coerce").mean() if not gd_df.empty else np.nan

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "ROE vs Peer Average",
        f"{dbs_roe:.1f}%" if pd.notna(dbs_roe) else "N/A",
        delta=f"{dbs_roe - peer_roe_avg:+.1f}pp" if pd.notna(dbs_roe) and pd.notna(peer_roe_avg) else None,
    )
    k2.metric(
        "NIM vs Best Peer",
        f"{dbs_nim:.2f}%" if pd.notna(dbs_nim) else "N/A",
        delta=f"{dbs_nim - peer_best_nim:+.2f}pp" if pd.notna(dbs_nim) and pd.notna(peer_best_nim) else None,
        delta_color="inverse",
    )
    k3.metric(
        "Attrition vs Sector",
        f"{attr_latest:.1f}%" if pd.notna(attr_latest) else "N/A",
        delta=f"{attr_latest - sector_attr:+.1f}pp" if pd.notna(attr_latest) and pd.notna(sector_attr) else None,
        delta_color="inverse",
    )
    k4.metric(
        "Employer Brand",
        f"{recommend_latest:.0f}%" if pd.notna(recommend_latest) else "N/A",
        delta=f"{recommend_latest - peer_recommend_avg:+.0f}pp" if pd.notna(recommend_latest) and pd.notna(peer_recommend_avg) else None,
    )


    issue_cols = st.columns(4)
    issue_cards = [
        (
            "Strategic Priority",
            "Protect margin resilience",
            (
                f"DBS NIM is {dbs_nim:.2f}% versus a peer best of {peer_best_nim:.2f}%."
                if pd.notna(dbs_nim) and pd.notna(peer_best_nim)
                else "Margin leadership should be monitored against peer pricing pressure."
            ),
        ),
        (
            "Operating Issue",
            "Close the efficiency gap",
            (
                f"Cost-to-income is {dbs_cost:.1f}% versus the best peer at {best_cost:.1f}%."
                if pd.notna(dbs_cost) and pd.notna(best_cost)
                else "Operating efficiency should be benchmarked against the peer frontier."
            ),
        ),
        (
            "HR Issue",
            "Sustain talent capability",
            (
                f"Training hours are {training_latest:.1f} per employee while engagement remains {engagement_latest:.0f}%."
                if pd.notna(training_latest) and pd.notna(engagement_latest)
                else "Capability development should be monitored alongside engagement and retention."
            ),
        ),
        (
            "People Risk",
            "Strengthen employee value proposition",
            (
                f"Glassdoor recommendation is {recommend_latest:.0f}% and work-life balance is {bank_metric(gd_df, 'DBS', 'work_life_balance'):.1f}/5."
                if pd.notna(recommend_latest) and pd.notna(bank_metric(gd_df, 'DBS', 'work_life_balance'))
                else "External employer-brand indicators should be tracked with retention outcomes."
            ),
        ),
    ]
    for col, (label, title, body) in zip(issue_cols, issue_cards):
        col.markdown(
            f"""
            <div class="brief-card">
                <div class="label">{label}</div>
                <h4>{title}</h4>
                <p>{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### Diagnosis Register")
        diagnosis_rows = [
            {
                "Issue": "Margin pressure as rates normalize",
                "Evidence": (
                    f"NIM {dbs_nim:.2f}% vs peer best {peer_best_nim:.2f}%"
                    if pd.notna(dbs_nim) and pd.notna(peer_best_nim)
                    else "NIM data pending"
                ),
                "Why it matters": "Lower margin momentum can weaken earnings quality and investor confidence.",
                "Decision supported": "Shift attention to fee income, pricing discipline, and mix management.",
                "Priority": "High" if pd.notna(dbs_nim) and pd.notna(peer_best_nim) and dbs_nim < peer_best_nim else "Medium",
            },
            {
                "Issue": "Efficiency gap versus best peer",
                "Evidence": (
                    f"Cost-to-income {dbs_cost:.1f}% vs best peer {best_cost:.1f}%"
                    if pd.notna(dbs_cost) and pd.notna(best_cost)
                    else "Efficiency benchmark pending"
                ),
                "Why it matters": "A persistent cost gap can reduce flexibility during revenue slowdown.",
                "Decision supported": "Prioritize process redesign and productivity initiatives.",
                "Priority": "High" if pd.notna(dbs_cost) and pd.notna(best_cost) and dbs_cost - best_cost > 1 else "Medium",
            },
            {
                "Issue": "Capability sustainability",
                "Evidence": (
                    f"Training at {training_latest:.1f} hours with engagement at {engagement_latest:.0f}%"
                    if pd.notna(training_latest) and pd.notna(engagement_latest)
                    else "Capability signal pending"
                ),
                "Why it matters": "DBS depends on digital and AI capability to defend strategic advantage.",
                "Decision supported": "Protect role-critical learning investment and succession depth.",
                "Priority": "Medium",
            },
            {
                "Issue": "External employer brand risk",
                "Evidence": (
                    f"Recommend {recommend_latest:.0f}% and work-life balance {bank_metric(gd_df, 'DBS', 'work_life_balance'):.1f}/5"
                    if pd.notna(recommend_latest) and pd.notna(bank_metric(gd_df, 'DBS', 'work_life_balance'))
                    else "Glassdoor signal pending"
                ),
                "Why it matters": "Employer brand influences attraction, retention, and replacement cost.",
                "Decision supported": "Target EVP improvements in manager quality, workload, and career clarity.",
                "Priority": "Medium",
            },
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

        stock_returns = {bank: one_year_return(hist) for bank, hist in stock_hist.items()}
        dbs_return = stock_returns.get("DBS", np.nan)
        best_peer_return = np.nanmax([v for v in stock_returns.values() if pd.notna(v)]) if any(pd.notna(v) for v in stock_returns.values()) else np.nan
        if pd.notna(dbs_return) and pd.notna(best_peer_return):
            if dbs_return < best_peer_return - 0.05:
                exec_alerts.append(alert_html("amber", "Market Signal: DBS share-price momentum trails the strongest local peer over the last year."))

        for alert in exec_alerts:
            st.markdown(alert, unsafe_allow_html=True)


    st.markdown("#### Predictive Watchlist")
    watch_rows = []

    if not dbs_inc.empty:
        rev_col = next((c for c in dbs_inc.columns if "Total Revenue" in str(c) or "revenue" in str(c).lower()), None)
        ni_col = next((c for c in dbs_inc.columns if "Net Income" in str(c) or "net income" in str(c).lower()), None)
        years = sorted(dbs_inc.index.tolist())
        if rev_col is not None:
            rev_vals = []
            for y in years:
                try:
                    rev_vals.append(float(dbs_inc.loc[y, rev_col]) / 1e9)
                except Exception:
                    rev_vals.append(np.nan)
            fy, fv = linear_forecast(years, rev_vals, 3)
            if fy:
                delta = fv[-1] - rev_vals[-1]
                watch_rows.append({
                    "Metric": "Revenue",
                    "Latest": fmt_billions(rev_vals[-1]),
                    "3Y Outlook": fmt_billions(fv[-1]),
                    "Direction": "Improving" if delta > 0.2 else "Stable" if abs(delta) <= 0.2 else "Weakening",
                    "Management use": "Track earnings resilience against rate normalization.",
                })
        if ni_col is not None:
            ni_vals = []
            for y in years:
                try:
                    ni_vals.append(float(dbs_inc.loc[y, ni_col]) / 1e9)
                except Exception:
                    ni_vals.append(np.nan)
            fy, fv = linear_forecast(years, ni_vals, 3)
            if fy:
                delta = fv[-1] - ni_vals[-1]
                watch_rows.append({
                    "Metric": "Net income",
                    "Latest": fmt_billions(ni_vals[-1]),
                    "3Y Outlook": fmt_billions(fv[-1]),
                    "Direction": "Improving" if delta > 0.2 else "Stable" if abs(delta) <= 0.2 else "Weakening",
                    "Management use": "Assess whether current strategy protects profit quality.",
                })

    hr_watch_specs = [
        ("Headcount", "headcount", "higher", 500, lambda v: f"{int(v):,}" if pd.notna(v) else "N/A", "Support workforce capacity planning."),
        ("Voluntary attrition", "voluntary_attrition_pct", "lower", 0.3, lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A", "Flag retention pressure before it hits cost and service continuity."),
        ("Engagement", "engagement_score_pct", "higher", 0.5, lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A", "Check whether culture strength is being sustained."),
    ]
    for label, col_name, better_when, stable_band, formatter, rationale in hr_watch_specs:
        subset = hr_df.dropna(subset=[col_name])
        if subset.empty:
            continue
        vals = subset[col_name].astype(float).tolist()
        yrs = subset["year"].astype(int).tolist()
        fy, fv = linear_forecast(yrs, vals, 3)
        if not fy:
            continue
        delta = fv[-1] - vals[-1]
        if abs(delta) <= stable_band:
            direction = "Stable"
        elif better_when == "higher":
            direction = "Improving" if delta > 0 else "Weakening"
        else:
            direction = "Improving" if delta < 0 else "Weakening"
        watch_rows.append({
            "Metric": label,
            "Latest": formatter(vals[-1]),
            "3Y Outlook": formatter(fv[-1]),
            "Direction": direction,
            "Management use": rationale,
        })

    if watch_rows:
        st.dataframe(pd.DataFrame(watch_rows), width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 - STRATEGIC OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Strategic Overview")

    # ── Top KPIs ─────────────────────────────────────────────────────────────
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


    # ── Competitor snapshot ───────────────────────────────────────────────────
    st.markdown("#### Competitor Snapshot - FY2024")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        if not sgx_df.empty:
            disp = sgx_df.copy()
            disp.columns = [c.replace("_", " ").title() for c in disp.columns]
            st.dataframe(disp.set_index("Bank"), width='stretch')

    with col_r:
        if not sgx_df.empty:
            fig = px.bar(
                sgx_df, x="bank", y="roe_pct",
                color="bank", color_discrete_map=COLORS,
                title="ROE (%) - FY2024",
                labels={"roe_pct": "ROE (%)", "bank": ""},
                text="roe_pct",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(showlegend=False, margin=dict(t=40, b=20))
            apply_chart_theme(fig, height=280)
            st.plotly_chart(fig, width='stretch')



    # ── Porter's Five Forces ──────────────────────────────────────────────────
    st.markdown("#### Porter's Five Forces - Singapore Banking")

    forces_data = {
        "Force": [
            "Supplier Power",
            "Buyer Power",
            "Substitution Threat",
            "New Entrants",
            "Competitive Rivalry"
        ],
        "Intensity": [2, 3, 5, 1, 5],
        "Label": ["Low-Medium", "Medium-High", "High", "Low", "High"]
    }
    df_forces = pd.DataFrame(forces_data)

    fig_forces = px.bar(
        df_forces,
        x="Intensity",
        y="Force",
        orientation="h",
        text="Label",
        title="Competitive Forces Intensity",
        color_discrete_sequence=[THEME["dbs_red"]]
    )
    fig_forces.update_layout(
        xaxis=dict(range=[0, 5.5], tickvals=[1, 2, 3, 4, 5]),
        yaxis=dict(autorange="reversed"),
        showlegend=False
    )
    fig_forces.update_traces(textposition="outside")
    apply_chart_theme(fig_forces, height=320)
    st.plotly_chart(fig_forces, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 - FINANCIAL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Financial Performance")

    # ── Relative stock performance ────────────────────────────────────────────
    st.markdown("#### Relative Stock Price Performance - 5 Years (Indexed to 100)")

    fig_px = go.Figure()
    for bank, hist in stock_hist.items():
        if hist.empty:
            continue
        idx = (hist["Close"] / hist["Close"].iloc[0]) * 100
        fig_px.add_trace(go.Scatter(
            x=idx.index, y=idx.values,
            name=bank, line=dict(color=COLORS[bank], width=2),
        ))
    fig_px.add_hline(y=100, line_dash="dash", line_color=THEME["border"], opacity=0.9)
    fig_px.update_layout(
        yaxis_title="Indexed Price (Base = 100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    apply_chart_theme(fig_px, height=380)
    st.plotly_chart(fig_px, width='stretch')


    # ── Revenue & Net Income ──────────────────────────────────────────────────
    st.markdown("#### DBS Annual Revenue & Net Income - with 3-Year Linear Forecast")

    if not dbs_inc.empty:
        rev_col = next(
            (c for c in dbs_inc.columns
             if "Total Revenue" in str(c) or "revenue" in str(c).lower()),
            None,
        )
        ni_col = next(
            (c for c in dbs_inc.columns
             if "Net Income" in str(c) or "net income" in str(c).lower()),
            None,
        )
        years = sorted(dbs_inc.index.tolist())

        fig_fin = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Total Revenue (SGD B)", "Net Income (SGD B)"),
        )

        for col_name, col_idx in [(rev_col, 1), (ni_col, 2)]:
            if col_name is None:
                continue
            vals = []
            for y in years:
                try:
                    v = dbs_inc.loc[y, col_name]
                    vals.append(float(v) / 1e9 if pd.notna(v) else np.nan)
                except Exception:
                    vals.append(np.nan)

            label = "Revenue" if col_idx == 1 else "Net Income"
            fig_fin.add_trace(go.Scatter(
                x=years, y=vals, name=f"{label} Actual",
                line=dict(color=COLORS["DBS"], width=2),
                mode="lines+markers",
            ), row=1, col=col_idx)

            fy, fv = linear_forecast(years, vals, 3)
            if fy:
                fig_fin.add_trace(go.Scatter(
                    x=[years[-1]] + fy, y=[vals[-1]] + fv,
                    name=f"{label} Forecast",
                    line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
                    mode="lines+markers", marker=dict(symbol="circle-open"),
                ), row=1, col=col_idx)

        fig_fin.update_layout(legend=dict(orientation="h", y=-0.15))
        apply_chart_theme(fig_fin, height=400)
        st.plotly_chart(fig_fin, width='stretch')


    # ── Banking KPIs ──────────────────────────────────────────────────────────
    st.markdown("#### Key Banking Ratios - DBS vs OCBC vs UOB (FY2024)")

    if not sgx_df.empty:
        kpis = [
            ("npl_ratio_pct",          "NPL Ratio (%)",            "↓ lower is better"),
            ("cet1_ratio_pct",         "CET1 Capital Ratio (%)",   "↑ higher is better"),
            ("roe_pct",                "Return on Equity (%)",     "↑ higher is better"),
            ("cost_to_income_pct",     "Cost-to-Income (%)",       "↓ lower is better"),
            ("net_interest_margin_pct","Net Interest Margin (%)",  "↑ higher is better"),
        ]
        kcols = st.columns(5)
        for kcol, (metric, label, direction) in zip(kcols, kpis):
            fig = px.bar(
                sgx_df, x="bank", y=metric,
                color="bank", color_discrete_map=COLORS,
                title=f"<b>{label}</b><br><sup>{direction}</sup>",
                text=metric,
            )
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(
                showlegend=False,
                margin=dict(t=70, b=10, l=10, r=10),
                xaxis_title="", yaxis_title="",
            )
            apply_chart_theme(fig, height=300)
            kcol.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 - HR ANALYTICS (LAMP)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("HR Analytics - LAMP Framework")

    if hr_df.empty:
        st.error("Could not load data/dbs_hr_metrics.csv.")
        st.stop()

    hr = hr_df.copy()

    # ── Headcount ─────────────────────────────────────────────────────────────
    st.markdown("### Workforce Size and Growth")
    col_l, col_r = st.columns(2)

    with col_l:
        hc   = hr.dropna(subset=["headcount"])
        yrs  = hc["year"].tolist()
        vals = hc["headcount"].tolist()
        fy, fv = linear_forecast(yrs, vals, 3)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yrs, y=vals, name="Actual",
            line=dict(color=COLORS["DBS"], width=2.5),
            mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(200,16,46,0.07)",
        ))
        if fy:
            fig.add_trace(go.Scatter(
                x=[yrs[-1]] + fy, y=[vals[-1]] + fv,
                name="Forecast",
                line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
                mode="lines+markers", marker=dict(symbol="circle-open"),
            ))
        fig.update_layout(
            title="Total Headcount (2020-2025 + Forecast)",
            yaxis_title="Employees",
        )
        apply_chart_theme(fig, height=340)
        st.plotly_chart(fig, width='stretch')

    with col_r:
        hc2 = hc.set_index("year").copy()
        hc2["growth_pct"] = hc2["headcount"].pct_change() * 100
        hc2 = hc2.dropna(subset=["growth_pct"]).reset_index()

        fig2 = px.bar(
            hc2, x="year", y="growth_pct",
            title="Headcount YoY Growth (%)",
            color_discrete_sequence=[COLORS["DBS"]],
            text="growth_pct",
        )
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(showlegend=False, yaxis_title="Growth (%)")
        apply_chart_theme(fig2, height=340)
        st.plotly_chart(fig2, width='stretch')

    # ── Attrition ─────────────────────────────────────────────────────────────
    st.markdown("### Voluntary Attrition")

    att   = hr.dropna(subset=["voluntary_attrition_pct"])
    ayrs  = att["year"].tolist()
    avals = att["voluntary_attrition_pct"].tolist()
    fy_a, fv_a = linear_forecast(ayrs, avals, 3)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ayrs, y=avals, name="Actual",
        line=dict(color=COLORS["DBS"], width=2.5),
        mode="lines+markers",
        fill="tozeroy", fillcolor="rgba(200,16,46,0.08)",
    ))
    if fy_a:
        fig.add_trace(go.Scatter(
            x=[ayrs[-1]] + fy_a, y=[avals[-1]] + fv_a,
            name="Forecast",
            line=dict(color=COLORS["DBS"], dash="dash", width=1.5),
            mode="lines+markers", marker=dict(symbol="circle-open"),
        ))
    fig.add_hline(y=10, line_dash="dot", line_color=THEME["charcoal"],
                  annotation_text="10% alert threshold")
    fig.update_layout(
        title="Voluntary Attrition Rate (%) + Forecast",
        yaxis_title="Attrition Rate (%)",
    )
    apply_chart_theme(fig, height=340)
    st.plotly_chart(fig, width='stretch')

    latest_att = att["voluntary_attrition_pct"].iloc[-1]
    prev_att   = att["voluntary_attrition_pct"].iloc[-2]
    st.metric(
        "Latest Voluntary Attrition",
        f"{latest_att}%",
        delta=f"{latest_att - prev_att:+.1f}pp vs prior year",
        delta_color="inverse",
    )

    # ── Training ──────────────────────────────────────────────────────────────
    st.markdown("### Training and Development")

    tr = hr.dropna(subset=["training_hrs_per_employee"])
    fig = px.bar(
        tr, x="year", y="training_hrs_per_employee",
        title="Avg Training Hours per Employee",
        color_discrete_sequence=[COLORS["DBS"]],
        text="training_hrs_per_employee",
    )
    fig.update_traces(texttemplate="%{text:.1f}h", textposition="outside")
    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, 50], yaxis_title="Hours",
    )
    apply_chart_theme(fig, height=320)
    st.plotly_chart(fig, width='stretch')

    # ── Engagement ────────────────────────────────────────────────────────────
    st.markdown("### Employee Engagement")

    eng   = hr.dropna(subset=["engagement_score_pct"])
    eyrs  = eng["year"].tolist()
    evals = eng["engagement_score_pct"].tolist()
    fy_e, fv_e = linear_forecast(eyrs, evals, 3)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eyrs, y=evals, name="Engagement Score",
        line=dict(color=COLORS["DBS"], width=2.5),
        mode="lines+markers",
    ))
    if fy_e:
        fig.add_trace(go.Scatter(
            x=[eyrs[-1]] + fy_e, y=[evals[-1]] + fv_e,
            name="Forecast",
            line=dict(color=THEME["charcoal"], dash="dash", width=1.5),
            mode="lines+markers", marker=dict(symbol="circle-open"),
        ))
    fig.add_hline(y=74, line_dash="dot", line_color=THEME["slate"],
                  annotation_text="APAC FS Industry Benchmark (74%)")
    fig.add_hline(y=85, line_dash="dot", line_color=THEME["dbs_red_dark"],
                  annotation_text="APAC Best Employers Benchmark (85%)")
    fig.update_layout(
        title="Employee Engagement Score (%) - My Voice Survey + Forecast",
        yaxis_title="Engagement (%)", yaxis_range=[65, 100],
    )
    apply_chart_theme(fig, height=360)
    st.plotly_chart(fig, width='stretch')

    # ── Gender Diversity ──────────────────────────────────────────────────────
    st.markdown("### Gender Diversity")
    col_l, col_r = st.columns(2)

    with col_l:
        wf = hr.dropna(subset=["female_workforce_pct"])
        fig = px.line(
            wf, x="year", y="female_workforce_pct",
            title="Female Workforce Representation (%)",
            markers=True, color_discrete_sequence=[COLORS["DBS"]],
        )
        fig.add_hline(y=50, line_dash="dash", line_color=THEME["slate"],
                      annotation_text="Gender Parity (50%)")
        fig.update_layout(yaxis_range=[40, 60], yaxis_title="%")
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, width='stretch')

    with col_r:
        sm = hr.dropna(subset=["female_senior_mgmt_pct"])
        fig = px.bar(
            sm, x="year", y="female_senior_mgmt_pct",
            title="Female in Senior Management - SVP to MD (%)",
            color_discrete_sequence=[THEME["charcoal"]],
            text="female_senior_mgmt_pct",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(
            showlegend=False,
            yaxis_range=[0, 60], yaxis_title="%",
        )
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, width='stretch')

    # ── LAMP Alerts ───────────────────────────────────────────────────────────
    st.markdown("### LAMP Process - Automated Decision Alerts")

    latest_hr = hr.sort_values("year").iloc[-1]
    att_val   = latest_hr.get("voluntary_attrition_pct")
    eng_val   = latest_hr.get("engagement_score_pct")
    tr_val    = latest_hr.get("training_hrs_per_employee")

    alerts = []
    if pd.notna(att_val):
        if att_val > 10:
            alerts.append(alert_html("red",
                f"Attrition Alert: {att_val}% exceeds 10% threshold. "
                "review retention strategy and compensation benchmarking immediately."))
        else:
            alerts.append(alert_html("green",
                f"Attrition Healthy: {att_val}% is within the 10% target. "
                "retention initiatives are effective."))

    if pd.notna(eng_val):
        if eng_val >= 85:
            alerts.append(alert_html("green",
                f"Engagement Excellent: {eng_val}% exceeds APAC Best Employers benchmark (85%)."))
        elif eng_val >= 74:
            alerts.append(alert_html("amber",
                f"Engagement Moderate: {eng_val}% exceeds APAC FS benchmark (74%) "
                "but below Best Employers threshold (85%)."))
        else:
            alerts.append(alert_html("red",
                f"Engagement Critical: {eng_val}% is below APAC FS industry benchmark. "
                "immediate cultural intervention required."))

    if pd.notna(tr_val):
        if tr_val < 30:
            alerts.append(alert_html("amber",
                f"Training Below Target: {tr_val}h/employee is below 30h threshold."))
        else:
            alerts.append(alert_html("green",
                f"Training On Track: {tr_val}h/employee meets the 30h target."))

    for h in alerts:
        st.markdown(h, unsafe_allow_html=True)


    # ── Attrition Cost Model ──────────────────────────────────────────────────
    st.markdown("#### HR-Finance Linkage: Attrition Cost Estimator")

    col_l, col_r = st.columns(2)

    with col_l:
        latest_att_val = float(
            hr_df.dropna(subset=["voluntary_attrition_pct"])
            ["voluntary_attrition_pct"].iloc[-1]
        )
        attrition_rate = st.slider(
            "Voluntary Attrition Rate (%)",
            min_value=1.0, max_value=20.0,
            value=latest_att_val, step=0.1,
            key="att_slider"
        )
        avg_salary = st.slider(
            "Average Annual Salary (SGD)",
            min_value=50_000, max_value=200_000,
            value=90_000, step=5_000, format="SGD %d",
            key="sal_slider"
        )
        replacement_mult = st.slider(
            "Replacement Cost (% of annual salary)",
            min_value=50, max_value=200,
            value=100, step=10, format="%d%%",
            key="repl_slider"
        )

    with col_r:
        headcount_val = int(
            hr_df.dropna(subset=["headcount"])["headcount"].iloc[-1]
        )
        leavers    = int(headcount_val * attrition_rate / 100)
        cost_per   = avg_salary * replacement_mult / 100
        total_cost = leavers * cost_per

        peak_att   = hr_df["voluntary_attrition_pct"].max()
        peak_cost  = int(headcount_val * peak_att / 100) * cost_per
        saving     = peak_cost - total_cost

        st.metric("Estimated Annual Leavers",      f"{leavers:,}")
        st.metric("Replacement Cost per Leaver",   f"SGD {cost_per:,.0f}")
        st.metric("Total Estimated Attrition Cost",f"SGD {total_cost / 1e6:.1f}M")
        st.metric(
            f"Saving vs Peak Attrition ({peak_att}%)",
            f"SGD {saving / 1e6:.1f}M",
            delta="reduction in attrition cost",
            delta_color="normal",
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 - WORKFORCE BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Workforce Benchmarking")

    # ── Glassdoor Radar ───────────────────────────────────────────────────────
    st.markdown("#### Employer Brand - Glassdoor Ratings (DBS vs OCBC vs UOB)")

    GD_CATS   = ["overall_rating", "work_life_balance", "culture_values",
                 "compensation_benefits", "career_opportunities", "senior_mngmnt"]
    GD_LABELS = ["Overall", "Work-Life Balance", "Culture & Values",
                 "Compensation", "Career Opps", "Senior Mgmt"]

    col_l, col_r = st.columns([3, 2])

    with col_l:
        if not gd_df.empty:
            fig = go.Figure()
            for _, row in gd_df.iterrows():
                bank = row["bank"]
                vals = [row[c] for c in GD_CATS] + [row[GD_CATS[0]]]
                lbls = GD_LABELS + [GD_LABELS[0]]
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=lbls, fill="toself",
                    name=bank, line=dict(color=COLORS.get(bank, "grey")),
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 5], tickvals=[1, 2, 3, 4, 5])),
                title="Glassdoor Ratings (out of 5.0)",
                height=440,
                paper_bgcolor="white",
                font=dict(color=THEME["charcoal"]),
            )
            st.plotly_chart(fig, width='stretch')

    with col_r:
        if not gd_df.empty:
            st.markdown("**Would Recommend to a Friend (%)**")
            fig = px.bar(
                gd_df, x="bank", y="recommend_pct",
                color="bank", color_discrete_map=COLORS, text="recommend_pct",
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(
                showlegend=False,
                yaxis_range=[0, 100], yaxis_title="%",
            )
            apply_chart_theme(fig, height=230)
            st.plotly_chart(fig, width='stretch')

            st.markdown("**Ratings Summary**")
            disp = gd_df.set_index("bank").copy()
            disp.columns = [c.replace("_", " ").title() for c in disp.columns]
            st.dataframe(disp, width='stretch')


    # ── Category-level bar comparison ─────────────────────────────────────────
    st.markdown("#### Glassdoor Sub-Ratings Breakdown")

    if not gd_df.empty:
        gd_long = gd_df.melt(
            id_vars="bank", value_vars=GD_CATS,
            var_name="Category", value_name="Score",
        )
        gd_long["Category"] = gd_long["Category"].map(dict(zip(GD_CATS, GD_LABELS)))
        fig = px.bar(
            gd_long, x="Category", y="Score",
            color="bank", barmode="group",
            color_discrete_map=COLORS,
            title="Glassdoor Sub-Ratings - All Banks",
            text="Score",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(
            yaxis_range=[0, 5.5],
            legend=dict(orientation="h", y=1.1),
        )
        apply_chart_theme(fig, height=400)
        st.plotly_chart(fig, width='stretch')


    # ── Attrition vs MOM ──────────────────────────────────────────────────────
    st.markdown("#### DBS Attrition vs Singapore Financial Sector (MOM)")

    att_data = hr_df.dropna(subset=["voluntary_attrition_pct"])[
        ["year", "voluntary_attrition_pct"]
    ].copy()
    mom_data = pd.DataFrame(
        list(MOM_RESIGNATION.items()), columns=["year", "mom_resignation_rate"]
    )
    merged = pd.merge(att_data, mom_data, on="year", how="inner")

    if not merged.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["year"], y=merged["voluntary_attrition_pct"],
            name="DBS Voluntary Attrition",
            line=dict(color=COLORS["DBS"], width=2.5),
            mode="lines+markers",
        ))
        fig.add_trace(go.Scatter(
            x=merged["year"], y=merged["mom_resignation_rate"],
            name="MOM - Financial & Insurance Sector Avg",
            line=dict(color=THEME["charcoal"], width=2, dash="dash"),
            mode="lines+markers",
        ))
        fig.update_layout(
            title="Voluntary Attrition: DBS vs Singapore Financial Sector (%)",
            yaxis_title="Rate (%)",
            legend=dict(orientation="h", y=1.08),
        )
        apply_chart_theme(fig, height=380)
        st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 - MACROECONOMIC CONTEXT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Macroeconomic Context")

    # ── NIM strategic insight ─────────────────────────────────────────────────
    st.markdown("#### Strategic Insight: Interest Rate Impact on NIM")

    if not sgx_df.empty:
        fig_nim = px.bar(
            sgx_df, x="bank", y="net_interest_margin_pct",
            color="bank", color_discrete_map=COLORS,
            title="Net Interest Margin Comparison - FY2024",
            labels={"net_interest_margin_pct": "NIM (%)", "bank": ""},
            text="net_interest_margin_pct",
            barmode="group"
        )
        fig_nim.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        apply_chart_theme(fig_nim, height=320)
        st.plotly_chart(fig_nim, width='stretch')

        st.divider()

        fig_cost = px.bar(
            sgx_df, x="bank", y="cost_to_income_pct",
            color="bank", color_discrete_map=COLORS,
            title="Cost-to-Income Ratio - FY2024",
            labels={"cost_to_income_pct": "Cost-to-Income (%)", "bank": ""},
            text="cost_to_income_pct",
            barmode="group"
        )
        fig_cost.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        apply_chart_theme(fig_cost, height=320)
        st.plotly_chart(fig_cost, width='stretch')

        st.divider()

        fig_npl = px.bar(
            sgx_df, x="bank", y="npl_ratio_pct",
            color="bank", color_discrete_map=COLORS,
            title="Non-Performing Loan Ratio - FY2024",
            labels={"npl_ratio_pct": "NPL Ratio (%)", "bank": ""},
            text="npl_ratio_pct",
            barmode="group"
        )
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

# --- Dashboard Header ---
# Integrated performance view across strategy, finance, workforce, and macro context.

# --- Tab 0: Executive Diagnosis ---
# This page translates the brief into a management view: what is happening, why it matters, and which signals require action.
# Forecast watchlist uses simple linear trend projections. It is intended as an early-warning tool, not as a formal forecast model.

# --- Tab 2: Financial Performance ---
# Annual income statement data could not be retrieved from yfinance for D05.SI. Yahoo Finance sometimes rate-limits Singapore tickers. Try refreshing.

# --- Tab 3: HR Analytics ---
# **LAMP Framework (Boudreau & Ramstad, 2007):** Analytics are structured across four dimensions: **L**ogic (strategic rationale), **A**nalytics (data insights), **M**easures (KPIs tracked), and **P**rocess (decisions enabled). Forecast series show a 3-year linear projection.
# **LAMP Logic: Why Attrition Matters**
# Voluntary attrition in financial services carries compounding costs:
# - Direct cost: Recruitment, onboarding, and ramp-up estimated at 50-200% of annual salary per leaver (Boushey & Glynn, 2012)
# - Revenue leakage: Relationship Manager turnover disrupts client continuity and delays loan origination
# - Strategic drag: High attrition in tech and data roles slows DBS's AI/ML transformation roadmap
# - Employer brand: Elevated attrition depresses Glassdoor ratings and future talent acquisition costs
# DBS attrition peaked at 14.7% in 2022 during the post-pandemic talent war, declining to 7.4% in 2025 and now below the Singapore Financial sector average.
# **LAMP Analytics: Training ROI**
# DBS's training investment correlates with digital transformation outcomes:
# | Year | Training Hrs | AI/ML Models | Economic Value |
# |------|-------------|-------------|----------------|
# | 2020 | 38.9h       | N/A         | N/A            |
# | 2021 | 39.2h       | N/A         | N/A            |
# | 2024 | 33.4h       | 1,500+      | SGD 750M       |
# The decline in training hours (2022-2024) reflects a shift from broad-based digital upskilling toward targeted AI/GenAI specialisation. DBS's iGrow AI career coach (2022) personalises learning paths, improving quality per hour.
# **LAMP Process:** Training hours below 30h/employee trigger a review of L&D budget allocation and programme relevance.
# This model quantifies the financial cost of voluntary attrition, directly linking HR performance to the income statement.

# --- Tab 4: Workforce Benchmarking ---
# MOM data: average annual resignation rate for Financial & Insurance Services. Source: Ministry of Manpower, Labour Turnover Statistics.

# --- Tab 5: Macroeconomic Context ---
# Net Interest Margin (NIM) is the primary driver of banking profitability.
# As interest rates rose sharply in 2022-2023, banks expanded NIM by repricing loans faster than deposits. Rate normalisation in 2024-2025 reverses this benefit.
# | Bank | NIM 2024 | Strategic Response |
# |------|----------|--------------------|
# | DBS  | 2.13%    | Offset via wealth management fee income |
# | OCBC | 2.20%    | Benefits from Great Eastern integration |
# | UOB  | 2.03%    | ASEAN regional diversification buffers compression |
# **DBS's strategic priority:** Grow non-interest income (wealth management, treasury, digital services) to compensate for NIM compression. NOII reached a record SGD 6.33 billion in 2024 (+22% YoY).




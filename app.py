import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm as stats_norm

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(layout="wide", page_title="Smart Investing EC | Portfolio Terminal")

# --------------------------------------------------
# STYLE
# --------------------------------------------------

st.markdown("""
<style>
.stApp{
    background-color:#0E1117;
    color:white;
}

h1,h2,h3{
    color:#B388FF;
}

.small-note {
    font-size: 0.72rem;
    color: #A8A8A8;
    margin-top: -10px;
    margin-bottom: 12px;
    line-height: 1.25;
}

.brand-wrap{
    display:flex;
    align-items:center;
    gap:16px;
    padding:14px 18px;
    border-radius:18px;
    margin-bottom:18px;
    background: linear-gradient(135deg, rgba(123,44,191,0.18) 0%, rgba(43,45,66,0.88) 100%);
    border: 1px solid rgba(179,136,255,0.18);
    box-shadow: 0 10px 24px rgba(0,0,0,0.28);
}

.brand-title{
    font-size: 2rem;
    font-weight: 700;
    color: #F5F0FF;
    line-height: 1.1;
}

.brand-subtitle{
    font-size: 0.95rem;
    color: #CFC6E8;
    margin-top: 3px;
}

.exec-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 16px;
    overflow: hidden;
    border-radius: 14px;
    border: 1px solid rgba(179,136,255,0.18);
    background: linear-gradient(180deg, rgba(32,35,48,0.95) 0%, rgba(18,20,31,0.98) 100%);
}

.exec-table thead th {
    background: linear-gradient(90deg, rgba(123,44,191,0.35) 0%, rgba(74,78,105,0.45) 100%);
    color: #F3EEFF;
    padding: 12px 14px;
    font-size: 0.92rem;
    text-align: left;
    border-bottom: 1px solid rgba(179,136,255,0.20);
}

.exec-table tbody td {
    padding: 11px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    color: #EAEAEA;
    font-size: 0.92rem;
}

.exec-table tbody tr:hover {
    background-color: rgba(157,78,221,0.08);
}

.metric-card {
    background: linear-gradient(135deg, rgba(123,44,191,0.28) 0%, rgba(74,78,105,0.42) 100%);
    border: 1px solid rgba(179,136,255,0.20);
    border-radius: 16px;
    padding: 18px 16px;
    min-height: 112px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.28);
    margin-bottom: 10px;
}

.metric-title {
    font-size: 0.86rem;
    color: #CFC6E8;
    margin-bottom: 8px;
    line-height: 1.2;
}

.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.1;
}

.section-subtitle {
    color: #D9CCFF;
    font-size: 1rem;
    margin-top: 2px;
    margin-bottom: 8px;
}

.bl-box {
    background: linear-gradient(180deg, rgba(40,44,62,0.95) 0%, rgba(21,23,35,0.98) 100%);
    border: 1px solid rgba(179,136,255,0.18);
    border-radius: 16px;
    padding: 16px 18px;
    margin-top: 6px;
    margin-bottom: 14px;
    color: #E7E2F2;
    line-height: 1.45;
    font-size: 0.92rem;
}

.bl-box strong {
    color: #FFFFFF;
}

[data-testid="stDataEditor"] {
    border: 1px solid rgba(179,136,255,0.18);
    border-radius: 14px;
    overflow: hidden;
    background: linear-gradient(180deg, rgba(32,35,48,0.95) 0%, rgba(18,20,31,0.98) 100%);
}

[data-testid="stDataEditor"] [role="grid"] {
    background: transparent;
}

[data-testid="stDataEditor"] [role="columnheader"] {
    background: linear-gradient(90deg, rgba(123,44,191,0.35) 0%, rgba(74,78,105,0.45) 100%) !important;
    color: #F3EEFF !important;
    font-weight: 600;
}

[data-testid="stDataEditor"] [role="gridcell"] {
    background: transparent !important;
    color: #EAEAEA !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# BRAND HEADER + LOGO
# --------------------------------------------------

st.markdown("""
<div class="brand-wrap">
    <svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#7B2CBF"/>
                <stop offset="60%" stop-color="#9D4EDD"/>
                <stop offset="100%" stop-color="#4A4E69"/>
            </linearGradient>
        </defs>
        <rect x="4" y="4" width="64" height="64" rx="18" fill="url(#g1)" stroke="#CFC6E8" stroke-width="1.2"/>
        <path d="M18 45 L28 35 L36 40 L50 24" fill="none" stroke="#F8F7FF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M46 24 H54 V32" fill="none" stroke="#F8F7FF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="17" y="49" width="8" height="8" rx="2" fill="#F8F7FF" opacity="0.95"/>
        <rect x="29" y="45" width="8" height="12" rx="2" fill="#F8F7FF" opacity="0.88"/>
        <rect x="41" y="39" width="8" height="18" rx="2" fill="#F8F7FF" opacity="0.80"/>
    </svg>
    <div>
        <div class="brand-title">Smart Investing EC</div>
        <div class="brand-subtitle">Institutional Portfolio Intelligence Terminal</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# COLOR PALETTE
# --------------------------------------------------

palette = [
    "#7B2CBF",
    "#9D4EDD",
    "#C9ADA7",
    "#4A4E69",
    "#6D597A",
    "#8D99AE",
    "#2B2D42",
    "#B8B8FF",
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_color_map(labels):
    return {label: palette[i % len(palette)] for i, label in enumerate(labels)}

def render_executive_table(df, title=None):
    if title:
        st.markdown(f'<div class="section-subtitle">{title}</div>', unsafe_allow_html=True)

    header_html = "".join([f"<th>{col}</th>" for col in df.columns])
    body_rows = []

    for _, row in df.iterrows():
        row_html = "".join([f"<td>{row[col]}</td>" for col in df.columns])
        body_rows.append(f"<tr>{row_html}</tr>")

    table_html = f"""
    <table class="exec-table">
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {''.join(body_rows)}
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

def render_metric_cards(metrics_df, columns_per_row=3):
    rows = [metrics_df.iloc[i:i + columns_per_row] for i in range(0, len(metrics_df), columns_per_row)]
    for row_df in rows:
        cols = st.columns(columns_per_row)
        for idx, (_, metric_row) in enumerate(row_df.iterrows()):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">{metric_row['Metric']}</div>
                        <div class="metric-value">{metric_row['Value']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def annualized_return(series):
    return series.mean() * 252

def annualized_vol(series):
    return series.std(ddof=1) * np.sqrt(252)

def portfolio_performance(weights, mu, cov, rf):
    weights = np.array(weights)
    ret = float(np.dot(mu, weights))
    vol = float(np.sqrt(np.dot(weights.T, np.dot(cov, weights))))
    sharpe = float((ret - rf) / vol) if vol != 0 else -np.inf
    return ret, vol, sharpe

def solve_max_sharpe(mu, cov, rf, min_weights, max_weights):
    n = len(mu)
    bounds = tuple((min_weights[i], max_weights[i]) for i in range(n))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)

    remaining = 1 - sum(min_weights)
    range_capacity = np.array(max_weights) - np.array(min_weights)

    if remaining < -1e-10:
        return None, "No feasible solution: minimum weights exceed 100%."
    if range_capacity.sum() <= 0 and abs(remaining) > 1e-10:
        return None, "No feasible solution with current min/max weights."

    if range_capacity.sum() > 0:
        init = np.array(min_weights) + remaining * (range_capacity / range_capacity.sum())
    else:
        init = np.array(min_weights)

    def neg_sharpe(w):
        return -portfolio_performance(w, mu, cov, rf)[2]

    opt = minimize(
        neg_sharpe,
        init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not opt.success:
        return None, opt.message

    return opt.x, None

def solve_min_vol(mu, cov, min_weights, max_weights):
    n = len(mu)
    bounds = tuple((min_weights[i], max_weights[i]) for i in range(n))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)

    remaining = 1 - sum(min_weights)
    range_capacity = np.array(max_weights) - np.array(min_weights)

    if range_capacity.sum() > 0:
        init = np.array(min_weights) + remaining * (range_capacity / range_capacity.sum())
    else:
        init = np.array(min_weights)

    def vol_fn(w):
        return np.sqrt(np.dot(w.T, np.dot(cov, w)))

    opt = minimize(
        vol_fn,
        init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not opt.success:
        return None, opt.message

    return opt.x, None

@st.cache_data(ttl=3600, show_spinner=False)
def load_prices_cached(tickers_tuple, start, end):
    data = yf.download(
        list(tickers_tuple),
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]

    if isinstance(data, pd.Series):
        data = data.to_frame()

    return data.dropna(how="all")

@st.cache_data(ttl=3600, show_spinner=False)
def load_benchmark_cached(benchmark, start, end):
    data = yf.download(
        benchmark,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]
    if isinstance(data, pd.DataFrame):
        data = data.squeeze()
    return data.dropna()

@st.cache_data(ttl=21600, show_spinner=False)
def load_rf_rate():
    try:
        rf_value = float(yf.download("^TYX", period="1d", progress=False)["Close"].iloc[-1] / 100)
        return rf_value
    except Exception:
        return 0.04

@st.cache_data(ttl=1800, show_spinner=False)
def compute_efficient_frontier(mu_tuple, cov_matrix, rf, min_weights_tuple, max_weights_tuple):
    mu = np.array(mu_tuple, dtype=float)
    cov = np.array(cov_matrix, dtype=float)
    min_weights = list(min_weights_tuple)
    max_weights = list(max_weights_tuple)

    min_vol_w, _ = solve_min_vol(mu, cov, min_weights, max_weights)
    max_sharpe_w, _ = solve_max_sharpe(mu, cov, rf, min_weights, max_weights)

    if min_vol_w is None or max_sharpe_w is None:
        return pd.DataFrame(), None, None

    target_returns = np.linspace(
        portfolio_performance(min_vol_w, mu, cov, rf)[0],
        portfolio_performance(max_sharpe_w, mu, cov, rf)[0] * 1.15,
        35
    )

    frontier_rows = []
    current_guess = max_sharpe_w.copy()
    bounds = tuple((min_weights[i], max_weights[i]) for i in range(len(mu)))

    for target in target_returns:
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x, t=target: np.dot(mu, x) - t}
        )

        def vol_fn(w):
            return np.sqrt(np.dot(w.T, np.dot(cov, w)))

        opt = minimize(
            vol_fn,
            current_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )

        if opt.success:
            current_guess = opt.x
            r, v, s = portfolio_performance(opt.x, mu, cov, rf)
            frontier_rows.append([r, v, s])

    frontier_df = pd.DataFrame(frontier_rows, columns=["Return", "Volatility", "Sharpe"])
    return frontier_df, min_vol_w, max_sharpe_w

@st.cache_data(ttl=1800, show_spinner=False)
def compute_random_portfolios(mu_tuple, cov_matrix, rf, n_portfolios=3000):
    mu = np.array(mu_tuple, dtype=float)
    cov = np.array(cov_matrix, dtype=float)
    n = len(mu)
    rows = []

    for _ in range(n_portfolios):
        w = np.random.random(n)
        w = w / w.sum()
        r, v, s = portfolio_performance(w, mu, cov, rf)
        rows.append([r, v, s])

    return pd.DataFrame(rows, columns=["Return", "Volatility", "Sharpe"])

@st.cache_data(ttl=1800, show_spinner=False)
def compute_black_litterman(mu_hist_tuple, cov_matrix, rf, min_weights_tuple, max_weights_tuple):
    cov = np.array(cov_matrix, dtype=float)
    mu_hist = np.array(mu_hist_tuple, dtype=float)
    n = len(mu_hist)

    tau = 0.05
    delta = 2.5
    w_mkt = np.repeat(1 / n, n)

    pi = delta * cov.dot(w_mkt)

    P = np.eye(n)
    Q = mu_hist.copy()
    omega = np.diag(np.diag(tau * cov)) * 0.25

    middle = np.linalg.inv(np.linalg.inv(tau * cov) + P.T @ np.linalg.inv(omega) @ P)
    mu_bl = middle @ (np.linalg.inv(tau * cov) @ pi + P.T @ np.linalg.inv(omega) @ Q)

    bl_weights, bl_err = solve_max_sharpe(mu_bl, cov, rf, list(min_weights_tuple), list(max_weights_tuple))
    return mu_bl, bl_weights, bl_err

@st.cache_data(ttl=1800, show_spinner=False)
def monte_carlo_paths(daily_mean, daily_std, horizon_days, simulations):
    sim_paths = np.zeros((horizon_days, simulations))
    sim_terminal_returns = np.zeros(simulations)

    for i in range(simulations):
        rand_returns = np.random.normal(daily_mean, daily_std, horizon_days)
        sim_paths[:, i] = (1 + rand_returns).cumprod()
        sim_terminal_returns[i] = sim_paths[-1, i] - 1

    return sim_paths, sim_terminal_returns

# --------------------------------------------------
# INPUTS
# --------------------------------------------------

top_col1, top_col2 = st.columns([2.4, 1.2])

with top_col1:
    tickers_input = st.text_input(
        "Tickers (comma separated)",
        "NVDA,XOM,AVGO,WMT,LLY"
    )
with top_col2:
    benchmark = st.text_input(
        "Benchmark",
        "^GSPC"
    )

tickers = [x.strip().upper() for x in tickers_input.split(",") if x.strip()]

st.subheader("Time Horizon (Years)")
years = st.radio(
    "Select timeframe",
    [1, 2, 5, 10],
    index=2,
    horizontal=True
)

end = dt.datetime.today() - dt.timedelta(days=1)
start = end - dt.timedelta(days=365 * years)

# --------------------------------------------------
# DATA LOAD
# --------------------------------------------------

if len(tickers) == 0:
    st.error("Please enter at least one ticker.")
    st.stop()

with st.spinner("Loading market data..."):
    data = load_prices_cached(tuple(tickers), start, end)
    benchmark_data = load_benchmark_cached(benchmark, start, end)
    rf = load_rf_rate()

if len(data.columns) == 0:
    st.error("No valid ticker data was downloaded.")
    st.stop()

returns = data.pct_change().dropna()
bench_returns = benchmark_data.pct_change().dropna()

# FIX ROBUSTO DE ALINEACIÓN
aligned_returns = pd.concat(
    [returns, bench_returns.rename("Benchmark")],
    axis=1,
    join="inner"
).dropna()

if aligned_returns.empty:
    st.error("Insufficient overlapping data between assets and benchmark.")
    st.stop()

returns = aligned_returns.drop(columns=["Benchmark"])
bench_returns = aligned_returns["Benchmark"]

color_map = get_color_map(list(data.columns))

# --------------------------------------------------
# PRICE CHARTS
# --------------------------------------------------

st.header("📈 Price Charts")

selected_chart_tickers = st.multiselect(
    "Select tickers to display in price charts",
    options=list(data.columns),
    default=list(data.columns)
)

if len(selected_chart_tickers) == 0:
    st.warning("Select at least one ticker to display the charts.")
    st.stop()

data_chart = data[selected_chart_tickers]
norm_chart = data_chart / data_chart.iloc[0]

price_long = data_chart.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Price")
norm_long = norm_chart.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Normalized Value")

fig_prices = px.line(
    price_long,
    x="Date",
    y="Price",
    color="Ticker",
    title="Daily Adjusted Prices",
    color_discrete_map=color_map
)
fig_prices.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Price"
)
st.plotly_chart(fig_prices, use_container_width=True)

fig_norm = px.line(
    norm_long,
    x="Date",
    y="Normalized Value",
    color="Ticker",
    title="Normalized Growth of $1 Invested",
    color_discrete_map=color_map
)
fig_norm.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Normalized Value"
)
st.plotly_chart(fig_norm, use_container_width=True)

st.markdown(
    '<div class="small-note">Daily Adjusted Prices shows split- and dividend-adjusted price history. '
    'Normalized Growth of $1 Invested lets you compare relative performance from the same starting base.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# RETURN DISTRIBUTION
# --------------------------------------------------

st.header("Return Distribution")

returns_long = returns.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Daily Return")
fig_dist = px.histogram(
    returns_long,
    x="Daily Return",
    color="Ticker",
    nbins=80,
    opacity=0.55,
    barmode="overlay",
    color_discrete_map=color_map
)
fig_dist.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Daily Return",
    yaxis_title="Frequency"
)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown(
    '<div class="small-note">This section shows the daily return distribution for each asset. '
    'It helps identify dispersion, skewness and the concentration of extreme observations.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# ASSET STATISTICS
# --------------------------------------------------

st.header("Asset Statistics")

ann_return = returns.mean() * 252
ann_vol = returns.std(ddof=1) * np.sqrt(252)
sharpe_assets = (ann_return - rf) / ann_vol
sortino_assets = (ann_return - rf) / (returns.where(returns < 0).std(ddof=1) * np.sqrt(252))

stats_display = pd.DataFrame({
    "Ticker": ann_return.index,
    "Annual Return": ann_return.map(lambda x: f"{x:.2%}").values,
    "Volatility": ann_vol.map(lambda x: f"{x:.2%}").values,
    "Sharpe Ratio": sharpe_assets.map(lambda x: f"{x:.3f}").values,
    "Sortino Ratio": sortino_assets.map(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A").values
})

render_executive_table(stats_display)

st.markdown(
    '<div class="small-note">Annual Return is the average annualized return. Volatility is annualized standard deviation. '
    'Sharpe Ratio measures excess return per unit of total risk. Sortino Ratio focuses only on downside volatility.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# CORRELATION
# --------------------------------------------------

st.header("Correlation Matrix")

fig_corr, ax = plt.subplots(figsize=(8, 6))
fig_corr.patch.set_facecolor("#0E1117")
ax.set_facecolor("#0E1117")

sns.heatmap(
    returns.corr(),
    annot=True,
    cmap="Purples",
    ax=ax,
    cbar=True
)

ax.tick_params(axis="x", colors="white")
ax.tick_params(axis="y", colors="white")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", color="white")
plt.setp(ax.get_yticklabels(), rotation=0, color="white")

st.pyplot(fig_corr)

st.markdown(
    '<div class="small-note">Correlation measures how similarly two assets move. Values close to 1 imply similar movement; '
    'values near 0 imply weak co-movement; negative values imply opposite movement.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# PORTFOLIO OPTIMIZATION INPUTS
# --------------------------------------------------

st.header("Optimized Portfolio")

st.subheader("Weight Constraints")

constraints_df_default = pd.DataFrame({
    "Ticker": tickers,
    "Min Weight %": [5.0] * len(tickers),
    "Max Weight %": [40.0] * len(tickers)
})

constraints_df = st.data_editor(
    constraints_df_default,
    use_container_width=True,
    hide_index=True,
    disabled=["Ticker"],
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker"),
        "Min Weight %": st.column_config.NumberColumn("Min Weight %", min_value=0.0, max_value=100.0, step=1.0, format="%.2f"),
        "Max Weight %": st.column_config.NumberColumn("Max Weight %", min_value=0.0, max_value=100.0, step=1.0, format="%.2f"),
    },
    key="weight_constraints_editor"
)

min_weights = (constraints_df["Min Weight %"].astype(float) / 100).tolist()
max_weights = (constraints_df["Max Weight %"].astype(float) / 100).tolist()

for i, t in enumerate(tickers):
    if min_weights[i] > max_weights[i]:
        st.error(f"For {t}, minimum weight cannot exceed maximum weight.")
        st.stop()

if sum(min_weights) > 1:
    st.error("The sum of minimum weights cannot exceed 100%.")
    st.stop()

if sum(max_weights) < 1:
    st.error("The sum of maximum weights must allow the portfolio to reach 100%.")
    st.stop()

mu = ann_return.values
cov = (returns.cov() * 252).values

weights, opt_err = solve_max_sharpe(mu, cov, rf, min_weights, max_weights)
if weights is None:
    st.error(f"Portfolio optimization failed: {opt_err}")
    st.stop()

port_ret, port_vol, port_sharpe = portfolio_performance(weights, mu, cov, rf)
port_series = pd.Series(returns.values @ weights, index=returns.index)
cum_port = (1 + port_series).cumprod()

# --------------------------------------------------
# PORTFOLIO OUTPUTS
# --------------------------------------------------

weights_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": weights
})

weights_df_display = pd.DataFrame({
    "Ticker": weights_df["Ticker"],
    "Weight": weights_df["Weight"].map(lambda x: f"{x:.2%}")
})

st.subheader("Maximum Sharpe Portfolio Weights")
render_executive_table(weights_df_display)

fig_pie = px.pie(
    weights_df,
    values="Weight",
    names="Ticker",
    color="Ticker",
    color_discrete_map=color_map
)
fig_pie.update_traces(textinfo="percent+label")
fig_pie.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white"
)
st.plotly_chart(fig_pie, use_container_width=True)

treynor = (port_ret - rf) / port_vol if port_vol != 0 else np.nan
max_dd = ((cum_port.cummax() - cum_port) / cum_port.cummax()).max()

metrics = pd.DataFrame({
    "Metric": [
        "Expected Return",
        "Volatility",
        "Sharpe Ratio",
        "Treynor Ratio",
        "Max Drawdown"
    ],
    "Value": [
        f"{port_ret:.2%}",
        f"{port_vol:.2%}",
        f"{port_sharpe:.3f}",
        f"{treynor:.3f}" if pd.notna(treynor) else "N/A",
        f"{max_dd:.2%}"
    ]
})

st.subheader("Maximum Sharpe Portfolio Metrics")
render_metric_cards(metrics, columns_per_row=3)

st.markdown(
    '<div class="small-note">Expected Return is the annual expected return of the optimized portfolio. Volatility is annualized risk. '
    'Sharpe Ratio measures excess return per unit of total risk. Treynor Ratio is shown as a simple high-level risk-adjusted indicator here. '
    'Max Drawdown captures the largest peak-to-trough fall.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# MINIMUM VARIANCE PORTFOLIO
# --------------------------------------------------

st.header("Minimum Variance Portfolio")

min_var_weights, min_var_err = solve_min_vol(mu, cov, min_weights, max_weights)
if min_var_weights is None:
    st.warning(f"Minimum variance optimization could not be solved: {min_var_err}")
else:
    min_var_ret, min_var_vol, min_var_sharpe = portfolio_performance(min_var_weights, mu, cov, rf)
    min_var_series = pd.Series(returns.values @ min_var_weights, index=returns.index)
    min_var_cum = (1 + min_var_series).cumprod()
    min_var_max_dd = ((min_var_cum.cummax() - min_var_cum) / min_var_cum.cummax()).max()

    min_var_weights_df = pd.DataFrame({
        "Ticker": tickers,
        "Weight": [f"{x:.2%}" for x in min_var_weights]
    })
    render_executive_table(min_var_weights_df, title="Minimum Variance Weights")

    fig_min_var_pie = px.pie(
        pd.DataFrame({"Ticker": tickers, "Weight": min_var_weights}),
        values="Weight",
        names="Ticker",
        color="Ticker",
        color_discrete_map=color_map
    )
    fig_min_var_pie.update_traces(textinfo="percent+label")
    fig_min_var_pie.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white"
    )
    st.plotly_chart(fig_min_var_pie, use_container_width=True)

    min_var_metrics = pd.DataFrame({
        "Metric": [
            "Expected Return",
            "Volatility",
            "Sharpe Ratio",
            "Max Drawdown"
        ],
        "Value": [
            f"{min_var_ret:.2%}",
            f"{min_var_vol:.2%}",
            f"{min_var_sharpe:.3f}",
            f"{min_var_max_dd:.2%}"
        ]
    })
    render_metric_cards(min_var_metrics, columns_per_row=4)

    st.markdown(
        '<div class="small-note">The Minimum Variance portfolio is the lowest-risk feasible allocation under your weight constraints. '
        'Compared with the Maximum Sharpe portfolio, it generally targets more stability and may sacrifice return in exchange for lower volatility.</div>',
        unsafe_allow_html=True
    )

# --------------------------------------------------
# RISK CONTRIBUTION
# --------------------------------------------------

st.header("Risk Contribution")

marginal_contrib = cov @ weights
portfolio_var = float(weights.T @ cov @ weights)
risk_contrib = weights * marginal_contrib / portfolio_var

risk_contrib_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": [f"{w:.2%}" for w in weights],
    "Risk Contribution": [f"{rc:.2%}" for rc in risk_contrib]
})

render_executive_table(risk_contrib_df)

st.markdown(
    '<div class="small-note">Risk Contribution shows how much each position contributes to total portfolio variance. '
    'This is useful when position size and risk contribution diverge.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# EFFICIENT FRONTIER
# --------------------------------------------------

st.header("Efficient Frontier")

frontier_df, min_vol_weights, max_sharpe_weights = compute_efficient_frontier(
    tuple(mu), cov, rf, tuple(min_weights), tuple(max_weights)
)
random_portfolios = compute_random_portfolios(tuple(mu), cov, rf, n_portfolios=3000)

fig_frontier = go.Figure()

fig_frontier.add_trace(go.Scatter(
    x=random_portfolios["Volatility"],
    y=random_portfolios["Return"],
    mode="markers",
    marker=dict(
        size=5,
        color=random_portfolios["Sharpe"],
        colorscale="Purples",
        opacity=0.35,
        showscale=True,
        colorbar=dict(title="Sharpe")
    ),
    name="Random Portfolios"
))

if not frontier_df.empty:
    fig_frontier.add_trace(go.Scatter(
        x=frontier_df["Volatility"],
        y=frontier_df["Return"],
        mode="lines",
        line=dict(color="#B8B8FF", width=3),
        name="Efficient Frontier"
    ))

if min_vol_weights is not None:
    min_vol_ret, min_vol_val, _ = portfolio_performance(min_vol_weights, mu, cov, rf)
    fig_frontier.add_trace(go.Scatter(
        x=[min_vol_val],
        y=[min_vol_ret],
        mode="markers",
        marker=dict(size=14, color="#8D99AE", symbol="diamond"),
        name="Min Vol Portfolio"
    ))

fig_frontier.add_trace(go.Scatter(
    x=[port_vol],
    y=[port_ret],
    mode="markers",
    marker=dict(size=16, color="#7B2CBF", symbol="star"),
    name="Max Sharpe Portfolio"
))

fig_frontier.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Annualized Volatility",
    yaxis_title="Annualized Return",
)

st.plotly_chart(fig_frontier, use_container_width=True)

st.markdown(
    '<div class="small-note">The Efficient Frontier shows the minimum achievable volatility for different return targets under your weight constraints. '
    'The Max Sharpe portfolio is the tangent solution; the Min Vol portfolio is the lowest-risk feasible mix.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# BLACK-LITTERMAN
# --------------------------------------------------

st.header("Black-Litterman Overlay")

st.markdown("""
<div class="bl-box">
<strong>Executive summary.</strong> The Black-Litterman methodology starts from an equilibrium return framework instead of relying only on raw historical averages. 
It then blends that equilibrium with investor views to produce a new set of expected returns that is usually more stable and less sensitive to estimation error.<br><br>

<strong>How to read this section.</strong> The table below compares the trailing historical view with the posterior Black-Litterman return estimate for each asset. 
The portfolio weights that come out of this process can differ from the Maximum Sharpe portfolio because the expected returns are being adjusted before optimization.<br><br>

<strong>Main difference vs. the optimized portfolio.</strong> The Maximum Sharpe portfolio uses direct historical estimates and may react aggressively to noisy return inputs. 
The Black-Litterman portfolio is often more balanced and institutionally robust because it smooths those inputs through an equilibrium prior plus investor views.
</div>
""", unsafe_allow_html=True)

mu_hist_12m = returns.tail(min(len(returns), 252)).mean().values * 252
mu_bl, bl_weights, bl_err = compute_black_litterman(
    tuple(mu_hist_12m), cov, rf, tuple(min_weights), tuple(max_weights)
)

if bl_weights is None:
    st.warning(f"Black-Litterman optimization could not be solved: {bl_err}")
else:
    bl_ret, bl_vol, bl_sharpe = portfolio_performance(bl_weights, mu_bl, cov, rf)

    bl_cols = st.columns([1.2, 1.8])

    with bl_cols[0]:
        bl_metrics = pd.DataFrame({
            "Metric": ["BL Expected Return", "BL Volatility", "BL Sharpe"],
            "Value": [f"{bl_ret:.2%}", f"{bl_vol:.2%}", f"{bl_sharpe:.3f}"]
        })
        render_metric_cards(bl_metrics, columns_per_row=1)

    with bl_cols[1]:
        bl_weights_df = pd.DataFrame({"Ticker": tickers, "Weight": bl_weights})
        fig_bl_pie = px.pie(
            bl_weights_df,
            values="Weight",
            names="Ticker",
            color="Ticker",
            color_discrete_map=color_map
        )
        fig_bl_pie.update_traces(textinfo="percent+label")
        fig_bl_pie.update_layout(
            title="Black-Litterman Portfolio Weights",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font_color="white"
        )
        st.plotly_chart(fig_bl_pie, use_container_width=True)

    bl_returns_table = pd.DataFrame({
        "Ticker": tickers,
        "Historical 12M View": [f"{x:.2%}" for x in mu_hist_12m],
        "BL Posterior Return": [f"{x:.2%}" for x in mu_bl]
    })
    render_executive_table(bl_returns_table)

    st.markdown(
        '<div class="small-note">Black-Litterman blends an equilibrium return prior with market views to produce more stable expected returns. '
        'Here, trailing 12-month annualized returns are used as soft views and combined with the covariance structure.</div>',
        unsafe_allow_html=True
    )

# --------------------------------------------------
# BETA ANALYSIS
# --------------------------------------------------

st.header("Beta Analysis")

aligned_bt = pd.concat([returns, bench_returns.rename("Benchmark")], axis=1).dropna()
benchmark_aligned = aligned_bt["Benchmark"]
asset_returns_aligned = aligned_bt.drop(columns=["Benchmark"])

asset_betas = asset_returns_aligned.apply(lambda s: s.cov(benchmark_aligned) / benchmark_aligned.var())
beta_table = pd.DataFrame({
    "Ticker": asset_betas.index,
    "Beta vs Benchmark": asset_betas.map(lambda x: f"{x:.3f}").values
})

render_executive_table(beta_table)

st.markdown(
    '<div class="small-note">Beta measures sensitivity to benchmark movements. Values above 1 imply more market sensitivity; '
    'values below 1 imply a more defensive profile.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# BACKTEST
# --------------------------------------------------

st.header("Backtest vs Benchmark")

aligned_port_bench = pd.concat([port_series.rename("Portfolio"), bench_returns.rename("Benchmark")], axis=1).dropna()
cum_bt = (1 + aligned_port_bench).cumprod()

fig_bt = px.line(
    cum_bt.reset_index().melt(id_vars="Date", var_name="Series", value_name="Cumulative Growth"),
    x="Date",
    y="Cumulative Growth",
    color="Series",
    color_discrete_map={"Portfolio": "#9D4EDD", "Benchmark": "#8D99AE"}
)
fig_bt.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Cumulative Growth"
)

st.plotly_chart(fig_bt, use_container_width=True)

st.markdown(
    '<div class="small-note">The backtest compares the cumulative performance of the optimized portfolio against the selected benchmark.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# ROLLING SHARPE
# --------------------------------------------------

st.header("Rolling Sharpe")

rolling_window = 126
rolling_sharpe = ((port_series.rolling(rolling_window).mean() * 252) - rf) / (port_series.rolling(rolling_window).std(ddof=1) * np.sqrt(252))
rolling_sharpe_df = rolling_sharpe.reset_index()
rolling_sharpe_df.columns = ["Date", "Rolling Sharpe"]

fig_rs = px.line(
    rolling_sharpe_df,
    x="Date",
    y="Rolling Sharpe",
    title="126-Day Rolling Sharpe Ratio",
    color_discrete_sequence=["#B8B8FF"]
)
fig_rs.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Rolling Sharpe"
)
st.plotly_chart(fig_rs, use_container_width=True)

st.markdown(
    '<div class="small-note">Rolling Sharpe tracks how risk-adjusted performance evolves over time instead of showing only one point estimate.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# ROLLING BETA
# --------------------------------------------------

st.header("Rolling Beta")

rolling_beta_df = aligned_port_bench.copy()
rolling_cov = rolling_beta_df["Portfolio"].rolling(rolling_window).cov(rolling_beta_df["Benchmark"])
rolling_var_bench = rolling_beta_df["Benchmark"].rolling(rolling_window).var()
rolling_beta = rolling_cov / rolling_var_bench
rolling_beta = rolling_beta.reset_index()
rolling_beta.columns = ["Date", "Rolling Beta"]

fig_rb = px.line(
    rolling_beta,
    x="Date",
    y="Rolling Beta",
    title="126-Day Rolling Beta vs Benchmark",
    color_discrete_sequence=["#7B2CBF"]
)
fig_rb.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Rolling Beta"
)
st.plotly_chart(fig_rb, use_container_width=True)

st.markdown(
    '<div class="small-note">Rolling Beta shows how market sensitivity changes over time. This helps detect regime shifts in portfolio behavior.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# VALUE AT RISK
# --------------------------------------------------

st.header("Value at Risk")

confidence_level = 0.95
alpha = 1 - confidence_level
horizon_days = 252

daily_mean = port_series.mean()
daily_std = port_series.std(ddof=1)

hist_var_daily = -np.percentile(port_series, alpha * 100)
hist_var_annual = max(hist_var_daily * np.sqrt(horizon_days), 0)

z_score = stats_norm.ppf(confidence_level)
param_var_daily = z_score * daily_std - daily_mean
param_var_annual = max(param_var_daily * np.sqrt(horizon_days), 0)

simulations = 10000
sim_paths, sim_terminal_returns = monte_carlo_paths(daily_mean, daily_std, horizon_days, simulations)

mc_var_daily = -np.percentile(np.random.normal(daily_mean, daily_std, simulations), alpha * 100)
mc_var_annual = max(mc_var_daily * np.sqrt(horizon_days), 0)

fig_hist = px.histogram(
    sim_terminal_returns,
    nbins=100,
    title="Monte Carlo Distribution of 1-Year Portfolio Returns",
    color_discrete_sequence=["#7B2CBF"]
)
fig_hist.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="1-Year Simulated Return",
    yaxis_title="Frequency"
)
st.plotly_chart(fig_hist, use_container_width=True)

fig_paths = go.Figure()
for i in range(min(50, simulations)):
    fig_paths.add_trace(
        go.Scatter(
            y=sim_paths[:, i],
            mode="lines",
            line=dict(color="#9D4EDD", width=1),
            opacity=0.30,
            showlegend=False
        )
    )

fig_paths.update_layout(
    title="Monte Carlo Simulation Paths (1-Year Horizon)",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Trading Days",
    yaxis_title="Cumulative Growth"
)
st.plotly_chart(fig_paths, use_container_width=True)

var_df = pd.DataFrame({
    "Method": ["Historical", "Parametric", "Monte Carlo"],
    "VaR (95%, Annualized)": [
        f"{hist_var_annual:.4%}",
        f"{param_var_annual:.4%}",
        f"{mc_var_annual:.4%}"
    ]
})
render_executive_table(var_df)

st.markdown(
    '<div class="small-note">Value at Risk estimates the potential loss of the optimized portfolio at a defined confidence level. '
    'All three methods are expressed in annualized terms for comparability.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# PERFORMANCE NOTE
# --------------------------------------------------

st.caption("Performance mode enabled: cached market downloads, Monte Carlo simulations and frontier computations reduce repeated rerun time materially.")

# --------------------------------------------------
# PORTFOLIO DRAWDOWN
# --------------------------------------------------

st.header("Portfolio Drawdown")

cum_port_dd = (1 + port_series).cumprod()
rolling_max_dd = cum_port_dd.cummax()
drawdown = (cum_port_dd - rolling_max_dd) / rolling_max_dd

drawdown_df = drawdown.reset_index()
drawdown_df.columns = ["Date", "Drawdown"]

fig_dd = px.area(
    drawdown_df,
    x="Date",
    y="Drawdown",
    title="Portfolio Drawdown",
    color_discrete_sequence=["#9D4EDD"]
)

fig_dd.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Drawdown"
)

st.plotly_chart(fig_dd, use_container_width=True)

st.markdown(
"""
<div class="small-note">
Drawdown measures the percentage decline from the portfolio's historical peak. 
It helps investors understand the depth and duration of losses during market stress.
</div>
""",
unsafe_allow_html=True
)

# --------------------------------------------------
# ROLLING CORRELATION VS BENCHMARK
# --------------------------------------------------

st.header("Rolling Correlation vs Benchmark")

aligned_corr = pd.concat(
    [port_series.rename("Portfolio"), bench_returns.rename("Benchmark")],
    axis=1
).dropna()

rolling_corr = aligned_corr["Portfolio"].rolling(126).corr(aligned_corr["Benchmark"])

corr_df = rolling_corr.reset_index()
corr_df.columns = ["Date", "Correlation"]

fig_corr_roll = px.line(
    corr_df,
    x="Date",
    y="Correlation",
    title="126-Day Rolling Correlation with Benchmark",
    color_discrete_sequence=["#B8B8FF"]
)

fig_corr_roll.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Correlation"
)

st.plotly_chart(fig_corr_roll, use_container_width=True)

st.markdown(
"""
<div class="small-note">
Rolling correlation measures how closely the portfolio moves with the benchmark over time. 
Changes in correlation often indicate regime shifts in market behavior.
</div>
""",
unsafe_allow_html=True
)

# --------------------------------------------------
# PORTFOLIO ALLOCATION
# --------------------------------------------------

st.header("Portfolio Allocation")

alloc_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": weights
})

fig_alloc = px.bar(
    alloc_df,
    x="Ticker",
    y="Weight",
    color="Ticker",
    color_discrete_map=color_map,
    title="Portfolio Allocation"
)

fig_alloc.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Ticker",
    yaxis_title="Weight"
)

st.plotly_chart(fig_alloc, use_container_width=True)

st.markdown(
"""
<div class="small-note">
This chart provides an alternative view of portfolio allocation. 
Bar charts are often preferred by institutional investors because they allow easier comparison between positions.
</div>
""",
unsafe_allow_html=True
)

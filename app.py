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

st.set_page_config(layout="wide", page_title="Portfolio Analytics")

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

</style>
""", unsafe_allow_html=True)

st.title("📊 Advanced Portfolio Analytics Dashboard")

# --------------------------------------------------
# COLOR PALETTE
# --------------------------------------------------

palette = [
    "#7B2CBF",  # morado fuerte
    "#9D4EDD",  # morado medio
    "#C9ADA7",  # gris lavanda
    "#4A4E69",  # gris oscuro
    "#6D597A",  # violeta gris
    "#8D99AE",  # gris azulado
    "#2B2D42",  # casi negro
    "#B8B8FF"   # lila claro
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def render_executive_table(df: pd.DataFrame, title: str | None = None):
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


def render_metric_cards(metrics_df: pd.DataFrame, columns_per_row: int = 3):
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
        if len(row_df) < columns_per_row:
            for idx in range(len(row_df), columns_per_row):
                cols[idx].empty()

# --------------------------------------------------
# INPUTS
# --------------------------------------------------

tickers_input = st.text_input(
    "Tickers (separados por coma)",
    "AAPL,MSFT,NVDA,GOOGL"
)

benchmark = st.text_input(
    "Benchmark",
    "^GSPC"
)

tickers = [x.strip().upper() for x in tickers_input.split(",") if x.strip()]

# --------------------------------------------------
# TIMEFRAME SELECTOR
# --------------------------------------------------

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
# DATA DOWNLOAD
# --------------------------------------------------

@st.cache_data
def load_prices(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]

    if isinstance(data, pd.Series):
        data = data.to_frame()

    return data


@st.cache_data
def load_benchmark(benchmark, start, end):
    data = yf.download(
        benchmark,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]

    return data


data = load_prices(tickers, start, end)
benchmark_data = load_benchmark(benchmark, start, end)

returns = data.pct_change().dropna()
bench_returns = benchmark_data.pct_change().dropna()

# --------------------------------------------------
# RISK FREE RATE
# --------------------------------------------------

try:
    rf = float(
        yf.download("^TYX", period="1d", progress=False)["Close"].iloc[-1] / 100
    )
except Exception:
    rf = 0.04

# --------------------------------------------------
# PRICE CHART FILTER
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

# --------------------------------------------------
# PRICE CHART
# --------------------------------------------------

fig_prices = px.line(
    data_chart,
    title="Daily Adjusted Prices",
    color_discrete_sequence=palette
)
fig_prices.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Price"
)
st.plotly_chart(fig_prices, use_container_width=True)

# --------------------------------------------------
# NORMALIZED PERFORMANCE
# --------------------------------------------------

fig_norm = px.line(
    norm_chart,
    title="Normalized Growth of $1 Invested",
    color_discrete_sequence=palette
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
    '<div class="small-note">Daily Adjusted Prices muestra la trayectoria histórica de precios ajustados por dividendos y splits. '
    'Normalized Growth of $1 Invested permite comparar desempeño relativo entre activos al llevar todos los precios a una misma base inicial.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# RETURN DISTRIBUTION
# --------------------------------------------------

st.header("Return Distribution")

fig_dist = px.histogram(
    returns,
    nbins=100,
    color_discrete_sequence=palette
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
    '<div class="small-note">Esta sección muestra la distribución de rendimientos diarios de cada activo. '
    'Ayuda a identificar dispersión, asimetría y concentración de resultados extremos.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# ASSET STATS
# --------------------------------------------------

st.header("Asset Statistics")

ann_return = returns.mean() * 252
ann_vol = returns.std() * np.sqrt(252)

sharpe = (ann_return - rf) / ann_vol
sortino = (ann_return - rf) / (returns[returns < 0].std() * np.sqrt(252))

stats_display = pd.DataFrame({
    "Ticker": ann_return.index,
    "Annual Return": ann_return.map(lambda x: f"{x:.2%}").values,
    "Volatility": ann_vol.map(lambda x: f"{x:.2%}").values,
    "Sharpe Ratio": sharpe.map(lambda x: f"{x:.3f}").values,
    "Sortino Ratio": sortino.map(lambda x: f"{x:.3f}").values
})

render_executive_table(stats_display)

st.markdown(
    '<div class="small-note">Annual Return es el rendimiento promedio anualizado. Volatility es la desviación estándar anualizada de los rendimientos. '
    'Sharpe Ratio mide retorno ajustado por riesgo total. Sortino Ratio mide retorno ajustado solo por volatilidad negativa.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# CORRELATION
# --------------------------------------------------

st.header("Correlation Matrix")

fig_corr, ax = plt.subplots()
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
    '<div class="small-note">La correlación mide qué tan parecido se mueven dos activos. Valores cercanos a 1 indican movimientos similares; '
    'valores cercanos a 0 indican poca relación; valores negativos indican movimientos opuestos.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# PORTFOLIO OPTIMIZATION
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
        "Min Weight %": st.column_config.NumberColumn(
            "Min Weight %",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            format="%.2f"
        ),
        "Max Weight %": st.column_config.NumberColumn(
            "Max Weight %",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            format="%.2f"
        ),
    },
    key="weight_constraints_editor"
)

min_weights = (constraints_df["Min Weight %"].astype(float) / 100).tolist()
max_weights = (constraints_df["Max Weight %"].astype(float) / 100).tolist()

for i, t in enumerate(tickers):
    if min_weights[i] > max_weights[i]:
        st.error(f"En {t}, el mínimo no puede ser mayor al máximo.")
        st.stop()

if sum(min_weights) > 1:
    st.error("La suma de los pesos mínimos no puede exceder 100%.")
    st.stop()

if sum(max_weights) < 1:
    st.error("La suma de los pesos máximos debe permitir llegar al 100% del portafolio.")
    st.stop()

ann_return_np = ann_return.values
cov_np = (returns.cov() * 252).values

def portfolio_performance(weights):
    weights = np.array(weights)
    ret = np.dot(ann_return_np, weights)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_np, weights)))
    sharpe_value = (ret - rf) / vol if vol != 0 else -np.inf
    return float(ret), float(vol), float(sharpe_value)

def neg_sharpe(weights):
    return -portfolio_performance(weights)[2]

n = len(tickers)
bounds = tuple((min_weights[i], max_weights[i]) for i in range(n))
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

remaining = 1 - sum(min_weights)
range_capacity = np.array(max_weights) - np.array(min_weights)

if remaining < -1e-10:
    st.error("No existe solución factible con esos mínimos.")
    st.stop()

if range_capacity.sum() <= 0 and abs(remaining) > 1e-10:
    st.error("No existe solución factible con esos mínimos y máximos.")
    st.stop()

if range_capacity.sum() > 0:
    init = np.array(min_weights) + remaining * (range_capacity / range_capacity.sum())
else:
    init = np.array(min_weights)

opt = minimize(
    neg_sharpe,
    init,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

if not opt.success:
    st.error(f"No se pudo optimizar el portafolio: {opt.message}")
    st.stop()

weights = opt.x

# --------------------------------------------------
# WEIGHT TABLE
# --------------------------------------------------

weights_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": weights
})

weights_df_display = pd.DataFrame({
    "Ticker": weights_df["Ticker"],
    "Weight": weights_df["Weight"].map(lambda x: f"{x:.2%}")
})

st.subheader("Portfolio Weights")
render_executive_table(weights_df_display)

# --------------------------------------------------
# PIE CHART
# --------------------------------------------------

fig_pie = px.pie(
    weights_df,
    values="Weight",
    names="Ticker",
    color_discrete_sequence=palette
)

fig_pie.update_traces(textinfo="percent+label")
fig_pie.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white"
)

st.plotly_chart(fig_pie, use_container_width=True)

# --------------------------------------------------
# PORTFOLIO SERIES
# --------------------------------------------------

port_ret, port_vol, port_sharpe = portfolio_performance(weights)

port_series = returns.values @ weights
port_series = pd.Series(port_series, index=returns.index)

cum_port = (1 + port_series).cumprod()

# --------------------------------------------------
# PORTFOLIO METRICS
# --------------------------------------------------

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
        f"{treynor:.3f}",
        f"{max_dd:.2%}"
    ]
})

st.subheader("Portfolio Metrics")
render_metric_cards(metrics, columns_per_row=3)

st.markdown(
    '<div class="small-note">Expected Return es el rendimiento anual esperado del portafolio. Volatility es el riesgo anualizado. '
    'Sharpe Ratio muestra cuánto retorno excedente se obtiene por unidad de riesgo total. Treynor Ratio relaciona el retorno excedente con el riesgo sistemático. '
    'Max Drawdown mide la mayor caída acumulada desde un pico hasta un mínimo posterior.</div>',
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

# Historical VaR from optimal portfolio daily returns, annualized
hist_var_daily = -np.percentile(port_series, alpha * 100)
hist_var_annual = hist_var_daily * np.sqrt(horizon_days)

# Parametric VaR from optimal portfolio daily returns, annualized
z_score = stats_norm.ppf(confidence_level)
param_var_daily = z_score * daily_std - daily_mean
param_var_annual = param_var_daily * np.sqrt(horizon_days)

# Monte Carlo VaR using optimal portfolio daily distribution
simulations = 10000
sim_paths = np.zeros((horizon_days, simulations))
sim_terminal_returns = np.zeros(simulations)

for i in range(simulations):
    rand_returns = np.random.normal(
        daily_mean,
        daily_std,
        horizon_days
    )
    sim_paths[:, i] = (1 + rand_returns).cumprod()
    sim_terminal_returns[i] = sim_paths[-1, i] - 1

mc_var_daily = -np.percentile(
    np.random.normal(daily_mean, daily_std, simulations),
    alpha * 100
)
mc_var_annual = mc_var_daily * np.sqrt(horizon_days)

hist_var_annual = max(hist_var_annual, 0)
param_var_annual = max(param_var_annual, 0)
mc_var_annual = max(mc_var_annual, 0)

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
            opacity=0.35,
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
    "Method": [
        "Historical",
        "Parametric",
        "Monte Carlo"
    ],
    "VaR (95%, Annualized)": [
        f"{hist_var_annual:.4%}",
        f"{param_var_annual:.4%}",
        f"{mc_var_annual:.4%}"
    ]
})

st.table(var_df)

st.markdown(
    '<div class="small-note">Value at Risk (VaR) estima la pérdida potencial máxima esperada del portafolio óptimo bajo un nivel de confianza definido. '
    'Aquí se calcula a partir de los rendimientos diarios del portafolio optimizado y luego se expresa en términos anualizados, por lo que funciona correctamente sin importar cuántos activos tenga el portafolio.</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# BACKTEST
# --------------------------------------------------

st.header("Backtest vs Benchmark")

cum_bench = (1 + bench_returns).cumprod()

df_bt = pd.concat([cum_port, cum_bench], axis=1)
df_bt.columns = ["Portfolio", "Benchmark"]

fig_bt = px.line(df_bt, color_discrete_sequence=["#9D4EDD", "#8D99AE"])
fig_bt.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    xaxis_title="Date",
    yaxis_title="Cumulative Growth"
)

st.plotly_chart(fig_bt, use_container_width=True)

st.markdown(
    '<div class="small-note">El backtest compara el desempeño histórico acumulado del portafolio optimizado frente al benchmark seleccionado. '
    'Permite visualizar periodos de sobre y bajo desempeño relativo.</div>',
    unsafe_allow_html=True
)

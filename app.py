import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.ensemble import RandomForestRegressor

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Coffee BI", layout="wide")

pio.templates.default = "plotly_white"

# =========================
# PALETA
# =========================
PRIMARY = "#4f6ef7"
FORECAST = "#f59e0b"

BG = "#fff6ea"
SIDEBAR_BG = "#fff9f1"
CARD_BG = "#fff2df"
CHART_BG = "#fff8ee"
BORDER = "#ead7bf"
TEXT = "#1f2937"
MUTED = "#6b7280"
SHADOW = "rgba(0,0,0,0.06)"
BORDER = "#ead7bf"

# =========================
# CSS
# =========================
st.markdown(f"""
<style>

/* =========================
FONDO GENERAL (NO TOCAR)
========================= */
html, body, .stApp,
[data-testid="stAppViewContainer"] {{
    background-color: {BG} !important;
}}

/* =========================
SIDEBAR LIMPIO Y LEGIBLE
========================= */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] {{
    background-color: #fff9f1 !important;
    border-right: 1px solid #ead7bf;
}}

/* SOLO TEXTO SIDEBAR (SIN ROMPER WIDGETS) */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p {{
    color: #1f2937 !important;
}}

/* inputs visibles */
[data-testid="stSidebar"] input {{
    color: #1f2937 !important;
    background-color: #ffffff !important;
}}

/* =========================
KPIs (CLAROS Y CON CONTRASTE)
========================= */
div[data-testid="stMetric"] {{
    background: #ffe8cc !important;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    border: 1px solid #f0d6b5;
}}

[data-testid="stMetricValue"] {{
    font-size: 28px;
    font-weight: 800;
    color: #1f2937 !important;
}}

[data-testid="stMetricLabel"] {{
    color: #6b7280 !important;
}}

/* =========================
CHARTS (SEPARADOS VISUALMENTE)
========================= */
div[data-testid="stPlotlyChart"] {{
    background: #fff8ee !important;
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 1px solid #ead7bf;
}}

/* =========================
TÍTULOS
========================= */
h1, h2, h3 {{
    color: #1f2937 !important;
    font-weight: 700;
}}

</style>
""", unsafe_allow_html=True)
# =========================
# DATA
# =========================
df = pd.read_csv("prediction_coffee.csv")

# =========================
# SIDEBAR

# =========================
st.sidebar.title("☕ Coffee BI")

# Convert coffee names to English (si tu dataset original tiene traducciones)
df["coffee_name_en"] = df["coffee_name"]  # <-- si ya están en inglés, esto deja igual

all_coffee = st.sidebar.checkbox("Select All Coffees", value=True)

coffee_options = df["coffee_name"].unique().tolist()

if all_coffee:
    selected_coffee = coffee_options
else:
    selected_coffee = st.sidebar.multiselect(
        "Coffee Type",
        options=coffee_options,
        default=[]
    )

df_filtered = df[df["coffee_name"].isin(selected_coffee)]
# =========================
# TITLE
# =========================
st.title("☕ Coffee Sales Intelligence")

# =========================
# KPIs
# =========================
# =========================
# KPIs
# =========================
revenue = df["money"].sum()
avg = df["money"].mean()
tx = len(df)
peak = df.groupby("hour_of_day")["money"].sum().idxmax()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"${revenue:,.0f}",
    delta_color="normal"
)

c2.metric(
    "Avg Ticket",
    f"${avg:.2f}",
    delta_color="normal"
)

c3.metric(
    "Transactions",
    f"{tx}",
    delta_color="normal"
)

c4.metric(
    "Peak Hour",
    f"{peak}:00",
    delta_color="off"
)

# =========================
# INSIGHTS
# =========================
st.markdown("## 📌 Insights")

hourly = df.groupby("hour_of_day")["money"].sum()
best_hour = hourly.idxmax()
share = hourly.max() / hourly.sum()

top_product = df.groupby("coffee_name")["money"].sum().idxmax()
best_day = df.groupby("Weekday")["money"].sum().idxmax()

st.success(f"Peak hour: {best_hour}:00 → {share:.0%} revenue")
st.info(f"Top product: {top_product} | Best day: {best_day}")

# =========================
# CHART 1 — POR CAFÉ
# =========================
st.markdown("## 📊 Revenue by Hour (by Coffee Type)")

hourly_df = df.groupby(["hour_of_day", "coffee_name"])["money"].sum().reset_index()

fig = px.bar(
    hourly_df,
    x="hour_of_day",
    y="money",
    color="coffee_name",
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig.update_layout(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font_color=TEXT
)

st.plotly_chart(fig, use_container_width=True)

# =========================
## =========================
# % VENTAS POR TIPO DE CAFÉ (LIMPIO)
# =========================
st.markdown("## ☕ Market Share by Coffee Type")

# Agrupar
coffee_df = df.groupby("coffee_name")["money"].sum().reset_index()

# % de ventas
total_sales = coffee_df["money"].sum()
coffee_df["share"] = coffee_df["money"] / total_sales * 100

# Ordenar
coffee_df = coffee_df.sort_values("share", ascending=False)

# Colores pastel consistentes
pastel_colors = px.colors.qualitative.Pastel

fig = px.bar(
    coffee_df,
    x="coffee_name",
    y="share",
    text=coffee_df["share"].round(1).astype(str) + "%",
    color="coffee_name",
    color_discrete_sequence=pastel_colors
)

fig.update_layout(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font_color=TEXT,
    xaxis_title="Coffee Type",
    yaxis_title="Sales Share (%)",
    showlegend=False
)

fig.update_traces(
    textposition="outside",
    marker_line_width=0,
    width=0.6  # 👈 barras más gruesas visualmente
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# ML FORECAST
# =========================
st.markdown("## 🤖 Forecast")

ml = df.groupby("hour_of_day")["money"].sum().reset_index()

X = ml[["hour_of_day"]]
y = ml["money"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

ml["forecast"] = model.predict(X)

fig3 = px.line(
    ml,
    x="hour_of_day",
    y=["money", "forecast"],
    color_discrete_sequence=[PRIMARY, FORECAST]
)

fig3.update_layout(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font_color=TEXT
)

st.plotly_chart(fig3, use_container_width=True)
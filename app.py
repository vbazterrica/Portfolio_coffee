import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Coffee Business Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme + custom CSS
st.markdown("""
<style>
/* Fondo general cálido tipo café */
.stApp {
    background-color: #F7F3EE;
}

/* Títulos */
h1, h2, h3 {
    color: #3B2F2F;
}

/* Texto general */
p, label {
    color: #5C4B3C;
}

/* KPIs estilo tarjetas */
div[data-testid="metric-container"] {
    background-color: #FFFFFF;
    border: 1px solid #E6D5C3;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

/* Números KPI */
div[data-testid="metric-value"] {
    font-size: 26px;
    color: #7A4E2D;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #EFE6DD;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div style='text-align:center; padding:20px 0px;'>
    <h1 style='font-size:46px; margin-bottom:5px; color:#3B2F2F;'>
        ☕ Coffee Business Intelligence
    </h1>
    <p style='font-size:18px; color:#7A5C45;'>
        Premium analytics dashboard for coffee shop performance & sales insights
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / "tables" / "df.csv")
    df["coffee_name"] = df["coffee_name"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Filters")
products = ["All"] + sorted(df["coffee_name"].unique())
product_filter = st.sidebar.selectbox("☕ Product", products)

min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "📅 Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# =========================
# FILTER DATA
# =========================
df_filtered = df.copy()
if product_filter != "All":
    df_filtered = df_filtered[df_filtered["coffee_name"] == product_filter]

if date_range:
    start_date, end_date = date_range
    df_filtered = df_filtered[
        (df_filtered["Date"] >= pd.to_datetime(start_date)) &
        (df_filtered["Date"] <= pd.to_datetime(end_date))
    ]

if len(df_filtered) == 0:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# =========================
# KPIs
# =========================
total_sales = df_filtered["money"].sum()
total_orders = len(df_filtered)
avg_ticket = df_filtered["money"].mean()
orders_per_day = len(df_filtered) / df_filtered["Date"].nunique()
top_product = df_filtered["coffee_name"].value_counts().idxmax()

col1, col2, col3, col4 = st.columns([1.5,1,1,1], gap="large")
col1.metric("💵 Total Revenue", f"${int(total_sales):,}")
col2.metric("☕ Total Orders", total_orders)
col3.metric("🧾 Avg Order Value", f"${int(avg_ticket):,}")
col4.metric("📊 Orders per Day", int(orders_per_day))
st.info(f"🏆 Best-selling product: **{top_product}**")

# =========================
# INSIGHTS
# =========================
st.subheader("🧠 Key Business Insights")
daily_sales = df_filtered.groupby("Date")["money"].sum()
best_day = daily_sales.idxmax()
best_day_value = daily_sales.max()
peak_hour = df_filtered.groupby("hour_of_day")["money"].sum().idxmax()
product_revenue = df_filtered.groupby("coffee_name")["money"].sum()
top_product_rev = product_revenue.idxmax()

st.success(f"📈 Best-performing product: **{top_product}**")
st.info(f"📅 Peak revenue day: **{best_day.date()}** (${best_day_value:,.0f})")
st.warning(f"🕒 Peak hour: **{peak_hour}:00**")
st.success(f"☕ Top revenue product: **{top_product_rev}**")

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Revenue Trends", "☕ Product Performance", "🕒 Demand Patterns", "💰 Financial Overview"
])

with tab1:
    st.subheader("📈 Daily Revenue")
    daily = df_filtered.groupby("Date")["money"].sum().reset_index()
    fig = px.line(daily, x="Date", y="money", markers=True, template="plotly_dark", color_discrete_sequence=["#FFD700"])
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("☕ Top Products")
    top_products = df_filtered["coffee_name"].value_counts().head(10).reset_index()
    top_products.columns = ["coffee_name", "count"]
    fig = px.bar(top_products, x="coffee_name", y="count", color="coffee_name", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🕒 Sales by Hour")
    hours = df_filtered.groupby("hour_of_day")["money"].sum().reset_index()
    fig = px.bar(hours, x="hour_of_day", y="money", template="plotly_dark", color_discrete_sequence=["#00BFFF"])
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("💰 Cumulative Revenue")
    cum = df_filtered.groupby("Date")["money"].sum().cumsum().reset_index()
    fig = px.line(cum, x="Date", y="money", template="plotly_dark", color_discrete_sequence=["#32CD32"])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
---
📌 This dashboard demonstrates end-to-end business analytics with interactive KPIs, charts, and insights.
""")
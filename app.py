import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sales Analytics Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".xlsx"):
            return pd.read_excel(uploaded_file)
        return pd.read_csv(uploaded_file)
    return pd.read_csv("data/sales_data.csv", parse_dates=["Date"])

st.title("📊 Sales Analytics Dashboard")
st.caption("Interactive Streamlit dashboard for sales, profit, customers, products, and regional performance.")

uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
df = load_data(uploaded)

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

st.sidebar.header("Filters")
if "Date" in df.columns and df["Date"].notna().any():
    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    dates = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(dates, tuple) and len(dates) == 2:
        df = df[(df["Date"].dt.date >= dates[0]) & (df["Date"].dt.date <= dates[1])]

for col, label in [
    ("Region", "Region"), ("Category", "Category"),
    ("Sales_Channel", "Sales Channel"), ("Customer_Segment", "Customer Segment")
]:
    if col in df.columns:
        vals = sorted(df[col].dropna().astype(str).unique())
        selected = st.sidebar.multiselect(label, vals, default=vals)
        df = df[df[col].astype(str).isin(selected)]

sales = df["Sales"].sum() if "Sales" in df.columns else 0
profit = df["Profit"].sum() if "Profit" in df.columns else 0
orders = df["Order_ID"].nunique() if "Order_ID" in df.columns else len(df)
aov = sales / orders if orders else 0
margin = (profit / sales * 100) if sales else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Sales", f"₹{sales:,.0f}")
c2.metric("Total Profit", f"₹{profit:,.0f}")
c3.metric("Total Orders", f"{orders:,}")
c4.metric("Avg. Order Value", f"₹{aov:,.0f}")
c5.metric("Profit Margin", f"{margin:.1f}%")

st.divider()

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

left, right = st.columns(2)

if "Date" in df.columns:
    monthly = df.assign(Month=df["Date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False)[["Sales","Profit"]].sum()
    with left:
        st.subheader("Monthly Sales & Profit")
        st.line_chart(monthly.set_index("Month")[["Sales","Profit"]])

if "Category" in df.columns:
    cat = df.groupby("Category", as_index=False)[["Sales","Profit"]].sum().sort_values("Sales", ascending=False)
    with right:
        st.subheader("Category Performance")
        st.bar_chart(cat.set_index("Category")[["Sales","Profit"]])

left, right = st.columns(2)

if "Region" in df.columns:
    reg = df.groupby("Region", as_index=False)[["Sales","Profit"]].sum().sort_values("Profit", ascending=False)
    with left:
        st.subheader("Regional Performance")
        st.bar_chart(reg.set_index("Region")[["Sales","Profit"]])

if "Product" in df.columns:
    prod = df.groupby("Product", as_index=False)[["Sales","Profit"]].sum().sort_values("Sales", ascending=False).head(10)
    with right:
        st.subheader("Top 10 Products by Sales")
        st.bar_chart(prod.set_index("Product")[["Sales"]])

st.subheader("🔎 Automated Business Insights")
insights = []
if "Category" in df.columns:
    best_cat = df.groupby("Category")["Sales"].sum().idxmax()
    insights.append(f"Highest-sales category: {best_cat}.")
if "Region" in df.columns:
    best_reg = df.groupby("Region")["Profit"].sum().idxmax()
    insights.append(f"Highest-profit region: {best_reg}.")
if "Product" in df.columns:
    best_product = df.groupby("Product")["Sales"].sum().idxmax()
    insights.append(f"Top product by sales: {best_product}.")
if "Customer_Segment" in df.columns:
    seg = df.groupby("Customer_Segment")["Sales"].sum()
    insights.append(f"Highest-sales customer segment: {seg.idxmax()}.")
for x in insights:
    st.write("• " + x)

st.subheader("📋 Filtered Transaction Data")
st.dataframe(df, use_container_width=True, height=350)
st.download_button(
    "⬇️ Download filtered data as CSV",
    df.to_csv(index=False).encode("utf-8"),
    "filtered_sales_data.csv",
    "text/csv"
)

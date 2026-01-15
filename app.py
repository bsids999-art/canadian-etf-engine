import streamlit as st
import pandas as pd
from src.etf_data_loader import load_etf_prices

st.set_page_config(page_title="Canadian ETF Paycheque Engine", layout="wide")

st.title("🇨🇦 Canadian ETF Paycheque Engine")
st.caption("Maximum growth → future income replacement (5–10 year horizon)")

# Load ETF universe
etfs = pd.read_csv("etf_universe.csv")
fundamentals = pd.read_csv("etf_fundamentals.csv")

tickers = etfs["ticker"].tolist()

# Load market data
with st.spinner("Loading ETF price data..."):
    price_df = load_etf_prices(tickers)

if price_df.empty:
    st.error("No ETF price data returned.")
    st.stop()

# Merge with fundamentals
df = price_df.merge(fundamentals, on="ticker", how="left")

# Income filter
st.sidebar.header("Income Filters")
min_yield = st.sidebar.slider("Minimum distribution yield", 0.0, 0.10, 0.04, step=0.005)

df = df[df["distribution_yield"] >= min_yield]

if df.empty:
    st.warning("No ETFs meet the income criteria.")
    st.stop()

# Growth + income score
df["income_score"] = df["distribution_yield"] * 100
df["growth_score"] = df["cagr_5y"] * 100

df["total_score"] = (
    0.6 * df["growth_score"] +
    0.4 * df["income_score"]
)

# Display
st.subheader("Top Canadian ETFs for Growth → Income")
st.dataframe(
    df.sort_values("total_score", ascending=False).style.format({
        "cagr_5y": "{:.2%}",
        "distribution_yield": "{:.2%}",
        "total_score": "{:.1f}"
    })
)
# ===============================
# AUTOMATIC PORTFOLIO BUILDER
# ===============================

st.header("🧩 Automatic Portfolio Builder")

portfolio_type = st.selectbox(
    "Select investment phase",
    ["Growth Phase", "Transition Phase", "Paycheque Phase"]
)

if portfolio_type == "Growth Phase":
    target_categories = ["Growth"]
    max_weight = 0.20

elif portfolio_type == "Transition Phase":
    target_categories = ["Growth", "Balanced", "Income"]
    max_weight = 0.15

else:
    target_categories = ["Income", "Real Assets", "Balanced"]
    max_weight = 0.12

portfolio_df = df[df["category"].isin(target_categories)].copy()

if portfolio_df.empty:
    st.warning("No ETFs available for this portfolio type.")
else:
    portfolio_df["weight"] = 1 / len(portfolio_df)
    portfolio_df["weight"] = portfolio_df["weight"].clip(upper=max_weight)
    portfolio_df["weight"] = portfolio_df["weight"] / portfolio_df["weight"].sum()

    st.subheader("📊 Suggested Portfolio Allocation")
    st.dataframe(
        portfolio_df[["ticker", "category", "distribution_yield", "weight"]]
        .sort_values("weight", ascending=False)
        .style.format({
            "distribution_yield": "{:.2%}",
            "weight": "{:.1%}"
        })
    )

    portfolio_yield = (
        portfolio_df["distribution_yield"] * portfolio_df["weight"]
    ).sum()

    st.metric("Estimated Portfolio Yield", f"{portfolio_yield:.2%}")

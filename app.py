import streamlit as st
import pandas as pd
from src.etf_data_loader import load_etf_prices

st.set_page_config(page_title="Canadian ETF Engine", layout="wide")

st.title("🇨🇦 Canadian ETF Intelligence Engine")
st.caption("Growth → Income portfolio research for 5–10 year timelines")

# Load ETF universe
etfs = pd.read_csv("etf_universe.csv")
tickers = etfs["ticker"].tolist()

st.subheader("ETF Universe")
st.dataframe(etfs)

# Load data
with st.spinner("Loading ETF data..."):
    df = load_etf_prices(tickers)

if df.empty:
    st.error("No ETF data returned.")
else:
    st.subheader("ETF Performance Metrics (5-Year)")
    st.dataframe(
        df.sort_values("cagr_5y", ascending=False).style.format({
            "cagr_5y": "{:.2%}",
            "volatility": "{:.2%}",
            "max_drawdown": "{:.2%}"
        })
    )

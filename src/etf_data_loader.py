import yfinance as yf
import pandas as pd

def load_etf_prices(tickers):
    prices = yf.download(
        tickers,
        period="5y",
        auto_adjust=True,
        threads=True,
        group_by="ticker"
    )

    records = []

    for ticker in tickers:
        try:
            if ticker not in prices:
                continue

            close = prices[ticker]["Close"].dropna()
            if close.empty:
                continue

            returns = close.pct_change().dropna()

            records.append({
                "ticker": ticker,
                "price": close.iloc[-1],
                "cagr_5y": (close.iloc[-1] / close.iloc[0]) ** (1/5) - 1,
                "volatility": returns.std() * (252 ** 0.5),
                "max_drawdown": (close / close.cummax() - 1).min()
            })
        except Exception:
            continue

    return pd.DataFrame(records)

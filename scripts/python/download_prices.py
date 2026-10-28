
from pathlib import Path

import pandas as pd
import yfinance as yf


START_DATE = "2016-01-01"
END_DATE = "2026-01-01"
RAW_DIR = Path("data/raw")


def download_ticker(ticker):
    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        actions=True,
        progress=False,
        threads=False,
    )

    if df.empty:
        print(f"No data returned for {ticker}")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    df.columns.name = None

    df = df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
            "Dividends": "dividends",
            "Stock Splits": "stock_splits",
        }
    )

    df.insert(1, "ticker", ticker)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DIR / f"{ticker}.csv"
    df.to_csv(output_path, index=False)

    print(f"{ticker}: saved {len(df)} rows to {output_path}")


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL"]

    for ticker in tickers:
        download_ticker(ticker)

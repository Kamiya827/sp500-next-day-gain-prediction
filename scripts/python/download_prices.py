
from pathlib import Path

import pandas as pd
import yfinance as yf


START_DATE = "2016-01-01"
END_DATE = "2026-01-01"
RAW_DIR = Path("data/raw")


def download_ticker(ticker):
    output_path = RAW_DIR / f"{ticker}.csv"
    existing = None
    start_date = START_DATE

    if output_path.exists():
        existing = pd.read_csv(output_path)
        if not existing.empty:
            last_date = pd.to_datetime(existing["date"]).max()
            start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

            if start_date >= END_DATE:
                print(f"{ticker}: already up to date")
                return {"ticker": ticker, "status": "up_to_date", "error": ""}
    try:
        df = yf.download(
            ticker,
            start=start_date,
            end=END_DATE,
            auto_adjust=False,
            actions=True,
            progress=False,
            threads=False,
        )
    except Exception as e:
        print(f"{ticker}: download failed - {e}")
        return {"ticker": ticker, "status": "failed", "error": str(e)}

    if df.empty:
        print(f"{ticker}: no data returned")
        return {"ticker": ticker, "status": "empty", "error": "No data returned"}

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

    if existing is not None:
        df = pd.concat([existing, df], ignore_index=True)
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates(subset=["date"], keep="last")
        df = df.sort_values("date")
    
    df.to_csv(output_path, index=False)

    print(f"{ticker}: saved {len(df)} rows to {output_path}")
    return {"ticker": ticker, "status": "success", "error": ""}


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL"]

    results = [download_ticker(ticker) for ticker in tickers]

    log_dir = Path("outputs/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(results).to_csv(
        log_dir / "download_manifest.csv", index=False
    )

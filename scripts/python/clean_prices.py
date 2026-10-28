
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

COLUMNS = [
    "date", "ticker", "open", "high", "low", "close",
    "adj_close", "volume", "dividends", "stock_splits"
]

NUMERIC_COLUMNS = [
    "open", "high", "low", "close", "adj_close",
    "volume", "dividends", "stock_splits"
]


def clean_ticker(path):
    df = pd.read_csv(path)

    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")

    df = df[COLUMNS].copy()

    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")

    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / path.name
    df.to_csv(output_path, index=False)

    print(f"{path.stem}: standardized {len(df)} rows")


if __name__ == "__main__":
    for path in sorted(RAW_DIR.glob("*.csv")):
        clean_ticker(path)

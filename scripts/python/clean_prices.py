
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

    
    # Identify duplicate ticker-date records
    duplicates = df.duplicated(subset=["ticker", "date"], keep=False)
    conflicting = df.loc[duplicates].groupby(["ticker", "date"]).nunique(dropna=False)
    if (conflicting > 1).any().any():
        raise ValueError(f"{path.name}: conflicting duplicate records")

    duplicate_count = df.duplicated(subset=["ticker", "date"]).sum()
    df = df.drop_duplicates(subset=["ticker", "date"])

    # Remove observations with invalid prices or volume
    price_columns = ["open", "high", "low", "close"]
    invalid_prices = df[price_columns].isna().any(axis=1)
    invalid_prices |= (df[price_columns] <= 0).any(axis=1)

    invalid_volume = df["volume"].isna() | (df["volume"] < 0)
    zero_volume = (df["volume"] == 0).sum()

    invalid_rows = invalid_prices | invalid_volume
    removed_count = invalid_rows.sum()
    df = df.loc[~invalid_rows].copy()

    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    print(
        f"{path.stem}: duplicates={duplicate_count}, "
        f"invalid_removed={removed_count}, zero_volume={zero_volume}"
    )


    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / path.name
    df.to_csv(output_path, index=False)

    print(f"{path.stem}: standardized {len(df)} rows")


if __name__ == "__main__":
    for path in sorted(RAW_DIR.glob("*.csv")):
        clean_ticker(path)


from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
REQUIRED = {"date", "ticker", "open", "high", "low", "close", "volume"}

failed = False

for path in sorted(RAW_DIR.glob("*.csv")):
    df = pd.read_csv(path)
    errors = []

    missing = REQUIRED - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
    else:
        dates = pd.to_datetime(df["date"], errors="coerce")

        if dates.isna().any():
            errors.append("Invalid dates")
        if df.duplicated(subset=["ticker", "date"]).any():
            errors.append("Duplicate ticker-date rows")
        if df[list(REQUIRED - {"date", "ticker"})].isna().any().any():
            errors.append("Missing OHLCV values")
        if (df[["open", "high", "low", "close"]] <= 0).any().any():
            errors.append("Nonpositive prices")
        if (df["volume"] < 0).any():
            errors.append("Negative volume")
        if not (df["ticker"] == path.stem).all():
            errors.append("Ticker mismatch")

    status = "PASS" if not errors else "FAIL"

    if errors:
        failed = True

    print(f"{path.stem}: {status} ({len(df)} rows)")

    for error in errors:
        print(f"  - {error}")
    if failed:
        raise SystemExit(1)

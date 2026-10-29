from pathlib import Path
import pandas as pd

import exchange_calendars as xcals

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/interim")
THRESHOLD = 0.01


def build_targets(df):
    df = df.sort_values(["ticker", "date"]).copy()

    df["date"] = pd.to_datetime(df["date"])

    calendar = xcals.get_calendar("XNYS")
    sessions = calendar.sessions_in_range(df["date"].min(), df["date"].max())
    sessions = sessions.tz_localize(None)
    # NYSE closed for Jimmy Carter's national day of mourning
    sessions = sessions.drop(pd.Timestamp("2025-01-09"))
    next_sessions = pd.Series(sessions[1:], index=sessions[:-1])

    expected_next = df["date"].map(next_sessions)
    actual_next = df.groupby("ticker")["date"].shift(-1)

    next_close = df.groupby("ticker")["close"].shift(-1)
    df["next_day_return"] = next_close / df["close"] - 1
    df.loc[actual_next != expected_next, "next_day_return"] = float("nan")

    df["target"] = (df["next_day_return"] >= THRESHOLD).astype("Int64")
    df.loc[df["next_day_return"].isna(), "target"] = pd.NA

    return df


if __name__ == "__main__":
    frames = [
        pd.read_csv(path)
        for path in sorted(PROCESSED_DIR.glob("*.csv"))
    ]

    if not frames:
        raise ValueError("No processed price files found")

    prices = pd.concat(frames, ignore_index=True)
    labeled = build_targets(prices)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "sample_targets.csv"
    labeled.to_csv(output_path, index=False)

    print("Total rows:", len(labeled))
    print("Positive labels:", (labeled["target"] == 1).sum())
    print("Negative labels:", (labeled["target"] == 0).sum())
    print("Unlabeled rows:", labeled["target"].isna().sum())
    print("Saved:", output_path)
from pathlib import Path
import pandas as pd
import exchange_calendars as xcals

INPUT_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/interim")


def build_features(df):
    df = df.sort_values(["ticker", "date"]).copy()
    df["date"] = pd.to_datetime(df["date"])

    calendar = xcals.get_calendar("XNYS")
    sessions = calendar.sessions_in_range(df["date"].min(), df["date"].max())
    sessions = sessions.tz_localize(None)

    # NYSE closed for Jimmy Carter's national day of mourning
    sessions = sessions.drop(pd.Timestamp("2025-01-09"), errors="ignore")

    session_numbers = pd.Series(range(len(sessions)), index=sessions)
    df["_session"] = df["date"].map(session_numbers)

    for days in (1, 5, 10, 20):
        previous_close = df.groupby("ticker")["close"].shift(days)
        previous_session = df.groupby("ticker")["_session"].shift(days)

        df[f"return_{days}d"] = df["close"] / previous_close - 1

        valid_window = df["_session"] - previous_session == days
        df.loc[~valid_window, f"return_{days}d"] = float("nan")

    return df.drop(columns="_session")
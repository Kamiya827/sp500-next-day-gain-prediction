from pathlib import Path

import pandas as pd

MEMBERSHIP_PATH = Path("data/membership/sp500_membership.csv")


def filter_membership(df, membership=None):
    if membership is None:
        membership = pd.read_csv(MEMBERSHIP_PATH)

    membership = membership.copy()
    membership["date_added"] = pd.to_datetime(membership["date_added"])
    membership["date_ended"] = pd.to_datetime(membership["date_ended"])

    result = df.copy()
    result["date"] = pd.to_datetime(result["date"])

    # Keep the original row order and avoid duplicate observations.
    result["_row_id"] = range(len(result))

    merged = result.merge(
        membership[["ticker", "date_added", "date_ended"]],
        on="ticker",
        how="inner",
    )

    active = (
        (merged["date"] >= merged["date_added"])
        & (
            merged["date_ended"].isna()
            | (merged["date"] < merged["date_ended"])
        )
    )

    filtered = merged.loc[active].copy()

    if filtered["_row_id"].duplicated().any():
        raise ValueError("Overlapping membership intervals detected")

    filtered = filtered.sort_values("_row_id")

    return filtered.drop(
        columns=["_row_id", "date_added", "date_ended"]
    ).reset_index(drop=True)

from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/membership/sp500_membership.csv")

df = pd.read_csv(DATA_PATH)

required = ["company_name", "ticker", "date_added", "date_ended"]
assert all(col in df.columns for col in required)

df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["date_ended"] = pd.to_datetime(df["date_ended"], errors="coerce")

print("Total membership records:", len(df))
print("Unique tickers:", df["ticker"].nunique())
print("Missing start dates:", df["date_added"].isna().sum())
print("Invalid intervals:", (
    df["date_ended"].notna()
    & (df["date_ended"] < df["date_added"])
).sum())
print("Duplicate rows:", df.duplicated().sum())

# Count constituents on the first calendar day of each month.
dates = pd.date_range("2016-01-01", "2025-12-01", freq="MS")

counts = []

for date in dates:
    active = df[
        (df["date_added"] <= date)
        & (
            df["date_ended"].isna()
            | (df["date_ended"] >= date)
        )
    ]

    counts.append({
        "date": date,
        "members": active["ticker"].nunique(),
    })

summary = pd.DataFrame(counts)

print("\nMembership count summary:")
print(summary["members"].describe().to_string())

print("\nJanuary membership counts by year:")
print(
    summary[summary["date"].dt.month == 1]
    .to_string(index=False)
)

print("\nMonths with unusual constituent counts:")
unusual = summary[
    (summary["members"] < 490)
    | (summary["members"] > 510)
]

print(
    unusual.to_string(index=False)
    if not unusual.empty
    else "None under the initial 490–510 screening range."
)

OUTPUT_DIR = Path("outputs/validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "membership_monthly_counts.csv"
summary.to_csv(output_path, index=False)

print(f"\nSaved: {output_path}")

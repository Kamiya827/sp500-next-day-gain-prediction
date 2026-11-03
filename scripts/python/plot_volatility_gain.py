
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_features import build_features
from build_targets import build_targets

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/figures")

tickers = ["AAPL", "GOOGL", "MSFT", "NVDA"]

frames = [
    pd.read_csv(DATA_DIR / f"{ticker}.csv")
    for ticker in tickers
]

prices = pd.concat(frames, ignore_index=True)
df = build_targets(build_features(prices))

# Exclude rows without a valid feature or next-day outcome.
df = df.dropna(subset=["volatility_20", "target"]).copy()

labels = ["Lowest", "Low", "Middle", "High", "Highest"]

# Use five equally populated volatility groups.
df["volatility_group"] = pd.qcut(
    df["volatility_20"],
    q=5,
    labels=labels,
)

summary = df.groupby(
    "volatility_group", observed=True
)["target"].agg(["mean", "count"])

assert summary["count"].sum() == len(df)
assert summary["count"].min() > 0
assert summary["mean"].between(0, 1).all()

print("Valid observations:", len(df))
print("\nNext-day gain rate by volatility:")
print(summary.to_string())

fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(
    summary.index.astype(str),
    summary["mean"].astype(float) * 100,
    color="#2563eb",
)

ax.bar_label(bars, fmt="%.1f%%", padding=3)

ax.set_title("Next-Day ≥1% Gain Rate by Historical Volatility")
ax.set_xlabel("20-Day Historical Volatility Quintile")
ax.set_ylabel("Next-Day Gain Rate (%)")
ax.set_ylim(0, float(summary["mean"].max()) * 120)

ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)

fig.text(
    0.5, 0.02,
    "Pilot sample: AAPL, GOOGL, MSFT, NVDA | 2016–2025",
    ha="center",
    fontsize=9,
)

fig.subplots_adjust(bottom=0.23)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "gain_rate_by_volatility.png"
fig.savefig(output_path, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {output_path}")

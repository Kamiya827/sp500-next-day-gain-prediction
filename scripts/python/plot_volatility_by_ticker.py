
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
labels = ["Lowest", "Low", "Middle", "High", "Highest"]

frames = [
    pd.read_csv(DATA_DIR / f"{ticker}.csv")
    for ticker in tickers
]

df = build_targets(build_features(pd.concat(frames, ignore_index=True)))
df = df.dropna(subset=["volatility_20", "target"]).copy()

# Use common volatility thresholds across all four stocks.
df["volatility_group"] = (
    df.groupby("ticker")["volatility_20"]
    .transform(lambda x: pd.qcut(x, q=5, labels=labels))
)

summary = (
    df.groupby(["ticker", "volatility_group"], observed=True)["target"]
    .agg(["mean", "count"])
    .reset_index()
)

assert summary["count"].sum() == len(df)

print("\nGain rates by ticker and volatility quintile:")
print(
    summary.pivot(
        index="volatility_group",
        columns="ticker",
        values="mean"
    ).round(3).to_string()
)

print("\nObservation counts:")
print(
    summary.pivot(
        index="volatility_group",
        columns="ticker",
        values="count"
    ).to_string()
)

fig, ax = plt.subplots(figsize=(10, 6))

for ticker in tickers:
    subset = summary[summary["ticker"] == ticker]
    subset = subset.set_index("volatility_group").reindex(labels)

    ax.plot(
        labels,
        subset["mean"].astype(float) * 100,
        marker="o",
        linewidth=2,
        label=ticker,
    )

ax.set_title("Next-Day ≥1% Gain Rate by Stock-Specific Volatility")
ax.set_xlabel("Stock-Specific 20-Day Volatility Quintile")
ax.set_ylabel("Next-Day Gain Rate (%)")
ax.set_ylim(bottom=0)
ax.legend(title="Stock")
ax.grid(alpha=0.25)

fig.text(
    0.5, 0.02,
    "Pilot sample: AAPL, GOOGL, MSFT, NVDA | 2016–2025",
    ha="center",
    fontsize=9,
)

fig.subplots_adjust(bottom=0.20)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / "volatility_gain_by_ticker.png"

fig.savefig(output_path, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {output_path}")

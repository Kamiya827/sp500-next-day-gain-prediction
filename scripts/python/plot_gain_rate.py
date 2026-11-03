
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

# Reuse the existing feature and target calculations.
df = build_features(prices)
df = build_targets(df)

# Keep observations with a valid feature and target.
df = df.dropna(subset=["return_1d", "target"]).copy()

# Divide historical returns into five equally populated groups.
df["return_group"] = pd.qcut(
    df["return_1d"],
    q=5,
    labels=["Lowest", "Low", "Middle", "High", "Highest"],
)

summary = df.groupby(
    "return_group", observed=True
)["target"].agg(["mean", "count"])

# Validate that every observation is accounted for.
assert summary["count"].sum() == len(df)
assert summary["count"].min() > 0

print(summary.to_string())

fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(
    summary.index.astype(str),
    summary["mean"] * 100,
    color="#2563eb",
)

ax.bar_label(bars, fmt="%.1f%%", padding=3)
ax.set_xlabel("Historical 1-Day Return Quintile")
ax.set_ylabel("Next-Day Gain Rate (%)")
ax.set_title("Next-Day ≥1% Gain Rate by Historical Return")
ax.set_ylim(0, max(summary["mean"] * 100) * 1.2)
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
output_path = OUTPUT_DIR / "gain_rate_by_return.png"

fig.savefig(output_path, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {output_path}")

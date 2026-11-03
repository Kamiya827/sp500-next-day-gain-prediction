
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_features import build_features

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/figures")

tickers = ["AAPL", "GOOGL", "MSFT", "NVDA"]

features = [
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "relative_volume_20",
    "volatility_20",
]

frames = [
    pd.read_csv(DATA_DIR / f"{ticker}.csv")
    for ticker in tickers
]

prices = pd.concat(frames, ignore_index=True)
df = build_features(prices)

# Use complete observations for all six predictors.
valid = df.dropna(subset=features).copy()

assert len(valid) > 0
assert valid[features].notna().all().all()

# Pearson correlation coefficients.
correlation = valid[features].corr(method="pearson")

assert correlation.shape == (6, 6)
assert np.allclose(np.diag(correlation), 1.0)

print("Valid observations:", len(valid))
print("\nFeature correlation matrix:")
print(correlation.round(3).to_string())

fig, ax = plt.subplots(figsize=(9, 7))

heatmap = ax.imshow(
    correlation,
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
)

labels = [
    "1-Day Return",
    "5-Day Return",
    "10-Day Return",
    "20-Day Return",
    "Relative Volume",
    "20-Day Volatility",
]

ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=40, ha="right")
ax.set_yticklabels(labels)

for i in range(len(features)):
    for j in range(len(features)):
        value = correlation.iloc[i, j]
        ax.text(
            j, i, f"{value:.2f}",
            ha="center",
            va="center",
            color="white" if abs(value) > 0.6 else "black",
        )

ax.set_title("Correlation Between Historical Market Features", pad=18)

colorbar = fig.colorbar(heatmap, ax=ax, shrink=0.8)
colorbar.set_label("Pearson Correlation")

fig.subplots_adjust(bottom=0.22)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / "feature_correlation_heatmap.png"

fig.savefig(output_path, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {output_path}")

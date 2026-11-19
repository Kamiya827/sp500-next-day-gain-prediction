from pathlib import Path

import pandas as pd

from build_targets import build_targets
from build_features import build_features
from filter_membership import filter_membership


PROCESSED_DIR = Path("data/processed")
OUTPUT_PATH = Path("data/interim/pilot_modeling_dataset.csv")

FEATURE_COLUMNS = [
    "return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "relative_volume_20",
    "volatility_20",
]


def main():
    paths = sorted(PROCESSED_DIR.glob("*.csv"))

    if not paths:
        raise ValueError("No processed price files found")

    prices = pd.concat(
        [pd.read_csv(path) for path in paths],
        ignore_index=True,
    )

    labeled = build_targets(prices)
    featured = build_features(labeled)
    filtered = filter_membership(featured)

    modeling = filtered.dropna(
        subset=FEATURE_COLUMNS + ["target"]
    ).copy()

    modeling = modeling.sort_values(
        ["date", "ticker"]
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    modeling.to_csv(OUTPUT_PATH, index=False)

    print("Original rows:", len(prices))
    print("After membership filtering:", len(filtered))
    print("Modeling rows:", len(modeling))
    print("Positive labels:", (modeling["target"] == 1).sum())
    print("Negative labels:", (modeling["target"] == 0).sum())
    print("Duplicate ticker-date rows:",
          modeling.duplicated(["ticker", "date"]).sum())
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
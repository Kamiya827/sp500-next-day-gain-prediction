from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/interim")
THRESHOLD = 0.01


def build_targets(df):
    df = df.sort_values(["ticker", "date"]).copy()

    next_close = df.groupby("ticker")["close"].shift(-1)
    df["next_day_return"] = next_close / df["close"] - 1

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
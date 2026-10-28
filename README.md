# Predicting Next-Day S&P 500 Stock Gains Using Historical Market Data

CSDS 133 project by Logan and Ariel.

## Research question
Can historical returns, relative trading volume, and volatility help predict whether an S&P 500 stock gains at least 1% on the next trading day?

## Structure
- `data/raw`: downloaded source data (not committed)
- `data/external`: historical index membership from Ariel (not committed)
- `data/processed`: generated analysis data (not committed)
- `scripts/python`: collection, cleaning, feature engineering
- `scripts/r`: modeling and evaluation
- `tests`: deterministic tests
- `outputs`: generated tables, figures, logs
- `presentation`: original Quarto proposal and CSS

## Setup
Create a Python virtual environment, activate it, and run `python -m pip install -r requirements.txt`.
Install R and the packages `readr`, `dplyr`, `ggplot2`, and `pROC`.

## Methodological decisions to confirm
- After-close prediction timestamp
- Split-adjusted close-to-close price return as target
- Historical membership source and effective-date conventions
- Date-based train/validation/test periods
- Coverage and limitations for delisted securities

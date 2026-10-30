# Predicting Next-Day S&P 500 Stock Gains Using Historical Market Data

CSDS 133 Introduction to Data Science project by Logan Leong and Ariel.

## Research Question

Can historical stock returns, relative trading volume, and volatility help predict whether an S&P 500 stock will gain at least 1% on the next trading day?

## Project Overview

This project uses historical stock market data to develop and evaluate machine learning models for predicting next-day stock price movements.

The prediction target is binary:

- `1`: The stock's closing price increases by at least 1% on the next trading day.
- `0`: The stock's closing price increases by less than 1%, remains unchanged, or decreases.

Predictions are intended to use only information available after the market closes on the prediction date.

The initial analysis covers January 2016 through December 2025. Historical S&P 500 membership will be used to reduce survivorship bias.

## Features

The following features have been implemented:

| Feature | Description |
|---|---|
| `return_1d` | Previous 1-trading-day price return |
| `return_5d` | Previous 5-trading-day price return |
| `return_10d` | Previous 10-trading-day price return |
| `return_20d` | Previous 20-trading-day price return |
| `relative_volume_20` | Current volume divided by the average volume of the previous 20 trading sessions |
| `volatility_20` | Standard deviation of the most recent 20 daily returns |

Feature calculations are performed separately for each stock. Missing trading sessions are checked to prevent calculations from using incomplete historical windows.

## Repository Structure

- `data/raw`: Downloaded source data (not committed)
- `data/external`: Historical S&P 500 membership data (not committed)
- `data/processed`: Cleaned and generated datasets (not committed)
- `scripts/python`: Data collection, cleaning, target construction, and feature engineering
- `scripts/r`: Modeling and evaluation
- `tests`: Automated tests
- `outputs`: Generated tables, figures, and logs
- `presentation`: Original Quarto proposal and CSS

## Setup

### Python

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### R

Install R and the following packages:

```r
install.packages(c("readr", "dplyr", "ggplot2", "pROC"))
```

## Collaboration

Development takes place on separate Git branches.

- `main`: Stable project code
- `feature/modeling`: Feature engineering and model development
- `feature/membership`: Historical S&P 500 membership collection

Changes should be submitted through pull requests before being merged into `main`.

## Methodological Decisions to Confirm

- Final prediction timestamp and available information
- Split-adjusted close-to-close price returns as the target
- Historical S&P 500 membership source and effective-date conventions
- Chronological training, validation, and testing periods
- Data coverage and limitations for delisted securities

## Project Status

Feature engineering and initial validation are complete for four sample stocks: AAPL, GOOGL, MSFT, and NVDA.

Historical index membership collection, full-universe data preparation, model training, and evaluation are still in progress.
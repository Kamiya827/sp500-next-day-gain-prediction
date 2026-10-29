# Stock Price Conventions

Data source: Yahoo Finance via yfinance.

Download settings:
- auto_adjust=False
- actions=True
- Start date: 2016-01-01
- End date: 2026-01-01 (exclusive)

## Price Columns

- close: Split-adjusted closing price.
- adj_close: Closing price adjusted for splits and dividends.
- stock_splits: Recorded stock split events.
- dividends: Recorded cash dividend events.

## Verification

Split events were examined for AAPL, GOOGL, and NVDA.

Observed closing-price movements around these events were
consistent with split-adjusted historical prices.

Dividend events were also identified for all four sample tickers.
The close and adj_close columns differed throughout the sample.

## Modeling Decision

Use close to calculate next-day price returns.

next_day_return = close(t+1) / close(t) - 1

target = 1 if next_day_return >= 0.01, otherwise 0.

The final observation for each ticker has no known next-day
return and must not receive a target label.

Returns must be calculated using consecutive valid trading
observations for the same ticker.

Do not apply stock split adjustments again.

Do not use adj_close for the prediction target.

All features must use information available by the close
of the prediction date.

Historical S&P 500 membership must be applied before
constructing the final modeling dataset.

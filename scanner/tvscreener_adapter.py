import pandas as pd
from tvscreener import StockScreener, StockField, Market

def fetch_universe():
    """Fetches market data from TradingView for Pakistan stocks."""
    ss = StockScreener()
    
    try:
        ss.set_markets(Market.PAKISTAN)
    except Exception:
        pass

    # Request available fields from StockField
    ss.select(
        StockField.NAME,
        StockField.PRICE,
        StockField.CHANGE_PERCENT,
        StockField.VOLUME,
        StockField.RELATIVE_STRENGTH_INDEX_14,
        StockField.SIMPLE_MOVING_AVERAGE_50,
        StockField.SIMPLE_MOVING_AVERAGE_200
    )
    
    return ss.get()

def normalize(df, target_tickers=None):
    """Dynamically maps tvscreener columns and filters for target universe tickers."""
    if df is None or df.empty:
        return []

    df = df.copy()

    # Identify a single primary ticker column to prevent duplicate 'Ticker' columns
    primary_ticker_col = None
    for candidate in ["Symbol", "Ticker", "Name"]:
        if candidate in df.columns:
            primary_ticker_col = candidate
            break

    # Dynamic column mapping to standard names (handles suffixes like '(1D)')
    column_mapping = {}
    for col in df.columns:
        if "Relative Strength Index" in col:
            column_mapping[col] = "RSI"
        elif "Simple Moving Average (50)" in col:
            column_mapping[col] = "SMA50"
        elif "Simple Moving Average (200)" in col:
            column_mapping[col] = "SMA200"
        elif col == primary_ticker_col:
            column_mapping[col] = "Ticker"
        elif "Change" in col:
            column_mapping[col] = "Change"
        elif col == "Price":
            column_mapping[col] = "Price"
        elif col == "Volume":
            column_mapping[col] = "Volume"

    df = df.rename(columns=column_mapping)

    # Ensure no duplicate columns exist in memory
    df = df.loc[:, ~df.columns.duplicated()]

    # Filter to KMI-30 tickers if provided
    if target_tickers and "Ticker" in df.columns:
        # Use vectorized pandas string accessors
        df["Ticker_Clean"] = (
            df["Ticker"]
            .astype(str)
            .str.split(":")
            .str[-1]
            .str.upper()
            .str.strip()
        )
        target_set = {t.upper().strip() for t in target_tickers}
        df = df[df["Ticker_Clean"].isin(target_set)]

    return df.to_dict(orient="records")

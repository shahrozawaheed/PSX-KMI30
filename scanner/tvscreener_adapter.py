import pandas as pd
from tvscreener import StockScreener, StockField, Market

def fetch_universe():
    """Fetches market data from TradingView for Pakistan stocks."""
    ss = StockScreener()
    
    # Set the market directly using the Market enum
    try:
        ss.set_markets(Market.PAKISTAN)
    except AttributeError:
        # Fallback if Market.PAKISTAN is not available in your library version
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

    # Dynamic column mapping to standard names (handles suffixes like '(1D)')
    column_mapping = {}
    for col in df.columns:
        if "Relative Strength Index" in col:
            column_mapping[col] = "RSI"
        elif "Simple Moving Average (50)" in col:
            column_mapping[col] = "SMA50"
        elif "Simple Moving Average (200)" in col:
            column_mapping[col] = "SMA200"
        elif col in ["Symbol", "Name", "Ticker"]:
            column_mapping[col] = "Ticker"
        elif "Change" in col:
            column_mapping[col] = "Change"
        elif col == "Price":
            column_mapping[col] = "Price"
        elif col == "Volume":
            column_mapping[col] = "Volume"

    df = df.rename(columns=column_mapping)

    # Filter to KMI-30 tickers if provided
    if target_tickers and "Ticker" in df.columns:
        # Strip prefixes like 'PSX:' or 'PAKISTAN:' if present
        df["Ticker_Clean"] = df["Ticker"].astype(str).apply(lambda x: x.split(":")[-1].upper().strip())
        df = df[df["Ticker_Clean"].isin([t.upper().strip() for t in target_tickers])]

    return df.to_dict(orient="records")

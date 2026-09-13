"""TradingView Screener adapter.

This module intentionally discovers fields at runtime because tvscreener's
field inventory can change. It also keeps the scanner strict: if a required
field cannot be found, it reports exactly what is missing.

NOTE: tvscreener is an unofficial third-party library. It supports multi-
timeframe technical fields, but Supertrend availability/name must be verified
against the installed field inventory before live alerts are enabled.
"""

import importlib
import pandas as pd


def _field_by_exact_or_search(StockField, name, search_term=None):
    if hasattr(StockField, name):
        return getattr(StockField, name)
    if search_term:
        hits = StockField.search(search_term)
        if hits:
            # search() may return field objects or metadata depending on version.
            for h in hits:
                candidate = h.get("name") if isinstance(h, dict) else getattr(h, "name", None)
                if candidate and hasattr(StockField, candidate):
                    return getattr(StockField, candidate)
    return None


def build_query():
    tvs = importlib.import_module("tvscreener")
    StockScreener, StockField = tvs.StockScreener, tvs.StockField

    required = {
        "name": _field_by_exact_or_search(StockField, "NAME", "name"),
        "price": _field_by_exact_or_search(StockField, "PRICE", "price"),
        "rsi": _field_by_exact_or_search(StockField, "RELATIVE_STRENGTH_INDEX_14", "rsi"),
        "sma50": _field_by_exact_or_search(StockField, "SIMPLE_MOVING_AVERAGE_50", "moving average 50"),
        "sma200": _field_by_exact_or_search(StockField, "SIMPLE_MOVING_AVERAGE_200", "moving average 200"),
        "volume": _field_by_exact_or_search(StockField, "VOLUME", "volume"),
    }
    missing=[k for k,v in required.items() if v is None]
    if missing:
        raise RuntimeError(
            "Required TradingView Screener fields were not found: "
            + ", ".join(missing)
            + ". Run the field-discovery diagnostics before enabling alerts."
        )

    # Daily interval for all technical fields.
    selected = [
        required["name"],
        required["price"],
        required["rsi"].with_interval("1D"),
        required["sma50"].with_interval("1D"),
        required["sma200"].with_interval("1D"),
        required["volume"],
    ]

    ss=StockScreener()
    ss.select(*selected)
    return ss, StockField


def fetch_universe():
    ss, _ = build_query()
    df=ss.get()
    if not isinstance(df, pd.DataFrame):
        df=pd.DataFrame(df)
    return df


def normalize(df, universe):
    """Best-effort normalization of TradingView output.

    We keep this isolated because column labels can differ between tvscreener
    versions. The diagnostic output should be checked once after installation.
    """
    cols={str(c).lower(): c for c in df.columns}
    def find(*names):
        for n in names:
            if n.lower() in cols:
                return cols[n.lower()]
        return None

    name_col=find("name")
    price_col=find("price")
    rsi_col=find("relative_strength_index_14","rsi")
    sma50_col=find("simple_moving_average_50","sma50")
    sma200_col=find("simple_moving_average_200","sma200")
    vol_col=find("volume")

    if not all([name_col,price_col,rsi_col,sma50_col,sma200_col,vol_col]):
        raise RuntimeError(
            "Unexpected tvscreener columns. Actual columns: "
            + ", ".join(map(str, df.columns))
        )

    # TradingView stock screener normally returns an exchange-qualified symbol
    # column in newer versions. If present, use it; otherwise match by ticker
    # appearing in the name/symbol text.
    sym_col=find("symbol","ticker","exchange_symbol")
    out=[]
    for _,r in df.iterrows():
        hay=str(r[sym_col] if sym_col else r[name_col]).upper()
        for symbol,meta in universe.items():
            if symbol in hay:
                out.append({
                    "symbol":symbol, "name":meta["name"], "url":meta["url"],
                    "price":r[price_col], "rsi":r[rsi_col], "sma50":r[sma50_col],
                    "sma200":r[sma200_col], "volume":r[vol_col],
                })
                break
    return out

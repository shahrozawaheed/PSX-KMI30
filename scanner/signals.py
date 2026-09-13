def evaluate_signals(rows):
    """Analyzes normalized rows and returns triggered alert signals."""
    alerts = []
    
    # Strategy Thresholds
    RSI_OVERSOLD = 35.0
    RSI_OVERBOUGHT = 70.0
    MIN_VOLUME = 100_000  # Adjust as needed

    for row in rows:
        symbol = row.get("Ticker_Clean", row.get("Ticker", "N/A"))
        price = row.get("Price", 0.0)
        change_pct = row.get("Change", 0.0)
        volume = row.get("Volume", 0)
        rsi = row.get("RSI")
        sma50 = row.get("SMA50")
        sma200 = row.get("SMA200")

        if rsi is None:
            continue

        # Criteria 1: Oversold RSI Bullish Signal
        if rsi <= RSI_OVERSOLD and volume >= MIN_VOLUME:
            trend_status = "Bullish" if sma50 and price > sma50 else "Neutral/Bearish"
            alerts.append({
                "ticker": symbol,
                "price": price,
                "change": change_pct,
                "rsi": rsi,
                "trend": trend_status,
                "reason": f"🟢 **Oversold RSI** ({rsi:.2f} <= {RSI_OVERSOLD})"
            })

        # Criteria 2: Overbought RSI Bearish Signal
        elif rsi >= RSI_OVERBOUGHT and volume >= MIN_VOLUME:
            alerts.append({
                "ticker": symbol,
                "price": price,
                "change": change_pct,
                "rsi": rsi,
                "trend": "Overextended",
                "reason": f"🔴 **Overbought RSI** ({rsi:.2f} >= {RSI_OVERBOUGHT})"
            })

    return alerts

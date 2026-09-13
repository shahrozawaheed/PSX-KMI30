"""V1 signal rules. No entry/SL/TP calculations are included yet."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Signal:
    symbol: str
    name: str
    url: str
    signal: str
    price: float
    rsi: float
    sma50: float
    sma200: float
    volume: float
    volume_avg20: Optional[float]
    supertrend: Optional[str]
    reasons: list[str]


def evaluate(row, meta):
    """Evaluate one row. Returns Signal or None.

    V1:
      BUY: price > 200 SMA, 50 SMA > 200 SMA, RSI > 50, Supertrend UP
      STRONG BUY: BUY + volume > 20D average + 20D breakout
      SELL: price < 200 SMA, 50 SMA < 200 SMA, RSI < 50, Supertrend DOWN
      STRONG SELL: SELL + volume > 20D average + 20D breakdown

    Supertrend and breakout fields are deliberately treated as required for a
    signal. If the upstream screener does not expose them, the scanner fails
    safely rather than substituting a different formula.
    """
    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    price=num(row.get("price"))
    rsi=num(row.get("rsi"))
    sma50=num(row.get("sma50"))
    sma200=num(row.get("sma200"))
    volume=num(row.get("volume"))
    volavg=num(row.get("volume_avg20"))
    high20=num(row.get("high20"))
    low20=num(row.get("low20"))
    st=(str(row.get("supertrend") or "").strip().lower())

    required=[price,rsi,sma50,sma200,volume]
    if any(v is None for v in required):
        return None
    if st not in {"up","down","uptrend","downtrend","buy","sell","1","-1"}:
        return None

    st_up=st in {"up","uptrend","buy","1"}
    st_down=st in {"down","downtrend","sell","-1"}

    buy = price > sma200 and sma50 > sma200 and rsi > 50 and st_up
    sell = price < sma200 and sma50 < sma200 and rsi < 50 and st_down

    if not (buy or sell):
        return None

    reasons=[]
    if buy:
        reasons=["Price > 200 SMA","50 SMA > 200 SMA","RSI > 50","Supertrend UP"]
        strong=(volavg is not None and volume > volavg and high20 is not None and price > high20)
        signal="STRONG BUY" if strong else "BUY"
        if strong:
            reasons += ["Volume > 20D average","Price > previous 20D high"]
    else:
        reasons=["Price < 200 SMA","50 SMA < 200 SMA","RSI < 50","Supertrend DOWN"]
        strong=(volavg is not None and volume > volavg and low20 is not None and price < low20)
        signal="STRONG SELL" if strong else "SELL"
        if strong:
            reasons += ["Volume > 20D average","Price < previous 20D low"]

    return Signal(
        symbol=meta["symbol"], name=meta["name"], url=meta["url"], signal=signal,
        price=price, rsi=rsi, sma50=sma50, sma200=sma200, volume=volume,
        volume_avg20=volavg, supertrend=st, reasons=reasons
    )

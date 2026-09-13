import json
import os
from pathlib import Path

from config.stocks import KMI30_STOCKS
from scanner.tvscreener_adapter import fetch_universe, normalize
from scanner.signals import evaluate
from scanner.discord import send

STATE=Path("data/sent_alerts.json")


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def main():
    print("KMI-30 scanner starting...")
    print(f"Universe: {len(KMI30_STOCKS)} stocks")

    raw=fetch_universe()
    print(f"TradingView screener rows: {len(raw)}")
    rows=normalize(raw, KMI30_STOCKS)

    signals=[]
    for row in rows:
        s=evaluate(row, KMI30_STOCKS[row["symbol"]])
        if s:
            signals.append(s)

    print(f"Signals: {len(signals)}")
    for s in signals:
        print(s.symbol, s.signal, s.reasons)

    # During initial testing, set DRY_RUN=true so nothing is posted.
    if os.getenv("DRY_RUN","true").lower()=="true":
        print("DRY_RUN=true; Discord not contacted.")
        return

    state=load_state()
    new=[]
    for s in signals:
        # Signal key is intentionally based on the current signal type.
        # We will refine this to candle date once the upstream field support is
        # confirmed.
        key=f"{s.symbol}:{s.signal}"
        if not state.get(key):
            new.append(s)
            state[key]=True

    if new:
        send(new)
        save_state(state)
        print(f"Sent {len(new)} new Discord alert(s).")
    else:
        print("No new Discord alerts.")


if __name__=="__main__":
    main()

import json
import os
from pathlib import Path

from config.stocks import KMI30_STOCKS
from scanner.tvscreener_adapter import fetch_universe, normalize
from scanner.signals import evaluate
from scanner.discord import send

STATE = Path("data/sent_alerts.json")


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def main():
    print("KMI-30 scanner starting...")
    print(f"Universe: {len(KMI30_STOCKS)} stocks")

    raw = fetch_universe()
    print(f"TradingView screener rows: {len(raw) if raw is not None else 0}")
    
    rows = normalize(raw, KMI30_STOCKS)
    print(f"Normalized rows: {len(rows)}")

    signals = []
    for row in rows:
        # Pass the row directly into evaluate()
        s = evaluate(row)
        if s:
            signals.append(s)

    print(f"Signals detected: {len(signals)}")
    for s in signals:
        # Access attributes dynamically or via dataclass / namedtuple
        symbol = getattr(s, "symbol", row.get("symbol", "N/A"))
        signal_name = getattr(s, "signal", "ALERT")
        reasons = getattr(s, "reasons", "")
        print(f"[{symbol}] {signal_name}: {reasons}")

    # Check DRY_RUN flag (Defaults to false if not specified in Production)
    if os.getenv("DRY_RUN", "false").lower() == "true":
        print("DRY_RUN=true; Discord notification skipped.")
        return

    state = load_state()
    new_signals = []
    for s in signals:
        symbol = getattr(s, "symbol", "UNKNOWN")
        signal_type = getattr(s, "signal", "SIGNAL")
        key = f"{symbol}:{signal_type}"
        
        if not state.get(key):
            new_signals.append(s)
            state[key] = True

    if new_signals:
        send(new_signals)
        save_state(state)
        print(f"Sent {len(new_signals)} new Discord alert(s).")
    else:
        print("No new Discord alerts to send.")


if __name__ == "__main__":
    main()

import os
import requests


def format_signal(s):
    return (
        f"**{s.signal}**\n\n"
        f"**{s.symbol}**\n"
        f"{s.name}\n\n"
        f"Price: {s.price:.2f}\n"
        f"RSI: {s.rsi:.2f}\n"
        f"50 SMA: {s.sma50:.2f}\n"
        f"200 SMA: {s.sma200:.2f}\n"
        f"Supertrend: {s.supertrend.upper()}\n"
        f"Volume: {s.volume:,.0f}\n\n"
        f"**Conditions met:**\n" + "\n".join(f"• {x}" for x in s.reasons) +
        f"\n\nTimeframe: 1D\n"
        f"PSX Company Page: {s.url}"
    )


def send(signals):
    webhook=os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("DISCORD_WEBHOOK_URL secret is not set.")

    for s in signals:
        r=requests.post(webhook, json={"content": format_signal(s)}, timeout=20)
        r.raise_for_status()

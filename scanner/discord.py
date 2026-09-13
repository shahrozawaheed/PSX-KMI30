import os
import requests

def send_discord_alerts(alerts):
    """Sends list of formatted strategy alerts to Discord webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("Warning: DISCORD_WEBHOOK_URL environment variable is not set.")
        return

    if not alerts:
        print("No strategy triggers detected. Skipping Discord notification.")
        return

    embeds = []
    for item in alerts:
        color = 3066993 if "🟢" in item["reason"] else 15158332
        embeds.append({
            "title": f"PSX KMI-30 Alert: {item['ticker']}",
            "color": color,
            "fields": [
                {"name": "Trigger Reason", "value": item["reason"], "inline": False},
                {"name": "Price (PKR)", "value": f"{item['price']:.2f}", "inline": True},
                {"name": "Change", "value": f"{item['change']:.2f}%", "inline": True},
                {"name": "RSI (14)", "value": f"{item['rsi']:.2f}", "inline": True},
                {"name": "Trend Context", "value": str(item.get("trend", "N/A")), "inline": True}
            ],
            "footer": {"text": "PSX KMI-30 Automated Screener Bot"}
        })

    payload = {
        "username": "PSX KMI-30 Bot",
        "embeds": embeds
    }

    res = requests.post(webhook_url, json=payload)
    if res.status_code == 204:
        print(f"Successfully sent {len(alerts)} alert(s) to Discord.")
    else:
        print(f"Failed to post alert: HTTP {res.status_code} - {res.text}")

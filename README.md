# PSX KMI-30 Discord Alerts

V1 of a KMI-30 daily technical scanner.

## Current goal

Test the algorithm first. V1 intentionally does **not** calculate Entry,
Stop Loss, or Take Profit.

### Signal rules

BUY:
- Price > 200 SMA
- 50 SMA > 200 SMA
- RSI(14) > 50
- Supertrend = UP

STRONG BUY:
- BUY conditions
- Volume > 20-day average
- Price > previous 20-day high

SELL:
- Price < 200 SMA
- 50 SMA < 200 SMA
- RSI(14) < 50
- Supertrend = DOWN

STRONG SELL:
- SELL conditions
- Volume > 20-day average
- Price < previous 20-day low

## Data architecture

The initial adapter uses `tvscreener` for TradingView Screener fields.
`tvscreener` is an unofficial third-party Python library. It exposes
multi-timeframe technical fields and field discovery, but exact field
availability can change. Therefore this repo fails safely if a required field
is not available instead of silently substituting another indicator.

The PSX company URLs are stored for all 30 stocks even though V1 does not need
them for calculations.

## Discord

Add a GitHub repository secret:

`DISCORD_WEBHOOK_URL`

Keep `DRY_RUN=true` until the scanner has been verified.

## Scheduling

No GitHub schedule is configured.

Use cron-job.org to trigger either:
- GitHub Actions `workflow_dispatch`, or
- GitHub `repository_dispatch` with event type `scan`.

## Important next validation

Run the scanner once in DRY_RUN mode and inspect the actual TradingView
Screener columns/fields returned by the installed library. Supertrend support
must be verified before live alerts are enabled.

## Disclaimer

This is an experimental research/alerting tool, not investment advice.

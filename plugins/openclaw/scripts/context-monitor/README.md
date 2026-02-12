# Context Monitor

One-time check of OpenClaw session context usage with threshold alerts.

## Usage

```bash
./context-monitor.sh
```

## What It Does

1. Checks current session file size
2. Outputs size in MB for monitoring

## Integration

```bash
# Add to crontab
0 * * * * ~/.openclaw/workspace/scripts/context-monitor.sh
```

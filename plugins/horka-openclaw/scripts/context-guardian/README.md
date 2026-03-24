# Context Guardian Daemon

Background daemon that monitors OpenClaw sessions and auto-compacts when they exceed threshold.

## Usage

```bash
# Direct run
./context-guardian-daemon.sh

# Via launchd
launchctl load com.openclaw.context-guardian.plist
```

## Behavior

1. Cleans blobs from sessions (via `clean-session-blobs.sh`)
2. Finds sessions over threshold (default: 10MB)
3. Runs `session-compactor.sh` if needed
4. Restarts OpenClaw gateway after compaction

## Configuration

- `THRESHOLD_MB`: Session size limit (default: 10)
- Logs to `~/.openclaw/logs/context-guardian.log`

## Dependencies

- `session-compactor.sh`
- `clean-session-blobs.sh`

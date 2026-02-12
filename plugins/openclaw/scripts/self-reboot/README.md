# Self Reboot

Graceful OpenClaw gateway restart with optional update and session compaction.

## Usage

```bash
./self-reboot.sh              # Full: update + compact + restart
./self-reboot.sh --update     # Update only + restart
./self-reboot.sh --compact    # Compact only + restart
./self-reboot.sh --full       # All steps (default)
```

## Steps

1. **Update**: Check and install latest OpenClaw version via npm
2. **Compact**: Run session-compactor to preserve learnings
3. **Restart**: Stop and start gateway

## When to Use

- Context approaching limits
- After long sessions
- Before major context-heavy tasks
- When experiencing slowdowns

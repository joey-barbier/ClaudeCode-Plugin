#!/bin/bash
# context-guardian-daemon.sh — Autonomous context overflow protection
# Runs independently of OpenClaw to prevent crashes
# Install as launchd plist or cron job

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
ARCHIVE_DIR="$HOME/.openclaw/agents/main/archive"
COMPACTOR="$HOME/.openclaw/workspace/scripts/session-compactor.sh"
LOG_FILE="$HOME/.openclaw/logs/context-guardian.log"
THRESHOLD_MB=${THRESHOLD_MB:-10}

mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$ARCHIVE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Guardian check started (threshold: ${THRESHOLD_MB}MB)"

# First: clean any blobs from sessions
BLOB_CLEANER="$HOME/.openclaw/workspace/scripts/clean-session-blobs.sh"
if [[ -x "$BLOB_CLEANER" ]]; then
    log "Running blob cleaner..."
    "$BLOB_CLEANER" >> "$LOG_FILE" 2>&1
fi

# Find sessions over threshold
THRESHOLD_BYTES=$((THRESHOLD_MB * 1024 * 1024))
NEEDS_COMPACTION=false

for f in "$SESSIONS_DIR"/*.jsonl; do
    [[ -f "$f" ]] || continue
    [[ "$f" == *.bak ]] && continue
    
    SIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    SIZE_MB=$((SIZE / 1024 / 1024))
    
    if [[ "$SIZE" -gt "$THRESHOLD_BYTES" ]]; then
        log "⚠️ Large session found: $(basename "$f") = ${SIZE_MB}MB"
        NEEDS_COMPACTION=true
    fi
done

if $NEEDS_COMPACTION; then
    log "🧹 Running compactor..."
    
    # Run compactor
    if [[ -x "$COMPACTOR" ]]; then
        "$COMPACTOR" --threshold-mb "$THRESHOLD_MB" >> "$LOG_FILE" 2>&1
        COMPACT_STATUS=$?
        log "Compactor exit status: $COMPACT_STATUS"
    else
        log "❌ Compactor not found or not executable: $COMPACTOR"
        exit 1
    fi
    
    # Restart OpenClaw gateway
    log "🔄 Restarting OpenClaw gateway..."
    openclaw gateway restart >> "$LOG_FILE" 2>&1
    
    log "✅ Guardian cycle complete"
else
    log "✅ All sessions under threshold"
fi

#!/bin/bash
# clean-session-blobs.sh — Remove base64 blobs from session files
# Replaces audio/image data URLs with placeholders to save context space

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
LOG_FILE="$HOME/.openclaw/logs/blob-cleaner.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

for f in "$SESSIONS_DIR"/*.jsonl; do
    [[ -f "$f" ]] || continue
    [[ "$f" == *.bak ]] && continue
    
    # Check for blobs (audio/image base64)
    BLOB_COUNT=$(grep -c 'data:\(audio\|image\)/[^;]*;base64,' "$f" 2>/dev/null || echo 0)
    
    if [[ "$BLOB_COUNT" -gt 0 ]]; then
        ORIGINAL_SIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f")
        
        log "Found $BLOB_COUNT blob(s) in $(basename "$f")"
        
        # Create backup
        cp "$f" "$f.blob-backup"
        
        # Replace audio blobs with placeholder
        sed -i.tmp 's/data:audio\/[^;]*;base64,[A-Za-z0-9+\/=]*/"[AUDIO_BLOB_REMOVED]"/g' "$f"
        
        # Replace image blobs with placeholder  
        sed -i.tmp 's/data:image\/[^;]*;base64,[A-Za-z0-9+\/=]*/"[IMAGE_BLOB_REMOVED]"/g' "$f"
        
        # Cleanup temp files
        rm -f "$f.tmp"
        
        NEW_SIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f")
        SAVED=$((ORIGINAL_SIZE - NEW_SIZE))
        SAVED_KB=$((SAVED / 1024))
        
        log "Cleaned $(basename "$f"): saved ${SAVED_KB}KB"
        echo "🧹 Cleaned $BLOB_COUNT blob(s) from $(basename "$f"), saved ${SAVED_KB}KB"
    fi
done

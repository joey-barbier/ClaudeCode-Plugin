#!/bin/bash
# Self-reboot OpenClaw — update + extract learnings + hard restart
# Usage: ./self-reboot.sh [--update] [--compact] [--full]
# --update  : npm update openclaw avant restart
# --compact : extraire learnings + archiver session avant restart  
# --full    : update + compact + restart

set -e

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPTS="$WORKSPACE/scripts"
OPENCLAW=$(command -v openclaw 2>/dev/null || echo "$HOME/.nvm/versions/node/$(node -v)/bin/openclaw")

ACTION="${1:---full}"

echo "🔄 Self-reboot OpenClaw"
echo "========================"

# Step 1: Update si demandé
if [[ "$ACTION" == "--update" || "$ACTION" == "--full" ]]; then
    echo ""
    echo "📦 Step 1: Checking for updates..."
    CURRENT=$($OPENCLAW --version 2>/dev/null || echo "unknown")
    echo "   Current: $CURRENT"
    
    LATEST=$(npm info openclaw version 2>/dev/null || echo "unknown")
    echo "   Latest:  $LATEST"
    
    if [[ "$CURRENT" != "$LATEST" ]]; then
        echo "   → Updating..."
        [ -s "$HOME/.nvm/nvm.sh" ] && source "$HOME/.nvm/nvm.sh"
        npm install -g openclaw@latest 2>&1 | tail -1
        NEW=$($OPENCLAW --version 2>/dev/null || echo "unknown")
        echo "   ✅ Updated to $NEW"
    else
        echo "   ✅ Already up to date"
    fi
fi

# Step 2: Compact session si demandé
if [[ "$ACTION" == "--compact" || "$ACTION" == "--full" ]]; then
    echo ""
    echo "🧹 Step 2: Session compaction..."
    if [[ -f "$SCRIPTS/session-compactor.sh" ]]; then
        bash "$SCRIPTS/session-compactor.sh" 2>&1 | tail -3
    else
        echo "   ⚠️ session-compactor.sh not found, skipping"
    fi
fi

# Step 3: Hard restart gateway (stop + start)
echo ""
echo ""
echo "🚀 Step 3: Hard restart gateway..."
echo "   Stopping..."
$OPENCLAW gateway stop 2>&1 || true
sleep 2

echo "   Starting..."
$OPENCLAW gateway start 2>&1 || echo "   ⚠️ Start failed"
sleep 3

# Verify
NEW_VERSION=$($OPENCLAW --version 2>/dev/null || echo "unknown")
echo ""
echo "✅ Self-reboot complete!"
echo "   Version: $NEW_VERSION"
echo "   Gateway will reconnect automatically."

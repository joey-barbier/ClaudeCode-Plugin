#!/bin/bash
# session-compactor.sh — Smart session compaction with intelligent summarization
# Usage: ./session-compactor.sh [--dry-run] [--threshold-mb N]

set -e

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
ARCHIVE_DIR="$HOME/.openclaw/agents/main/archive"  # Parent level to avoid accidental reload
WORKSPACE="$HOME/.openclaw/workspace"
THRESHOLD_MB=${THRESHOLD_MB:-20}
DRY_RUN=false

# Parse args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true ;;
        --threshold-mb) THRESHOLD_MB="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "🔍 Scanning sessions in $SESSIONS_DIR (threshold: ${THRESHOLD_MB}MB)"

# Find large sessions
THRESHOLD_BYTES=$((THRESHOLD_MB * 1024 * 1024))
LARGE_SESSIONS=()

for f in "$SESSIONS_DIR"/*.jsonl; do
    [[ -f "$f" ]] || continue
    [[ "$f" == *.bak ]] && continue
    [[ "$f" == *.lock ]] && continue
    
    SIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    if [[ "$SIZE" -gt "$THRESHOLD_BYTES" ]]; then
        SIZE_MB=$((SIZE / 1024 / 1024))
        echo "  ⚠️  $(basename "$f"): ${SIZE_MB}MB"
        LARGE_SESSIONS+=("$f")
    fi
done

if [[ ${#LARGE_SESSIONS[@]} -eq 0 ]]; then
    echo "✅ No sessions above ${THRESHOLD_MB}MB threshold"
    exit 0
fi

echo ""
echo "📦 Found ${#LARGE_SESSIONS[@]} large session(s) to process"

if $DRY_RUN; then
    echo "🏃 Dry run mode — no changes will be made"
    exit 0
fi

mkdir -p "$ARCHIVE_DIR"

# Process each large session
for SESSION_FILE in "${LARGE_SESSIONS[@]}"; do
    SESSION_ID=$(basename "$SESSION_FILE" .jsonl)
    SIZE_MB=$(($(stat -f%z "$SESSION_FILE" 2>/dev/null || stat -c%s "$SESSION_FILE" 2>/dev/null) / 1024 / 1024))
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📜 Processing: $SESSION_ID (${SIZE_MB}MB)"
    
    # Extract date range
    FIRST_DATE=$(head -1 "$SESSION_FILE" | jq -r '.timestamp // empty' | cut -dT -f1)
    LAST_DATE=$(tail -1 "$SESSION_FILE" | jq -r '.timestamp // empty' | cut -dT -f1)
    echo "   Date range: $FIRST_DATE → $LAST_DATE"
    
    # Extract clean messages for analysis
    EXTRACT_FILE="/tmp/session-extract-$SESSION_ID.txt"
    echo "   📝 Extracting messages..."
    
    jq -r '
        select(.type == "message") |
        select(.message.role == "user" or .message.role == "assistant") |
        {
            role: .message.role,
            text: [.message.content[]? | select(.type == "text") | .text] | join(" ")
        } |
        select(.text | length > 30) |
        select(.text | contains("HEARTBEAT") | not) |
        "[\(.role | ascii_upcase)] \(.text[0:800])\n---"
    ' "$SESSION_FILE" > "$EXTRACT_FILE"
    
    EXTRACT_LINES=$(wc -l < "$EXTRACT_FILE" | tr -d ' ')
    echo "   Extracted $EXTRACT_LINES lines"
    
    # Truncate if too large (max 100KB for Claude)
    if [[ $(wc -c < "$EXTRACT_FILE") -gt 100000 ]]; then
        echo "   ✂️  Truncating to 100KB..."
        # Keep first 40% and last 40%
        TOTAL_LINES=$(wc -l < "$EXTRACT_FILE" | tr -d ' ')
        HEAD_LINES=$((TOTAL_LINES * 40 / 100))
        TAIL_LINES=$((TOTAL_LINES * 40 / 100))
        {
            head -$HEAD_LINES "$EXTRACT_FILE"
            echo -e "\n[...middle of session truncated...]\n"
            tail -$TAIL_LINES "$EXTRACT_FILE"
        } > "/tmp/truncated-$SESSION_ID.txt"
        mv "/tmp/truncated-$SESSION_ID.txt" "$EXTRACT_FILE"
    fi
    
    # Generate intelligent summary via Claude Code
    SUMMARY_FILE="/tmp/session-summary-$SESSION_ID.md"
    echo "   🤖 Generating intelligent summary via Claude..."
    
    PROMPT="Tu es un assistant qui extrait les informations importantes d'une session de conversation.

Voici le contenu d'une session du $FIRST_DATE au $LAST_DATE (${SIZE_MB}MB original).

Produis un résumé STRUCTURÉ avec EXACTEMENT ce format (max 60 lignes) :

## 📦 Session Compactée [$FIRST_DATE → $LAST_DATE]

### Configurations réalisées
- [liste des configs/setups faits]

### Décisions prises
- [liste des décisions importantes]

### Learnings
- [problème] → [solution]

### Projets touchés
- [projet]: [ce qui a été fait]

RÈGLES:
- SEULEMENT ce qui est explicitement dans les logs
- PAS d'invention
- Concis et factuel
- Ignorer les salutations, small talk, heartbeats
- Focus: configs, décisions, learnings, projets

Contenu de la session:
$(cat "$EXTRACT_FILE")"

    # Call Claude Code CLI for summarization
    cd "$WORKSPACE"
    if claude -p "$PROMPT" --output-format text > "$SUMMARY_FILE" 2>/dev/null; then
        echo "   ✅ Summary generated ($(wc -l < "$SUMMARY_FILE" | tr -d ' ') lines)"
    else
        echo "   ⚠️  Claude CLI failed, using basic summary"
        cat > "$SUMMARY_FILE" << EOF
## 📦 Session Compactée [$FIRST_DATE → $LAST_DATE]

*Résumé automatique (Claude CLI indisponible)*

### Stats
- Session ID: $SESSION_ID
- Taille: ${SIZE_MB}MB
- Messages extraits: $EXTRACT_LINES lignes

### Note
Analyser manuellement l'archive si besoin:
\`gunzip -c $ARCHIVE_DIR/${SESSION_ID}.jsonl.gz | less\`
EOF
    fi
    
    # Append to daily memory file
    MEMORY_FILE="$WORKSPACE/memory/${FIRST_DATE}.md"
    if [[ -f "$SUMMARY_FILE" && -s "$SUMMARY_FILE" ]]; then
        echo "" >> "$MEMORY_FILE"
        echo "---" >> "$MEMORY_FILE"
        echo "" >> "$MEMORY_FILE"
        cat "$SUMMARY_FILE" >> "$MEMORY_FILE"
        echo "" >> "$MEMORY_FILE"
        echo "   ✅ Summary added to $MEMORY_FILE"
    fi
    
    # Archive original
    TIMESTAMP=$(date '+%Y%m%d-%H%M')
    ARCHIVE_FILE="$ARCHIVE_DIR/${SESSION_ID}-${TIMESTAMP}.jsonl.gz"
    echo "   📦 Archiving to $ARCHIVE_FILE..."
    gzip -c "$SESSION_FILE" > "$ARCHIVE_FILE"
    
    # Clear the session (keep only header)
    echo "   🗑️  Clearing session..."
    head -1 "$SESSION_FILE" > "/tmp/session-header-$SESSION_ID.jsonl"
    mv "/tmp/session-header-$SESSION_ID.jsonl" "$SESSION_FILE"
    
    NEW_SIZE=$(stat -f%z "$SESSION_FILE" 2>/dev/null || stat -c%s "$SESSION_FILE" 2>/dev/null)
    echo "   ✅ Cleared: ${SIZE_MB}MB → $(echo "scale=2; $NEW_SIZE / 1024" | bc)KB"
    
    # Cleanup
    rm -f "$EXTRACT_FILE" "$SUMMARY_FILE"
done

# Cleanup: move .bak files and old sessions to archive
echo ""
echo "🧹 Cleaning up stale files..."
BAK_COUNT=0
OLD_COUNT=0

# Move .bak files
for bak in "$SESSIONS_DIR"/*.bak; do
    [[ -f "$bak" ]] || continue
    mv "$bak" "$ARCHIVE_DIR/"
    ((BAK_COUNT++))
done

# Move .deleted files
for del in "$SESSIONS_DIR"/*.deleted.*; do
    [[ -f "$del" ]] || continue
    mv "$del" "$ARCHIVE_DIR/"
    ((OLD_COUNT++))
done

if [[ $BAK_COUNT -gt 0 || $OLD_COUNT -gt 0 ]]; then
    echo "   Moved $BAK_COUNT .bak and $OLD_COUNT .deleted files to archive"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Smart compaction complete!"
echo "   Archives: $ARCHIVE_DIR"
echo "   Summaries: $WORKSPACE/memory/"
echo ""
echo "📁 Sessions folder now contains only active sessions"

# Clean Session Blobs

Remove base64 audio/image blobs from session files to reduce context size.

## Problem

Voice messages add ~150KB base64 blobs per message. These accumulate and waste context tokens.

## Usage

```bash
./clean-session-blobs.sh
```

## What It Does

1. Scans session JSONL files for base64 blobs
2. Replaces with `[AUDIO_BLOB_REMOVED]` / `[IMAGE_BLOB_REMOVED]` placeholders
3. Creates `.blob-backup` before modification

## Typical Savings

- 10 voice messages: ~1.5MB → ~50KB
- 50 voice messages: ~7.5MB → ~250KB

#!/bin/bash
# Copyright (c) 2026 Nardo. AGPL-3.0 — see LICENSE
# fswatch wrapper — watches ~/.claude/skills/ recursively,
# debounces (5s latency), then runs rescan on changed skills.
# Launched by launchd, runs forever.

SKILLS_DIR="$HOME/.claude/skills"
RESCAN="$HOME/.claude/skills/skillguard/scripts/rescan_skills.py"
LOG="/tmp/skill-rescan.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') skill-rescan-watch started (pid $$)" >> "$LOG"

/opt/homebrew/bin/fswatch \
  --recursive \
  --latency 5 \
  --exclude '\.DS_Store' \
  --exclude '__pycache__' \
  --exclude '\.pyc$' \
  "$SKILLS_DIR" | while read -r _event; do
    # Drain any queued events within the debounce window
    while read -r -t 2 _extra; do :; done
    echo "$(date '+%Y-%m-%d %H:%M:%S') Change detected, rescanning..." >> "$LOG"
    /usr/bin/python3 "$RESCAN" >> "$LOG" 2>&1
done

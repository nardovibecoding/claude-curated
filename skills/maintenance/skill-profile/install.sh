#!/bin/bash
# Copyright (c) 2026 Nardo. AGPL-3.0 — see LICENSE
# Install skillswitch for Claude Code
echo "Installing skillswitch..."

# Copy skill
mkdir -p ~/.claude/skills/skillswitch
cp SKILL.md ~/.claude/skills/skillswitch/

# Copy profile switcher
cp switch-profile.sh ~/.claude/
chmod +x ~/.claude/switch-profile.sh

echo "Installed. Usage:"
echo '  Say "coding mode", "outreach mode", "minimal mode", or "all skills"'
echo '  Or run: ~/.claude/switch-profile.sh <profile>'
echo ""
echo "Edit ~/.claude/switch-profile.sh to customize profiles."

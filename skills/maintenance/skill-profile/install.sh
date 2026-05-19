#!/usr/bin/env bash
set -euo pipefail

AI_TOOL_HOME="${AI_TOOL_HOME:-$HOME/.ai-tool}"
mkdir -p "$AI_TOOL_HOME/skills/skill-profile"
cp SKILL.md switch-profile.sh "$AI_TOOL_HOME/skills/skill-profile/"
chmod +x "$AI_TOOL_HOME/skills/skill-profile/switch-profile.sh"
echo "Installed skill-profile into $AI_TOOL_HOME/skills/skill-profile"

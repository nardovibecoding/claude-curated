#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-all}"
AI_TOOL_HOME="${AI_TOOL_HOME:-$HOME/.ai-tool}"
SKILLS_DIR="$AI_TOOL_HOME/skills"
BACKUP_DIR="$AI_TOOL_HOME/skills-master"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "No skills directory found at $SKILLS_DIR" >&2
  exit 2
fi

if [ ! -d "$BACKUP_DIR" ]; then
  cp -R "$SKILLS_DIR" "$BACKUP_DIR"
fi

case "$PROFILE" in
  all)
    for d in "$BACKUP_DIR"/*/; do
      name="$(basename "$d")"
      if [ -f "$SKILLS_DIR/$name/SKILL.md.disabled" ]; then
        mv "$SKILLS_DIR/$name/SKILL.md.disabled" "$SKILLS_DIR/$name/SKILL.md"
      fi
    done
    ;;
  coding)
    KEEP="red-alert research-council skill-extractor tldr-eli5 skill-profile"
    ;;
  writing)
    KEEP="tldr-eli5 red-alert skill-profile"
    ;;
  minimal)
    KEEP="tldr-eli5 skill-profile"
    ;;
  *)
    echo "Unknown profile: $PROFILE (use: all|coding|writing|minimal)" >&2
    exit 2
    ;;
esac

if [ "$PROFILE" != "all" ]; then
  for d in "$SKILLS_DIR"/*/; do
    [ -f "$d/SKILL.md" ] && mv "$d/SKILL.md" "$d/SKILL.md.disabled" 2>/dev/null || true
  done
  for skill in $KEEP; do
    if [ -f "$SKILLS_DIR/$skill/SKILL.md.disabled" ]; then
      mv "$SKILLS_DIR/$skill/SKILL.md.disabled" "$SKILLS_DIR/$skill/SKILL.md"
    fi
  done
fi

enabled="$(find "$SKILLS_DIR" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Profile: $PROFILE; $enabled skills active"

#!/usr/bin/env bash
set -euo pipefail

CONFIGURE=0
if [ "${1:-}" = "--configure" ]; then
  CONFIGURE=1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_TOOL_HOME="${AI_TOOL_HOME:-$HOME/.ai-tool}"
INSTALL_SKILLS="${INSTALL_SKILLS:-1}"
INSTALL_HOOKS="${INSTALL_HOOKS:-1}"
ASSISTANT_SETTINGS="${ASSISTANT_SETTINGS:-}"

mkdir -p "$AI_TOOL_HOME"

if [ "$INSTALL_SKILLS" = "1" ]; then
  mkdir -p "$AI_TOOL_HOME/skills"
  cp -R "$REPO_DIR/skills/discovery" "$AI_TOOL_HOME/skills/"
  cp -R "$REPO_DIR/skills/maintenance" "$AI_TOOL_HOME/skills/"
  cp -R "$REPO_DIR/skills/security" "$AI_TOOL_HOME/skills/"
  cp -R "$REPO_DIR/skills/workflow" "$AI_TOOL_HOME/skills/"
fi

if [ "$INSTALL_HOOKS" = "1" ]; then
  mkdir -p "$AI_TOOL_HOME/hooks"
  cp -R "$REPO_DIR/hooks/shared" "$AI_TOOL_HOME/hooks/"
  cp -R "$REPO_DIR/hooks/dependency-grep" "$AI_TOOL_HOME/hooks/"
  cp -R "$REPO_DIR/hooks/guard-safety" "$AI_TOOL_HOME/hooks/"
  cp -R "$REPO_DIR/hooks/auto-license" "$AI_TOOL_HOME/hooks/"
  cp -R "$REPO_DIR/hooks/auto-repo-check" "$AI_TOOL_HOME/hooks/"
fi

if [ "$CONFIGURE" = "1" ]; then
  if [ -z "$ASSISTANT_SETTINGS" ]; then
    echo "ASSISTANT_SETTINGS is required when --configure is used." >&2
    exit 2
  fi
  mkdir -p "$(dirname "$ASSISTANT_SETTINGS")"
  python3 "$REPO_DIR/scripts/configure-settings.py" "$ASSISTANT_SETTINGS" "$AI_TOOL_HOME"
fi

echo "Installed simply-skills-curation into $AI_TOOL_HOME"
if [ "$CONFIGURE" != "1" ]; then
  echo "Settings were not changed. Re-run with --configure to opt in."
fi

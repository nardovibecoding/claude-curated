#!/usr/bin/env bash
# Claude Skills Curation — one-liner installer
# curl -fsSL https://raw.githubusercontent.com/nardovibecoding/claude-skills-curation/main/install.sh | bash
set -euo pipefail

INSTALL_DIR="$HOME/claude-skills-curation"
SETTINGS="$HOME/.claude/settings.json"

RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' CYAN='\033[0;36m' BOLD='\033[1m' NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Claude Skills Curation Installer    ║"
echo "  ║   13 hooks + 6 skills for Claude Code ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# --- Clone or update ---
if [ -d "$INSTALL_DIR/.git" ]; then
  echo -e "${YELLOW}→ Updating existing install...${NC}"
  git -C "$INSTALL_DIR" pull --ff-only 2>/dev/null || true
else
  if [ -d "$INSTALL_DIR" ]; then
    echo -e "${RED}✗ $INSTALL_DIR exists but is not a git repo. Remove it first.${NC}"
    exit 1
  fi
  echo -e "${GREEN}→ Cloning repository...${NC}"
  git clone https://github.com/nardovibecoding/claude-skills-curation.git "$INSTALL_DIR"
fi

# --- Patch settings.json ---
echo -e "${GREEN}→ Configuring Claude Code hooks...${NC}"
mkdir -p "$HOME/.claude"

python3 << 'PYEOF'
import json, os

INSTALL_DIR = os.path.expanduser("~/claude-skills-curation")
SETTINGS = os.path.expanduser("~/.claude/settings.json")

if os.path.exists(SETTINGS):
    with open(SETTINGS) as f:
        settings = json.load(f)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
MARKER = "claude-skills-curation"

# Hook definitions from the plugin
TG_HOOKS = {
    "PreToolUse": [
        {"matcher": "Bash", "hooks": [
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/guard-safety/guard_safety.py", "timeout": 5000}
        ]},
    ],
    "PostToolUse": [
        {"matcher": "Bash", "hooks": [
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/vps-sync/auto_vps_sync.py", "timeout": 15000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/dependency-grep/auto_dependency_grep.py", "timeout": 10000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-license/auto_license.py", "timeout": 15000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-repo-check/auto_repo_check.py", "timeout": 5000},
        ]},
        {"matcher": "Edit|Write", "hooks": [
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/dependency-grep/auto_dependency_grep.py", "timeout": 10000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/pip-install/auto_pip_install.py", "timeout": 30000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/bot-restart/auto_bot_restart.py", "timeout": 15000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-skill-sync/auto_skill_sync.py", "timeout": 5000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-restart-process/auto_restart_process.py", "timeout": 15000},
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/memory-index/auto_memory_index.py", "timeout": 5000},
        ]},
    ],
    "UserPromptSubmit": [
        {"matcher": "", "hooks": [
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-context-checkpoint/auto_context_checkpoint.py", "timeout": 3000},
        ]},
    ],
    "Stop": [
        {"matcher": "", "hooks": [
            {"type": "command", "command": f"python3 {INSTALL_DIR}/hooks/auto-content-remind/auto_content_remind.py", "timeout": 3000},
        ]},
    ],
}

for event, entries in TG_HOOKS.items():
    event_hooks = hooks.setdefault(event, [])
    # Remove existing entries from this plugin (idempotent)
    event_hooks[:] = [h for h in event_hooks if not any(MARKER in hook.get("command", "") for hook in h.get("hooks", []))]
    event_hooks.extend(entries)

with open(SETTINGS, "w") as f:
    json.dump(settings, f, indent=2)

print("  Hooks configured in ~/.claude/settings.json")
PYEOF

# --- Done ---
echo ""
echo -e "${GREEN}${BOLD}✓ Claude Skills Curation installed!${NC}"
echo ""
echo -e "  ${BOLD}13 hooks${NC} + ${BOLD}6 skills${NC} are now active."
echo ""
echo -e "  Skills available in Claude Code:"
echo -e "    ${CYAN}/research-council${NC}  — multi-model debate"
echo -e "    ${CYAN}/red-alert${NC}         — adversarial security scan"
echo -e "    ${CYAN}/md-cleanup${NC}        — context budget audit"
echo -e "    ${CYAN}/skill-extractor${NC}   — evaluate community skills"
echo -e "    ${CYAN}/skill-profile${NC}     — switch skill profiles"
echo -e "    ${CYAN}/tldr-eli5${NC}         — explain anything simply"
echo ""
echo -e "  ${YELLOW}Restart Claude Code if it's already running.${NC}"
echo ""

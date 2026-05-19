#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: configure-settings.py SETTINGS_PATH AI_TOOL_HOME", file=sys.stderr)
        return 2

    settings_path = Path(sys.argv[1]).expanduser()
    ai_tool_home = Path(sys.argv[2]).expanduser()

    if settings_path.exists():
        settings = json.loads(settings_path.read_text())
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})
    marker = "simply-skills-curation"
    entries = {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {ai_tool_home}/hooks/guard-safety/guard_safety.py",
                    "timeout": 5000,
                }],
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"python3 {ai_tool_home}/hooks/dependency-grep/auto_dependency_grep.py",
                        "timeout": 10000,
                    },
                    {
                        "type": "command",
                        "command": f"python3 {ai_tool_home}/hooks/auto-license/auto_license.py",
                        "timeout": 5000,
                    },
                    {
                        "type": "command",
                        "command": f"python3 {ai_tool_home}/hooks/auto-repo-check/auto_repo_check.py",
                        "timeout": 5000,
                    },
                ],
            },
            {
                "matcher": "Edit|Write",
                "hooks": [{
                    "type": "command",
                    "command": f"python3 {ai_tool_home}/hooks/dependency-grep/auto_dependency_grep.py",
                    "timeout": 10000,
                }],
            },
        ],
    }

    for event, new_entries in entries.items():
        existing = hooks.setdefault(event, [])
        existing[:] = [
            entry for entry in existing
            if not any(marker in hook.get("command", "") for hook in entry.get("hooks", []))
        ]
        existing.extend(new_entries)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"Updated {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

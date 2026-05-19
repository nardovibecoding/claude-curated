#!/usr/bin/env python3
"""Remind after repo creation to add public project basics."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "shared"))
from hook_base import run_hook


def check(tool_name, tool_input, _input_data):
    if tool_name != "Bash":
        return False
    return bool(re.search(r"gh\s+repo\s+create|git\s+init", tool_input.get("command", "")))


def action(_tool_name, _tool_input, input_data):
    cwd = Path(input_data.get("cwd") or ".")
    missing = [name for name in ("README.md", "LICENSE", "SECURITY.md", ".gitignore")
               if not (cwd / name).exists()]
    if not missing:
        return None
    return "New repo checklist: add " + ", ".join(missing) + " before publishing."


if __name__ == "__main__":
    run_hook(check, action, "auto-license")

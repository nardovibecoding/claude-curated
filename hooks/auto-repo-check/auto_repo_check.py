#!/usr/bin/env python3
"""Remind after git push to check public-facing metadata."""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "shared"))
from hook_base import run_hook


def check(tool_name, tool_input, _input_data):
    if tool_name != "Bash":
        return False
    return bool(re.search(r"git\s+push", tool_input.get("command", "")))


def action(_tool_name, _tool_input, input_data):
    cwd = input_data.get("cwd") or "."
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    remote_url = result.stdout.strip()
    repo_name = remote_url.rstrip("/").split("/")[-1].replace(".git", "") or "repo"

    readme = Path(cwd) / "README.md"
    if not readme.exists():
        return f"Pushed to {repo_name}, but README.md is missing."

    try:
        result = subprocess.run(
            ["git", "-C", cwd, "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        changed = result.stdout.strip().splitlines()
    except Exception:
        changed = []
    stale_triggers = ("SKILL.md", "hooks/", "pyproject.toml", "package.json")
    stale_files = [f for f in changed if any(t in f for t in stale_triggers)]
    if stale_files and "README.md" not in changed:
        return f"Pushed to {repo_name}; check README for: {', '.join(stale_files[:5])}"
    return None


if __name__ == "__main__":
    run_hook(check, action, "auto-repo-check")

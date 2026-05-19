#!/usr/bin/env python3
"""Warn when moved, deleted, or edited files may have references."""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "shared"))
from hook_base import run_hook


def check(tool_name, tool_input, _input_data):
    if tool_name == "Bash":
        return bool(re.search(r"\b(mv|rm|git\s+rm)\b", tool_input.get("command", "")))
    if tool_name in ("Edit", "Write"):
        return bool(tool_input.get("file_path"))
    return False


def _project_root(input_data):
    cwd = input_data.get("cwd") or os.environ.get("PROJECT_ROOT") or "."
    return str(Path(cwd).resolve())


def action(tool_name, tool_input, input_data):
    if tool_name == "Bash":
        parts = tool_input.get("command", "").split()
        files = [p for p in parts if ("/" in p or "." in p) and not p.startswith("-")]
        if not files:
            return None
        basename = Path(files[-1]).name
        if not basename or basename in {".", ".."}:
            return None
        try:
            result = subprocess.run(
                [
                    "grep", "-RIl", basename, _project_root(input_data),
                    "--include=*.py", "--include=*.md", "--include=*.json",
                    "--include=*.sh", "--include=*.yaml", "--include=*.yml",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            return None
        refs = result.stdout.strip().splitlines()[:10]
        if refs:
            return "Dependency check: `{}` still appears in:\n{}".format(
                basename, "\n".join(f"- {ref}" for ref in refs)
            )
        return None

    basename = Path(tool_input.get("file_path", "")).name
    if basename in {"pyproject.toml", "package.json", "requirements.txt", "README.md"}:
        return f"`{basename}` changed. Check install docs and examples before publishing."
    return None


if __name__ == "__main__":
    run_hook(check, action, "dependency-grep")

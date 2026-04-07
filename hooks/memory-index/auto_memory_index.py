#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""PostToolUse hook: check if new memory file is listed in MEMORY.md index.

Fires when Claude writes a new .md file in a memory/ directory.
Warns if the file isn't listed in MEMORY.md so nothing falls through the cracks.

Register in settings.json under hooks.PostToolUse:
  python3 ~/.claude/hooks/auto_memory_index.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_base import run_hook


def _find_memory_index(file_path):
    """Locate MEMORY.md in the same memory/ directory."""
    p = Path(file_path)
    for parent in p.parents:
        if parent.name == "memory":
            idx = parent / "MEMORY.md"
            return idx if idx.exists() else None
    return None


def check(tool_name, tool_input, input_data):
    if tool_name != "Write":
        return False
    file_path = tool_input.get("file_path", "")
    filename = Path(file_path).name
    return (
        "memory/" in file_path
        and file_path.endswith(".md")
        and "MEMORY.md" not in file_path
        and not filename.startswith("convo_")
    )


def action(tool_name, tool_input, input_data):
    file_path = tool_input.get("file_path", "")
    filename = Path(file_path).name
    index = _find_memory_index(file_path)
    if not index:
        return None
    if filename in index.read_text():
        return None
    return f"New memory file `{filename}` is NOT in MEMORY.md index. Add it."


if __name__ == "__main__":
    run_hook(check, action, "auto_memory_index")

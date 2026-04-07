#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""PostToolUse hook: bump importance + access_count when a memory file is read.

Stats stored in separate JSON to avoid race conditions with Edit tool.

Register in settings.json under hooks.PostToolUse:
  python3 ~/.claude/hooks/memory_access_tracker.py
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_base import run_hook

MEMORY_BASE = Path.home() / ".claude" / "projects"
SKIP_FILES = {"MEMORY.md", "memory_stats.json"}


def _find_stats_file(file_path):
    """Locate memory_stats.json in the same memory/ directory as the file."""
    p = Path(file_path)
    for parent in p.parents:
        if parent.name == "memory":
            return parent / "memory_stats.json"
    return None


def _load_stats(stats_file):
    if stats_file and stats_file.exists():
        try:
            return json.loads(stats_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_stats(stats_file, stats):
    if not stats_file:
        return
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = stats_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(stats, indent=2))
    tmp.rename(stats_file)


def check(tool_name, tool_input, input_data):
    if tool_name != "Read":
        return False
    file_path = tool_input.get("file_path", "")
    return (
        "memory/" in file_path
        and file_path.endswith(".md")
        and Path(file_path).name not in SKIP_FILES
        and "/archive/" not in file_path
    )


def action(tool_name, tool_input, input_data):
    file_path = Path(tool_input.get("file_path", ""))
    if not file_path.exists():
        return None

    key = file_path.name
    today = date.today().isoformat()

    stats_file = _find_stats_file(str(file_path))
    stats = _load_stats(stats_file)
    entry = stats.get(key, {"access_count": 0, "importance": 50, "last_accessed": today})

    entry["access_count"] = entry.get("access_count", 0) + 1
    entry["importance"] = min(100, entry.get("importance", 50) + 3)
    entry["last_accessed"] = today

    stats[key] = entry
    _save_stats(stats_file, stats)

    return None


if __name__ == "__main__":
    run_hook(check, action, "memory_access_tracker")

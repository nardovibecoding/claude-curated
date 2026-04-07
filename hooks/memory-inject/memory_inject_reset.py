#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""SessionStart hook: reset memory inject state so fresh injection happens.

Register in settings.json under hooks.SessionStart:
  python3 ~/.claude/hooks/memory_inject_reset.py
"""
import os
from pathlib import Path

MARKER_DIR = Path("/tmp/claude_memory_inject")


def main():
    tty = os.environ.get("CLAUDE_TTY_ID", "default")
    for suffix in [".json", "_topic.json"]:
        f = MARKER_DIR / f"{tty}{suffix}"
        f.unlink(missing_ok=True)
    print("{}")


if __name__ == "__main__":
    main()

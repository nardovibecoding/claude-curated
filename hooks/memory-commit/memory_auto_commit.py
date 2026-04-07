#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""Stop hook: auto-sync and commit changed memory files when session ends.

Rsyncs memory files from ~/.claude/projects/*/memory/ to a git repo,
then auto-commits any changes.

Configuration (edit the variables below or use env vars):
  MEMORY_SRC  — source memory directory (default: ~/.claude/projects/<project>/memory)
  MEMORY_REPO — git repo to sync memory into (set MEMORY_REPO_PATH env var)
  MEMORY_DST  — destination directory inside the repo (default: memory/)

Register in settings.json under hooks.Stop:
  python3 ~/.claude/hooks/memory_auto_commit.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Skip during auto-clear flow (e.g. context checkpoint exit)
_tty = os.environ.get("CLAUDE_TTY_ID", "").strip()
if Path(f"/tmp/claude_ctx_exit_pending_{_tty}").exists() if _tty else Path("/tmp/claude_ctx_exit_pending").exists():
    print("{}")
    sys.exit(0)

# Configure these for your setup
# Set MEMORY_REPO_PATH env var to your git repo, or edit the default below.
MEMORY_REPO = Path(os.environ.get("MEMORY_REPO_PATH", str(Path.home() / "my-memory-repo")))

# Source: first project's memory dir found, or set MEMORY_PROJECT env var
_project = os.environ.get("MEMORY_PROJECT", "")
if _project:
    MEMORY_SRC = Path.home() / ".claude" / "projects" / _project / "memory"
else:
    # Auto-detect: use the largest memory dir
    _projects_dir = Path.home() / ".claude" / "projects"
    _candidates = []
    if _projects_dir.exists():
        for _p in _projects_dir.iterdir():
            _m = _p / "memory"
            if _m.exists():
                _candidates.append(_m)
    MEMORY_SRC = max(_candidates, key=lambda p: sum(1 for _ in p.glob("*.md")), default=None)

MEMORY_DST = MEMORY_REPO / "memory"


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=15, **kwargs)


def main():
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    if not MEMORY_SRC or not MEMORY_SRC.exists() or not MEMORY_REPO.exists():
        print("{}")
        return

    # Rsync memory to repo
    MEMORY_DST.mkdir(parents=True, exist_ok=True)
    run(["rsync", "-a", "--delete",
         str(MEMORY_SRC) + "/",
         str(MEMORY_DST) + "/"])

    # Check for changes
    diff = run(["git", "status", "--porcelain", "memory/"], cwd=MEMORY_REPO)
    changed_lines = [l for l in diff.stdout.strip().splitlines() if l.strip()]

    if not changed_lines:
        print("{}")
        return

    # Count files and commit
    n = len(changed_lines)
    run(["git", "add", "memory/"], cwd=MEMORY_REPO)
    run(["git", "commit", "-m", f"memory: auto-sync {n} file(s) at session end"],
        cwd=MEMORY_REPO)

    print(json.dumps({"systemMessage": f"Memory auto-committed: {n} file(s) synced."}))


if __name__ == "__main__":
    main()

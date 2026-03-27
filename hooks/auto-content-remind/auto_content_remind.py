#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""Stop hook: remind to save content-worthy moments before session ends."""
import json
import sys
from pathlib import Path

import os as _os
_vps_repo = _os.environ.get("VPS_REPO_PATH", "")
CONTENT_LOG = Path(_vps_repo) / "content_drafts" / "running_log.md" if _vps_repo else Path.home() / ".claude" / "content_drafts" / "running_log.md"
CTX_FILE = Path("/tmp/claude_ctx_pct")


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print("{}")
        return

    # Check if context is high enough that session is substantial
    ctx_pct = 0
    if CTX_FILE.exists():
        try:
            ctx_pct = float(CTX_FILE.read_text().strip())
        except (ValueError, OSError):
            pass

    # Only trigger if session is substantial (>15% context used)
    if ctx_pct < 15:
        print("{}")
        return

    # Check if anything was already saved to content log this session
    already_saved = False
    if CONTENT_LOG.exists():
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            content = CONTENT_LOG.read_text()
            already_saved = today in content
        except Exception:
            pass

    if already_saved:
        print("{}")
        return

    # Prompt Claude to save content
    msg = (
        "📝 **Session ending — any content worth capturing?**\n"
        "If this session had insights, discoveries, or results worth tweeting:\n"
        "Call `content_capture` with the key moments before /clear.\n"
        "Categories: insight, result, code, number, journey, mistake"
    )
    print(json.dumps({"systemMessage": msg}))


if __name__ == "__main__":
    main()

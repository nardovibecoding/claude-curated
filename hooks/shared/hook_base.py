"""Small helper for local assistant hooks.

Hooks read one JSON object from stdin and print either "{}" or a
{"systemMessage": "..."} response.
"""
import json
import os
from datetime import datetime
from pathlib import Path

DEBUG_LOG = Path(os.environ.get("AI_HOOK_DEBUG_LOG", "/tmp/ai_hooks_debug.log"))
DEBUG = os.environ.get("AI_HOOKS_DEBUG", "0") == "1"


def _log(hook_name, msg):
    if not DEBUG:
        return
    ts = datetime.now().strftime("%H:%M:%S")
    with open(DEBUG_LOG, "a") as f:
        f.write(f"[{ts}] {hook_name}: {msg}\n")


def run_hook(check_fn, action_fn, hook_name="unknown"):
    """Run a check/action hook pair."""
    import sys

    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        _log(hook_name, "bad stdin")
        print("{}")
        return

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if not check_fn(tool_name, tool_input, input_data):
        print("{}")
        return

    message = action_fn(tool_name, tool_input, input_data)
    if message:
        print(json.dumps({"systemMessage": message}))
    else:
        print("{}")

#!/usr/bin/env python3
"""Block high-risk local shell commands unless explicitly allowed."""
import json
import re
import sys

ALLOW_TOKEN = "ALLOW_UNSAFE_LOCAL_COMMAND=1"
BLOCK_PATTERNS = [
    r"\b(cat|less|tail|head)\b\s+.*(\.env|id_rsa|id_ed25519|token|secret|cookie|oauth)",
    r"\b(scp|rsync)\b.*:",
    r"\bssh\b.*\b(sed\s+-i|tee|rm\s+-rf|pkill|systemctl|launchctl)\b",
    r"git\s+commit\s+.*--no-verify",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+-fd",
    r"rm\s+-rf\s+(/|~|\$HOME)(\s|$)",
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("{}")
        return
    if data.get("tool_name") != "Bash":
        print("{}")
        return
    command = data.get("tool_input", {}).get("command", "")
    if ALLOW_TOKEN in command:
        print("{}")
        return
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, command):
            print(json.dumps({
                "decision": "block",
                "reason": f"guard-safety blocked `{pattern}`. Add {ALLOW_TOKEN} only after review.",
            }))
            return
    print("{}")


if __name__ == "__main__":
    main()

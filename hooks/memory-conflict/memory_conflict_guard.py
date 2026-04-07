#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""Git-style conflict detection + 3-way merge for memory files.

Two modes (same file, registered on both events):
1. PostToolUse (Read): store file content + mtime when memory file is read
2. PreToolUse (Write/Edit): check if file changed since our read — auto-merge or warn

Like git: Read = checkout, Write = commit, mtime mismatch = someone pushed before you.
3-way merge: original (at read time) vs current (on disk now) vs new (our write).

Register in settings.json:
  PostToolUse: python3 ~/.claude/hooks/memory_conflict_guard.py
  PreToolUse:  python3 ~/.claude/hooks/memory_conflict_guard.py
"""
import difflib
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_base import _log

HOOK_NAME = "memory_conflict"
MEMORY_DIR = Path.home() / ".claude" / "projects"
SNAPSHOT_DIR = Path("/tmp/claude_memory_snapshots")
STATE_FILE = Path("/tmp/claude_memory_reads.json")


def _load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_state(state):
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.rename(STATE_FILE)


def _file_hash(path):
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def _content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()


def _is_memory_file(file_path):
    return (
        file_path
        and "memory/" in file_path
        and file_path.endswith(".md")
        and Path(file_path).name != "memory_stats.json"
    )


def _snapshot_path(tty, file_path):
    """Path to stored snapshot of file content at read time."""
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    safe_name = Path(file_path).name.replace("/", "_")
    return SNAPSHOT_DIR / f"{tty}_{safe_name}"


def _three_way_merge(original, current, new_content):
    """Attempt 3-way merge like git.

    Returns (merged_content, had_conflicts).
    If no conflicts, merged_content is the clean merge.
    If conflicts, merged_content contains conflict markers.
    """
    orig_lines = original.splitlines(keepends=True)
    curr_lines = current.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    theirs_diff = set()
    ours_diff = set()

    theirs_ops = difflib.SequenceMatcher(None, orig_lines, curr_lines).get_opcodes()
    ours_ops = difflib.SequenceMatcher(None, orig_lines, new_lines).get_opcodes()

    for tag, i1, i2, j1, j2 in theirs_ops:
        if tag != "equal":
            theirs_diff.update(range(i1, max(i2, i1 + 1)))

    for tag, i1, i2, j1, j2 in ours_ops:
        if tag != "equal":
            ours_diff.update(range(i1, max(i2, i1 + 1)))

    overlap = theirs_diff & ours_diff

    if not overlap:
        if not theirs_diff:
            return "".join(new_lines), False
        if not ours_diff:
            return "".join(curr_lines), False

        merged_text = _apply_non_overlapping(orig_lines, curr_lines, new_lines, theirs_diff, ours_diff)
        return merged_text, False

    else:
        conflict_lines = []
        conflict_lines.append("<<<<<<< CURRENT (other session)\n")
        for line in curr_lines:
            conflict_lines.append(line)
        conflict_lines.append("=======\n")
        for line in new_lines:
            conflict_lines.append(line)
        conflict_lines.append(">>>>>>> YOURS (this session)\n")
        return "".join(conflict_lines), True


def _apply_non_overlapping(orig, curr, new, theirs_lines, ours_lines):
    """Apply non-overlapping changes from both sides.

    Strategy for memory files (append-heavy): take new (our write) as base,
    then append any lines from current that weren't in original
    (i.e., lines the other session added).
    """
    orig_set = set(l.strip() for l in orig if l.strip())
    curr_set = set(l.strip() for l in curr if l.strip())
    new_set = set(l.strip() for l in new if l.strip())

    theirs_additions = [l for l in curr if l.strip() and l.strip() not in orig_set and l.strip() not in new_set]

    if theirs_additions:
        result = "".join(new)
        if not result.endswith("\n"):
            result += "\n"
        result += "\n## Merged from other session\n"
        result += "".join(theirs_additions)
        return result
    else:
        return "".join(new)


# -- PostToolUse: record read --

def _handle_post_read(input_data):
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name != "Read":
        print("{}")
        return

    file_path = tool_input.get("file_path", "")
    if not _is_memory_file(file_path):
        print("{}")
        return

    p = Path(file_path)
    if not p.exists():
        print("{}")
        return

    tty = os.environ.get("CLAUDE_TTY_ID", "default")

    try:
        content = p.read_text()
        snapshot = _snapshot_path(tty, file_path)
        snapshot.write_text(content)
    except OSError:
        print("{}")
        return

    state = _load_state()
    key = f"{tty}:{file_path}"
    state[key] = {
        "mtime": p.stat().st_mtime,
        "hash": _content_hash(content),
        "path": file_path,
        "snapshot": str(snapshot),
    }
    _save_state(state)
    _log(HOOK_NAME, f"recorded read + snapshot: {p.name}")
    print("{}")


# -- PreToolUse: check + merge --

def _handle_pre_write(input_data):
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        print("{}")
        return

    file_path = tool_input.get("file_path", "")
    if not _is_memory_file(file_path):
        print("{}")
        return

    p = Path(file_path)
    if not p.exists():
        print("{}")
        return

    tty = os.environ.get("CLAUDE_TTY_ID", "default")
    state = _load_state()
    key = f"{tty}:{file_path}"

    recorded = state.get(key)
    if not recorded:
        print("{}")
        return

    current_mtime = p.stat().st_mtime
    recorded_mtime = recorded.get("mtime", 0)

    if current_mtime == recorded_mtime:
        _log(HOOK_NAME, f"no conflict: {p.name}")
        print("{}")
        return

    try:
        current_content = p.read_text()
    except OSError:
        print("{}")
        return

    current_hash = _content_hash(current_content)
    recorded_hash = recorded.get("hash", "")

    if current_hash == recorded_hash:
        _log(HOOK_NAME, f"mtime changed but same content: {p.name}")
        print("{}")
        return

    # Real conflict — try 3-way merge
    _log(HOOK_NAME, f"CONFLICT detected: {p.name}")

    snapshot_path = recorded.get("snapshot", "")
    original_content = ""
    if snapshot_path and Path(snapshot_path).exists():
        try:
            original_content = Path(snapshot_path).read_text()
        except OSError:
            pass

    if not original_content:
        msg = (
            f"CONFLICT: {p.name} modified by another session since your read.\n"
            f"No snapshot available for merge. Re-read the file before editing."
        )
        print(json.dumps({"additionalContext": msg}))
        return

    new_content = ""
    if tool_name == "Write":
        new_content = tool_input.get("content", "")
    elif tool_name == "Edit":
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        if old_string in current_content:
            msg = (
                f"NOTE: {p.name} was modified by another session, but your edit target "
                f"still exists in current file. Edit will apply to the updated version. "
                f"Review the result to ensure both changes are preserved."
            )
            print(json.dumps({"additionalContext": msg}))
            return
        elif old_string in original_content:
            msg = (
                f"CONFLICT: {p.name} — your edit target was modified by another session.\n"
                f"The text you're trying to replace no longer exists in the file.\n"
                f"Re-read the file to see current state, then retry your edit."
            )
            print(json.dumps({"additionalContext": msg}))
            return
        else:
            print("{}")
            return

    if not new_content:
        print("{}")
        return

    merged, had_conflicts = _three_way_merge(original_content, current_content, new_content)

    if had_conflicts:
        diff_preview = ""
        for line in difflib.unified_diff(
            original_content.splitlines(keepends=True)[:20],
            current_content.splitlines(keepends=True)[:20],
            fromfile="your_read", tofile="current_on_disk", n=3
        ):
            diff_preview += line
        if len(diff_preview) > 500:
            diff_preview = diff_preview[:500] + "..."

        msg = (
            f"CONFLICT: {p.name} has overlapping changes from another session.\n"
            f"Cannot auto-merge. Diff of other session's changes:\n"
            f"```\n{diff_preview}\n```\n"
            f"Re-read the file, then manually merge your changes with theirs."
        )
        print(json.dumps({"additionalContext": msg}))
    else:
        _log(HOOK_NAME, f"auto-merged {p.name} (no conflicts)")
        if tool_name == "Write":
            msg = (
                f"AUTO-MERGED: {p.name} was modified by another session. "
                f"Changes were in different sections — merged automatically. "
                f"Writing merged content instead of your original."
            )
            print(json.dumps({
                "additionalContext": msg,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "updatedInput": {
                        "file_path": file_path,
                        "content": merged,
                    }
                }
            }))
        else:
            print(json.dumps({"additionalContext":
                f"AUTO-MERGED: {p.name} had non-overlapping changes from another session. Merge applied."}))

    state[key] = {
        "mtime": p.stat().st_mtime,
        "hash": _content_hash(current_content),
        "path": file_path,
        "snapshot": snapshot_path,
    }
    _save_state(state)


# -- Entry point --

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print("{}")
        return

    if "tool_result" in input_data or input_data.get("_event") == "PostToolUse":
        _handle_post_read(input_data)
    else:
        _handle_pre_write(input_data)


if __name__ == "__main__":
    main()

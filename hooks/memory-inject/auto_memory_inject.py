#!/usr/bin/env python3
# Copyright (c) 2026 Nardo (nardovibecoding). AGPL-3.0 — see LICENSE
"""Memory inject hook — runs in TWO modes via same file:

1. UserPromptSubmit: tokenize user message, compare with stored topic.
   If new convo or topic shifted → write marker with query tokens.
2. PreToolUse: if marker exists → BM25 search memories → inject → delete marker.

Register the SAME file under both hook events in settings.json:
  hooks.UserPromptSubmit: python3 ~/.claude/hooks/auto_memory_inject.py
  hooks.PreToolUse:       python3 ~/.claude/hooks/auto_memory_inject.py

Mode is detected from stdin (UserPromptSubmit has "prompt", PreToolUse has "tool_name").

Requires: memory files in ~/.claude/projects/*/memory/*.md
"""
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_base import _log

HOOK_NAME = "memory_inject"
PROJECTS_DIR = Path.home() / ".claude" / "projects"
MARKER_DIR = Path("/tmp/claude_memory_inject")
SKIP_FILES = {"MEMORY.md", "memory_stats.json"}
SKIP_PREFIXES = {"convo_"}
MAX_INJECT = 5
MAX_SNIPPET = 300
MIN_SCORE = 0.5
TOPIC_SHIFT_THRESHOLD = 0.2

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "and", "but", "or", "nor",
    "not", "no", "so", "if", "this", "that", "these", "those", "it", "its",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "only", "own", "same", "than", "too", "very", "just", "because",
    "about", "up", "which", "what", "when", "where", "who", "how", "file",
    "path", "true", "false", "null", "none", "read", "write", "edit",
    "command", "bash", "tool", "input", "output", "use", "using",
    "lets", "let", "go", "want", "need", "make", "get", "set", "hey",
    "ok", "yes", "yeah", "yea", "please", "thanks", "check", "look",
}

K1 = 1.5
B = 0.75


def _tty():
    return os.environ.get("CLAUDE_TTY_ID", "default")


def _marker_path():
    return MARKER_DIR / f"{_tty()}.json"


def _topic_path():
    return MARKER_DIR / f"{_tty()}_topic.json"


def _tokenize(text):
    words = re.findall(r'[a-z0-9_]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


# -- Phase 1: UserPromptSubmit --

def _handle_prompt(prompt):
    """Tokenize user message. If topic shifted or first message, write marker."""
    MARKER_DIR.mkdir(exist_ok=True)

    tokens = _tokenize(prompt)
    if not tokens:
        _marker_path().write_text(json.dumps({"tokens": []}))
        print("{}")
        return

    topic_file = _topic_path()
    should_inject = False

    if not topic_file.exists():
        should_inject = True
        _log(HOOK_NAME, "first message, will inject")
    else:
        try:
            old = json.loads(topic_file.read_text())
            old_tokens = old.get("tokens", [])
            old_ts = old.get("ts", "")
            if old_ts:
                age = (datetime.now() - datetime.fromisoformat(old_ts)).total_seconds()
                if age > 300:
                    should_inject = True
                    _log(HOOK_NAME, f"stale topic ({age:.0f}s old), will inject")
            if not should_inject:
                overlap = _topic_overlap(tokens, old_tokens)
                if overlap < TOPIC_SHIFT_THRESHOLD:
                    should_inject = True
                    _log(HOOK_NAME, f"topic shift ({overlap:.0%} overlap), will inject")
                else:
                    _log(HOOK_NAME, f"same topic ({overlap:.0%} overlap), skipping")
        except (json.JSONDecodeError, OSError):
            should_inject = True

    if should_inject:
        _marker_path().write_text(json.dumps({"tokens": tokens[:30]}))
        topic_file.write_text(json.dumps({"tokens": tokens[:30], "ts": datetime.now().isoformat()}))

    print("{}")


def _topic_overlap(new_tokens, old_tokens):
    if not old_tokens or not new_tokens:
        return 0.0
    new_set = set(new_tokens)
    old_set = set(old_tokens)
    return len(new_set & old_set) / min(len(new_set), len(old_set))


# -- Phase 2: PreToolUse --

def _handle_tool():
    """If marker exists, search memories and inject. One-shot per marker."""
    marker = _marker_path()
    if not marker.exists():
        print("{}")
        return

    try:
        data = json.loads(marker.read_text())
        query_tokens = data.get("tokens", [])
    except (json.JSONDecodeError, OSError):
        query_tokens = []
    marker.unlink(missing_ok=True)

    if not query_tokens:
        print("{}")
        return

    _log(HOOK_NAME, f"injecting for tokens: {query_tokens[:10]}")
    memories = _load_memories()
    results = _bm25_search(query_tokens, memories)
    top = [(s, m) for s, m in results if s >= MIN_SCORE][:MAX_INJECT]

    if not top:
        print("{}")
        return

    lines = ["Relevant memories auto-loaded:"]
    for score, mem in top:
        snippet = mem["body"][:MAX_SNIPPET].replace("\n", " ").strip()
        if len(mem["body"]) > MAX_SNIPPET:
            snippet += "..."
        lines.append(f"- [{mem['type']}] {mem['name']}: {snippet}")

    msg = "\n".join(lines)
    _log(HOOK_NAME, f"injected context ({len(lines)} lines)")
    print(json.dumps({"additionalContext": msg}))


# -- Shared: memory loading + BM25 --

def _load_memories():
    memories = []
    today = date.today()

    # Search all projects under ~/.claude/projects/*/memory/
    if not PROJECTS_DIR.exists():
        return memories

    for project_dir in PROJECTS_DIR.iterdir():
        memory_dir = project_dir / "memory"
        if not memory_dir.exists():
            continue

        stats_file = memory_dir / "memory_stats.json"
        stats = {}
        if stats_file.exists():
            try:
                stats = json.loads(stats_file.read_text())
            except (json.JSONDecodeError, OSError):
                pass

        for f in memory_dir.glob("*.md"):
            if f.name in SKIP_FILES:
                continue
            if any(f.name.startswith(p) for p in SKIP_PREFIXES):
                continue

            try:
                text = f.read_text(errors="replace")
            except OSError:
                continue

            meta = {}
            body = text
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            meta[k.strip()] = v.strip()
                    body = parts[2].strip()

            file_stats = stats.get(f.name, {})
            importance = file_stats.get("importance", 50)
            last_accessed = file_stats.get("last_accessed", "2020-01-01")

            try:
                days_ago = (today - date.fromisoformat(last_accessed)).days
            except ValueError:
                days_ago = 30

            memories.append({
                "name": meta.get("name", f.stem),
                "description": meta.get("description", ""),
                "type": meta.get("type", "unknown"),
                "body": body,
                "file": f.name,
                "importance": importance,
                "days_ago": days_ago,
            })

    return memories


def _bm25_search(query_tokens, memories):
    if not query_tokens or not memories:
        return []

    doc_count = len(memories)
    df = Counter()
    doc_tokens = []

    for mem in memories:
        text = (
            (mem["description"] + " ") * 3 +
            (mem["name"] + " ") * 2 +
            mem["body"]
        )
        tokens = _tokenize(text)
        doc_tokens.append(tokens)
        for t in set(tokens):
            df[t] += 1

    avg_dl = sum(len(dt) for dt in doc_tokens) / max(doc_count, 1)

    scored = []
    for mem, tokens in zip(memories, doc_tokens):
        dl = len(tokens)
        tf = Counter(tokens)
        score = 0.0

        for qt in query_tokens:
            if qt not in df:
                continue
            idf = math.log((doc_count - df[qt] + 0.5) / (df[qt] + 0.5) + 1)
            term_tf = tf.get(qt, 0)
            tf_norm = (term_tf * (K1 + 1)) / (term_tf + K1 * (1 - B + B * dl / avg_dl))
            score += idf * tf_norm

        if score <= 0:
            continue

        recency = max(0, 1 - mem["days_ago"] / 30)
        imp = mem["importance"] / 100
        final = score * 0.6 + recency * score * 0.2 + imp * score * 0.2
        scored.append((final, mem))

    scored.sort(key=lambda x: -x[0])
    return scored


# -- Entry point: detect mode from stdin --

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print("{}")
        return

    if "prompt" in input_data:
        _handle_prompt(input_data["prompt"])
    elif "tool_name" in input_data:
        _handle_tool()
    else:
        print("{}")


if __name__ == "__main__":
    main()

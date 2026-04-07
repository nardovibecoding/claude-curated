---
name: recall
description: Hybrid search across memory + wiki. Supports semantic search, keyword match, and tag filtering. /recall <query> or /recall #tag
user-invocable: true
---
<recall>
Search indexed files (memory, code, hooks, skills) via Vector + BM25 + tag index.

1. If query starts with `#`: read `~/.claude/tag_index.json`, list files under tag, read top 2-3.

2. Otherwise: `node ~/.claude/skills/recall/search.mjs "<QUERY>"` — top 5 by RRF. Read top 2-3 (RRF > 0.02).

3. Answer using retrieved context.

Rebuild index: `node ~/.claude/skills/recall/build-index.mjs`
</recall>

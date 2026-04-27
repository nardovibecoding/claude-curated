<div align="center">

```bash
claude plugins install nardovibecoding/simply-skills-curation
```

**Production-tested Claude Code skills + hooks — LLM reasoning where you need it, deterministic automation where you don't.**

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet?style=for-the-badge)](https://claude.com/claude-code)
[![Skills](https://img.shields.io/badge/Skills-7-blue?style=for-the-badge)](#skills)
[![Hooks](https://img.shields.io/badge/Hooks-10-orange?style=for-the-badge)](#hooks)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-AGPL--3.0-red?style=for-the-badge)](LICENSE)

<img src="demo.gif" alt="6-model debate, adversarial critic, and context budget audit" width="700">

</div>

---

One Claude gives you one perspective. For code review, architecture decisions, or anything that matters — one opinion isn't enough. This brings structured debate, adversarial review, and automated context management.

## Skills

Skills invoke the LLM with a structured prompt. They activate automatically on matching trigger phrases — no slash commands needed.

| Category | Skill | What it does |
|----------|-------|-------------|
| **Security** | [red-alert](#red-alert--adversarial-self-review) | Adversarial red team — finds security holes, logic bugs, wasted resources |
| **Maintenance** | [md-cleanup](#md-cleanup--unified-context-budget-auditor) | Unified context budget auditor — CLAUDE.md, hookify rules, memory files, skills |
| **Maintenance** | skill-profile | Profile switching: load only the skills relevant to your current task |
| **Workflow** | [research-council](#research-council--6-model-debate-at-0cost) | 6 free LLMs debate, cross-examine, deliver consensus — $0/decision |
| **Discovery** | skill-extractor | Evaluates community skills before you install — catches overlap and bloat |
| **Discovery** | tldr-eli5 | Adaptive summarization + ELI5 mode for non-technical stakeholders |
| **Memory** | [recall](#recall--hybrid-memory-search) | Hybrid Vector + BM25 + Graph search across all memory files — `/recall <query>` |

## Hooks

Hooks are plain Python scripts that fire on Claude Code `PostToolUse` events — no LLM call, no latency, no cost.

| Hook | Trigger | What it does |
|------|---------|-------------|
| **vps-sync** | `git push` | Auto SSH-pulls on the remote server — keeps VPS in sync with every push |
| **dependency-grep** | `mv` / `rm` | Greps for references to moved or deleted files before you move on |
| **pip-install** | `requirements.txt` edit | Auto runs `pip install -r requirements.txt` on the remote server |
| **bot-restart** | persona JSON edit | Auto `pkill`s the affected bot process — `start_all.sh` restarts it within 10s |
| **memory-index** | new `memory/*.md` (Write) | Checks that new memory files are listed in the `MEMORY.md` index |
| **memory-inject** | UserPromptSubmit + PreToolUse | BM25 search on every new topic — auto-injects relevant memory snippets into context |
| **memory-conflict** | Read + Write/Edit | Git-style conflict detection + 3-way auto-merge for memory files edited across sessions |
| **memory-access** | PostToolUse (Read) | Tracks access frequency + importance score per memory file |
| **memory-commit** | Stop (session end) | Rsyncs changed memory files to a git repo and auto-commits |
| **memory-inject-reset** | SessionStart | Resets inject state so fresh memory injection happens each session |

---

## Research Council — 6-Model Debate at $0/Decision

The standout feature. LLMs are sycophantic by default — they agree with whoever asked. Research Council fixes this by making six models argue with each other.

**How it works:**

```
/debate Should we migrate from REST to GraphQL for our internal API?
```

| Round | What happens |
|-------|-------------|
| **Round 1** | Six models answer in parallel (~10 seconds) |
| **Round 2** | Each model reads all others' answers, identifies the strongest and weakest arguments, refines its position |
| **Round 3** | Final positions with explicit "I changed my mind because…" or "I maintain because…" |
| **Synthesis** | A judge model produces an executive memo: consensus, open disagreements, action items, contrarian insights |

**Quick mode** (3 models, 2 rounds) for lightweight questions. **Full council** (6 models, 3 rounds) for architecture decisions, vendor choices, or anything where the stakes justify 3 minutes of compute.

**Cost:** $0. All six models are free-tier API calls. The council that would cost $40/hour in meeting time costs nothing.

---

## Red Alert — Adversarial Self-Review

Standard code review is agreeable. Red Alert uses a "paid-to-find-flaws" prompt — the reviewer is explicitly rewarded for finding real problems, not for being supportive.

**Three modes:**
- **On-demand** — point it at any file, commit, or feature description
- **Post-change** — auto-triggers after large diffs (>50 lines changed)
- **Scheduled** — full system red team against an 8-point checklist: security, reliability, cost, data loss, stale state, dead code, dependencies, monitoring gaps

**Multi-model review:** run a second model as external critic — different training data finds different blind spots.

---

## MD Cleanup — Unified Context Budget Auditor

Replaces three separate maintenance tasks with one five-phase command:

```
md cleanup
```

| Phase | What it audits |
|-------|---------------|
| 1 | **CLAUDE.md** — classifies each rule as INTERNALIZED / REINFORCED / CUSTOM / HISTORICAL / REDUNDANT |
| 2 | **Hookify rules** — deduplicates against CLAUDE.md and feedback memory |
| 3 | **Memory files** — checks line counts, staleness, duplicate topics, promotion candidates |
| 4 | **Skills inventory** — detects duplicate triggers, broken scripts, missing deps, upstream updates |
| 5 | **Budget table** — token count across all context sources with thresholds |

One command. One report. Recommendations held until you approve.

---

## Recall — Hybrid Memory Search

`/recall <query>` searches all your memory files using four signals fused together:

```
/recall how did we fix the rate limiter?
/recall #trading
```

**How it works:**

| Signal | Method | Strength |
|--------|--------|---------|
| **Vector** | all-MiniLM-L6-v2 (local, no API key) | Semantic similarity — finds conceptually related files |
| **BM25** | TF-IDF with field weighting (name 3x, description 2x, body 1x) | Keyword precision — exact term matches |
| **Recency** | Exponential decay from last-modified date | Recent files rank higher |
| **Graph** | Optional — traverses a knowledge graph for connected nodes | Expands to related topics |

All four signals are merged using **Reciprocal Rank Fusion (k=60)** — a parameter-free fusion method that outperforms weighted averaging.

**Tag search:** prefix with `#` to filter by tag instead of searching:
```
/recall #hooks
/recall #security
```

Tags are built by `build-index.mjs`, which scans all memory files, hooks, and skills and classifies them by content keywords.

**Embedding cache:** vectors are cached in `~/.claude/.memory_embeddings_cache.json`. Only new or modified files are re-embedded. First run downloads the model (~22MB).

**Install:**
```bash
cd ~/.claude/skills/recall
npm install
node build-index.mjs   # build tag index
node search.mjs "test query"
```

**Why it's better than grep:**

Standard `grep` finds files with the exact words you typed. Recall finds files about the *concept* you're thinking of — even if you don't remember the exact terminology you used when you wrote the note.

---

## Where These Came From

Every item was extracted from a real production failure:

| Item | Real problem |
|------|-------------|
| **red-alert** | Code review kept missing security holes. Needed a reviewer that's paid to disagree. |
| **research-council** | LLMs agreed with whatever framing the question had. Built adversarial cross-examination instead. |
| **md-cleanup** | Three separate maintenance skills kept running in the wrong order. Merged into one five-phase audit. |
| **skill-extractor** | Installed a community skill that overlapped 80% with existing tools. Built an evaluator to check first. |
| **skill-profile** | Hit the 15K YAML skills limit with 30+ skills loaded. Needed profile switching per task context. |
| **tldr-eli5** | Needed different compression ratios for different audiences and languages. |
| **vps-sync** | Edited code on laptop, forgot to push, server ran stale code for 3 days. Hook fires on every push. |
| **dependency-grep** | Renamed a config file, broke 6 downstream references silently. Hook greps before you move on. |
| **pip-install** | Added a dependency, forgot to install on server, service crashed at 2am. Hook installs automatically. |
| **bot-restart** | Edited a persona config, had to manually SSH and restart. Hook handles it in 10 seconds. |
| **memory-index** | Created a memory file, forgot to index it, couldn't find it two weeks later. Hook catches it immediately. |
| **recall** | Searched memory with grep, got zero results because the note used different words. Built semantic search. |
| **memory-inject** | Kept forgetting context from previous sessions. Hook auto-loads the 5 most relevant files on topic shift. |
| **memory-conflict** | Two Claude sessions edited the same memory file simultaneously and clobbered each other. Built 3-way merge. |
| **memory-commit** | Memory edits stayed local, never backed up. Stop hook syncs to git on every session end. |

---

## Architecture: Skills vs Hooks

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code CLI                      │
├────────────────────────┬────────────────────────────────┤
│        SKILLS          │           HOOKS                 │
│  (LLM reasoning)       │   (deterministic automation)    │
│                        │                                 │
│  Trigger phrase →      │   Tool event fires →            │
│  Structured prompt →   │   Python check() →              │
│  LLM generates output  │   Python action()               │
│                        │   (no LLM, no latency)          │
│  Use for:              │   Use for:                      │
│  debate, critique,     │   sync, grep, install,          │
│  summarize, evaluate   │   restart, validate             │
└────────────────────────┴────────────────────────────────┘
```

Skills and hooks are independent — install only what you need.

---

## Install

One command. Takes 30 seconds.

```bash
curl -fsSL https://raw.githubusercontent.com/nardovibecoding/simply-skills-curation/main/install.sh | bash
```

Clones the repo, registers all 13 hooks + 6 skills in `~/.claude/settings.json`. Restart Claude Code.

<details>
<summary>Manual install</summary>

### Skills — as a plugin

```bash
claude plugins install nardovibecoding/simply-skills-curation
```

### Skills — manual (one at a time)

```bash
git clone https://github.com/nardovibecoding/simply-skills-curation.git
cp -r simply-skills-curation/skills/workflow/research-council ~/.claude/skills/
```

### Hooks

```bash
# Shared library (required by all hooks)
cp simply-skills-curation/hooks/shared/hook_base.py ~/.claude/hooks/
cp simply-skills-curation/hooks/shared/vps_config.py ~/.claude/hooks/

# Copy whichever hooks you need
cp simply-skills-curation/hooks/vps-sync/auto_vps_sync.py ~/.claude/hooks/
cp simply-skills-curation/hooks/dependency-grep/auto_dependency_grep.py ~/.claude/hooks/
cp simply-skills-curation/hooks/pip-install/auto_pip_install.py ~/.claude/hooks/
cp simply-skills-curation/hooks/bot-restart/auto_bot_restart.py ~/.claude/hooks/
cp simply-skills-curation/hooks/memory-index/auto_memory_index.py ~/.claude/hooks/
```

Register hooks in `~/.claude/settings.json` under `hooks.PostToolUse`. Each hook's directory contains a README with the exact registration block.

**Prerequisite:** [Claude Code](https://claude.com/claude-code) CLI installed.

</details>

---

## Project Structure

```
simply-skills-curation/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── security/
│   │   └── red-alert/           # Adversarial red team (SKILL.md + prompt)
│   ├── maintenance/
│   │   ├── md-cleanup/          # 5-phase context budget auditor
│   │   └── skill-profile/       # Profile switching (all/coding/outreach/minimal)
│   ├── workflow/
│   │   └── research-council/    # 6-model debate at $0/decision
│   ├── discovery/
│   │   ├── skill-extractor/     # Community skill evaluator
│   │   └── tldr-eli5/           # Adaptive summarization + ELI5
│   └── memory/
│       └── recall/              # Hybrid search (Vector + BM25 + Graph + RRF)
│           ├── SKILL.md
│           ├── search.mjs       # Main search script
│           ├── build-index.mjs  # Tag index builder
│           └── package.json
├── hooks/
│   ├── shared/
│   │   ├── hook_base.py         # run_hook(), check(), action() pattern
│   │   └── vps_config.py        # SSH config (reads from .env)
│   ├── vps-sync/
│   ├── dependency-grep/
│   ├── pip-install/
│   ├── bot-restart/
│   ├── memory-index/            # Warn when new memory file not in MEMORY.md
│   ├── memory-inject/           # Auto-inject relevant memories on topic shift
│   ├── memory-conflict/         # 3-way merge conflict guard for memory files
│   ├── memory-access/           # Track access frequency + importance scores
│   └── memory-commit/           # Auto-commit memory changes at session end
├── README.md
└── LICENSE
```

---

## Contributing

Each skill is self-contained: a `SKILL.md` defines triggers, allowed tools, and behavior — that file is the entire skill. Hooks follow a two-function pattern from `hook_base.py`: `check()` decides whether to fire, `action()` does the work.

Open an issue or PR. If you've extracted a skill from a real production problem, it belongs here.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=nardovibecoding/simply-skills-curation&type=Date)](https://star-history.com/#nardovibecoding/simply-skills-curation&Date)

---

## License

[AGPL-3.0](LICENSE)

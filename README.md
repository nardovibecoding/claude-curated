<div align="center">

```bash
claude plugins install nardovibecoding/claude-skills-curation
```

**Production-tested Claude Code skills + hooks — LLM reasoning where you need it, deterministic automation where you don't.**

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet?style=for-the-badge)](https://claude.com/claude-code)
[![Skills](https://img.shields.io/badge/Skills-6-blue?style=for-the-badge)](#skills)
[![Hooks](https://img.shields.io/badge/Hooks-5-orange?style=for-the-badge)](#hooks)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-AGPL--3.0-red?style=for-the-badge)](LICENSE)

<img src="demo.gif" alt="6-model debate, adversarial critic, and context budget audit" width="700">

</div>

---

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

## Hooks

Hooks are plain Python scripts that fire on Claude Code `PostToolUse` events — no LLM call, no latency, no cost.

| Hook | Trigger | What it does |
|------|---------|-------------|
| **vps-sync** | `git push` | Auto SSH-pulls on the remote server — keeps VPS in sync with every push |
| **dependency-grep** | `mv` / `rm` | Greps for references to moved or deleted files before you move on |
| **pip-install** | `requirements.txt` edit | Auto runs `pip install -r requirements.txt` on the remote server |
| **bot-restart** | persona JSON edit | Auto `pkill`s the affected bot process — `start_all.sh` restarts it within 10s |
| **memory-index** | new `memory/*.md` (Write) | Checks that new memory files are listed in the `MEMORY.md` index |

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
curl -fsSL https://raw.githubusercontent.com/nardovibecoding/claude-skills-curation/main/install.sh | bash
```

Clones the repo, registers all 13 hooks + 6 skills in `~/.claude/settings.json`. Restart Claude Code.

<details>
<summary>Manual install</summary>

### Skills — as a plugin

```bash
claude plugins install nardovibecoding/claude-skills-curation
```

### Skills — manual (one at a time)

```bash
git clone https://github.com/nardovibecoding/claude-skills-curation.git
cp -r claude-skills-curation/skills/workflow/research-council ~/.claude/skills/
```

### Hooks

```bash
# Shared library (required by all hooks)
cp claude-skills-curation/hooks/shared/hook_base.py ~/.claude/hooks/
cp claude-skills-curation/hooks/shared/vps_config.py ~/.claude/hooks/

# Copy whichever hooks you need
cp claude-skills-curation/hooks/vps-sync/auto_vps_sync.py ~/.claude/hooks/
cp claude-skills-curation/hooks/dependency-grep/auto_dependency_grep.py ~/.claude/hooks/
cp claude-skills-curation/hooks/pip-install/auto_pip_install.py ~/.claude/hooks/
cp claude-skills-curation/hooks/bot-restart/auto_bot_restart.py ~/.claude/hooks/
cp claude-skills-curation/hooks/memory-index/auto_memory_index.py ~/.claude/hooks/
```

Register hooks in `~/.claude/settings.json` under `hooks.PostToolUse`. Each hook's directory contains a README with the exact registration block.

**Prerequisite:** [Claude Code](https://claude.com/claude-code) CLI installed.

</details>

---

## Project Structure

```
claude-skills-curation/
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
│   └── discovery/
│       ├── skill-extractor/     # Community skill evaluator
│       └── tldr-eli5/           # Adaptive summarization + ELI5
├── hooks/
│   ├── shared/
│   │   ├── hook_base.py         # run_hook(), check(), action() pattern
│   │   └── vps_config.py        # SSH config (reads from .env)
│   ├── vps-sync/
│   ├── dependency-grep/
│   ├── pip-install/
│   ├── bot-restart/
│   └── memory-index/
├── README.md
└── LICENSE
```

---

## Contributing

Each skill is self-contained: a `SKILL.md` defines triggers, allowed tools, and behavior — that file is the entire skill. Hooks follow a two-function pattern from `hook_base.py`: `check()` decides whether to fire, `action()` does the work.

Open an issue or PR. If you've extracted a skill from a real production problem, it belongs here.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=nardovibecoding/claude-skills-curation&type=Date)](https://star-history.com/#nardovibecoding/claude-skills-curation&Date)

---

## License

[AGPL-3.0](LICENSE)

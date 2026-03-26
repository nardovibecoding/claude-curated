<div align="center">
  <h1>claude-curated</h1>
  <p><strong>Claude Code skills + Python hooks — LLM-powered workflows and deterministic automation from production usage.</strong></p>

  ![Claude Code](https://img.shields.io/badge/Claude_Code-skills%20%2B%20hooks-blueviolet)
  ![Skills](https://img.shields.io/badge/skills-6-blue)
  ![Hooks](https://img.shields.io/badge/hooks-5-orange)
  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
  ![License](https://img.shields.io/badge/license-Apache--2.0-red)
</div>

---

Every skill and hook was built from real production usage — not written as demos.

## Skills vs Hooks

Claude Code supports two automation layers. Knowing which to use matters:

| Layer | Use when | Examples |
|-------|----------|---------|
| **Skills** | You need LLM reasoning — debate, critique, summarize, evaluate | research-council, red-alert, tldr-eli5 |
| **Hooks** | You need deterministic automation — sync, grep, restart, install | vps-sync, pip-install, bot-restart |

Skills invoke the LLM with a structured prompt. Hooks are plain Python scripts that run on `PostToolUse` events — no LLM call, no latency, no cost.

## Skills

| Category | Skill | What it does |
|----------|-------|-------------|
| Security | **Red Alert** | Adversarial red team — finds security holes, logic bugs |
| Maintenance | **MD Cleanup** | Unified context budget auditor — CLAUDE.md, hookify rules, memory files, skills |
| Maintenance | **Skill Profile** | Skill profile switching (all/coding/outreach/minimal) |
| Workflow | **Research Council** | 6 free LLMs debate, cross-examine, deliver consensus — $0/decision |
| Discovery | **Skill Extractor** | Evaluates community skills before install |
| Discovery | **TLDR+ELI5** | Adaptive summarization + simple explanation mode |

## Hooks (Python-powered)

Drop these into `~/.claude/hooks/` — Claude Code runs them automatically on matching tool events.

| Hook | Trigger | What it does |
|------|---------|-------------|
| **vps-sync** | PostToolUse: `git push` | Auto SSH sync VPS — `git fetch && reset --hard origin/main` |
| **dependency-grep** | PostToolUse: `mv`/`rm` | Auto grep for references to moved/deleted files across the codebase |
| **pip-install** | PostToolUse: `requirements.txt` edit | Auto `pip install -r requirements.txt` on VPS |
| **bot-restart** | PostToolUse: persona JSON edit | Auto `pkill` the affected bot process on VPS — start_all.sh auto-restarts it |
| **memory-index** | PostToolUse: new memory file (Write) | Checks that new `.md` files in `memory/` are listed in MEMORY.md index |

### Install hooks

```bash
git clone https://github.com/nardovibecoding/claude-curated.git

# Copy the shared library first
cp claude-curated/hooks/shared/hook_base.py ~/.claude/hooks/
cp claude-curated/hooks/shared/vps_config.py ~/.claude/hooks/

# Copy whichever hooks you want
cp claude-curated/hooks/vps-sync/auto_vps_sync.py ~/.claude/hooks/
cp claude-curated/hooks/dependency-grep/auto_dependency_grep.py ~/.claude/hooks/
cp claude-curated/hooks/pip-install/auto_pip_install.py ~/.claude/hooks/
cp claude-curated/hooks/bot-restart/auto_bot_restart.py ~/.claude/hooks/
cp claude-curated/hooks/memory-index/auto_memory_index.py ~/.claude/hooks/
```

Then register them in your `~/.claude/settings.json` under `hooks.PostToolUse`.

## Where These Came From

Each skill and hook was extracted from a real problem:

- **red-alert** — Standard code review kept missing security holes. Built an adversarial reviewer that's paid to find flaws.
- **tldr-eli5** — Needed different compression ratios for English vs Chinese summaries, plus simple explanations for non-technical stakeholders.
- **skill-extractor** — Installed a community skill that overlapped 80% with existing tools. Built an evaluator to check before installing.
- **skill-profile** — Hit the 15K YAML limit with 30+ skills. Needed profile switching to load only relevant skills per task.
- **research-council** — LLMs are sycophantic. They agree with you. Built a council of 6 models that cross-examine each other — they disagree, change their minds, and produce answers none of them would give alone. Cost per decision: $0.
- **md-cleanup** — Three separate maintenance skills (`claude-md-trim`, `memory-keeper`, `skill-guard`'s skill-cleaning sub-feature) kept being invoked in the wrong order or piecemeal. Merged into one unified context budget auditor: one command, one report, five phases (CLAUDE.md → hookify rules → memory files → skills inventory → budget table).
- **vps-sync** — Edited code on laptop, deployed to server, forgot to push. Server had stale code for 3 days. Now a hook fires on every `git push` and pulls on the VPS automatically. Replaced the `single-source-of-truth` skill.
- **dependency-grep** — Renamed a config file, broke 6 downstream references silently. Now a hook fires on every `mv`/`rm` and greps for references before you move on. Replaced the `dependency-tracker` skill.
- **pip-install** — Added a dependency to requirements.txt, forgot to install on VPS, bot crashed at 2am. Hook fires automatically on every requirements.txt edit.
- **bot-restart** — Edited a persona JSON, had to manually SSH and pkill the bot. Hook handles it. start_all.sh auto-restarts within 10 seconds.
- **memory-index** — Created a new memory file, forgot to add it to MEMORY.md index, couldn't find it two weeks later. Hook catches it immediately.

## Who This Is For

**Using these skills** — Copy any skill folder to `~/.claude/skills/` and it activates automatically.

**Using these hooks** — Copy hook files to `~/.claude/hooks/` and register them in `~/.claude/settings.json`.

**Building your own** — Study the SKILL.md files as skill templates. Study `hook_base.py` as the hook pattern: `check()` decides whether to fire, `action()` does the work, `run_hook()` wires them together.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI installed

## Install Skills

### As a plugin (recommended)
```bash
/plugin marketplace add nardovibecoding/claude-curated
/plugin install claude-curated
```

### Manual (one skill at a time)
```bash
git clone https://github.com/nardovibecoding/claude-curated.git
cp -r claude-curated/skills/maintenance/md-cleanup ~/.claude/skills/
```

### Manual (all skills)
```bash
git clone https://github.com/nardovibecoding/claude-curated.git
find claude-curated/skills -mindepth 2 -maxdepth 2 -type d -exec cp -r {} ~/.claude/skills/ \;
```

Each skill works independently — install only what you need. Skills activate automatically when Claude Code detects matching trigger phrases.

## Highlights

### MD Cleanup — Unified Context Budget Auditor

Replaces three separate maintenance skills (`claude-md-trim`, `memory-keeper`, `skill-guard`'s skill-cleaning sub-feature) with a single five-phase audit:

1. **CLAUDE.md Audit** — classifies each rule as INTERNALIZED / REINFORCED / CUSTOM / HISTORICAL / REDUNDANT, estimates token savings
2. **Hookify Rules Audit** — deduplicates hookify rules against CLAUDE.md and feedback memory
3. **Memory Audit** — checks line counts, staleness, duplicate topics, and promotion candidates
4. **Skills Audit** — inventory, duplicate trigger detection, broken scripts, missing deps, upstream updates
5. **Budget Report** — token table across all context sources with thresholds

One command. One report. Actionable recommendations on approval.

### Red Alert — Adversarial Self-Review

Standard code review is sycophantic. Red Alert uses a "paid-to-find-flaws" prompt that rewards genuine issues over agreeable responses.

**Three modes:**
- **On-demand** — point it at any file, commit, or feature
- **Post-change** — auto-triggers after major diffs (>50 lines)
- **Scheduled red team** — full-system attack against an 8-point checklist (security, reliability, cost, data loss, stale state, dead code, dependencies, monitoring gaps)

Supports multi-model review: use a different LLM as an external critic since different training data catches different blind spots.

### Research Council — Multi-Model Debate

6 AI models debate a topic across 3 rounds, cross-examine each other, then produce an executive consensus memo.

**How it works:**
1. **Round 1** — Each model answers independently (parallel, ~10s)
2. **Round 2** — Each model reads all others' answers, identifies strongest/weakest arguments, refines position
3. **Round 3** — Final positions with "I changed my mind because..." or "I maintain because..."
4. **Synthesis** — Judge model produces a memo with consensus, disagreements, action items, and contrarian insights

Supports quick mode (3 models, 2 rounds) and full council (6 models, 3 rounds). Model roster is configurable via env vars.

## Project Structure

```
claude-curated/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── hooks/
│   ├── shared/
│   │   ├── hook_base.py         # Shared runner: run_hook(), ssh_cmd()
│   │   └── vps_config.py        # VPS SSH config (reads from .env)
│   ├── vps-sync/
│   │   └── auto_vps_sync.py     # Auto git pull on VPS after push
│   ├── dependency-grep/
│   │   └── auto_dependency_grep.py  # Grep references after mv/rm
│   ├── pip-install/
│   │   └── auto_pip_install.py  # Auto pip install after requirements.txt edit
│   ├── bot-restart/
│   │   └── auto_bot_restart.py  # Auto restart bot after persona JSON edit
│   └── memory-index/
│       └── auto_memory_index.py # Check MEMORY.md index after new memory file
├── skills/
│   ├── security/
│   │   └── red-alert/           # Adversarial red team review
│   ├── maintenance/
│   │   ├── md-cleanup/          # Unified context budget auditor (5-phase)
│   │   └── skill-profile/       # Profile switching
│   ├── workflow/
│   │   └── research-council/    # 6-model debate ($0/decision)
│   └── discovery/
│       ├── skill-extractor/     # Community skill evaluator
│       └── tldr-eli5/           # Adaptive summarization + ELI5
├── README.md
└── LICENSE
```

## Contributing

Open an issue or PR. Each skill is self-contained in its own directory with a `SKILL.md` that defines triggers, allowed tools, and behavior. Hooks follow the `hook_base.py` pattern: one `check()` function, one `action()` function.

## License

Apache-2.0 — see [LICENSE](LICENSE)

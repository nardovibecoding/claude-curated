<div align="center">
  <h1>claude-curated</h1>
  <p><strong>8 original Claude Code skills built from real-world usage — security scanning, adversarial review, multi-model debate, dev-server sync, and more.</strong></p>

  ![Claude Code](https://img.shields.io/badge/Claude_Code-skills-blueviolet)
  ![Skills](https://img.shields.io/badge/skills-8-blue)
  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
  ![License](https://img.shields.io/badge/license-Apache--2.0-red)
</div>

---

Every skill was built from real production usage — not written as demos.

## Skills

| Category | Skill | What it does |
|----------|-------|-------------|
| Security | **Red Alert** | Adversarial red team — finds security holes, logic bugs |
| Maintenance | **MD Cleanup** | Unified context budget auditor — CLAUDE.md, hookify rules, memory files, skills |
| Maintenance | **Skill Profile** | Skill profile switching (all/coding/outreach/minimal) |
| Workflow | **Dependency Tracker** | Finds stale references after renames/moves |
| Workflow | **Research Council** | 6 free LLMs debate, cross-examine, deliver consensus — $0/decision |
| Workflow | **Single Source of Truth** | Dev machine to server sync via GitHub — no rsync, no scp |
| Discovery | **Skill Extractor** | Evaluates community skills before install |
| Discovery | **TLDR+ELI5** | Adaptive summarization + simple explanation mode |

## Where These Came From

Each skill was extracted from a real problem:
- **red-alert** — Standard code review kept missing security holes. Built an adversarial reviewer that's paid to find flaws.
- **dependency-tracker** — Renamed a config file, broke 6 downstream references silently. Never again.
- **tldr-eli5** — Needed different compression ratios for English vs Chinese summaries, plus simple explanations for non-technical stakeholders.
- **skill-extractor** — Installed a community skill that overlapped 80% with existing tools. Built an evaluator to check before installing.
- **skill-profile** — Hit the 15K YAML limit with 30+ skills. Needed profile switching to load only relevant skills per task.
- **research-council** — LLMs are sycophantic. They agree with you. Built a council of 6 models that cross-examine each other — they disagree, change their minds, and produce answers none of them would give alone. Cost per decision: $0.
- **single-source-of-truth** — Edited code on laptop, deployed to server, forgot to push. Server had stale code for 3 days. Built a git-only sync workflow that makes this impossible.
- **md-cleanup** — Three separate maintenance skills (claude-md-trim, memory-keeper, skill-guard's skill-cleaning sub-feature) kept being invoked in the wrong order or piecemeal. Merged into one unified context budget auditor: one command, one report, five phases (CLAUDE.md → hookify rules → memory files → skills inventory → budget table).

## Who This Is For

**Using these skills** — Copy any skill folder to `~/.claude/skills/` and it activates automatically.

**Building your own** — Study the SKILL.md files as templates. The trigger/anti-trigger/produces pattern works for any skill.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI installed

## Install

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

### Single Source of Truth — Dev Machine to Server Sync

Git-only sync between your dev machine and remote server. No rsync. No scp. Git is the bus.

Includes:
- Setup templates for Mac+Cloud, Mac+AWS, Laptop+Desktop, Local+Docker
- Auto-pull cron for the server
- Conflict resolution guide
- Safety rules (never scp, never dual-run, always pull before push)

## Project Structure

```
claude-curated/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── security/
│   │   └── red-alert/           # Adversarial red team review
│   ├── maintenance/
│   │   ├── md-cleanup/          # Unified context budget auditor (5-phase)
│   │   └── skill-profile/       # Profile switching
│   ├── workflow/
│   │   ├── dependency-tracker/  # Stale reference finder
│   │   ├── research-council/    # 6-model debate ($0/decision)
│   │   └── single-source-of-truth/  # Dev ↔ server sync
│   └── discovery/
│       ├── skill-extractor/     # Community skill evaluator
│       └── tldr-eli5/           # Adaptive summarization + ELI5
├── README.md
└── LICENSE
```

## Contributing

Open an issue or PR. Each skill is self-contained in its own directory with a `SKILL.md` that defines triggers, allowed tools, and behavior.

## License

Apache-2.0 — see [LICENSE](LICENSE)

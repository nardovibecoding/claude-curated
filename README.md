<div align="center">
  <h1>claude-curated</h1>
  <p><strong>10 original Claude Code skills built from real-world usage — security scanning, adversarial review, multi-model debate, dev-server sync, and more.</strong></p>

  ![Claude Code](https://img.shields.io/badge/Claude_Code-skills-blueviolet)
  ![Skills](https://img.shields.io/badge/skills-10-blue)
  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
  ![License](https://img.shields.io/badge/license-MIT-green)
</div>

---

Every skill was built from real production usage — not written as demos.

## Skills

| Folder | Name | What it does |
|--------|------|-------------|
| `red-alert` | **Red Alert** | Adversarial red team — finds security holes, logic bugs |
| `dependency-tracker` | **Dependency Tracker** | Finds stale references after renames/moves |
| `tldr-eli5` | **TLDR+ELI5** | Compression mode + simple explanation mode |
| `skill-extractor` | **Skill Extractor** | Evaluates community skills before install |
| `claude-md-trim` | **Claude MD Trim** | CLAUDE.md rule optimizer |
| `skill-profile` | **Skill Profile** | Skill profile switching |
| `memory-keeper` | **Memory Keeper** | Memory lifecycle management |
| `skill-guard` | **Skill Guard** | Security scanner + health auditor (60 patterns, 14 categories) |
| `rd-council` | **R&D Council** | 6 free LLMs debate, cross-examine, and deliver a consensus memo — $0/decision |
| `single-source` | **Single Source** | Dev machine to server sync via GitHub — no rsync, no scp |

## Where These Came From

Each skill was extracted from a real problem:
- **red-alert** — Standard code review kept missing security holes. Built an adversarial reviewer that's paid to find flaws.
- **dependency-tracker** — Renamed a config file, broke 6 downstream references silently. Never again.
- **tldr-eli5** — Needed different compression ratios for English vs Chinese summaries, plus simple explanations for non-technical stakeholders.
- **skill-extractor** — Installed a community skill that overlapped 80% with existing tools. Built an evaluator to check before installing.
- **claude-md-trim** — CLAUDE.md grew to 400+ lines, burning tokens on every message. Most rules Claude already knew.
- **skill-profile** — Hit the 15K YAML limit with 30+ skills. Needed profile switching to load only relevant skills per task.
- **memory-keeper** — Memory files went stale within weeks. Needed automated lifecycle: mine, prune, promote.
- **skill-guard** — Installed a community skill that had obfuscated code. Built a scanner before it happened again.
- **rd-council** — LLMs are sycophantic. They agree with you. Built a council of 6 models that cross-examine each other — they disagree, change their minds, and produce answers none of them would give alone. Cost per decision: $0.
- **single-source** — Edited code on laptop, deployed to server, forgot to push. Server had stale code for 3 days. Built a git-only sync workflow that makes this impossible.

## Who This Is For

**Using these skills** — Copy any skill folder to `~/.claude/skills/` and it activates automatically.

**Building your own** — Study the SKILL.md files as templates. The trigger/anti-trigger/produces pattern works for any skill.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI installed

## Install

```bash
# Install one skill
cp -r claude-curated/red-alert ~/.claude/skills/

# Install all
for skill in claude-curated/*/; do cp -r "$skill" ~/.claude/skills/; done
```

Each skill works independently — install only what you need. Skills activate automatically when Claude Code detects matching trigger phrases.

## Highlights

### Skill Guard — Security Scanner + Health Auditor

The most code-heavy skill in the collection. Includes three Python scripts and a full threat model reference:

- **`skill_security_auditor.py`** — static analysis scanner with 60+ detection patterns across 14 categories (command injection, code execution, obfuscation, network exfiltration, credential harvesting, filesystem abuse, privilege escalation, deserialization, prompt injection, supply chain, and more)
- **`rescan_skills.py`** — checksum-based change detection that re-audits only modified or new skills
- **`skill_rescan_watch.sh`** — fswatch daemon that auto-triggers rescans on file changes

Produces a clear **PASS / WARN / FAIL** verdict with findings, severity levels, and remediation guidance. Supports `--strict` mode, JSON output, batch auditing, and CI/CD integration.

```bash
python3 skill-guard/scripts/skill_security_auditor.py /path/to/skill/
python3 skill-guard/scripts/skill_security_auditor.py /path/to/skill/ --strict --json
```

Also includes **Skill Cleaning** — a health audit sub-skill that checks for duplicates, broken scripts, missing dependencies, unused skills, and upstream updates.

### Red Alert — Adversarial Self-Review

Standard code review is sycophantic. Red Alert uses a "paid-to-find-flaws" prompt that rewards genuine issues over agreeable responses.

**Three modes:**
- **On-demand** — point it at any file, commit, or feature
- **Post-change** — auto-triggers after major diffs (>50 lines)
- **Scheduled red team** — full-system attack against an 8-point checklist (security, reliability, cost, data loss, stale state, dead code, dependencies, monitoring gaps)

Supports multi-model review: use a different LLM as an external critic since different training data catches different blind spots.

### Memory Keeper — Full Lifecycle Management

Five jobs in one skill:

1. **Extract** — mine expiring sessions for unsaved knowledge before they disappear
2. **Detect stale** — verify memory claims against actual code, cron, processes, file paths
3. **Clean up** — remove obsolete entries, consolidate overlapping topic files
4. **Auto-promote** — score memory entries on durability/impact/scope, graduate proven patterns to enforced rules in CLAUDE.md
5. **Skill extraction** — identify recurring multi-step solutions and extract them into standalone reusable skills

Includes a capacity monitoring table to keep memory, rules, and topic files within healthy limits.

### R&D Council — Multi-Model Debate

6 AI models debate a topic across 3 rounds, cross-examine each other, then produce an executive consensus memo.

**How it works:**
1. **Round 1** — Each model answers independently (parallel, ~10s)
2. **Round 2** — Each model reads all others' answers, identifies strongest/weakest arguments, refines position
3. **Round 3** — Final positions with "I changed my mind because..." or "I maintain because..."
4. **Synthesis** — Judge model produces a memo with consensus, disagreements, action items, and contrarian insights

Supports quick mode (3 models, 2 rounds) and full council (6 models, 3 rounds). Model roster is configurable via env vars.

### Single Source — Dev Machine to Server Sync

Git-only sync between your dev machine and remote server. No rsync. No scp. Git is the bus.

Includes:
- Setup templates for Mac+Cloud, Mac+AWS, Laptop+Desktop, Local+Docker
- Auto-pull cron for the server
- Conflict resolution guide
- Safety rules (never scp, never dual-run, always pull before push)

## Project Structure

```
claude-curated/
├── red-alert/              # Adversarial red team review
├── dependency-tracker/     # Stale reference finder
│   └── references/         # Anti-patterns, dependency chains
├── tldr-eli5/              # Adaptive summarization + ELI5
├── skill-extractor/        # Community skill evaluator
├── claude-md-trim/         # CLAUDE.md rule optimizer
├── skill-profile/          # Profile switching (all/coding/outreach/minimal)
├── memory-keeper/          # Memory lifecycle management
├── skill-guard/            # Security scanner + health auditor
│   ├── scripts/            # Python scanners + fswatch daemon
│   ├── references/         # Threat model
│   └── skills/             # Skill cleaning sub-skill
├── rd-council/             # 6-model debate with cross-examination
└── single-source/          # Dev machine ↔ server sync via GitHub
```

## Contributing

Open an issue or PR. Each skill is self-contained in its own directory with a `SKILL.md` that defines triggers, allowed tools, and behavior.

## License

MIT — see [LICENSE](LICENSE)

# simply-skills-curation

A curated AI coding skill and hook pack for safe local workflows.

`simply-skills-curation` is a public-safe starter pack for local assistant
skills and deterministic hooks. It shows the reusable patterns without shipping
private memory, deployment, bot, or host-specific automation.

## What Is Included

| area | included |
|---|---|
| Skills | `red-alert`, `research-council`, `skill-extractor`, `tldr-eli5`, `skill-profile` |
| Hooks | `dependency-grep`, `guard-safety`, `auto-license`, `auto-repo-check` |
| Examples | fake environment file, dry-run remote-sync config, manual notes backup script |
| Governance | `SECURITY.md`, CODEOWNERS, AGPL-3.0 license |

## Install

The installer copies files into configurable local paths. It does not edit your
assistant settings unless you pass `--configure` and provide `ASSISTANT_SETTINGS`.

```bash
git clone https://github.com/nardovibecoding/simply-skills-curation.git
cd simply-skills-curation
./install.sh
```

Optional settings update:

```bash
ASSISTANT_SETTINGS="$HOME/.config/assistant/settings.json" ./install.sh --configure
```

Useful variables:

| variable | default | meaning |
|---|---|---|
| `AI_TOOL_HOME` | `$HOME/.ai-tool` | install root for skills and hooks |
| `ASSISTANT_SETTINGS` | unset | settings file to update when `--configure` is used |
| `INSTALL_SKILLS` | `1` | copy included skills |
| `INSTALL_HOOKS` | `1` | copy included hooks |

## Skills

| skill | purpose |
|---|---|
| `red-alert` | adversarial self-review for security, reliability, cost, and correctness gaps |
| `research-council` | structured multi-perspective decision review |
| `skill-extractor` | review a community skill before installing it |
| `tldr-eli5` | adaptive summary and plain-English explanation |
| `skill-profile` | switch between small named skill sets |

## Hooks

Hooks are plain Python scripts. They read one JSON event from stdin and either
return `{}` or a small `systemMessage`.

| hook | trigger idea | behavior |
|---|---|---|
| `dependency-grep` | file move/delete or edit | searches the current project for references |
| `guard-safety` | shell command before execution | blocks destructive local commands unless explicitly allowed |
| `auto-license` | repo initialization | reminds you to add license, security, and README files |
| `auto-repo-check` | git push | reminds you to check README and public metadata |

## Configuration

Copy `.env.example` to `.env` only if you want local examples.

```bash
cp .env.example .env
```

The example values are fake. Do not put real tokens or private hosts in public
forks.

## Intentionally Omitted

The private system this template was extracted from includes behavior that does
not belong in a public starter pack:

| omitted private behavior | public replacement |
|---|---|
| real remote deploy sync | `examples/remote-sync.example.yml` dry-run shape |
| real process or bot restart wiring | local, opt-in process examples only |
| private memory search and injection | no bundled private-memory hooks |
| unattended session-end memory commits | `scripts/backup-notes.example.sh` manual example |
| assistant settings mutation by default | explicit `--configure` gate |

## Project Layout

```text
simply-skills-curation/
  skills/
    discovery/
    maintenance/
    security/
    workflow/
  hooks/
    auto-license/
    auto-repo-check/
    dependency-grep/
    guard-safety/
    shared/
  examples/
  scripts/
```

## Release Posture

This repo is a template-style release. It does not publish packages, binaries,
containers, or release archives. SBOM and artifact provenance are therefore not
required for the initial public template, but future packaged releases should
add them before tagging.

## License

[AGPL-3.0](LICENSE)

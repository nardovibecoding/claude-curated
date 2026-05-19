---
name: skill-profile
description: Switch between small local skill profiles: all, coding, writing, or minimal.
---

# Skill Profile

Use this when a user wants a smaller active skill set for a task.

Profiles are examples. Edit `switch-profile.sh` to fit your local skill names.

## Profiles

| profile | keeps |
|---|---|
| `all` | restores every backed-up skill |
| `coding` | review, debug, build, dependency, test, summarize |
| `writing` | summarize, explain, rewrite, review |
| `minimal` | summarize, remind, status |

## Command

```bash
AI_TOOL_HOME="$HOME/.ai-tool" ./switch-profile.sh coding
```

The script only touches `AI_TOOL_HOME/skills`.

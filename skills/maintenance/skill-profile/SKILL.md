---
name: skill-profile
description: |
  Switch skill profiles mid-session. Profiles: all, coding, outreach, minimal.
  Triggers: "coding mode", "outreach mode", "minimal mode", "all skills",
  "switch profile", "load skills for".
  NOT FOR: switching AI models (use /model), changing settings.
  produces: Updated skill profile with only relevant skills loaded for the current task context
---

# Skill Router — Profile Switching

Swap active skills mid-session without restarting.

## Profiles

| Profile | Skills loaded | When |
|---------|-------------|------|
| `all` | Everything | Default, general work |
| `coding` | investigate, review, ship, critic, dependency-tracker, plan-eng-review | Dev/debugging |
| `outreach` | debate, content-humanizer, eli5, office-hours | BD/content work |
| `minimal` | chatid, remind, system-check, home | Quick tasks |

## How to Switch

```bash
# The router script handles symlink swapping
~/.claude/switch-profile.sh <profile>
```

After switching, tell the user: "Switched to {profile} mode. {N} skills active."
The new skills take effect on the NEXT prompt.

## Auto-Detect (optional)
If user's message contains keywords, suggest switching:
- "debug", "fix", "error", "broken" -> suggest coding
- "outreach", "BD", "message", "DM" -> suggest outreach
- Don't auto-switch without asking -- just suggest

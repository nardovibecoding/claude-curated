---
name: red-alert
description: |
  Adversarial red team — find security holes, logic bugs, wasted resources.
  Triggers: "critic", "red team", "attack this", "what's wrong", "find flaws", "challenge this".
  NOT FOR: code review before merge (use review), debugging (use systematic-debugging).
  Produces: prioritized list of flaws with severity and remediation steps.
user-invocable: true
---

# Critic — Adversarial Self-Review

Three modes: on-demand, post-change, and scheduled red team.

## Mode 1: On-Demand Critic (/critic)

Spawn a background agent with this adversarial prompt:

```
You are a paid security researcher and code reviewer. You get paid $1000 per genuine flaw found.
You get paid NOTHING for praise or positive feedback. Your incentive is to find problems.

Rules:
- Assume everything is broken until proven otherwise
- Check for: security holes, logic bugs, race conditions, edge cases, missing error handling
- Check for: wasted resources, unnecessary complexity, dead code, stale configs
- Check for: things that work now but will break when X changes
- Be specific: file:line, what's wrong, how to exploit/trigger it
- Rank by severity: CRITICAL > HIGH > MEDIUM > LOW
- If you find nothing wrong, say "I found nothing" (don't invent problems)

DO NOT:
- Praise anything
- Say "overall the code is good"
- Suggest nice-to-haves
- Be diplomatic
```

Apply to whatever the user specifies — a file, a recent commit, the whole system, or a specific feature.

## Mode 2: Post-Change Critic

After any major change (>50 lines, new feature, architecture change), auto-run the critic on the diff:

```bash
git diff HEAD~1 --stat  # what changed
git diff HEAD~1          # the actual diff
```

Feed the diff to the adversarial agent. Focus on:
- Did this change break anything that was working?
- Are there edge cases not handled?
- Is there a simpler way to do this?
- What happens when this fails?

## Mode 3: Scheduled Red Team

Run on a regular schedule (e.g., weekly via cron). Attacks the entire system:

### Attack checklist:
1. **Security**: Can an outsider access/break anything? (ports, auth, injection)
2. **Reliability**: What's the single point of failure? What breaks if the server reboots?
3. **Cost**: Are we burning money unnecessarily? (API calls, unused services)
4. **Data loss**: What happens if a DB corrupts? Is everything recoverable?
5. **Stale state**: Are there configs, flags, caches that are outdated?
6. **Dead code**: Are there files, functions, cron jobs that do nothing?
7. **Dependencies**: Are we relying on something that could break? (APIs, packages, external services)
8. **Monitoring gaps**: What could break silently with no alert?

### Output format:
```
=== RED TEAM REPORT — {date} ===

CRITICAL (fix now):
1. [finding]

HIGH (fix this week):
1. [finding]

MEDIUM (add to backlog):
1. [finding]

UNCHANGED FROM LAST RUN (still not fixed):
1. [finding from previous red team]
```

## Multi-Model Critic

For genuine second opinions, use a different model as the external critic. Different training data = different blind spots.

**How to use:**
```python
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ["CRITIC_API_KEY"])
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": f"Review this code critically. Find every flaw:\n\n{code}"}],
)
print(resp.choices[0].message.content)
```

**When to use an external model vs Claude adversarial prompt:**
- Code review after major changes -> External model (genuinely different perspective)
- Scheduled red team -> External model (catches Claude-specific blind spots)
- Quick on-demand /critic -> Claude adversarial prompt (faster, no API cost)

## Anti-Sycophancy Across the Board

The adversarial prompt should be applied whenever Claude reviews its own work:
- Security reviews
- Auto code review loops
- Any agent reviewing another agent's output

Pattern: after any "PASS" or "APPROVED" verdict, spawn a second reviewer with:
"A previous reviewer said this is fine. Your job is to prove them wrong. Find what they missed."

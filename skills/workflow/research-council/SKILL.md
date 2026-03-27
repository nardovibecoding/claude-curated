---
name: research-council
description: |
  6-model R&D Council debate — multi-round argument, cross-examination, consensus memo.
  Triggers: "/debate", "council", "R&D meeting", "model debate", "6 models discuss".
  NOT FOR: simple questions (just ask), code review (use review), brainstorming.
  Produces: executive memo with consensus position from 6 AI models.
user-invocable: true
---

# Research Council — Multi-Model Debate

6 AI models autonomously debate a topic across multiple rounds, cross-examine each
other's arguments, then produce an executive memo with consensus and action items.

**Why this exists:** Asking one model gives you one perspective. Asking six models that
argue with each other surfaces blind spots, contrarian insights, and stronger conclusions.

## How it works

### Round 1: Independent Analysis
Each model independently answers the question. No model sees the others' responses.
All 6 run in parallel for speed.

### Round 2: Cross-Examination
Each model receives ALL other models' Round 1 answers and must:
- Identify the **strongest argument** they AGREE with (and why)
- Challenge the **weakest argument** they DISAGREE with (and why)
- **Refine** their own position based on what they learned

### Round 3: Final Position
Each model gives their final answer after seeing Round 2 cross-examinations.
Must state: "I changed my mind because..." or "I maintain my position because..."

### Synthesis: Judge Memo
A judge model reads all 3 rounds and produces a structured memo:

```
R&D COUNCIL MEMO — {date}
Topic: {topic}

CONSENSUS (what all models agree on):
- ...

KEY DISAGREEMENTS:
- Model A vs Model B on X — Model A won because...

TOP 3 ACTION ITEMS:
1. [Actionable, specific, with owner if applicable]
2. ...
3. ...

CONTRARIAN INSIGHT (what only 1-2 models saw):
- ...

Confidence: X/10 | Models: 6/6 responded
```

## Usage

```
/debate Should we use microservices or a monolith for this project?
/debate React vs Svelte vs Vue for our new dashboard?
/debate Is this acquisition worth the asking price?
/debate Review our API design — what are the hidden scaling issues?
```

## Model roster

The council uses 6 different AI models for genuine diversity of thought.
Configure via environment variables or use defaults:

| Role | Default Model | Why |
|------|--------------|-----|
| Analyst 1 | Gemini 2.5 Flash | Strong reasoning, free tier |
| Analyst 2 | DeepSeek V3 | Different training data, strong on code |
| Analyst 3 | Qwen3 | Chinese AI perspective, good at edge cases |
| Analyst 4 | Kimi K2 | Moonshot's model, strong context handling |
| Analyst 5 | Cerebras Llama | Fast inference, different architecture |
| Judge | MiniMax M1 | Good at synthesis and summarization |

### Configuration

Set these env vars to customize the model roster:

| Variable | Default | Description |
|----------|---------|-------------|
| `COUNCIL_MODEL_1` | `gemini-2.5-flash` | First analyst model |
| `COUNCIL_MODEL_2` | `deepseek-chat` | Second analyst model |
| `COUNCIL_MODEL_3` | `qwen3-235b-a22b` | Third analyst model |
| `COUNCIL_MODEL_4` | `kimi-k2` | Fourth analyst model |
| `COUNCIL_MODEL_5` | `llama-4-scout-17b-16e` | Fifth analyst model |
| `COUNCIL_JUDGE` | `minimax-m1` | Judge/synthesis model |
| `COUNCIL_ROUNDS` | `3` | Number of debate rounds (2 = quick, 3 = full) |

## Quick mode vs Full council

- **Quick mode** (`/debate quick ...`): 3 models, 2 rounds, ~1 minute
- **Full council** (`/debate ...`): 6 models, 3 rounds, ~3 minutes

## Implementation notes

Each round uses parallel API calls to minimize latency:
- Round 1: 6 parallel calls (~10s)
- Round 2: 6 sequential calls with context (~30s each)
- Round 3: 6 sequential calls (~30s each)
- Judge: 1 final synthesis call (~15s)

Total: ~20 API calls per full debate. Uses free-tier APIs where available.

## Debate history

All debates are saved to `debate_history.json`:
- Date, topic, all rounds, final memo
- Keeps last 90 days
- Review past debates: `/debate history`

## Example output

```
R&D COUNCIL MEMO — 2026-03-26
Topic: Should we migrate from REST to GraphQL for our public API?

CONSENSUS:
- All 6 models agree: do NOT migrate the existing REST API
- All agree: GraphQL is better for the NEW mobile client (flexible queries)
- All agree: running both in parallel is the pragmatic path

KEY DISAGREEMENTS:
- Gemini vs DeepSeek on timeline: Gemini says 2 months, DeepSeek says 4+
  Winner: DeepSeek — cited migration complexity from similar projects
- Qwen vs Kimi on caching: Qwen says GraphQL caching is solved,
  Kimi says it's still painful at scale
  Winner: Kimi — provided specific examples of cache invalidation issues

TOP 3 ACTION ITEMS:
1. Build GraphQL gateway for mobile client only (2 weeks)
2. Keep REST API as-is for web + external consumers
3. Measure mobile query patterns for 30 days before expanding GraphQL scope

CONTRARIAN INSIGHT:
- Cerebras (only model to mention): "Consider tRPC instead of GraphQL —
  if both client and server are TypeScript, you get type safety without
  the schema overhead"

Confidence: 8/10 | Models: 6/6 responded
```

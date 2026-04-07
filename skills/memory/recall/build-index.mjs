#!/usr/bin/env node
/**
 * Auto-tag index builder — scans code, memory, hooks, skills
 * and assigns topic tags based on path, filename, and content keywords.
 *
 * Outputs tag_index.json: { tag: [file_paths] }
 *
 * Usage: node build-index.mjs
 *
 * Configuration:
 *   Set CLAUDE_DIR env var to override ~/.claude (default).
 *   Add custom paths in the discoverFiles() function.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from "fs";
import { join, basename } from "path";
import { homedir } from "os";

const HOME = homedir();
const CLAUDE_DIR = process.env.CLAUDE_DIR || join(HOME, ".claude");
const INDEX_FILE = join(CLAUDE_DIR, "tag_index.json");

// ---------------------------------------------------------------------------
// Tag rules — keyword patterns → tags
// ---------------------------------------------------------------------------

const TAG_RULES = [
  // Trading & Finance
  { tag: "trading", patterns: [/whale|trade|trading|executor|order|position|portfolio/i] },
  { tag: "strategies", patterns: [/stale|resolution|arb|orderbook|whale.*strat|signal|edge|fair.?value/i] },
  { tag: "polymarket", patterns: [/polymarket|poly_|clob|gamma.?api|condition.?id|token.?id/i] },
  { tag: "kalshi", patterns: [/kalshi/i] },
  { tag: "risk", patterns: [/risk|drawdown|kelly|position.?size|max.?loss/i] },
  { tag: "market-making", patterns: [/market.?mak|spread|bid.?ask|liquidity.?provid/i] },
  { tag: "crypto", patterns: [/crypto|bitcoin|btc|eth|token|blockchain/i] },

  // AI & ML
  { tag: "ai", patterns: [/claude|anthropic|llm|gpt|embedding|transformer|model|ai.?agent/i] },
  { tag: "embeddings", patterns: [/embed|vector|cosine|semantic|bm25|minilm/i] },

  // Infrastructure
  { tag: "hooks", patterns: [/hook|pre.?tool|post.?tool|guard/i] },
  { tag: "telegram", patterns: [/telegram|tg_|chat.?id|bot.?token/i] },
  { tag: "vps", patterns: [/vps|server|deploy|ssh|remote/i] },
  { tag: "mcp", patterns: [/mcp|model.?context|mcp.?server/i] },
  { tag: "security", patterns: [/security|audit|malware|private.?key|auth|permission|guard/i] },

  // Claude Code
  { tag: "memory", patterns: [/memory|recall|remember|MEMORY\.md/i] },
  { tag: "skills", patterns: [/skill|SKILL\.md/i] },
  { tag: "config", patterns: [/config|settings|\.env|environment/i] },

  // Content & Social
  { tag: "x-twitter", patterns: [/twitter|tweet|x\.com/i] },
  { tag: "content", patterns: [/content|digest|newsletter|article|post/i] },

  // Code quality
  { tag: "testing", patterns: [/test|spec|assert|expect|jest|pytest/i] },
  { tag: "dashboard", patterns: [/dashboard|chart|graph|visuali/i] },
  { tag: "data", patterns: [/data|csv|json|pipeline|ingest|scrape/i] },
  { tag: "github", patterns: [/github|repo|git\b|publish/i] },
];

// ---------------------------------------------------------------------------
// File discovery
// ---------------------------------------------------------------------------

function discoverFiles() {
  const files = [];

  // Memory files (all projects under ~/.claude/projects/)
  const projectsDir = join(CLAUDE_DIR, "projects");
  if (existsSync(projectsDir)) {
    for (const project of readdirSync(projectsDir)) {
      const memDir = join(projectsDir, project, "memory");
      if (!existsSync(memDir)) continue;
      for (const f of readdirSync(memDir)) {
        if (f.endsWith(".md") && f !== "MEMORY.md") {
          files.push({ path: join(memDir, f), category: "memory" });
        }
      }
    }
  }

  // Hooks
  const hooksDir = join(CLAUDE_DIR, "hooks");
  if (existsSync(hooksDir)) {
    for (const f of readdirSync(hooksDir)) {
      if (f.endsWith(".py") || f.endsWith(".sh")) {
        files.push({ path: join(hooksDir, f), category: "hook" });
      }
    }
  }

  // Skills
  const skillsDir = join(CLAUDE_DIR, "skills");
  if (existsSync(skillsDir)) {
    for (const d of readdirSync(skillsDir)) {
      const skillFile = join(skillsDir, d, "SKILL.md");
      if (existsSync(skillFile)) {
        files.push({ path: skillFile, category: "skill" });
      }
      const skillDir = join(skillsDir, d);
      if (statSync(skillDir).isDirectory()) {
        for (const f of readdirSync(skillDir)) {
          if (/\.(py|mjs|js|ts|sh)$/.test(f)) {
            files.push({ path: join(skillDir, f), category: "skill" });
          }
        }
      }
    }
  }

  // Add custom project directories here:
  // walkDir(join(HOME, "my-project"), files, "code-python", 3);

  return files;
}

function walkDir(dir, files, category, maxDepth, depth = 0) {
  if (depth >= maxDepth) return;

  let entries;
  try { entries = readdirSync(dir); } catch { return; }

  for (const e of entries) {
    if (["node_modules", "dist", "__pycache__", ".venv", "venv", ".git"].includes(e)) continue;

    const full = join(dir, e);
    let stat;
    try { stat = statSync(full); } catch { continue; }

    if (stat.isDirectory()) {
      walkDir(full, files, category, maxDepth, depth + 1);
    } else if (/\.(py|ts|tsx|js|mjs|md)$/.test(e)) {
      files.push({ path: full, category });
    }
  }
}

// ---------------------------------------------------------------------------
// Tagging
// ---------------------------------------------------------------------------

function tagFile(file) {
  const tags = new Set();
  tags.add(file.category);

  let content = "";
  try {
    content = readFileSync(file.path, "utf-8").slice(0, 2000);
  } catch { return [...tags]; }

  const nameAndContent = basename(file.path) + " " + content;

  for (const rule of TAG_RULES) {
    for (const pat of rule.patterns) {
      if (pat.test(nameAndContent)) {
        tags.add(rule.tag);
        break;
      }
    }
  }

  return [...tags];
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const files = discoverFiles();
  console.log(`Discovered ${files.length} files to index`);

  const tagIndex = {};
  const fileIndex = {};

  for (const file of files) {
    const tags = tagFile(file);
    const shortPath = file.path.replace(HOME + "/", "~/");

    fileIndex[shortPath] = tags;

    for (const tag of tags) {
      if (!tagIndex[tag]) tagIndex[tag] = [];
      tagIndex[tag].push(shortPath);
    }
  }

  const sortedTags = Object.entries(tagIndex)
    .sort((a, b) => b[1].length - a[1].length);

  const output = {
    updated: new Date().toISOString(),
    totalFiles: files.length,
    totalTags: sortedTags.length,
    tags: Object.fromEntries(sortedTags),
    files: fileIndex,
  };

  writeFileSync(INDEX_FILE, JSON.stringify(output, null, 2));

  console.log(`\nTag index saved to ${INDEX_FILE}`);
  console.log(`\nTags (${sortedTags.length}):`);
  for (const [tag, paths] of sortedTags) {
    console.log(`  ${tag.padEnd(20)} ${paths.length} files`);
  }
}

main();

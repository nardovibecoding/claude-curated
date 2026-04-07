#!/usr/bin/env node
/**
 * Hybrid memory search — Vector + BM25 + Recency + Graph with RRF fusion.
 *
 * Usage: node search.mjs "how did we fix the matcher?"
 *        node search.mjs "query" --json    (for hook auto-inject)
 *
 * Vector: all-MiniLM-L6-v2 (22M params, runs locally, no API key).
 * BM25:   TF-IDF with field weighting (name 3x, description 2x, body 1x).
 * Recency: files modified in last 7 days get a rank boost.
 * Graph:  optional traversal of a graph.json for connected nodes.
 * Source: results tagged "mem" (memory) or "wiki" (extra dirs) in output.
 * Fusion: Reciprocal Rank Fusion (k=60) merges all ranked lists.
 *
 * Caches embeddings to avoid re-computing on every search.
 * Uses file content (up to 1000 chars, frontmatter stripped) for embedding.
 *
 * Configuration:
 *   Set MEMORY_DIRS env var to a colon-separated list of directories to search.
 *   Default: ~/.claude/projects/*/memory and ~/wiki (if they exist).
 *   Set GRAPH_FILE env var to point to your graph.json for graph expansion.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const HOME = homedir();
const CLAUDE_DIR = join(HOME, ".claude");
const PROJECTS_DIR = join(CLAUDE_DIR, "projects");
const CACHE_FILE = join(CLAUDE_DIR, ".memory_embeddings_cache.json");

// Configurable: set GRAPH_FILE env var or edit this path
const GRAPH_FILE = process.env.GRAPH_FILE || join(HOME, "graphify-out", "graph.json");

// Configurable: extra wiki/knowledge directories to search
const EXTRA_DIRS = process.env.MEMORY_DIRS
  ? process.env.MEMORY_DIRS.split(":").filter(Boolean)
  : [join(HOME, "wiki"), join(HOME, "NardoWorld")].filter(existsSync);

const args = process.argv.slice(2);
const jsonMode = args.includes("--json");
const query = args.filter(a => a !== "--json")[0];
if (!query) {
  console.error("Usage: node search.mjs \"<query>\" [--json]");
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Find all memory files
// ---------------------------------------------------------------------------

function findFilesRecursive(dir, source) {
  const results = [];
  if (!existsSync(dir)) return results;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== '__pycache__' && entry.name !== 'node_modules') {
      results.push(...findFilesRecursive(fullPath, source));
    } else if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'MEMORY.md' && entry.name !== '_index.md') {
      const stat = statSync(fullPath);
      results.push({ path: fullPath, project: source, name: entry.name, mtime: stat.mtimeMs });
    }
  }
  return results;
}

function findMemoryFiles() {
  const files = [];
  if (existsSync(PROJECTS_DIR)) {
    for (const project of readdirSync(PROJECTS_DIR)) {
      const memDir = join(PROJECTS_DIR, project, "memory");
      files.push(...findFilesRecursive(memDir, project));
    }
  }
  for (const dir of EXTRA_DIRS) {
    files.push(...findFilesRecursive(dir, dir.split("/").pop()));
  }
  return files;
}

// ---------------------------------------------------------------------------
// Frontmatter parsing
// ---------------------------------------------------------------------------

function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)/);
  if (!m) return { fm: {}, body: text.trim() };
  const fm = {};
  for (const line of m[1].split("\n")) {
    const idx = line.indexOf(":");
    if (idx > 0) {
      fm[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
  return { fm, body: m[2].trim() };
}

// ---------------------------------------------------------------------------
// BM25 with field weighting
// ---------------------------------------------------------------------------

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9_\-]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 1);
}

function bm25Search(docs, queryText, k1 = 1.5, b = 0.75) {
  const queryTokens = tokenize(queryText);
  if (queryTokens.length === 0) return docs.map(() => 0);

  const N = docs.length;
  const tokenizedDocs = docs.map((d) => tokenize(d));
  const avgDl = tokenizedDocs.reduce((s, d) => s + d.length, 0) / N || 1;

  const df = {};
  for (const qt of queryTokens) {
    df[qt] = 0;
    for (const doc of tokenizedDocs) {
      if (doc.includes(qt)) df[qt]++;
    }
  }

  const scores = tokenizedDocs.map((docTokens) => {
    const dl = docTokens.length;
    let score = 0;
    const tf = {};
    for (const t of docTokens) tf[t] = (tf[t] || 0) + 1;

    for (const qt of queryTokens) {
      const termFreq = tf[qt] || 0;
      if (termFreq === 0) continue;
      const docFreq = df[qt] || 0;
      const idf = Math.log((N - docFreq + 0.5) / (docFreq + 0.5) + 1);
      const tfNorm = (termFreq * (k1 + 1)) / (termFreq + k1 * (1 - b + b * (dl / avgDl)));
      score += idf * tfNorm;
    }
    return score;
  });

  return scores;
}

// ---------------------------------------------------------------------------
// Embedding (vector search)
// ---------------------------------------------------------------------------

let embedder = null;

async function getEmbedder() {
  if (embedder) return embedder;
  const { pipeline } = await import("@huggingface/transformers");
  embedder = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2", { dtype: "fp32" });
  return embedder;
}

async function embed(texts) {
  const model = await getEmbedder();
  const output = await model(texts, { pooling: "mean", normalize: true });
  const data = output.data;
  const dim = output.dims[output.dims.length - 1];

  const vectors = [];
  for (let i = 0; i < texts.length; i++) {
    const vec = new Float32Array(dim);
    for (let k = 0; k < dim; k++) vec[k] = data[i * dim + k];
    vectors.push(Array.from(vec));
  }
  return vectors;
}

function cosineSim(a, b) {
  let dot = 0;
  for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
  return dot;
}

// ---------------------------------------------------------------------------
// Recency ranking
// ---------------------------------------------------------------------------

function recencyRanked(files) {
  const now = Date.now();
  const SEVEN_DAYS = 7 * 24 * 60 * 60 * 1000;
  return files
    .map((f, index) => {
      const age = now - f.mtime;
      const score = age < SEVEN_DAYS ? 1.0 - (age / SEVEN_DAYS) * 0.5 : 0.5 * Math.exp(-(age - SEVEN_DAYS) / (30 * 24 * 60 * 60 * 1000));
      return { index, score };
    })
    .sort((a, b) => b.score - a.score);
}

// ---------------------------------------------------------------------------
// Graph-augmented retrieval
// ---------------------------------------------------------------------------

let graphData = null;

function loadGraph() {
  if (graphData !== null) return graphData;
  if (!existsSync(GRAPH_FILE)) { graphData = false; return false; }
  try {
    graphData = JSON.parse(readFileSync(GRAPH_FILE, "utf-8"));
    return graphData;
  } catch {
    graphData = false;
    return false;
  }
}

function graphExpand(topFilePaths) {
  const graph = loadGraph();
  if (!graph || !graph.nodes) return new Set();

  const matchedNodeIds = new Set();
  for (const node of graph.nodes) {
    const sf = node.source_file || "";
    if (!sf) continue;
    for (const fp of topFilePaths) {
      const fpBase = fp.split("/").pop().replace(".md", "");
      const sfBase = sf.split("/").pop().replace(/\.\w+$/, "");
      if (fpBase === sfBase || sf.includes(fpBase) || fp.includes(sfBase)) {
        matchedNodeIds.add(node.id);
      }
    }
  }

  const neighborIds = new Set();
  if (graph.links) {
    for (const link of graph.links) {
      if (matchedNodeIds.has(link.source)) neighborIds.add(link.target);
      if (matchedNodeIds.has(link.target)) neighborIds.add(link.source);
    }
  }

  const expandedFiles = new Set();
  for (const node of graph.nodes) {
    if (neighborIds.has(node.id) && !matchedNodeIds.has(node.id)) {
      const sf = node.source_file || "";
      if (sf) expandedFiles.add(sf.split("/").pop().replace(/\.\w+$/, ""));
    }
  }
  return expandedFiles;
}

// ---------------------------------------------------------------------------
// Reciprocal Rank Fusion
// ---------------------------------------------------------------------------

function reciprocalRankFusion(rankedLists, k = 60) {
  const fusedScores = {};

  for (const ranked of rankedLists) {
    for (let rank = 0; rank < ranked.length; rank++) {
      const idx = ranked[rank].index;
      if (!fusedScores[idx]) fusedScores[idx] = 0;
      fusedScores[idx] += 1 / (k + rank + 1);
    }
  }

  return Object.entries(fusedScores)
    .map(([index, score]) => ({ index: parseInt(index), score }))
    .sort((a, b) => b.score - a.score);
}

// ---------------------------------------------------------------------------
// Cache
// ---------------------------------------------------------------------------

function loadCache() {
  if (!existsSync(CACHE_FILE)) return {};
  try { return JSON.parse(readFileSync(CACHE_FILE, "utf-8")); }
  catch { return {}; }
}

function saveCache(cache) {
  writeFileSync(CACHE_FILE, JSON.stringify(cache));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const files = findMemoryFiles();
  if (files.length === 0) {
    console.log("No memory files found.");
    process.exit(0);
  }

  const fileParsed = files.map((f) => {
    const raw = readFileSync(f.path, "utf-8");
    return parseFrontmatter(raw);
  });

  // Build search text with field weighting: name 3x, description 2x, body 1x
  const fileTexts = files.map((f, i) => {
    const name = f.name.replace(".md", "").replace(/_/g, " ");
    const desc = fileParsed[i].fm.description || "";
    const body = fileParsed[i].body.slice(0, 1000);
    return `${name} ${name} ${name} ${desc} ${desc} ${body}`;
  });

  // BM25 scores
  const bm25Scores = bm25Search(fileTexts, query);
  const bm25Ranked = bm25Scores
    .map((score, index) => ({ index, score }))
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score);

  // Vector scores — compact text for embedding
  const embedTexts = files.map((f, i) => {
    const name = f.name.replace(".md", "").replace(/_/g, " ");
    const desc = fileParsed[i].fm.description || "";
    const body = fileParsed[i].body.slice(0, 800);
    return `${name}: ${desc} ${body}`;
  });

  const cache = loadCache();
  const textsToEmbed = [];
  const textsToEmbedIdx = [];

  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    const cached = cache[f.path];
    if (cached && cached.mtime >= f.mtime) continue;
    textsToEmbed.push(embedTexts[i]);
    textsToEmbedIdx.push(i);
  }

  if (textsToEmbed.length > 0) {
    const BATCH_SIZE = 16;
    process.stderr.write(`Embedding ${textsToEmbed.length} memory files (batch=${BATCH_SIZE})...\n`);
    for (let b = 0; b < textsToEmbed.length; b += BATCH_SIZE) {
      const batchTexts = textsToEmbed.slice(b, b + BATCH_SIZE);
      const batchIdx = textsToEmbedIdx.slice(b, b + BATCH_SIZE);
      const vectors = await embed(batchTexts);
      for (let j = 0; j < batchIdx.length; j++) {
        const i = batchIdx[j];
        const f = files[i];
        cache[f.path] = {
          mtime: f.mtime,
          vector: vectors[j],
          name: f.name,
          project: f.project,
        };
      }
      saveCache(cache);
      if (b + BATCH_SIZE < textsToEmbed.length) {
        process.stderr.write(`  ${Math.min(b + BATCH_SIZE, textsToEmbed.length)}/${textsToEmbed.length} done\n`);
      }
    }
  }

  const [queryVec] = await embed([query]);

  const vectorScores = files.map((f, i) => {
    const cached = cache[f.path];
    if (!cached || !cached.vector) return { index: i, score: 0 };
    return { index: i, score: cosineSim(queryVec, cached.vector) };
  });

  const vectorRanked = [...vectorScores].sort((a, b) => b.score - a.score);

  // Recency ranking
  const recencyRank = recencyRanked(files);

  // RRF Fusion (3 signals: vector, BM25, recency)
  const fused = reciprocalRankFusion([vectorRanked, bm25Ranked, recencyRank]);

  // Graph expansion: boost files connected to top results
  const top5 = fused.slice(0, 5);
  const topFilePaths = top5.map(r => files[r.index].path);
  const graphNeighborFiles = graphExpand(topFilePaths);

  if (graphNeighborFiles.size > 0) {
    for (const r of fused.slice(5, 20)) {
      const f = files[r.index];
      const fBase = f.name.replace(".md", "");
      for (const gf of graphNeighborFiles) {
        if (fBase === gf || fBase.includes(gf) || gf.includes(fBase)) {
          r.score += 0.005;
          r.graphBoosted = true;
          break;
        }
      }
    }
    fused.sort((a, b) => b.score - a.score);
  }

  const top = fused.slice(0, 5);

  if (jsonMode) {
    // JSON output for hook auto-inject
    const results = top.map(r => {
      const f = files[r.index];
      const desc = fileParsed[r.index].fm.description || "";
      const label = EXTRA_DIRS.some(d => f.path.startsWith(d)) ? "wiki" : "mem";
      return {
        score: r.score.toFixed(4),
        source: label,
        file: f.name,
        path: f.path,
        description: desc.slice(0, 120),
        graphBoosted: !!r.graphBoosted,
      };
    });
    console.log(JSON.stringify(results));
  } else {
    console.log(`Query: "${query}"\n`);
    console.log(`  Found ${files.length} memory files | BM25 hits: ${bm25Ranked.length} | Vector: all scored | Graph: ${graphNeighborFiles.size} neighbors\n`);

    for (const r of top) {
      const f = files[r.index];
      const vecScore = vectorScores[r.index].score;
      const bm25Score = bm25Scores[r.index];
      const bar = "█".repeat(Math.round(r.score * 600));
      const graphTag = r.graphBoosted ? " [G]" : "";
      const label = EXTRA_DIRS.some(d => f.path.startsWith(d)) ? "wiki" : "mem";

      console.log(`  [RRF ${r.score.toFixed(4)}] ${bar}${graphTag}`);
      console.log(`  vec=${vecScore.toFixed(3)}  bm25=${bm25Score.toFixed(2)}`);
      console.log(`  [${label}] ${f.name}`);
      console.log(`  ${f.path}\n`);
    }
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});

#!/usr/bin/env node
// refresh-meta.mjs — opt-in metadata injector for index.html
//
// For each featured repo, fetch `pushed_at` via `gh api` and rewrite the
// text content of <span data-meta="<repo>.last_commit"> in index.html.
// Also stamps the footer <span data-meta="last_deployed"> with today's
// ISO date.
//
// Usage:   node scripts/refresh-meta.mjs
// Requires: gh CLI, authenticated as a user with read access to each repo.

import { execSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const INDEX = resolve(HERE, "..", "index.html");

const REPOS = [
  { owner: "jakethehoffer", name: "trader",    key: "trader.last_commit" },
  { owner: "jakethehoffer", name: "arbitrage", key: "arbitrage.last_commit" },
];

function ghPushedAt(owner, name) {
  try {
    const json = execSync(`gh api repos/${owner}/${name}`, { encoding: "utf8" });
    return JSON.parse(json).pushed_at;
  } catch (err) {
    console.warn(`[skip] ${owner}/${name}: ${err.message.split("\n")[0]}`);
    return null;
  }
}

function humanize(iso) {
  if (!iso) return null;
  const then = new Date(iso);
  const now = new Date();
  const days = Math.floor((now - then) / 86400000);
  if (days <= 0) return "last commit: today";
  if (days === 1) return "last commit: 1d ago";
  if (days < 14) return `last commit: ${days}d ago`;
  if (days < 60) return `last commit: ${Math.round(days / 7)}w ago`;
  return `last commit: ${then.toISOString().slice(0, 10)}`;
}

function replaceMeta(html, key, value) {
  if (value == null) return html;
  // Match any text between the opening and closing tag.
  const pattern = new RegExp(
    `(<span[^>]*data-meta="${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*>)([^<]*)(</span>)`,
    "g"
  );
  return html.replace(pattern, (_, open, _old, close) => `${open}${value}${close}`);
}

function main() {
  let html = readFileSync(INDEX, "utf8");
  let touched = 0;

  for (const repo of REPOS) {
    const value = humanize(ghPushedAt(repo.owner, repo.name));
    if (!value) continue;
    const before = html;
    html = replaceMeta(html, repo.key, value);
    if (html !== before) {
      touched++;
      console.log(`[ok]   ${repo.key} = "${value}"`);
    } else {
      console.warn(`[miss] ${repo.key} (no sentinel found in index.html)`);
    }
  }

  // Footer last_deployed
  const today = new Date().toISOString().slice(0, 10);
  const before = html;
  html = replaceMeta(html, "last_deployed", `last_deployed: ${today}`);
  if (html !== before) {
    touched++;
    console.log(`[ok]   last_deployed = ${today}`);
  }

  if (touched > 0) {
    writeFileSync(INDEX, html, "utf8");
    console.log(`\nWrote ${touched} update(s) to ${INDEX}.`);
  } else {
    console.log("\nNo updates written.");
  }
}

main();

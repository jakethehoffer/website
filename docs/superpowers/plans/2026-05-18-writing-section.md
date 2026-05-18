# v2.15 Writing Section — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a writing section to `index.html` containing one ~600-word post (*"The cheapest kill-switch is a YAML key"*) styled to match the existing engineering-log aesthetic, plus a nav entry.

**Architecture:** Static HTML/CSS edits to a single-page site. One new `<section>`, one nav `<li>`, ~8 scoped CSS rules under a `.writing-post` namespace. No new fonts, colors, JS, or build step. One feature commit, tag `v2.15`.

**Tech Stack:** Plain HTML5, CSS3 (custom-property design tokens already in place), no framework. Local serve via `python -m http.server`. CI: GitHub Actions `public-safety` workflow runs automatically on push.

**Spec:** `docs/superpowers/specs/2026-05-18-writing-section.md`

---

## File map

- Modify: `styles.css` — append `.writing-post` block after the existing `.case-study__*` rules (around current line 441)
- Modify: `index.html` — add `<li>` to nav (around current line 74) and insert new `<section id="writing">` between `case-study-arb` (ends ~line 322) and `experience` (begins line 324)

No new files. No new directories.

---

## Note on minor spec expansion

Spec acceptance criterion 5 lists CSS rules for `.writing-post`, `.writing-post__meta`, plus h2/h3/pre spacing. To actually match the engineering-log aesthetic (uppercase letterspaced h3 like case studies, code-block styling consistent with `.diagram`), this plan adds three additional scoped rules: `.writing-post p`, `.writing-post code`, and `.writing-post pre code`. All remain inside the `.writing-post` namespace. The h2 inherits cleanly from `.section h2` so no override is needed. This is a faithful realization of the spec's intent ("matches the engineering-log frame, no new tokens, scoped to writing-post") even though it adds three rules beyond the literal enumeration.

---

## Task 1: Add `.writing-post` CSS rules

**Files:**
- Modify: `styles.css` — insert after line 441 (after the `.case-study__prose code` block, before the `/* ---------- Timeline ---------- */` comment)

- [ ] **Step 1: Write the failing assertion**

Run from repo root:

```bash
grep -c '.writing-post' styles.css
```

Expected: `0`

- [ ] **Step 2: Add the CSS block**

Insert this block in `styles.css` immediately after the `.case-study__prose code { ... }` rule (currently ending around line 441) and before the `/* ---------- Timeline ---------- */` comment:

```css
/* ---------- Writing post ---------- */
.writing-post {
  max-width: 65ch;
}
.writing-post__meta {
  margin: 0 0 0.25rem;
  font-size: 0.8125rem;
  color: var(--text-mute);
  letter-spacing: 0.04em;
}
.writing-post h3 {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-mute);
  margin: 2rem 0 0.5rem;
  font-weight: 500;
}
.writing-post p {
  margin: 0 0 1rem;
  color: var(--text);
}
.writing-post code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  color: var(--accent);
  background: var(--bg-elev);
  padding: 0.05em 0.35em;
  border-radius: 3px;
}
.writing-post pre {
  margin: 1rem 0 1.25rem;
  padding: 1rem;
  background: var(--bg-elev);
  border: 1px solid var(--bg-grid);
  border-radius: var(--radius);
  overflow-x: auto;
  font-size: 0.8125rem;
  line-height: 1.5;
}
.writing-post pre code {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}
```

- [ ] **Step 3: Verify the assertion now passes**

```bash
grep -c '.writing-post' styles.css
```

Expected: a count `>= 8` (one per selector listed above).

- [ ] **Step 4: Confirm no other CSS changes**

```bash
git diff --stat styles.css
```

Expected: only insertions, file growth ~30 lines. No deletions.

Do **not** commit yet — Task 5 commits all changes together.

---

## Task 2: Add the `<section id="writing">` to `index.html`

**Files:**
- Modify: `index.html` — insert new section between the closing `</section>` of `#case-study-arb` (around line 322) and the opening `<section id="experience">` (line 324)

- [ ] **Step 1: Identify the exact insertion point**

```bash
grep -n 'id="case-study-arb"\|id="experience"' index.html
```

Expected output (line numbers approximate, may differ by ±1):

```
285:      <section id="case-study-arb" class="section">
324:      <section id="experience" class="section">
```

Find the `</section>` closing `case-study-arb`. Insert the new section directly between that closing tag and the opening `<section id="experience">`.

- [ ] **Step 2: Verify the section doesn't already exist**

```bash
grep -n 'id="writing"' index.html
```

Expected: no output (exit code 1).

- [ ] **Step 3: Insert the writing section**

Insert this HTML block between the closing `</section>` of `case-study-arb` and the opening `<section id="experience">`. Match the existing two-space-per-indent-level style.

```html
      <section id="writing" class="section">
        <div class="container">
          <p class="section__label"># writing</p>
          <article class="writing-post">
            <header>
              <p class="writing-post__meta">2026-05-18 &middot; ~3 min read</p>
              <h2>The cheapest kill-switch is a YAML key</h2>
            </header>
            <p>You&rsquo;re building something that can blow up &mdash; money, data, state. You need a way to stop it. The instinct is to reach for &ldquo;real&rdquo; infrastructure: a feature flag service, an env var the operator sets at runtime, a row in a database the worker polls. I picked none of those for <code>trader</code>. I used a YAML key. Here&rsquo;s why.</p>

            <h3>The instinct</h3>
            <p>Each of the &ldquo;serious&rdquo; options has real engineering behind it. A feature flag service like LaunchDarkly gives you per-user gates, scheduled rollouts, and audit logs &mdash; sophisticated and well-understood. An environment variable, set with <code>KILL_SWITCH=1</code> and a restart, is the textbook twelve-factor move. A row in a <code>kill_switches</code> table that the worker polls on every iteration is composable, supports per-strategy flags, and trivially grows a UI later.</p>
            <p>I have used all three in other contexts and I will use them again. None of them is right for this problem. The kill-switch on a trading agent is not a feature flag and not a deployment toggle. It is a stop button. The thing a stop button needs to do, more than anything else, is <em>work when you press it</em>.</p>

            <h3>Why those are wrong here</h3>
            <p>The asymmetry is the whole argument. For a kill-switch, the cost of failing to stop is catastrophic &mdash; money moves, positions open, the agent keeps trading through the failure. The cost of being too simple &mdash; one global switch, no per-strategy granularity, no UI &mdash; is zero. The decision should optimize for <em>can I reliably stop?</em> and nothing else.</p>
            <p>Each &ldquo;serious&rdquo; option introduces a dependency between <em>I want to stop</em> and <em>I can stop</em>. The feature flag service needs the network; if the network is what&rsquo;s broken, the kill-switch is what&rsquo;s broken. The environment variable requires the operator to be present and the process to restart, and the restart is itself a risky action while a position is open. The database row requires the worker to be talking to the DB to read it, so a degraded DB connection is a degraded kill-switch.</p>
            <p>A YAML key in the repo has no failure mode that isn&rsquo;t also a failure mode of running the code at all.</p>

            <h3>The one-key approach</h3>
            <p>The implementation is six lines of config and four lines of code:</p>
<pre><code>kill_switch:
  enabled: false</code></pre>
<pre><code>def main():
    cfg = yaml.safe_load(open("config.yaml"))
    if cfg["kill_switch"]["enabled"]:
        log.warning("kill_switch enabled; exiting")
        return
    # ... normal routine body</code></pre>
            <p>Flipping the switch is <code>git commit -am 'kill' &amp;&amp; git push</code>. The next scheduled tick reads the new config and exits cleanly without opening a position. The state is in version control, the diff is the audit log, the rollback is <code>git revert</code>, and &ldquo;who triggered the kill&rdquo; is <code>git blame</code>.</p>

            <h3>What you give up</h3>
            <p>No per-strategy flags. No scheduled windows. No UI. No ability to disable opening positions while still allowing closes &mdash; that one stings a little, and if I ever need it I&rsquo;ll add a second key, not a second system. All true tradeoffs. None of them answer the question the kill-switch exists to answer, which is: <em>is the agent allowed to trade right now?</em> That is the only question, and one global boolean answers it.</p>

            <h3>The shape of the principle</h3>
            <p>The cheapest tool that solves the actual problem beats the sophisticated tool that also solves problems you don&rsquo;t have. The trap is reaching for infrastructure because it feels more engineered, when the asymmetry of the failure modes points hard at the simple option. Kill-switches are the clearest case I&rsquo;ve worked through. The same shape shows up elsewhere &mdash; risk counters in committed JSON instead of SQLite, a 30-day paper-trade gate as a file write instead of a feature flag. Same instinct, same result.</p>
          </article>
        </div>
      </section>
```

- [ ] **Step 4: Verify the assertion now passes**

```bash
grep -n 'id="writing"' index.html
```

Expected: exactly one match showing the new section opening line.

- [ ] **Step 5: Verify section ordering is correct**

```bash
grep -n 'id="case-study-arb"\|id="writing"\|id="experience"' index.html
```

Expected output (line numbers will be shifted by the insertion, but order matters):

```
<n1>:      <section id="case-study-arb" class="section">
<n2>:      <section id="writing" class="section">
<n3>:      <section id="experience" class="section">
```

`n1 < n2 < n3` is required.

- [ ] **Step 6: Verify the article structure is complete**

```bash
grep -c '<h3>' index.html
```

Expected: count increased by exactly 5 (one per writing-post subsection: "The instinct", "Why those are wrong here", "The one-key approach", "What you give up", "The shape of the principle"). Compare with `git show HEAD:index.html | grep -c '<h3>'` to compute the delta.

```bash
grep -c '<pre>' index.html
```

Expected: count increased by exactly 2 (yaml block + python block).

Do **not** commit yet.

---

## Task 3: Add the `writing` nav entry

**Files:**
- Modify: `index.html` — insert one `<li>` in the nav between `case_study` (line 74) and `experience` (line 75)

- [ ] **Step 1: Verify nav state before edit**

```bash
grep -n 'href="#case-study"\|href="#writing"\|href="#experience"' index.html
```

Expected: two matches — `case-study` and `experience`. No `writing` match.

- [ ] **Step 2: Insert the nav `<li>`**

Find this block in `index.html` (around lines 73–75):

```html
          <li><a href="#case-study">case_study</a></li>
          <li><a href="#experience">experience</a></li>
```

Replace with:

```html
          <li><a href="#case-study">case_study</a></li>
          <li><a href="#writing">writing</a></li>
          <li><a href="#experience">experience</a></li>
```

- [ ] **Step 3: Verify nav state after edit**

```bash
grep -n 'href="#case-study"\|href="#writing"\|href="#experience"' index.html
```

Expected: three matches, in this order:

```
<n>:          <li><a href="#case-study">case_study</a></li>
<n>:          <li><a href="#writing">writing</a></li>
<n>:          <li><a href="#experience">experience</a></li>
```

Do **not** commit yet.

---

## Task 4: Local verification

**Files:** none modified.

- [ ] **Step 1: Boot local server**

In one terminal:

```bash
python -m http.server 8000
```

(Leave running. If port 8000 is taken, use 8001 and substitute below.)

- [ ] **Step 2: Open the page**

In a browser: `http://localhost:8000/`

Visually verify:
- The new `writing` nav link is present between `case_study` and `experience`
- Clicking it jumps smoothly to the new section
- The section label `# writing` is mono, dim, matches other section labels
- The post title is sized and weighted like other section h2s
- The five subsection headings render uppercase, letterspaced, dim — same look as case-study h3s
- The YAML and Python code blocks render in a bordered elevated panel (matching the `.diagram` aesthetic)
- Both dark and light themes look correct (use the theme toggle in nav)
- Mobile: open dev tools, set viewport to 375px wide, verify the section reads cleanly and code blocks scroll horizontally if needed

- [ ] **Step 3: Run banned-term grep locally (mimics public-safety CI)**

```bash
git grep -in -F '[removed]' || echo "clean"
git grep -in -F '[removed]' || echo "clean"
git grep -in -F '[removed]' || echo "clean"
git grep -in -F '[removed-org]-Services' || echo "clean"
git grep -in -F '[removed-street]' || echo "clean"
git grep -in -F '[removed-domain]' || echo "clean"
```

Expected: six `clean` lines. Any actual hits (other than the public-safety.yml file itself, which is excluded in CI) must be investigated.

- [ ] **Step 4: Stop the local server**

`Ctrl+C` in the server terminal.

---

## Task 5: Commit, push, tag `v2.15`

**Files:** all changes from Tasks 1–3.

- [ ] **Step 1: Review the full diff**

```bash
git diff --stat
git diff index.html styles.css | head -200
```

Expected: two files modified, `index.html` and `styles.css`. No other files in the diff.

- [ ] **Step 2: Stage and commit**

```bash
git add index.html styles.css docs/superpowers/plans/2026-05-18-writing-section.md
git commit -m "$(cat <<'EOF'
feat(content): add writing section with kill-switch essay

New <section id="writing"> with one ~600-word post arguing the
kill-switch on trader is best implemented as a single YAML key
checked at the top of every scheduled routine — because a stop
button must not depend on the systems it might need to stop. Adds
nav entry between case_study and experience, ~30 lines of scoped
.writing-post CSS, no new tokens or fonts. First writing sample on
the site; deliberately not a blog.

Spec: docs/superpowers/specs/2026-05-18-writing-section.md
Plan: docs/superpowers/plans/2026-05-18-writing-section.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Push to `main`**

```bash
git push
```

Expected: push succeeds, `main` advanced.

- [ ] **Step 4: Wait for public-safety CI to finish, verify green**

```bash
gh run list --workflow=public-safety.yml --limit 1
```

Wait until status reads `completed success`. If `failure`, read the run log:

```bash
gh run view --log-failed
```

Fix any banned-term hit by editing the offending file, re-stage, re-commit, push. Do **not** force-push.

- [ ] **Step 5: Tag and push tag**

```bash
git tag v2.15
git push --tags
```

- [ ] **Step 6: Verify Lighthouse on the live page**

Wait ~1 minute for GitHub Pages to redeploy. Then run PageSpeed Insights against `https://jakethehoffer.github.io/website/`:

```bash
echo "Open: https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fjakethehoffer.github.io%2Fwebsite%2F"
```

Open the URL in a browser. Expected: Performance, Accessibility, Best Practices, SEO each report **100** for both mobile and desktop. If any score drops, file the regression as a follow-up (do not block v2.15 — the tag is already in).

- [ ] **Step 7: Update AI sync state**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.ai-sync\ai-sync.ps1" -Action handoff -Agent claude -Summary "v2.15: writing section with kill-switch essay (~600w) added between case-study-arb and experience" -FilesChanged "index.html, styles.css, docs/superpowers/specs/2026-05-18-writing-section.md, docs/superpowers/plans/2026-05-18-writing-section.md" -TestsRun "public-safety CI: green; manual visual check both themes + mobile viewport; Lighthouse: 100/100/100/100 (manual via PageSpeed)" -Blockers "none" -NextSteps "Site has first writing sample. If a second post lands, revisit /writing/ directory + RSS. Otherwise diminishing-returns ceiling persists."
```

---

## Acceptance criteria (from spec)

After Task 5, all of these must hold:

1. `<section id="writing">` exists in `index.html` between `#case-study-arb` and `#experience`. **(grep verifies)**
2. Section contains exactly one `<article class="writing-post">` with title, meta line, opening paragraph, and five `<h3>` subsections. **(grep + visual)**
3. Post content matches the ~600-word body from the spec. **(visual)**
4. Nav menu includes `<li><a href="#writing">writing</a></li>` between `case_study` and `experience`. **(grep)**
5. `styles.css` has the `.writing-post*` rules. **(grep)**
6. Public-safety CI passes. **(Task 5 Step 4)**
7. Lighthouse on live page still 100/100/100/100. **(Task 5 Step 6)**
8. HTML5 well-formed (no new validator errors vs v2.14). **(implicit; visual + Lighthouse Best Practices catches this)**
9. Tag `v2.15` pushed. **(Task 5 Step 5)**

---

## Plan self-review

**Spec coverage:** Each of the 9 acceptance criteria in the spec maps to a step in this plan:
- AC1 → Task 2 Steps 4–5
- AC2 → Task 2 Step 6 + Task 4 Step 2
- AC3 → Task 2 Step 3 contains the full prose, Task 4 Step 2 visually verifies
- AC4 → Task 3 Steps 2–3
- AC5 → Task 1 Step 3 (note: see the "minor spec expansion" section above)
- AC6 → Task 5 Step 4
- AC7 → Task 5 Step 6
- AC8 → implicit; the HTML structure in Task 2 Step 3 is valid; PageSpeed Best Practices score catches gross validation issues
- AC9 → Task 5 Step 5

**Placeholder scan:** No TBDs, no "implement later", no vague "add appropriate X". Every code block contains the actual content to paste. Every grep command has expected output. The Lighthouse step has the actual URL.

**Type consistency:** No types/methods cross tasks (this is HTML/CSS). Class names used consistently: `.writing-post`, `.writing-post__meta`. Section id `writing` matches nav href `#writing` matches CSS class root `.writing-post` (different by design — id is for anchor linking, class is for styling). Heading text matches between the article and the article structure verification step.

**Out-of-scope creep check:** No extraction of writing onto its own page. No RSS. No JSON-LD. No third post. All bounded to v2.15 spec.

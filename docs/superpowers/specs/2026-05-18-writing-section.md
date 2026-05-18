# v2.15 — writing section with one focused post

Date: 2026-05-18

## Why

After v2.14 the site has two case studies, perfect Lighthouse, CI privacy
guards, idempotent resume pipeline, JSON-LD, and weekly auto-refresh. The
remaining gap is technical-communication signal: a recruiter or engineering
reviewer can see *what* was built but not *how the author thinks* in prose.
A focused writing sample fills that gap without adding infrastructure debt.

One post — not a blog, not RSS, not a separate page. The principle is the
same one this site already lives by: ship the cheapest thing that solves
the actual problem. If a second post ever exists, *then* `/writing/` and
RSS become worth their weight.

## What ships

A new section `<section id="writing">` inserted between
`#case-study-arb` and `#experience` in `index.html`, containing one
~600-word post titled **"The cheapest kill-switch is a YAML key."**

The post is rendered inline as an `<article class="writing-post">` with a
short meta line (date + read time), an `<h2>` title, and five `<h3>`
subsections. No new colors, fonts, or CSS architecture — just two small
additions to `styles.css` for the article max-width and meta line.

The nav gains one entry `writing` between `case_study` and `experience`.

## Post content (~600 words)

### Title
> The cheapest kill-switch is a YAML key

### Meta line
> 2026-05-18 · ~3 min read

### Opening paragraph (~60w)
You're building something that can blow up — money, data, state. You need
a way to stop it. The instinct is to reach for "real" infrastructure: a
feature flag service, an env var the operator sets at runtime, a row in a
database the worker polls. I picked none of those for `trader`. I used a
YAML key. Here's why.

### `### The instinct` (~120w)
Walks through the three "serious" options:
- **Feature flag service** (LaunchDarkly etc.) — gives you per-user gates,
  scheduled rollouts, audit logs. Sophisticated and well-understood.
- **Env var the operator sets** — `KILL_SWITCH=1` and restart. Standard
  twelve-factor move.
- **Database row** — the worker polls a `kill_switches` table on every
  iteration. Composable, supports per-strategy flags, has a UI.

All three are real engineering. None of them is right for this problem.

### `### Why those are wrong here` (~160w)
The asymmetry is the whole argument. For a kill-switch, the cost of
failing to stop is catastrophic (money moves, positions open, the agent
keeps going). The cost of being too simple — one global switch, no
per-strategy granularity, no UI — is zero. The decision should optimize
for *can I reliably stop?* and nothing else.

Each "serious" option introduces a dependency between *I want to stop* and
*I can stop*:
- Feature flag service: needs network. If the network is what's broken,
  you can't stop.
- Env var: requires the operator to be present and the process to
  restart. The restart is itself a risky action while a position is open.
- DB row: the worker has to be talking to the DB to read it. If the DB
  connection is degraded, the kill-switch is degraded.

The YAML key has no failure mode that isn't also a failure mode of
running the code at all. If git is broken, the routine can't start in the
first place — so the kill-switch is fine.

### `### The one-key approach` (~150w)
The actual implementation:

```yaml
# config.yaml
kill_switch:
  enabled: false
```

```python
# Top of every scheduled routine
import yaml

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    if cfg["kill_switch"]["enabled"]:
        print("kill_switch.enabled = true, exiting")
        return
    # ... normal routine body
```

Flipping the switch is `git commit -am 'kill' && git push`. The next
scheduled tick reads the new config and exits cleanly without opening a
position. The state is in version control, the diff is the audit log, and
the rollback is `git revert`.

### `### What you give up` (~80w)
No per-strategy flags. No scheduled windows. No UI. No ability to disable
buying while still allowing closing positions (that one stings a little).
All true. You don't need any of them to answer the question "is the
agent allowed to trade right now?" — which is the only question the
kill-switch is here to answer.

### `### The shape of the principle` (~80w)
The cheapest tool that solves the actual problem beats the sophisticated
tool that also solves problems you don't have. The trap is reaching for
infrastructure because it feels *more engineered*, when in fact the
asymmetry of the failure modes points hard at the simple option.
Kill-switches are the clearest example I've worked through. There are
others.

## Markup

```html
<section id="writing" class="section">
  <div class="container">
    <p class="section__label"># writing</p>
    <article class="writing-post">
      <header>
        <p class="writing-post__meta">2026-05-18 &middot; ~3 min read</p>
        <h2>The cheapest kill-switch is a YAML key</h2>
      </header>
      <p>...opening...</p>

      <h3>The instinct</h3>
      <p>...</p>

      <h3>Why those are wrong here</h3>
      <p>...</p>

      <h3>The one-key approach</h3>
      <p>...</p>
      <pre><code class="lang-yaml">...</code></pre>
      <pre><code class="lang-python">...</code></pre>

      <h3>What you give up</h3>
      <p>...</p>

      <h3>The shape of the principle</h3>
      <p>...</p>
    </article>
  </div>
</section>
```

The existing `<section>` and `.container` classes provide spacing and
width. The `section__label` provides the mono `# writing` lead-in
matching every other section.

## Styles

Two additions to `styles.css`, placed near the existing case-study rules:

```css
/* writing post — long-form essay column */
.writing-post {
  max-width: 65ch;
}

.writing-post__meta {
  margin: 0 0 0.25em;
  font-size: 0.85em;
  color: var(--c-text-dim);
  letter-spacing: 0.04em;
}

.writing-post h2 {
  margin: 0 0 1.25em;
}

.writing-post h3 {
  margin: 1.75em 0 0.5em;
}

.writing-post pre {
  margin: 1em 0 1.25em;
}
```

No new custom properties, no new font sizes outside the existing scale,
no new colors.

## Nav

Insert one `<li>` after the `case_study` entry and before `experience`:

```html
<li><a href="#case-study">case_study</a></li>
<li><a href="#writing">writing</a></li>    <!-- NEW -->
<li><a href="#experience">experience</a></li>
```

Mobile nav inherits the same change automatically (same `<ul>`).

## What this does NOT do

- No `/writing/` directory or separate HTML page.
- No RSS feed, no Atom, no JSON feed.
- No `BlogPosting` JSON-LD (one inline post does not warrant schema
  noise; revisit if a second post lands).
- No tags, categories, archive page, or post index.
- No comments, reactions, or webmentions.
- No code-syntax highlighting library — `<code>` blocks render with the
  existing JetBrains Mono and no syntax color. Accept that.

## Risks and mitigations

**Risk:** a weak 600 words damages the signal more than no writing
section. **Mitigation:** the post draft will be read end-to-end before
commit; the spec content above is the contract. If on review the prose
reads as thin or generic, kill the section and revisit.

**Risk:** vertical length increases on a page that's already long.
**Mitigation:** the section is opt-in via nav, and visitors who scroll
past it pay only one section's worth of scroll distance. Acceptable.

**Risk:** the kill-switch argument is reductive — there *are* real cases
where a feature flag service is the right call. **Mitigation:** the post
explicitly says "for this problem" and "kill-switches specifically." The
shape-of-the-principle paragraph is one paragraph, not a manifesto.

**Risk:** code snippet drift — if `trader/config.yaml` or its
kill-switch handler ever changes shape, the post becomes stale.
**Mitigation:** the snippet is a *minimal* illustration of the pattern,
not a copy of the live file. It's labeled as the pattern, not as a code
exhibit. No update obligation.

## Acceptance criteria

1. New `<section id="writing">` exists in `index.html` between
   `#case-study-arb` and `#experience`.
2. Section contains exactly one `<article class="writing-post">` with
   the title, meta line, opening paragraph, and five `<h3>` subsections
   in the order listed above.
3. The post content matches the ~600-word body in this spec (small
   editorial polish at write-time is fine; structural changes need spec
   revision).
4. Nav menu includes `<li><a href="#writing">writing</a></li>` between
   `case_study` and `experience`.
5. `styles.css` has `.writing-post`, `.writing-post__meta`, and the h2/h3/pre
   spacing rules listed above. No other CSS changes.
6. The public-safety CI passes on the commit. No banned terms.
7. Lighthouse on the live page still reports 100/100/100/100 after
   deploy (manual verification via the PageSpeed Insights URL the
   project already uses).
8. The page validates as well-formed HTML5 (no new validator errors
   compared to v2.14 baseline).
9. The tag `v2.15` is pushed after the commit lands on `main`.

## Out of scope (for this cycle)

- A second post.
- Splitting writing onto its own page or adding an index.
- RSS, JSON-LD, or schema additions.
- Adding any syntax-highlighting library or build step.
- Updating the resume PDF to mention the writing section (resume is a
  PDF, not a marketing piece; if the recruiter is reading the resume
  they're already on the site).

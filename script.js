(function () {
  "use strict";

  // ---------- Hero boot sequence ----------
  (function bootSequence() {
    const lines = Array.from(document.querySelectorAll("[data-boot-line]"));
    if (lines.length === 0) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const smallViewport = window.matchMedia("(max-width: 640px)").matches;
    let alreadyPlayed = false;
    try { alreadyPlayed = sessionStorage.getItem("jh-boot-played") === "1"; } catch (e) {}

    // No-op path: leave the static end-state alone.
    // Small viewports skip the animation entirely — the per-char
    // textContent updates count as layout shifts and drag mobile CLS
    // below the "good" threshold even with the outer min-height lock.
    if (reduceMotion || alreadyPlayed || smallViewport) return;

    // (CLS guard for the hero box height is now in CSS via
    // `.hero__boot { min-height }` so the lock applies before first
    // paint — earlier JS-based lock fired too late to prevent the
    // font-swap shift.)

    const skipBtn = document.querySelector(".hero__skip");
    const cached = lines.map((el) => el.textContent);
    lines.forEach((el) => (el.textContent = ""));

    let cancelled = false;
    function finish() {
      cancelled = true;
      lines.forEach((el, i) => (el.textContent = cached[i]));
      if (skipBtn) skipBtn.hidden = true;
      try { sessionStorage.setItem("jh-boot-played", "1"); } catch (e) {}
    }

    if (skipBtn) {
      skipBtn.addEventListener("click", finish);
      // Reveal skip only once the animation has run long enough to be
      // worth skipping (it stays hidden if the boot already finished).
      setTimeout(() => { if (!cancelled) skipBtn.hidden = false; }, 800);
    }

    const charDelay = 14;   // ms per character
    const lineDelay = 220;  // ms pause between lines

    (async function play() {
      for (let i = 0; i < lines.length; i++) {
        const el = lines[i];
        const target = cached[i];
        for (let c = 0; c < target.length; c++) {
          if (cancelled) return;
          el.textContent += target[c];
          await sleep(charDelay);
        }
        if (cancelled) return;
        await sleep(lineDelay);
      }
      finish();
    })();

    function sleep(ms) {
      return new Promise((r) => setTimeout(r, ms));
    }
  })();

  // ---------- Mobile nav ----------
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    });
    // Close the menu after tapping a link on mobile.
    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menu.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation");
      });
    });
  }

  // ---------- Footer year ----------
  const yearEl = document.getElementById("footer-year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // ---------- Stale-metadata guard ----------
  // The freshness pills ("last commit: today") are baked into the page
  // by the deploy job, so they stay true only for as long as deploys
  // keep happening. If deploys stop — GitHub disables a daily schedule
  // after 60 days with no commits, a PAT expires, Actions gets paused —
  // the pills keep asserting a reading that nothing is taking any more,
  // and no server-side check can catch it, because nothing is running.
  // So the page checks its own age against the visitor's clock and
  // drops the day-granularity claim it can no longer stand behind.
  (function staleMetaGuard() {
    // The deploy runs daily. A week of silence is a failure, not a
    // hiccup, and one skipped cron run must not blank the pills.
    const STALE_AFTER_DAYS = 7;

    const stampEl = document.querySelector('[data-meta="last_deployed"]');
    if (!stampEl) return;
    const stamp = /\d{4}-\d{2}-\d{2}/.exec(stampEl.textContent || "");
    if (!stamp) return;

    const parts = stamp[0].split("-");
    const built = Date.UTC(+parts[0], +parts[1] - 1, +parts[2]);
    const now = new Date();
    const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
    const ageDays = Math.round((today - built) / 86400000);
    // A visitor clock set in the past gives a negative age and counts as
    // fresh: a wrong clock should not get to rewrite the page.
    if (ageDays <= STALE_AFTER_DAYS) return;

    // Only a relative phrase rots. A pill that already names an
    // absolute date ("last commit: 2026-05-18") stays true forever.
    const relative = /:\s*(today|\d+d ago|\d+w ago)\s*$/;
    document.querySelectorAll('[data-meta$=".last_commit"]').forEach((el) => {
      if (!relative.test(el.textContent || "")) return;
      // Shorter than the absolute-date pill already rendered on the
      // shipped page, so this branch cannot introduce an overflow the
      // layout checks have not already cleared.
      el.textContent = "last check: " + stamp[0];
      el.title =
        "Activity readings stopped refreshing on " + stamp[0] +
        ", so this card no longer shows how long ago the last commit was.";
    });
  })();

  // ---------- Theme toggle ----------
  const themeBtn = document.querySelector(".theme-toggle");
  const labelEl = themeBtn ? themeBtn.querySelector(".theme-toggle__label") : null;

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (labelEl) labelEl.textContent = theme === "dark" ? "Light" : "Dark";
    if (themeBtn) themeBtn.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
  }

  // Reflect whatever the early-paint script applied.
  applyTheme(document.documentElement.getAttribute("data-theme") || "light");

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      try { localStorage.setItem("jh-theme", next); } catch (e) {}
      applyTheme(next);
    });
  }

  // ---------- Reveal on scroll ----------
  const targets = document.querySelectorAll("main > section");
  targets.forEach((el) => el.classList.add("reveal"));

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-visible"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -10% 0px" }
    );
    targets.forEach((el) => io.observe(el));
  }
})();

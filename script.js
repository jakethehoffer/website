(function () {
  "use strict";

  // Navigation remains usable on a short screen and from a keyboard.
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-menu");
  function closeMenu(returnFocus = false) {
    if (!toggle || !menu) return;
    menu.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation");
    if (returnFocus) toggle.focus();
  }
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    });
    menu.querySelectorAll("a").forEach(link => {
      link.addEventListener("click", () => closeMenu());
    });
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && menu.classList.contains("is-open")) closeMenu(true);
    });
    document.addEventListener("click", event => {
      if (!event.target.closest(".site-nav")) closeMenu();
    });
    document.addEventListener("focusin", event => {
      if (!event.target.closest(".site-nav")) closeMenu();
    });
    window.matchMedia("(min-width: 851px)").addEventListener("change", () => closeMenu());
  }

  // Filters are an enhancement. Without JS, all work and native details remain.
  const toolbar = document.querySelector(".project-toolbar");
  const cards = Array.from(document.querySelectorAll(".project"));
  if (toolbar && cards.length) {
    const filters = Array.from(toolbar.querySelectorAll("[data-filter]"));
    const count = toolbar.querySelector(".project-count");
    const filterCards = value => {
      let shown = 0;
      cards.forEach(card => {
        const data = card.querySelector("[data-category]").dataset;
        card.hidden = value === "selected" ? data.selected !== "true" : value !== "all" && data.category !== value;
        if (!card.hidden) shown++;
      });
      filters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.filter === value)));
      count.textContent = `${shown} ${shown === 1 ? "project" : "projects"}`;
    };
    filters.forEach(button => button.addEventListener("click", () => filterCards(button.dataset.filter)));
    filterCards("selected");
    toolbar.hidden = false;
  }

  // Existing case-study links open the full story, including direct URL visits.
  function openLinkedStory(hash) {
    if (!hash || hash === "#") return;
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); } catch (_) { return; }
    const details = target && target.querySelector(".case-detail");
    if (details) details.open = true;
  }
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", () => openLinkedStory(link.hash));
  });
  window.addEventListener("hashchange", () => openLinkedStory(location.hash));
  openLinkedStory(location.hash);

  // An email link always works; copying is an optional convenience.
  const copyButton = document.querySelector(".copy-email");
  const copyStatus = document.querySelector(".copy-status");
  if (copyButton && navigator.clipboard && window.isSecureContext) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText("14jakehoffman@gmail.com");
        copyStatus.textContent = "Email address copied.";
      } catch (_) {
        copyStatus.textContent = "Copy did not work. You can select the address above or use Email me.";
      }
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

  // Mark the current navigation section without hiding any page content.
  const navLinks = Array.from(document.querySelectorAll('.nav-menu a[href^="#"]'));
  let scrollPending = false;
  function markSection() {
    scrollPending = false;
    let current = null;
    navLinks.forEach(link => {
      const section = document.getElementById(link.hash.slice(1));
      if (section && section.getBoundingClientRect().top <= 150) current = link;
    });
    navLinks.forEach(link => {
      if (link === current) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }
  window.addEventListener("scroll", () => {
    if (!scrollPending) { scrollPending = true; requestAnimationFrame(markSection); }
  }, { passive: true });
  markSection();
})();

(function () {
  "use strict";

  // ---------- Hero boot sequence ----------
  (function bootSequence() {
    const lines = Array.from(document.querySelectorAll("[data-boot-line]"));
    if (lines.length === 0) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let alreadyPlayed = false;
    try { alreadyPlayed = sessionStorage.getItem("jh-boot-played") === "1"; } catch (e) {}

    // No-op path: leave the static end-state alone.
    if (reduceMotion || alreadyPlayed) return;

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
      skipBtn.hidden = false;
      skipBtn.addEventListener("click", finish);
      // Auto-hide skip after 800ms.
      setTimeout(() => { if (skipBtn && !cancelled) skipBtn.hidden = false; }, 800);
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

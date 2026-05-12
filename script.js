(function () {
  "use strict";

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

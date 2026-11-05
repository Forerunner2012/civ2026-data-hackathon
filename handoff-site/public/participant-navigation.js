/* Local participant navigation. No imports, network calls or persisted state. */
(function () {
  "use strict";
  let cleanup = null;
  function initialize() {
    const offline = document.querySelector("script[data-offline-navigation]");
    if (!offline && document.documentElement.dataset.participantNavigationHydrated !== "true") return;
    const header = document.querySelector("[data-participant-navigation]");
    if (!header || header.dataset.navigationReady) return;
    const page = header.closest("main");
    const row = header.querySelector("nav");
    const links = Array.from(row.querySelectorAll('a[href^="#"]'));
    const sections = links.map((link) => document.getElementById(link.hash.slice(1)));
    if (sections.some((section) => !section)) return;
    if (cleanup) cleanup();
    const controller = new AbortController();
    const signal = controller.signal;
    const controls = header.querySelector(".participant-section-controls");
    const previous = header.querySelector("[data-section-previous]");
    const next = header.querySelector("[data-section-next]");
    const position = header.querySelector("[data-section-position]");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let current = 0;
    let pendingFrame = 0;
    let destination = null;
    let settleTimer = 0;

    function measure() {
      page.style.setProperty("--participant-header-height", header.offsetHeight + "px");
    }
    function activate(index) {
      current = index;
      const counter = (index + 1) + "/" + sections.length;
      if (position.textContent !== counter) position.textContent = counter;
      previous.disabled = index === 0;
      next.disabled = index === sections.length - 1;
      links.forEach((link, offset) => {
        if (offset === index) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      const active = links[index];
      const bounds = active.getBoundingClientRect();
      const viewport = row.getBoundingClientRect();
      if (bounds.left < viewport.left) row.scrollLeft += bounds.left - viewport.left;
      else if (bounds.right > viewport.right) row.scrollLeft += bounds.right - viewport.right;
    }
    function updateFromScroll() {
      pendingFrame = 0;
      if (!header.isConnected || destination !== null) return;
      const boundary = header.getBoundingClientRect().bottom + 20;
      let index = 0;
      sections.forEach((section, offset) => {
        if (section.getBoundingClientRect().top <= boundary) index = offset;
      });
      if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
        index = sections.length - 1;
      }
      activate(index);
    }
    function scheduleScroll() {
      if (!pendingFrame) pendingFrame = window.requestAnimationFrame(updateFromScroll);
      if (destination !== null) {
        window.clearTimeout(settleTimer);
        settleTimer = window.setTimeout(() => { destination = null; scheduleScroll(); }, 150);
      }
    }
    function jump(index, recordHistory, focus) {
      if (!header.isConnected || index < 0 || index >= sections.length) return;
      measure();
      destination = index;
      activate(index);
      const section = sections[index];
      if (recordHistory && window.location.hash !== "#" + section.id) {
        window.history.pushState(null, "", "#" + section.id);
      }
      const heading = section.querySelector("h1, h2, h3");
      if (focus && heading) {
        heading.setAttribute("tabindex", "-1");
        heading.focus({ preventScroll: true });
      }
      const top = Math.max(0, section.getBoundingClientRect().top + window.scrollY - header.offsetHeight - 16);
      window.scrollTo({ top, behavior: reducedMotion.matches ? "instant" : "smooth" });
      window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(() => { destination = null; scheduleScroll(); }, 300);
    }
    function restoreFragment() {
      if (!header.isConnected) return;
      const index = sections.findIndex((section) => "#" + section.id === window.location.hash);
      if (index >= 0) jump(index, false, false);
      else { destination = null; scheduleScroll(); }
    }
    function eligible(event) {
      if (!header.isConnected || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.repeat || event.isComposing) return false;
      const selection = window.getSelection();
      if (selection && !selection.isCollapsed) return false;
      const target = event.target;
      if (!(target instanceof Element)) return false;
      const forbidden = 'a, button, input, textarea, select, summary, [contenteditable]:not([contenteditable="false"]), [role]:not([role="heading"]), [data-viewer-control], canvas, video';
      if (target.closest(forbidden)) return false;
      if (!(target === document.body || target === document.documentElement || target === page || /^H[1-6]$/.test(target.tagName))) return false;
      for (let element = target; element && element !== document.body; element = element.parentElement) {
        const overflow = window.getComputedStyle(element).overflowX;
        if (/auto|scroll/.test(overflow) && element.scrollWidth > element.clientWidth) return false;
      }
      return true;
    }
    page.addEventListener("click", (event) => {
      const link = event.target instanceof Element && event.target.closest('a[href^="#"]');
      if (!link || event.defaultPrevented || event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const index = sections.findIndex((section) => "#" + section.id === link.getAttribute("href"));
      if (index < 0) return;
      event.preventDefault();
      jump(index, true, true);
    }, { capture: true, signal });
    previous.addEventListener("click", () => jump(current - 1, true, true), { signal });
    next.addEventListener("click", () => jump(current + 1, true, true), { signal });
    document.addEventListener("keydown", (event) => {
      if ((event.key !== "ArrowLeft" && event.key !== "ArrowRight") || !eligible(event)) return;
      const index = current + (event.key === "ArrowRight" ? 1 : -1);
      if (!header.isConnected || index < 0 || index >= sections.length) return;
      event.preventDefault();
      jump(index, true, true);
    }, { signal });
    window.addEventListener("scroll", scheduleScroll, { passive: true, signal });
    window.addEventListener("popstate", restoreFragment, { signal });
    window.addEventListener("hashchange", restoreFragment, { signal });
    window.addEventListener("resize", () => { measure(); scheduleScroll(); }, { signal });
    const observer = typeof ResizeObserver !== "undefined" ? new ResizeObserver(measure) : null;
    if (observer) observer.observe(header);
    cleanup = () => {
      controller.abort();
      if (observer) observer.disconnect();
      window.clearTimeout(settleTimer);
      window.cancelAnimationFrame(pendingFrame);
      delete header.dataset.navigationReady;
    };
    header.dataset.navigationReady = "true";
    controls.hidden = false;
    measure();
    restoreFragment();
    scheduleScroll();
  }
  document.addEventListener("civ:participant-navigation-ready", initialize);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, { once: true });
  else initialize();
})();

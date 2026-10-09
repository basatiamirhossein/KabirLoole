/** Header: scroll state, mobile drawer, language memory, back-to-top, mobile CTA. */

const DRAWER_BREAKPOINT = 1100;

function initHeaderScroll(): void {
  const header = qs("[data-header]");
  const toTop = qs<HTMLButtonElement>("[data-to-top]");
  if (!header) return;

  let ticking = false;
  const update = (): void => {
    const y = window.scrollY;
    header.classList.toggle("is-scrolled", y > 24);
    if (toTop) toTop.hidden = y < 700;
    ticking = false;
  };
  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    },
    { passive: true },
  );
  update();

  toTop?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? "auto" : "smooth" });
    const main = qs("#main");
    main?.setAttribute("tabindex", "-1");
    main?.focus({ preventScroll: true });
  });
}

function initDrawer(): void {
  const burger = qs<HTMLButtonElement>("[data-burger]");
  const nav = qs("[data-nav]");
  const backdrop = qs("[data-nav-backdrop]");
  const label = qs("[data-burger-label]");
  if (!burger || !nav || !backdrop) return;

  const setOpen = (open: boolean): void => {
    nav.classList.toggle("is-open", open);
    backdrop.hidden = !open;
    document.body.classList.toggle("nav-open", open);
    burger.setAttribute("aria-expanded", String(open));
    if (label) label.textContent = (open ? burger.dataset.labelClose : burger.dataset.labelOpen) ?? "";
    if (open) qs<HTMLAnchorElement>(".nav__link", nav)?.focus();
  };

  burger.addEventListener("click", () => setOpen(burger.getAttribute("aria-expanded") !== "true"));
  backdrop.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (event: KeyboardEvent) => {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      setOpen(false);
      burger.focus();
    }
  });
  qsa<HTMLAnchorElement>("a", nav).forEach((link) => link.addEventListener("click", () => setOpen(false)));
  window.addEventListener("resize", () => {
    if (window.innerWidth >= DRAWER_BREAKPOINT && nav.classList.contains("is-open")) setOpen(false);
  });
}

function initLanguageMemory(): void {
  qsa<HTMLAnchorElement>("[data-lang]").forEach((link) => {
    link.addEventListener("click", () => {
      const lang = link.dataset.lang;
      if (lang) storageSet("kl-lang", lang);
    });
  });
  storageSet("kl-lang", pageLang());
}

/** The call button's number list closes on a tap outside it, on Escape, and when the bar hides. */
function bindCallPopover(cta: HTMLElement): void {
  const pop = qs<HTMLDetailsElement>(".call-pop", cta);
  if (!pop) return;
  document.addEventListener("click", (event: MouseEvent) => {
    if (pop.open && event.target instanceof Node && !pop.contains(event.target)) pop.open = false;
  });
  document.addEventListener("keydown", (event: KeyboardEvent) => {
    if (event.key === "Escape") pop.open = false;
  });
}

function initMobileCta(): void {
  const cta = qs("[data-mobile-cta]");
  const footer = qs(".site-footer");
  if (!cta) return;
  bindCallPopover(cta);
  if (!footer || !("IntersectionObserver" in window)) return;
  const pop = qs<HTMLDetailsElement>(".call-pop", cta);
  const observer = new IntersectionObserver(
    (entries) =>
      entries.forEach((entry) => {
        cta.classList.toggle("is-hidden", entry.isIntersecting);
        if (entry.isIntersecting && pop) pop.open = false;
      }),
    { threshold: 0.05 },
  );
  observer.observe(footer);
}

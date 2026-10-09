/** Entry point: each feature initialises independently so one failure never breaks the page. */

function boot(): void {
  safeInit("header-scroll", initHeaderScroll);
  safeInit("drawer", initDrawer);
  safeInit("language-memory", initLanguageMemory);
  safeInit("mobile-cta", initMobileCta);
  safeInit("reveal", initReveal);
  safeInit("counters", initCounters);
  safeInit("hero", initHeroScene);
  safeInit("flow", initFlow);
  safeInit("calculator", initCalculator);
  safeInit("lightbox", initLightbox);
  safeInit("contact-form", initContactForm);
  safeInit("copy-buttons", initCopyButtons);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

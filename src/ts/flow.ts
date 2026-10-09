/** Fill the decorative pipes (journey, timeline) with water as the visitor scrolls. */

function initFlow(): void {
  const sections = qsa("[data-flow]");
  if (sections.length === 0) return;

  if (prefersReducedMotion()) {
    sections.forEach((section) => section.style.setProperty("--flow", "1"));
    return;
  }

  let ticking = false;
  const update = (): void => {
    const viewport = window.innerHeight;
    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      const progress = clamp((viewport * 0.8 - rect.top) / (rect.height * 0.85), 0, 1);
      section.style.setProperty("--flow", progress.toFixed(3));
    });
    ticking = false;
  };
  const request = (): void => {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  };
  window.addEventListener("scroll", request, { passive: true });
  window.addEventListener("resize", request);
  update();
}

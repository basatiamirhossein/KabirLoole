/** Count numbers up from zero when they scroll into view. */

const COUNT_DURATION_MS = 1600;

function animateCount(el: HTMLElement, target: number, format: Intl.NumberFormat): void {
  const start = performance.now();
  const step = (now: number): void => {
    const progress = clamp((now - start) / COUNT_DURATION_MS, 0, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = format.format(Math.round(target * eased));
    if (progress < 1) window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

function initCounters(): void {
  const items = qsa("[data-count]");
  if (items.length === 0 || prefersReducedMotion()) return;
  const format = numberFormatter(pageLang());

  onVisible(items, (el) => {
    if (!(el instanceof HTMLElement)) return;
    const target = Number(el.dataset.count);
    if (Number.isFinite(target)) animateCount(el, target, format);
  });
}

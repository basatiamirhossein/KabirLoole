/** Fade/slide elements in as they enter the viewport. */

function initReveal(): void {
  const items = qsa("[data-reveal]");
  if (items.length === 0) return;

  if (prefersReducedMotion()) {
    items.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  items.forEach((el) => {
    const parent = el.parentElement;
    if (!parent) return;
    const siblings = Array.from(parent.children).filter((child) => child.hasAttribute("data-reveal"));
    const index = siblings.indexOf(el);
    if (index > 0) el.style.transitionDelay = `${Math.min(index, 6) * 70}ms`;
  });

  onVisible(items, (el) => el.classList.add("is-visible"), "0px 0px -8% 0px");
}

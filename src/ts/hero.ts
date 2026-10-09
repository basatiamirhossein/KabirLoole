/** Pause the hero farm animation when it is off-screen or the tab is hidden, to save battery. */

function initHeroScene(): void {
  const hero = qs("[data-hero]");
  if (!hero) return;

  let onScreen = true;
  const sync = (): void => {
    hero.classList.toggle("is-paused", !onScreen || document.hidden);
  };

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        onScreen = entry.isIntersecting;
        sync();
      });
    });
    observer.observe(hero);
  }
  document.addEventListener("visibilitychange", sync);
}

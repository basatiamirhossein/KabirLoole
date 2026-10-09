/** Certificate lightbox built on <dialog>, with keyboard, swipe and RTL-aware navigation. */

interface LightboxItem {
  full: string;
  caption: string;
  trigger: HTMLButtonElement;
}

interface LightboxElements {
  dialog: HTMLDialogElement;
  img: HTMLImageElement;
  caption: HTMLElement;
}

const SWIPE_MIN_PX = 40;

function collectLightboxItems(): LightboxItem[] {
  return qsa<HTMLButtonElement>("[data-lightbox-item]").flatMap((trigger) => {
    const full = trigger.dataset.full;
    return full ? [{ full, caption: trigger.dataset.caption ?? "", trigger }] : [];
  });
}

function collectLightboxElements(): LightboxElements | null {
  const dialog = qs<HTMLDialogElement>("[data-lightbox-dialog]");
  const img = qs<HTMLImageElement>("[data-lightbox-img]");
  const caption = qs("[data-lightbox-caption]");
  return dialog && img && caption ? { dialog, img, caption } : null;
}

function openDialog(dialog: HTMLDialogElement): void {
  if (typeof dialog.showModal === "function") {
    if (!dialog.open) dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
  document.body.classList.add("lightbox-open");
}

function closeDialog(dialog: HTMLDialogElement): void {
  if (typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

/** Arrow keys follow reading direction: in RTL the left arrow means "next". */
function stepFromKey(key: string): number {
  const forward = isRtl() ? "ArrowLeft" : "ArrowRight";
  const back = isRtl() ? "ArrowRight" : "ArrowLeft";
  if (key === forward) return 1;
  if (key === back) return -1;
  return 0;
}

function stepFromSwipe(deltaX: number): number {
  if (Math.abs(deltaX) < SWIPE_MIN_PX) return 0;
  const leftSwipe = deltaX < 0;
  return leftSwipe !== isRtl() ? 1 : -1;
}

/** Warm the cache for the previous and next certificate so paging feels instant. */
function preloadNeighbours(items: LightboxItem[], index: number): void {
  [index - 1, index + 1].forEach((i) => {
    const item = items[(i + items.length) % items.length];
    if (item) new Image().src = item.full;
  });
}

function initLightbox(): void {
  const items = collectLightboxItems();
  const els = collectLightboxElements();
  if (items.length === 0 || !els) return;

  let index = 0;
  let opener: HTMLButtonElement | null = null;

  const show = (next: number): void => {
    index = (next + items.length) % items.length;
    const item = items[index];
    if (!item) return;
    els.img.src = item.full;
    els.img.alt = item.caption;
    els.caption.textContent = item.caption;
    preloadNeighbours(items, index);
  };

  items.forEach((item, i) =>
    item.trigger.addEventListener("click", () => {
      opener = item.trigger;
      show(i);
      openDialog(els.dialog);
    }),
  );

  qs("[data-lightbox-close]", els.dialog)?.addEventListener("click", () => closeDialog(els.dialog));
  qs("[data-lightbox-prev]", els.dialog)?.addEventListener("click", () => show(index - 1));
  qs("[data-lightbox-next]", els.dialog)?.addEventListener("click", () => show(index + 1));

  els.dialog.addEventListener("click", (event: MouseEvent) => {
    if (event.target === els.dialog) closeDialog(els.dialog);
  });
  els.dialog.addEventListener("keydown", (event: KeyboardEvent) => {
    const step = stepFromKey(event.key);
    if (step !== 0) {
      event.preventDefault();
      show(index + step);
    }
  });

  let touchX = 0;
  els.dialog.addEventListener("touchstart", (event: TouchEvent) => {
    touchX = event.changedTouches[0]?.clientX ?? 0;
  }, { passive: true });
  els.dialog.addEventListener("touchend", (event: TouchEvent) => {
    const endX = event.changedTouches[0]?.clientX ?? touchX;
    const step = stepFromSwipe(endX - touchX);
    if (step !== 0) show(index + step);
  }, { passive: true });

  els.dialog.addEventListener("close", () => {
    document.body.classList.remove("lightbox-open");
    opener?.focus();
  });
}

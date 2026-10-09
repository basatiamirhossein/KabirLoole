/** Shared DOM helpers. All files are global scripts, bundled into one IIFE by build/build_js.py. */

type QueryRoot = Document | Element;

function qs<T extends Element = HTMLElement>(selector: string, root: QueryRoot = document): T | null {
  return root.querySelector<T>(selector);
}

function qsa<T extends Element = HTMLElement>(selector: string, root: QueryRoot = document): T[] {
  return Array.from(root.querySelectorAll<T>(selector));
}

function pageLang(): string {
  return document.documentElement.lang || "fa";
}

function isRtl(): boolean {
  return document.documentElement.dir === "rtl";
}

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const AR_DIGITS = "٠١٢٣٤٥٦٧٨٩";

/** Convert ASCII digits (and the decimal point) to the page language's digits. */
function localizeDigits(value: string, lang: string = pageLang()): string {
  const digits = lang === "fa" ? FA_DIGITS : lang === "ar" ? AR_DIGITS : null;
  if (digits === null) return value;
  return value.replace(/[0-9.]/g, (ch) => (ch === "." ? "٫" : digits.charAt(Number(ch))));
}

/** Convert Persian/Arabic digits to ASCII so user input can be validated. */
function normalizeDigits(value: string): string {
  return value.replace(/[۰-۹٠-٩]/g, (ch) => {
    const fa = FA_DIGITS.indexOf(ch);
    return String(fa > -1 ? fa : AR_DIGITS.indexOf(ch));
  });
}

function localeFor(lang: string): string {
  if (lang === "fa") return "fa-IR-u-nu-arabext";
  if (lang === "ar") return "ar-u-nu-arab";
  return "en-US";
}

function numberFormatter(lang: string, maxFraction = 0, grouping = lang === "en", minFraction = maxFraction): Intl.NumberFormat {
  return new Intl.NumberFormat(localeFor(lang), {
    useGrouping: grouping,
    minimumFractionDigits: minFraction,
    maximumFractionDigits: maxFraction,
  });
}

function storageSet(key: string, value: string): boolean {
  try {
    window.localStorage.setItem(key, value);
    return true;
  } catch {
    return false;
  }
}

function onVisible(elements: Element[], callback: (el: Element) => void, rootMargin = "0px 0px -10% 0px"): void {
  if (!("IntersectionObserver" in window)) {
    elements.forEach(callback);
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin, threshold: 0.12 },
  );
  elements.forEach((el) => observer.observe(el));
}

function safeInit(name: string, init: () => void): void {
  try {
    init();
  } catch (error: unknown) {
    console.error(`[kabirloole] ${name} failed to initialise`, error);
  }
}

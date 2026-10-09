/**
 * Pipe price calculator: raw material, outside diameter, pressure class and length give the SDR,
 * wall, bore and weight from the factory spec sheet, and a price from the daily rate the admin
 * panel publishes at api/price.php.
 */

type SpecCell = [number, number] | null; // [wall mm, weight kg per metre]

interface CalcText {
  loading: string;
  unavailable: string;
  updated: string;
}

interface PipeData {
  pressures: string[];
  sdr: Record<string, string[]>;
  spec: Record<string, Record<string, SpecCell[]>>;
  priceUrl: string;
  text: CalcText;
}

interface PriceList {
  updatedAt: string | null;
  prices: Record<string, number | null>;
}

type PriceState = { status: "loading" } | { status: "error" } | { status: "ready"; list: PriceList };

interface CalcState {
  material: string;
  od: number;
  pn: string;
  length: number | null;
}

interface CalcElements {
  root: HTMLElement;
  form: HTMLFormElement;
  lengthField: HTMLElement | null;
  inner: SVGCircleElement | null;
  tables: HTMLElement[];
  outputs: Map<string, HTMLElement>;
}

const DASH = "–";
const PRICE_TIMEOUT_MS = 8000;
const MAX_LENGTH_M = 1_000_000;
const PRICE_TIME_ZONE = "Asia/Tehran"; // the admin sets prices in Iran time

// ---------------------------------------------------------------- data contracts

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((v) => typeof v === "string");
}

function isSpecCell(value: unknown): value is SpecCell {
  return value === null || (Array.isArray(value) && value.length === 2 && value.every((v) => typeof v === "number"));
}

function isSpec(value: unknown): value is PipeData["spec"] {
  return (
    isRecord(value) &&
    Object.values(value).every(
      (rows) => isRecord(rows) && Object.values(rows).every((row) => Array.isArray(row) && row.every(isSpecCell)),
    )
  );
}

function isCalcText(value: unknown): value is CalcText {
  return isRecord(value) && ["loading", "unavailable", "updated"].every((k) => typeof value[k] === "string");
}

function isPipeData(value: unknown): value is PipeData {
  return (
    isRecord(value) &&
    isStringArray(value.pressures) &&
    isRecord(value.sdr) &&
    Object.values(value.sdr).every(isStringArray) &&
    isSpec(value.spec) &&
    typeof value.priceUrl === "string" &&
    isCalcText(value.text)
  );
}

function isPriceList(value: unknown): value is PriceList {
  return (
    isRecord(value) &&
    (value.updatedAt === null || typeof value.updatedAt === "string") &&
    isRecord(value.prices) &&
    Object.values(value.prices).every((p) => p === null || (typeof p === "number" && Number.isFinite(p)))
  );
}

function readPipeData(): PipeData | null {
  const script = qs<HTMLScriptElement>("#pipe-data");
  if (!script?.textContent) return null;
  try {
    const parsed: unknown = JSON.parse(script.textContent);
    return isPipeData(parsed) ? parsed : null;
  } catch (error: unknown) {
    console.error("[kabirloole] pipe data is not valid JSON", error);
    return null;
  }
}

async function fetchPrices(url: string): Promise<PriceList> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), PRICE_TIMEOUT_MS);
  try {
    const response = await fetch(url, { headers: { Accept: "application/json" }, signal: controller.signal });
    if (!response.ok) throw new Error(`price API answered ${response.status}`);
    const body: unknown = await response.json();
    if (!isPriceList(body)) throw new Error("price API returned an unexpected shape");
    return body;
  } finally {
    window.clearTimeout(timer);
  }
}

// ---------------------------------------------------------------- reading the form

function parseLength(raw: string): number | null {
  const text = normalizeDigits(raw).replace(/[٫,]/g, ".").replace(/\s+/g, "");
  if (!/^\d+(\.\d+)?$/.test(text)) return null;
  const value = Number(text);
  return value > 0 && value <= MAX_LENGTH_M ? value : null;
}

function readState(form: HTMLFormElement): CalcState {
  const fields = new FormData(form);
  return {
    material: String(fields.get("material") ?? ""),
    od: Number(fields.get("od")),
    pn: String(fields.get("pn") ?? ""),
    length: parseLength(String(fields.get("length") ?? "")),
  };
}

function lookup(data: PipeData, state: CalcState): SpecCell {
  const index = data.pressures.indexOf(state.pn);
  return data.spec[state.material]?.[String(state.od)]?.[index] ?? null;
}

// ---------------------------------------------------------------- rendering

function setOut(els: CalcElements, key: string, text: string): void {
  const el = els.outputs.get(key);
  if (el) el.textContent = text;
}

function fmt(value: number, maxDecimals: number, minDecimals = maxDecimals): string {
  return numberFormatter(pageLang(), maxDecimals, true, minDecimals).format(value);
}

function renderSpec(els: CalcElements, data: PipeData, state: CalcState, cell: SpecCell): void {
  const sdr = data.sdr[state.material]?.[data.pressures.indexOf(state.pn)] ?? DASH;
  setOut(els, "material", state.material.toUpperCase());
  setOut(els, "sdr", `SDR ${localizeDigits(sdr)}`);
  els.root.classList.toggle("is-na", cell === null);
  const na = els.outputs.get("na");
  if (na) na.hidden = cell !== null;

  const [wall, weight] = cell ?? [Number.NaN, Number.NaN];
  const ok = cell !== null;
  setOut(els, "wall", ok ? localizeDigits(String(wall)) : DASH);
  setOut(els, "id", ok ? fmt(state.od - 2 * wall, 1, 0) : DASH);
  setOut(els, "weight", ok ? fmt(weight, weight < 10 ? 3 : 2) : DASH);
  setOut(els, "total-weight", ok && state.length !== null ? fmt(weight * state.length, 1, 0) : DASH);
  if (els.inner) {
    const ratio = ok ? clamp((state.od - 2 * wall) / state.od, 0.5, 0.98) : 0.82;
    els.inner.style.transform = `scale(${ratio.toFixed(3)})`;
  }
}

function formatUpdated(iso: string | null, text: CalcText): string {
  if (iso === null) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const formatted = new Intl.DateTimeFormat(localeFor(pageLang()), {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: PRICE_TIME_ZONE,
  }).format(date);
  return text.updated.replace("{date}", formatted);
}

function renderPrice(els: CalcElements, data: PipeData, state: CalcState, cell: SpecCell, price: PriceState): void {
  const perKg = price.status === "ready" ? price.list.prices[state.material] ?? null : null;
  const usable = perKg !== null && perKg > 0;
  const perMetre = usable && cell !== null ? cell[1] * perKg : null;
  setOut(els, "price-kg", usable ? fmt(perKg, 0) : DASH);
  setOut(els, "price-m", perMetre !== null ? fmt(Math.round(perMetre), 0) : DASH);
  setOut(els, "price-total", perMetre !== null && state.length !== null ? fmt(Math.round(perMetre * state.length), 0) : DASH);

  let status = data.text.unavailable;
  if (price.status === "loading") status = data.text.loading;
  else if (price.status === "ready" && usable) status = formatUpdated(price.list.updatedAt, data.text);
  setOut(els, "price-status", status);
}

function syncTables(els: CalcElements, state: CalcState): void {
  els.tables.forEach((wrap) => {
    wrap.hidden = wrap.dataset.specTable !== state.material;
    qsa(".is-row, .is-col, .is-hit", wrap).forEach((el) => el.classList.remove("is-row", "is-col", "is-hit"));
    if (wrap.hidden) return;
    qsa(`[data-col="${state.pn}"]`, wrap).forEach((el) => el.classList.add("is-col"));
    const row = qs(`tr[data-row="${state.od}"]`, wrap);
    row?.classList.add("is-row");
    if (row) qsa(`td[data-col="${state.pn}"]`, row).forEach((el) => el.classList.add("is-hit"));
  });
}

// ---------------------------------------------------------------- wiring

function collectCalcElements(): CalcElements | null {
  const root = qs("[data-calc]");
  const form = root ? qs<HTMLFormElement>("[data-calc-form]", root) : null;
  if (!root || !form) return null;
  const outputs = new Map<string, HTMLElement>();
  qsa("[data-out]", root).forEach((el) => {
    if (el.dataset.out) outputs.set(el.dataset.out, el);
  });
  return {
    root,
    form,
    lengthField: qs("[data-calc-error]", form)?.closest<HTMLElement>(".field") ?? null,
    inner: qs<SVGCircleElement>("[data-xs-inner]", root),
    tables: qsa("[data-spec-table]"),
    outputs,
  };
}

function setChoice(form: HTMLFormElement, name: string, value: string): void {
  const control = form.elements.namedItem(name);
  if (control instanceof RadioNodeList || control instanceof HTMLSelectElement) control.value = value;
}

/** A click on a spec table cell picks that diameter and pressure. */
function bindTableClicks(els: CalcElements, update: () => void): void {
  els.tables.forEach((wrap) =>
    wrap.addEventListener("click", (event: MouseEvent) => {
      const cell = event.target instanceof Element ? event.target.closest<HTMLElement>("td[data-col]") : null;
      const od = cell?.closest<HTMLElement>("tr[data-row]")?.dataset.row;
      const pn = cell?.dataset.col;
      if (!od || !pn || cell?.classList.contains("is-na")) return;
      setChoice(els.form, "od", od);
      setChoice(els.form, "pn", pn);
      update();
    }),
  );
}

function initCalculator(): void {
  const data = readPipeData();
  const els = collectCalcElements();
  if (!data || !els) return;
  let price: PriceState = { status: "loading" };

  const update = (): void => {
    const state = readState(els.form);
    const cell = lookup(data, state);
    els.lengthField?.classList.toggle("is-invalid", state.length === null);
    renderSpec(els, data, state, cell);
    renderPrice(els, data, state, cell, price);
    syncTables(els, state);
  };

  els.form.addEventListener("submit", (event: SubmitEvent) => event.preventDefault());
  els.form.addEventListener("input", update);
  els.form.addEventListener("change", update);
  bindTableClicks(els, update);
  update();

  if (location.protocol === "file:") {
    // Opened straight from the folder: there is no PHP to answer, so skip the request.
    price = { status: "error" };
    update();
    return;
  }
  fetchPrices(data.priceUrl)
    .then((list) => {
      price = { status: "ready", list };
    })
    .catch((error: unknown) => {
      console.warn("[kabirloole] daily price unavailable", error);
      price = { status: "error" };
    })
    .finally(update);
}

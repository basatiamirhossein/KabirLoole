/** Contact form (validates, then opens the visitor's mail app) and copy-to-clipboard buttons. */

type FieldName = "name" | "phone" | "message";

interface ContactValues {
  name: string;
  phone: string;
  subject: string;
  message: string;
}

/** 8–13 digits once spaces and dashes are removed, with an optional leading +. */
const PHONE_PATTERN = /^\+?[0-9]{8,13}$/;
const COPY_RESET_MS = 2000;

function fieldValue(form: HTMLFormElement, name: string): string {
  const field = form.elements.namedItem(name);
  if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement || field instanceof HTMLSelectElement) {
    return field.value.trim();
  }
  return "";
}

function readContactValues(form: HTMLFormElement): ContactValues {
  return {
    name: fieldValue(form, "name"),
    phone: normalizeDigits(fieldValue(form, "phone")),
    subject: fieldValue(form, "subject"),
    message: fieldValue(form, "message"),
  };
}

function setFieldError(form: HTMLFormElement, name: FieldName, message: string | null): void {
  const error = qs(`[data-error="${name}"]`, form);
  const field = error?.closest(".field");
  const input = form.elements.namedItem(name);
  if (!error || !field) return;
  if (message !== null) error.textContent = message;
  field.classList.toggle("is-invalid", message !== null);
  if (input instanceof HTMLElement) input.setAttribute("aria-invalid", String(message !== null));
}

function phoneError(form: HTMLFormElement, phone: string): string | null {
  const el = qs("[data-error=\"phone\"]", form);
  if (phone === "") return el?.dataset.msgRequired ?? "";
  if (!PHONE_PATTERN.test(phone.replace(/[\s-]/g, ""))) return el?.dataset.msgInvalid ?? "";
  return null;
}

function requiredError(form: HTMLFormElement, name: FieldName, value: string): string | null {
  if (value !== "") return null;
  return qs(`[data-error="${name}"]`, form)?.textContent ?? "";
}

/** Returns the first invalid field name, or null when the form is valid. */
function validateContact(form: HTMLFormElement, values: ContactValues): FieldName | null {
  const errors: [FieldName, string | null][] = [
    ["name", requiredError(form, "name", values.name)],
    ["phone", phoneError(form, values.phone)],
    ["message", requiredError(form, "message", values.message)],
  ];
  let firstInvalid: FieldName | null = null;
  errors.forEach(([name, message]) => {
    setFieldError(form, name, message);
    if (message !== null && firstInvalid === null) firstInvalid = name;
  });
  return firstInvalid;
}

function buildMailto(address: string, values: ContactValues): string {
  const subject = `[${values.subject}] ${values.name}`;
  const body = `${values.message}\n\n— ${values.name}\n${values.phone}`;
  return `mailto:${address}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

function initContactForm(): void {
  const form = qs<HTMLFormElement>("[data-contact-form]");
  const address = form?.dataset.mailto;
  if (!form || !address) return;
  const status = qs("[data-form-status]", form);

  form.addEventListener("submit", (event: SubmitEvent) => {
    event.preventDefault();
    const values = readContactValues(form);
    const invalid = validateContact(form, values);
    if (invalid !== null) {
      const input = form.elements.namedItem(invalid);
      if (input instanceof HTMLElement) input.focus();
      return;
    }
    window.location.href = buildMailto(address, values);
    if (status) status.hidden = false;
  });

  form.addEventListener("input", (event: Event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement)) return;
    const field = target.closest(".field");
    if (field?.classList.contains("is-invalid") && target.value.trim() !== "") field.classList.remove("is-invalid");
  });
}

function legacyCopy(text: string): boolean {
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  try {
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    area.remove();
  }
}

async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Permission denied or unsupported: fall through to the legacy path.
  }
  return legacyCopy(text);
}

function flashCopied(button: HTMLButtonElement): void {
  const label = qs("span", button);
  const original = label?.textContent ?? "";
  button.classList.add("is-done");
  if (label) label.textContent = button.dataset.copied ?? original;
  window.setTimeout(() => {
    button.classList.remove("is-done");
    if (label) label.textContent = original;
  }, COPY_RESET_MS);
}

function initCopyButtons(): void {
  qsa<HTMLButtonElement>("[data-copy]").forEach((button) => {
    button.addEventListener("click", () => {
      const text = button.dataset.copy;
      if (!text || button.classList.contains("is-done")) return;
      copyText(text)
        .then((ok) => {
          if (ok) flashCopied(button);
        })
        .catch((error: unknown) => console.error("[kabirloole] copy failed", error));
    });
  });
}

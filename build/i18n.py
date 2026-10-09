"""Content loading, consistency checks and locale-aware number formatting."""

from __future__ import annotations

from typing import Any, Final

import content_ar
import content_en
import content_fa
from data import DEFAULT_LANG, LANGS

Content = dict[str, Any]
CONTENT: Final[dict[str, Content]] = {"fa": content_fa.T, "ar": content_ar.T, "en": content_en.T}

_DIGITS: Final[dict[str, dict[int, str]]] = {
    "fa": str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫"),
    "ar": str.maketrans("0123456789.", "٠١٢٣٤٥٦٧٨٩٫"),
}


def local_digits(value: str, lang: str) -> str:
    """Write ASCII digits (and the decimal point) in the page language's digits."""
    table = _DIGITS.get(lang)
    return value.translate(table) if table else value


def fmt_number(value: float, decimals: int, lang: str, group: bool = True) -> str:
    """Match the browser's Intl.NumberFormat output so server and script render alike."""
    text = f"{value:,.{decimals}f}" if group else f"{value:.{decimals}f}"
    if lang in _DIGITS:
        text = text.replace(",", "٬")
    return local_digits(text, lang)


def fmt_weight(kg_per_m: float, lang: str) -> str:
    """Weights keep the factory sheet's precision: three decimals below 10 kg/m, two above."""
    return fmt_number(kg_per_m, 3 if kg_per_m < 10 else 2, lang)


def _shape(obj: Any, path: str = "") -> set[str]:
    """Every key path plus every list length, so translations must match structurally."""
    out: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            out.add(f"{path}{key}")
            out |= _shape(value, f"{path}{key}.")
    elif isinstance(obj, list):
        out.add(f"{path}#len={len(obj)}")
        for i, value in enumerate(obj):
            out |= _shape(value, f"{path}{i}.")
    return out


def check_content() -> None:
    if set(CONTENT) != set(LANGS):
        raise SystemExit(f"Content languages {sorted(CONTENT)} do not match LANGS {list(LANGS)}")
    base = _shape(CONTENT[DEFAULT_LANG])
    for lang, t in CONTENT.items():
        if t["lang"] != lang:
            raise SystemExit(f"content_{lang}.py declares lang={t['lang']!r}")
        diff = base ^ _shape(t)
        if diff:
            raise SystemExit(f"[{lang}] content differs from {DEFAULT_LANG}: {sorted(diff)[:12]}")

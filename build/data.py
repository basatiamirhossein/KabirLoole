"""Language-independent site settings: URLs, contacts, pages and fonts."""

from __future__ import annotations

from typing import Final, NamedTuple, TypedDict

SITE_URL: Final[str] = ""  # e.g. "https://kabirloole.ir"; enables canonical, hreflang, sitemap and robots
ASSET_VERSION: Final[str] = "2.2.0"  # bump to bust browser caches after a release

LANGS: Final[tuple[str, ...]] = ("fa", "ar", "en")
DEFAULT_LANG: Final[str] = "fa"
PAGES: Final[tuple[str, ...]] = ("index", "about", "products", "quality", "projects", "blog", "contact")


class Phone(TypedDict):
    key: str
    display: str
    tel: str
    quote: bool  # listed wherever the site offers a price inquiry


PHONES: Final[list[Phone]] = [
    {"key": "ceo", "display": "0918 141 0327", "tel": "+989181410327", "quote": True},
    {"key": "sales", "display": "0912 224 1585", "tel": "+989122241585", "quote": True},
    {"key": "sales", "display": "0910 224 1585", "tel": "+989102241585", "quote": False},
    {"key": "fax", "display": "084 3522 4111", "tel": "+988435224111", "quote": False},
]

# Price-inquiry numbers, sales line first.
QUOTE_PHONES: Final[list[Phone]] = sorted((p for p in PHONES if p["quote"]), key=lambda p: p["key"] != "sales")

EMAIL: Final[str] = "KLS_Basati@yahoo.com"
INSTAGRAM: Final[str] = "kabirloole"
INSTAGRAM_URL: Final[str] = "https://www.instagram.com/kabirloole/"
MAP_QUERY: Final[str] = "کبیر لوله دره شهر"

CERTS: Final[tuple[str, ...]] = ("cert-5", "cert-4", "cert-1", "cert-2", "cert-3", "award")


class FontFace(NamedTuple):
    family: str
    file: str  # woff2 file name in assets/fonts, without extension
    weight: int
    unicode_range: str = ""


class Typeface(NamedTuple):
    body: str  # CSS family names, the fallback stack is appended
    display: str
    display_weight: int
    preload: tuple[str, ...]  # FontFace.file names worth preloading


# To change a font: drop the woff2 files into assets/fonts, list them here, point TYPEFACES at
# the family and rebuild. The build writes the @font-face rules and per-language variables.
FONT_FACES: Final[tuple[FontFace, ...]] = (
    # Dana FaNum (fontiran.com, licensed) draws ASCII digits as Persian ones, so 0-9 come from KL Latin.
    FontFace("Dana", "Dana-FaNum-Regular", 400, "U+0000-002F, U+003A-10FFFF"),
    # Latin digits and a few punctuation marks Dana lacks; a 4 KB subset of Vazir (see build/make_latin_subset.py).
    FontFace("KL Latin", "KL-Latin", 400),
    FontFace("Vazir", "Vazir", 400),
    FontFace("Vazir", "Vazir-Bold", 700),
    FontFace("Sahel", "Sahel-Black", 900),
)
FALLBACK_STACK: Final[str] = 'system-ui, -apple-system, "Segoe UI", Tahoma, "Noto Sans Arabic", sans-serif'

# Only Dana Regular exists, so headings use the browser's synthetic bold.
_DANA: Final[Typeface] = Typeface('"Dana", "KL Latin"', '"Dana", "KL Latin"', 700, ("Dana-FaNum-Regular",))
TYPEFACES: Final[dict[str, Typeface]] = {
    "fa": _DANA,
    "en": _DANA,
    # Dana draws the Arabic final yeh without dots (علي reads as على) and Arabic-Indic digits in
    # Persian shapes, so Arabic pages keep Vazir and Sahel, which render both correctly.
    "ar": Typeface('"Vazir"', '"Sahel", "Vazir"', 900, ("Vazir", "Sahel-Black")),
}

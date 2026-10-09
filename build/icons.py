"""Inline SVG icon sprite (24×24 stroke icons).

icon() records every name it emits, so each page ships a sprite with only the icons it uses:
call take_used() before rendering a page body and again after it.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

ICONS: Final[dict[str, str]] = {
    "leaf": '<path d="M19.8 4.2C12 4.4 6.6 7.3 6.6 13c0 2.1 1.6 3.8 3.8 3.8 5.7 0 8.6-5.4 9.4-12.6Z"/><path d="M4 20c2.4-5.5 6.2-8.9 11.4-10.6"/>',
    "drop": '<path d="M12 3S6.5 9.1 6.5 14a5.5 5.5 0 0 0 11 0C17.5 9.1 12 3 12 3Z"/><path d="M9.5 14.5a2.7 2.7 0 0 0 2.5 2"/>',
    "shield": '<path d="M12 3.5 19 6v5.3c0 4.4-2.8 7.7-7 9.2-4.2-1.5-7-4.8-7-9.2V6l7-2.5Z"/><path d="m9 12 2 2 4-4"/>',
    "flask": '<path d="M9 3h6M10 3v6.2L4.8 18a2 2 0 0 0 1.7 3h11a2 2 0 0 0 1.7-3L14 9.2V3"/><path d="M7.5 15h9"/>',
    "award": '<circle cx="12" cy="9" r="5.5"/><path d="m8.6 13.4-1.4 7.1 4.8-2.4 4.8 2.4-1.4-7.1"/><path d="m10 9 1.4 1.4L14 7.8"/>',
    "layers": '<path d="m12 3 9 4.5-9 4.5-9-4.5L12 3Z"/><path d="m3 12 9 4.5 9-4.5"/><path d="m3 16.5 9 4.5 9-4.5"/>',
    "factory": '<path d="M3 21V10l5 3V10l5 3V10l5 3V4h3v17H3Z"/><path d="M7 17h2M12 17h2M17 17h1"/>',
    "sprout": '<path d="M12 21v-8"/><path d="M12 13c0-4-3-6.5-7-6.5 0 4 3 6.5 7 6.5Z"/><path d="M12 11c0-3.6 2.6-6 6.5-6 0 3.6-2.6 6-6.5 6Z"/><path d="M7 21h10"/>',
    "gauge": '<path d="M4.5 18a8.5 8.5 0 1 1 15 0"/><path d="m12 13 4-4.5"/><circle cx="12" cy="13.5" r="1.4"/><path d="M8 18h8"/>',
    "map": '<path d="m9 4-6 2.5v13.5l6-2.5 6 2.5 6-2.5V4l-6 2.5L9 4Z"/><path d="M9 4v13.5M15 6.5V20"/>',
    "truck": '<path d="M2.5 6h11v10h-11z"/><path d="M13.5 9.5h4l3 3.5V16h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "wave": '<path d="M3 9c2.5-2.5 4.5-2.5 6 0s3.5 2.5 6 0 4.5-2.5 6 0"/><path d="M3 15c2.5-2.5 4.5-2.5 6 0s3.5 2.5 6 0 4.5-2.5 6 0"/>',
    "feather": '<path d="M20 4c-7 0-12 4-12 11v5"/><path d="M8 15c4 0 8.5-1.5 10-6"/><path d="M8 11.5c2.5 0 5-.7 6.5-2.2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "flame": '<path d="M12 21c3.9 0 6.5-2.6 6.5-6.2 0-3.4-2.4-5.6-3.6-8.3-.5 2-1.6 3.1-2.9 3.6C12 6.8 10.5 4.3 8.5 3c.3 3.4-3 5.8-3 10.4C5.5 18 8.3 21 12 21Z"/><path d="M12 21c-1.7 0-3-1.3-3-3 0-2 1.6-2.7 2.4-4.4.9 1.6 3.6 2.4 3.6 4.4 0 1.7-1.3 3-3 3Z"/>',
    "microscope": '<path d="M6 21h12"/><path d="M8 18h8"/><path d="M14 18a5 5 0 0 0-2.5-9.3"/><path d="m9 3 3.5 2-3 5.2L6 8.2 9 3Z"/><path d="M8 11v4"/>',
    "thermo": '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0Z"/><path d="M12 9v7"/>',
    "stretch": '<path d="M4 12h16"/><path d="m7 9-3 3 3 3M17 9l3 3-3 3"/><path d="M10 7h4M10 17h4"/>',
    "cut": '<circle cx="6" cy="7" r="2.5"/><circle cx="6" cy="17" r="2.5"/><path d="M8.2 8.3 20 18M8.2 15.7 20 6"/>',
    "beaker": '<path d="M5 3h14M6.5 3v13.5A4.5 4.5 0 0 0 11 21h2a4.5 4.5 0 0 0 4.5-4.5V3"/><path d="M6.5 11h11"/>',
    "scale": '<path d="M12 4v16M6 20h12"/><path d="M4.5 7h15"/><path d="m4.5 7-2.5 6a2.8 2.8 0 0 0 5 0L4.5 7ZM19.5 7 17 13a2.8 2.8 0 0 0 5 0l-2.5-6Z"/>',
    "ruler": '<path d="m3.5 15.5 12-12 5 5-12 12-5-5Z"/><path d="m7.5 11.5 2 2M10.5 8.5l2 2M13.5 5.5l2 2"/>',
    "caliper": '<path d="M4 4h16v4H4z"/><path d="M6 8v12l3-3V8M15 8v6"/><path d="M8 6h1M11 6h1M14 6h1M17 6h1"/>',
    "phone": '<path d="M5 4h3.5l1.7 4.3-2.2 1.4a11 11 0 0 0 6.3 6.3l1.4-2.2L20 15.5V19a1.5 1.5 0 0 1-1.6 1.5C10.6 20 4 13.4 3.5 5.6A1.5 1.5 0 0 1 5 4Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "pin": '<path d="M12 21s-6.5-6.2-6.5-11.2a6.5 6.5 0 0 1 13 0C18.5 14.8 12 21 12 21Z"/><circle cx="12" cy="10" r="2.3"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/>',
    "arrow": '<path d="M19 12H5m6-6-6 6 6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
    "close": '<path d="m6 6 12 12M18 6 6 18"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.4 3.5 5.2 3.5 8.5s-1.1 6.1-3.5 8.5c-2.4-2.4-3.5-5.2-3.5-8.5S9.6 5.9 12 3.5Z"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    "chevron": '<path d="m6 15 6-6 6 6"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/>',
    "fax": '<path d="M7 9V3.5h10V9"/><rect x="3.5" y="9" width="17" height="8" rx="2"/><path d="M7 14h10v6.5H7z"/>',
    "zoom": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4M11 8.5v5M8.5 11h5"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "users": '<circle cx="9" cy="8.5" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 5.2a3.5 3.5 0 0 1 0 6.6M18 14.5a6.5 6.5 0 0 1 3.5 5.5"/>',
}


_used: set[str] = set()


def take_used() -> set[str]:
    """Return the icons used since the last call and reset the record."""
    names = set(_used)
    _used.clear()
    return names


def sprite(names: Iterable[str]) -> str:
    symbols = "".join(
        f'<symbol id="i-{name}" viewBox="0 0 24 24">{ICONS[name]}</symbol>' for name in sorted(names)
    )
    return (
        '<svg class="sprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
        f"{symbols}</svg>"
    )


def icon(name: str, cls: str = "") -> str:
    if name not in ICONS:
        raise KeyError(f"Unknown icon: {name}")
    _used.add(name)
    extra = f" {cls}" if cls else ""
    return f'<svg class="icon{extra}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'

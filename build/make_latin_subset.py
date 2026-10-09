"""Write assets/fonts/KL-Latin.woff2: Latin digits and a few punctuation marks taken from Vazir.

Dana FaNum maps 0-9 to Persian digit shapes and has no dashes, ellipsis or copyright sign.
This 4 KB subset fills those gaps. Vazir's licence allows modified copies under another name.
Needs fontTools and brotli (pip install fonttools brotli); run it only when the glyph list changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from fontTools import subset
from fontTools.ttLib import TTFont

FONTS: Final[Path] = Path(__file__).resolve().parent.parent / "assets" / "fonts"
CODEPOINTS: Final[list[int]] = [
    *range(0x30, 0x3A),  # 0-9
    0x7E, 0xA9, 0xB2, 0xB7,  # ~ © ² ·
    0x2013, 0x2014, 0x2022, 0x2026,  # – — • …
]
NAMES: Final[dict[int, str]] = {1: "KL Latin", 3: "KL Latin Regular", 4: "KL Latin Regular", 6: "KLLatin-Regular", 16: "KL Latin"}


def main() -> None:
    font = TTFont(FONTS / "Vazir.woff2")
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "tnum", "lnum"]
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=CODEPOINTS)
    subsetter.subset(font)
    for record in font["name"].names:
        if record.nameID in NAMES:
            record.string = NAMES[record.nameID]
    font.flavor = "woff2"
    out = FONTS / "KL-Latin.woff2"
    font.save(out)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

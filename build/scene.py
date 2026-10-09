"""Procedural hero scene: a farm in perspective, irrigated by an HDPE pipe with water flowing through it.

The scene is drawn left-to-right (water flows from the left edge). RTL pages mirror it with CSS.
"""

from __future__ import annotations

from typing import Final

W: Final[int] = 1600
H: Final[int] = 1000
HORIZON: Final[float] = 470.0
VP_X: Final[float] = 800.0
ROW_GAP: Final[float] = 170.0
ROWS: Final[range] = range(-11, 12)
IRRIGATED: Final[tuple[int, ...]] = (-4, -2, 0, 2, 4)
HEADER_S: Final[float] = 0.86
DEPTHS: Final[tuple[float, ...]] = tuple(1 / (1 + j * 0.42) for j in range(0, 13))


def _f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _row_point(row: int, s: float) -> tuple[float, float]:
    xb = VP_X + row * ROW_GAP
    return VP_X + (xb - VP_X) * s, HORIZON + (H - HORIZON) * s


def _defs() -> str:
    return f"""
<defs>
  <linearGradient id="sc-sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d9eef0"/>
    <stop offset=".55" stop-color="#eef3ea"/>
    <stop offset="1" stop-color="#f5f1e6"/>
  </linearGradient>
  <radialGradient id="sc-sun" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#fffdf2"/>
    <stop offset=".45" stop-color="#fff3c9" stop-opacity=".85"/>
    <stop offset="1" stop-color="#fff3c9" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="sc-field" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#b9d49a"/>
    <stop offset=".5" stop-color="#a3c47f"/>
    <stop offset="1" stop-color="#8fb56a"/>
  </linearGradient>
  <linearGradient id="sc-soil" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#c8b48f" stop-opacity=".0"/>
    <stop offset="1" stop-color="#9c7f57" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="sc-water" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#bfeaff"/>
    <stop offset=".5" stop-color="#4fb3e0"/>
    <stop offset="1" stop-color="#1f7fb6"/>
  </linearGradient>
  <radialGradient id="sc-drop" cx=".35" cy=".3" r=".75">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".95"/>
    <stop offset=".35" stop-color="#bfe8fb" stop-opacity=".75"/>
    <stop offset="1" stop-color="#3fa3d6" stop-opacity=".55"/>
  </radialGradient>
  <radialGradient id="sc-bubble" cx=".32" cy=".28" r=".8">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".9"/>
    <stop offset=".25" stop-color="#ffffff" stop-opacity=".25"/>
    <stop offset=".8" stop-color="#9fd8f2" stop-opacity=".18"/>
    <stop offset="1" stop-color="#5bb8e4" stop-opacity=".45"/>
  </radialGradient>
  <filter id="sc-soft" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="8"/>
  </filter>
  <clipPath id="sc-field-clip">
    <rect x="0" y="{_f(HORIZON)}" width="{W}" height="{_f(H - HORIZON)}"/>
  </clipPath>
  <g id="sc-plant">
    <path d="M0 0V-18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/>
    <path d="M0-14C-2-24-10-30-19-30-18-21-10-15 0-14Z" fill="currentColor"/>
    <path d="M0-18C2-28 9-35 18-35 18-25 10-19 0-18Z" fill="currentColor"/>
  </g>
</defs>"""


def _backdrop() -> str:
    h = HORIZON
    return f"""
<rect width="{W}" height="{H}" fill="url(#sc-sky)"/>
<g class="sc-sun"><circle cx="1230" cy="230" r="230" fill="url(#sc-sun)"/><circle cx="1230" cy="230" r="58" fill="#fffaf0"/></g>
<g class="sc-clouds" fill="#ffffff">
  <g class="sc-cloud sc-cloud--a" opacity=".85"><ellipse cx="300" cy="190" rx="120" ry="34"/><ellipse cx="360" cy="170" rx="70" ry="40"/><ellipse cx="250" cy="176" rx="56" ry="30"/></g>
  <g class="sc-cloud sc-cloud--b" opacity=".7"><ellipse cx="980" cy="120" rx="96" ry="26"/><ellipse cx="1030" cy="104" rx="56" ry="30"/></g>
</g>
<path class="sc-mountains" d="M0 {_f(h - 40)} L120 {_f(h - 120)} L230 {_f(h - 70)} L360 {_f(h - 190)} L470 {_f(h - 95)} L560 {_f(h - 140)} L700 {_f(h - 60)} L820 {_f(h - 160)} L960 {_f(h - 80)} L1080 {_f(h - 210)} L1210 {_f(h - 100)} L1330 {_f(h - 150)} L1470 {_f(h - 70)} L1600 {_f(h - 120)} V{_f(h)} H0Z" fill="#c4d8d2" opacity=".85"/>
<path d="M0 {_f(h - 22)} C200 {_f(h - 70)} 380 {_f(h - 30)} 560 {_f(h - 52)} S900 {_f(h - 20)} 1080 {_f(h - 58)} 1420 {_f(h - 18)} 1600 {_f(h - 46)} V{_f(h)} H0Z" fill="#a9c99a"/>
<path d="M0 {_f(h - 6)} C260 {_f(h - 30)} 520 {_f(h + 4)} 800 {_f(h - 16)} S1300 {_f(h + 2)} 1600 {_f(h - 20)} V{_f(h + 10)} H0Z" fill="#94bb7f"/>
<rect x="0" y="{_f(h)}" width="{W}" height="{_f(H - h)}" fill="url(#sc-field)"/>
<rect x="0" y="{_f(h)}" width="{W}" height="{_f(H - h)}" fill="url(#sc-soil)"/>"""


def _furrows() -> str:
    lines: list[str] = []
    for row in ROWS:
        x0, y0 = _row_point(row, 1.08)
        lines.append(f"M{_f(x0)} {_f(y0)}L{_f(VP_X)} {_f(HORIZON)}")
    return f'<path class="sc-furrows" d="{"".join(lines)}" stroke="#7c9b5a" stroke-opacity=".35" stroke-width="2" fill="none" clip-path="url(#sc-field-clip)"/>'


def _plants() -> str:
    groups: list[str] = []
    for row in ROWS:
        irrigated = row in IRRIGATED
        cls = "sc-row sc-row--wet" if irrigated else "sc-row"
        delay = abs(row) * 0.08
        items: list[str] = []
        for s in DEPTHS[1:]:
            x, y = _row_point(row, s)
            if x < -40 or x > W + 40:
                continue
            scale = 1.25 * s
            # The <g> places the plant; the <use> carries the CSS grow animation.
            items.append(f'<g transform="translate({_f(x)} {_f(y)}) scale({scale:.3f})"><use href="#sc-plant"/></g>')
        groups.append(f'<g class="{cls}" style="--d:{delay:.2f}s">{"".join(items)}</g>')
    return f'<g class="sc-plants" clip-path="url(#sc-field-clip)">{"".join(groups)}</g>'


def _main_pipe_d() -> str:
    hx_start, hy = _row_point(IRRIGATED[0], HEADER_S)
    hx_end, _ = _row_point(IRRIGATED[-1], HEADER_S)
    return (
        f"M-90 760 C40 770 70 {_f(hy - 8)} {_f(hx_start - 70)} {_f(hy)} "
        f"L{_f(hx_end + 26)} {_f(hy)}"
    )


def _laterals() -> str:
    parts: list[str] = []
    for idx, row in enumerate(IRRIGATED):
        x0, y0 = _row_point(row, HEADER_S)
        x1, y1 = _row_point(row, DEPTHS[-1])
        w0, w1 = 7.0, 2.0
        body = (
            f"M{_f(x0 - w0)} {_f(y0)}L{_f(x1 - w1)} {_f(y1)}"
            f"L{_f(x1 + w1)} {_f(y1)}L{_f(x0 + w0)} {_f(y0)}Z"
        )
        water = f"M{_f(x0)} {_f(y0)}L{_f(x1)} {_f(y1)}"
        drips: list[str] = []
        for j, s in enumerate(DEPTHS[1:-1]):
            if s > HEADER_S - 0.02:
                continue
            x, y = _row_point(row, s)
            r = 4.2 * s + 1.2
            drop_delay = (j * 0.37 + idx * 0.23) % 1.6
            drips.append(
                f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 0.7)}" fill="#1b2125"/>'
                f'<circle class="sc-drip" cx="{_f(x)}" cy="{_f(y + r)}" r="{_f(r)}" fill="url(#sc-drop)" '
                f'style="--dd:{drop_delay:.2f}s;--fall:{_f(22 * s + 4)}px"/>'
            )
        parts.append(
            f'<g class="sc-lateral" style="--ld:{idx * 0.14:.2f}s">'
            f'<path d="{body}" fill="#1f2529"/>'
            f'<path class="sc-lateral-water" d="{water}" pathLength="1" stroke="#7fd0f3" stroke-width="2" stroke-linecap="round" fill="none"/>'
            f'{"".join(drips)}</g>'
        )
    return f'<g class="sc-laterals">{"".join(parts)}</g>'


def _pipe() -> str:
    d = _main_pipe_d()
    return f"""
<g class="sc-pipe">
  <path d="{d}" transform="translate(0 16)" stroke="#2d3a2a" stroke-opacity=".22" stroke-width="40" stroke-linecap="round" fill="none" filter="url(#sc-soft)"/>
  <path d="{d}" stroke="#161b1e" stroke-width="34" stroke-linecap="round" fill="none"/>
  <path d="{d}" stroke="#233037" stroke-width="26" stroke-linecap="round" fill="none"/>
  <path class="sc-water-fill" d="{d}" pathLength="1" stroke="url(#sc-water)" stroke-width="20" stroke-linecap="round" fill="none"/>
  <path class="sc-water-flow" d="{d}" pathLength="1" stroke="#ffffff" stroke-opacity=".7" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="{d}" transform="translate(0 -9)" stroke="#2f86d6" stroke-width="3" fill="none"/>
  <path d="{d}" transform="translate(0 -12)" stroke="#ffffff" stroke-opacity=".28" stroke-width="3" stroke-linecap="round" fill="none"/>
</g>"""


def _bubbles() -> str:
    return """
<g class="sc-bubbles">
  <circle class="sc-bubble sc-bubble--a" cx="560" cy="300" r="44" fill="url(#sc-bubble)" stroke="#ffffff" stroke-opacity=".7"/>
  <circle class="sc-bubble sc-bubble--b" cx="1430" cy="420" r="26" fill="url(#sc-bubble)" stroke="#ffffff" stroke-opacity=".7"/>
  <circle class="sc-bubble sc-bubble--c" cx="150" cy="420" r="18" fill="url(#sc-bubble)" stroke="#ffffff" stroke-opacity=".7"/>
</g>"""


def hero_scene() -> str:
    return (
        f'<svg class="scene" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" '
        f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
        f"{_defs()}{_backdrop()}{_furrows()}{_plants()}{_laterals()}{_pipe()}{_bubbles()}</svg>"
    )


def wave_divider(cls: str = "") -> str:
    """A soft water wave used at the bottom of inner-page banners."""
    extra = f" {cls}" if cls else ""
    return (
        f'<svg class="wave{extra}" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        '<path class="wave__back" d="M0 40C160 10 320 10 480 34S800 70 960 46 1280 6 1440 30V80H0Z"/>'
        '<path class="wave__front" d="M0 52C200 28 360 32 520 50S860 78 1040 56 1300 34 1440 46V80H0Z"/>'
        "</svg>"
    )

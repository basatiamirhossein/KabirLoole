"""Kabirloole pipe specifications, transcribed from the factory's own PE80 and PE100 sheets
(INSO 14427-2). Each cell is "wall/weight": wall thickness in mm, weight in kg per metre.
"-" means the size is not made in that pressure class.
"""

from __future__ import annotations

from typing import Final, NamedTuple


class Series(NamedTuple):
    sdr: str
    pn: str  # nominal working pressure (bar / atm), as printed on the sheet


class Cell(NamedTuple):
    wall: float
    weight: float


Row = tuple[Cell | None, ...]

MATERIALS: Final[tuple[str, ...]] = ("pe100", "pe80")
PRESSURES: Final[tuple[str, ...]] = ("12.5", "10", "8", "6", "4")

SERIES: Final[dict[str, tuple[Series, ...]]] = {
    "pe100": tuple(Series(s, p) for s, p in zip(("13.6", "17", "21", "26", "41"), PRESSURES)),
    "pe80": tuple(Series(s, p) for s, p in zip(("11", "13.6", "17", "21", "33"), PRESSURES)),
}

# Columns follow PRESSURES: 12.5 | 10 | 8 | 6 | 4
_SHEETS: Final[dict[str, str]] = {
    "pe100": """
        20   -          -          -          -           -
        25   2/0.147    -          -          -           -
        32   2.4/0.228  2/0.191    -          -           -
        40   3/0.356    2.4/0.290  2/0.243    -           -
        50   3.7/0.543  3/0.447    2.4/0.368  2/0.307     -
        63   4.7/0.865  3.8/0.720  3/0.571    2.5/0.486   -
        75   5.6/1.226  4.5/1.005  3.6/0.817  2.9/0.665   -
        90   6.7/1.756  5.4/1.445  4.3/1.172  3.5/0.965   -
        110  8.1/2.601  6.6/2.151  5.3/1.759  4.2/1.416   -
        125  9.2/3.352  7.4/2.743  6/2.247    4.8/1.824   -
        160  11.8/5.480 9.5/4.495  7.7/3.692  6.2/3.020   -
        200  14.7/8.531 11.9/7.018 9.6/5.748  7.7/4.664   -
        250  18.4/13.34 14.8/10.91 11.9/8.889 9.6/7.262   -
        315  23.2/21.19 18.7/17.35 15/14.1    12.1/11.54  7.7/7.460
        355  26.1/26.87 21.1/22.09 16.9/17.9  13.6/14.58  8.7/9.490
        400  29.4/34.07 23.7/27.91 19.1/22.83 15.3/18.49  9.8/12.03
    """,
    "pe80": """
        20   2/0.114    -          -          -           -
        25   2.3/0.168  2/0.147    -          -           -
        32   3/0.275    2.4/0.228  2/0.191    -           -
        40   3.7/0.425  3/0.356    2.4/0.290  2/0.243     -
        50   4.6/0.659  3.7/0.543  3/0.447    2.4/0.368   -
        63   5.8/1.043  4.7/0.865  3.8/0.720  3/0.571     -
        75   6.8/1.456  5.6/1.226  4.5/1.005  3.6/0.817   -
        90   8.2/2.110  6.7/1.756  5.4/1.445  4.3/1.172   -
        110  10/3.130   8.1/2.601  6.6/2.151  5.3/1.759   -
        125  11.4/4.060 9.2/3.352  7.4/2.743  6/2.247     -
        160  14.6/6.643 11.8/5.480 9.5/4.495  7.7/3.692   -
        200  18.2/10.36 14.7/8.531 11.9/7.018 9.6/5.748   -
        250  22.7/16.12 18.4/13.34 14.8/10.91 11.9/8.889  -
        315  28.6/25.58 23.2/21.19 18.7/17.35 15/14.1     9.7/9.318
        355  32.2/32.47 26.1/26.87 21.1/22.09 16.9/17.9   10.9/11.78
        400  36.3/41.23 29.4/34.07 23.7/27.91 19.1/22.83  12.3/15.01
    """,
}


def _parse_cell(token: str) -> Cell | None:
    if token == "-":
        return None
    wall, weight = token.split("/")
    return Cell(float(wall), float(weight))


def _parse_sheet(sheet: str) -> dict[int, Row]:
    rows: dict[int, Row] = {}
    for line in sheet.strip().splitlines():
        od, *cells = line.split()
        if len(cells) != len(PRESSURES):
            raise ValueError(f"Spec row {od} has {len(cells)} cells, expected {len(PRESSURES)}")
        rows[int(od)] = tuple(_parse_cell(c) for c in cells)
    return rows


SPEC: Final[dict[str, dict[int, Row]]] = {m: _parse_sheet(s) for m, s in _SHEETS.items()}
DIAMETERS: Final[tuple[int, ...]] = tuple(SPEC["pe100"])

if tuple(SPEC["pe80"]) != DIAMETERS:
    raise ValueError("PE80 and PE100 sheets must list the same diameters")

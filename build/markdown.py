"""A small, dependency-free Markdown renderer for the blog articles.

Covers what the articles use: front matter, headings with GitHub-style ids, paragraphs, block
quotes, nested ordered and unordered lists, pipe tables, fenced code, rules, bold, italic,
inline code, links and bare URLs. Everything else is escaped and shown as plain text.
"""

from __future__ import annotations

import html
import re
import unicodedata
from typing import Final, NamedTuple

FrontMatter = dict[str, str | list[str]]


class Heading(NamedTuple):
    level: int
    id: str
    text: str


class Rendered(NamedTuple):
    html: str
    headings: list[Heading]


_FENCE: Final = re.compile(r"^```")
_HEADING: Final = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_RULE: Final = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})\s*$")
_LIST_ITEM: Final = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
_TABLE_SEP: Final = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
_LINK: Final = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BARE_URL: Final = re.compile(r"https?://[^\s<>()\"]+")
_CODE: Final = re.compile(r"`([^`]+)`")
_BOLD: Final = re.compile(r"\*\*(.+?)\*\*")
_ITALIC: Final = re.compile(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])")
_RTL_LETTER: Final = re.compile(r"[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufeff]")
_URL_TAIL: Final = ".,;:!?،؛)»"
_TOKEN: Final = "\x00{}\x00"


# ---------------------------------------------------------------- front matter

def _fm_value(raw: str) -> str | list[str]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [item.strip().strip("\"'") for item in raw[1:-1].split(",") if item.strip()]
    return raw.strip("\"'")


def split_front_matter(text: str) -> tuple[FrontMatter, str]:
    """`---` delimited `key: value` lines at the top of the file; lists use [a, b]."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            meta: FrontMatter = {}
            for line in lines[1:end]:
                key, sep, value = line.partition(":")
                if sep and key.strip():
                    meta[key.strip()] = _fm_value(value)
            return meta, "\n".join(lines[end + 1:])
    raise ValueError("front matter is not closed with ---")


# ---------------------------------------------------------------- inline

def _anchor_char(ch: str) -> bool:
    category = unicodedata.category(ch)
    return ch in "- " or category[0] in "LMN" or category == "Pc"


def slugify(text: str) -> str:
    """GitHub's heading anchors: lower case, punctuation (and ZWNJ) dropped, spaces to hyphens."""
    plain = re.sub(r"[*`]", "", _LINK.sub(r"\1", text)).strip().lower()
    return "".join(filter(_anchor_char, plain)).replace(" ", "-")


def _link(label: str, href: str) -> str:
    external = href.startswith(("http://", "https://"))
    attrs = ' target="_blank" rel="noopener"' if external else ""
    return f'<a href="{html.escape(href)}"{attrs}>{label}</a>'


def _bare_url(match: re.Match[str], tokens: list[str]) -> str:
    url = match.group(0)
    tail = ""
    while url and url[-1] in _URL_TAIL:
        url, tail = url[:-1], url[-1] + tail
    tokens.append(f'<a class="url" href="{html.escape(url)}" target="_blank" rel="noopener" dir="ltr">{html.escape(url)}</a>')
    return _TOKEN.format(len(tokens) - 1) + tail


def _stash(tokens: list[str], markup: str) -> str:
    tokens.append(markup)
    return _TOKEN.format(len(tokens) - 1)


def inline(text: str) -> str:
    """Escape the text, then turn Markdown emphasis, code and links into HTML."""
    tokens: list[str] = []
    text = _CODE.sub(lambda m: _stash(tokens, f"<code>{html.escape(m.group(1))}</code>"), text)
    text = _LINK.sub(lambda m: _stash(tokens, _link(inline(m.group(1)), m.group(2))), text)
    text = _BARE_URL.sub(lambda m: _bare_url(m, tokens), text)
    text = html.escape(text, quote=False)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    for _ in range(3):  # links can hold tokens of their own
        text = re.sub("\x00(\\d+)\x00", lambda m: tokens[int(m.group(1))], text)
    return text


# ---------------------------------------------------------------- blocks

def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_table_start(lines: list[str], i: int) -> bool:
    return lines[i].lstrip().startswith("|") and i + 1 < len(lines) and bool(_TABLE_SEP.match(lines[i + 1]))


def _starts_block(lines: list[str], i: int) -> bool:
    line = lines[i]
    return bool(
        not line.strip() or _FENCE.match(line) or _HEADING.match(line) or _RULE.match(line)
        or line.startswith(">") or _LIST_ITEM.match(line) or _is_table_start(lines, i)
    )


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _cell(text: str) -> str:
    """Cells without right-to-left letters ("2.0 / 0.147") keep their left-to-right order in an RTL table."""
    markup = inline(text)
    return markup if _RTL_LETTER.search(text) or not text.strip() else f'<span dir="ltr">{markup}</span>'


def _table(lines: list[str], i: int) -> tuple[str, int]:
    head = "".join(f'<th scope="col">{_cell(c)}</th>' for c in _cells(lines[i]))
    i += 2
    rows: list[str] = []
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        rows.append("<tr>" + "".join(f"<td>{_cell(c)}</td>" for c in _cells(lines[i])) + "</tr>")
        i += 1
    table = f'<table class="md-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    return f'<div class="table-wrap md-table-wrap" tabindex="0">{table}</div>', i


def _list(lines: list[str], i: int) -> tuple[str, int]:
    first = _LIST_ITEM.match(lines[i])
    assert first is not None
    base = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    start = int(first.group(2)[:-1]) if ordered else 1
    items: list[str] = []
    while i < len(lines):
        match = _LIST_ITEM.match(lines[i])
        if not match or len(match.group(1)) != base:
            break
        body, i = [inline(match.group(3))], i + 1
        while i < len(lines) and lines[i].strip() and _indent(lines[i]) > base:
            if _LIST_ITEM.match(lines[i]):
                nested, i = _list(lines, i)
                body.append(nested)
            else:
                body.append(" " + inline(lines[i].strip()))
                i += 1
        items.append(f"<li>{''.join(body)}</li>")
        if i < len(lines) and not lines[i].strip() and i + 1 < len(lines):
            nxt = _LIST_ITEM.match(lines[i + 1])
            if nxt and len(nxt.group(1)) == base and nxt.group(2)[0].isdigit() == ordered:
                i += 1  # a loose list: blank lines between items
    tag = "ol" if ordered else "ul"
    start_attr = f' start="{start}"' if ordered and start != 1 else ""
    return f"<{tag}{start_attr}>{''.join(items)}</{tag}>", i


class _Renderer:
    def __init__(self) -> None:
        self.headings: list[Heading] = []
        self._ids: dict[str, int] = {}

    def _unique_id(self, text: str) -> str:
        slug = slugify(text) or "section"
        count = self._ids.get(slug, 0)
        self._ids[slug] = count + 1
        return slug if count == 0 else f"{slug}-{count}"

    def _heading(self, match: re.Match[str]) -> str:
        level, text = len(match.group(1)), match.group(2)
        anchor = self._unique_id(text)
        self.headings.append(Heading(level, anchor, text))
        return f'<h{level} id="{html.escape(anchor)}">{inline(text)}</h{level}>'

    def blocks(self, lines: list[str]) -> str:
        out: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
            elif _FENCE.match(line):
                end = next((j for j in range(i + 1, len(lines)) if _FENCE.match(lines[j])), len(lines))
                out.append(f"<pre><code>{html.escape(chr(10).join(lines[i + 1:end]))}</code></pre>")
                i = end + 1
            elif heading := _HEADING.match(line):
                out.append(self._heading(heading))
                i += 1
            elif _RULE.match(line):
                out.append("<hr>")
                i += 1
            elif line.startswith(">"):
                quoted: list[str] = []
                while i < len(lines) and lines[i].startswith(">"):
                    quoted.append(re.sub(r"^>\s?", "", lines[i]))
                    i += 1
                out.append(f"<blockquote>{self.blocks(quoted)}</blockquote>")
            elif _is_table_start(lines, i):
                table, i = _table(lines, i)
                out.append(table)
            elif _LIST_ITEM.match(line):
                listing, i = _list(lines, i)
                out.append(listing)
            else:
                para = [line.strip()]
                i += 1
                while i < len(lines) and not _starts_block(lines, i):
                    para.append(lines[i].strip())
                    i += 1
                out.append(f"<p>{'<br>'.join(inline(line) for line in para)}</p>")  # line breaks are kept, as in chat Markdown
        return "".join(out)


def render(markdown: str) -> Rendered:
    renderer = _Renderer()
    body = renderer.blocks(markdown.replace("\r\n", "\n").split("\n"))
    return Rendered(body, renderer.headings)

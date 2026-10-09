"""Blog: loads the Markdown articles in content/blog and renders the list, the article pages and
the home page teaser.

The articles are written in Persian, so article pages exist under fa/ only. The Arabic and
English blog pages list the same articles with a note and link to the Persian pages.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Final, NamedTuple

from components import cta_band, e, eyebrow, page_hero, section_head
from data import SITE_URL
from i18n import CONTENT, Content, local_digits
from icons import ICONS, icon
from layout import PageInfo, page_url
from markdown import FrontMatter, render, split_front_matter
from scene import wave_divider

BLOG_DIR: Final[Path] = Path(__file__).resolve().parent.parent / "content" / "blog"
ARTICLE_LANG: Final[str] = "fa"
WORDS_PER_MINUTE: Final[int] = 200
_REQUIRED: Final[tuple[str, ...]] = ("title", "slug", "description", "category", "date")
_SLUG: Final = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TOC: Final = re.compile(r'(<h2 id="([^"]+)">[^<]*</h2>)(<ol>(?:<li><a href="#[^"]+">.*?</a></li>)+</ol>)')
_PERSIAN_DIGITS: Final = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class Article(NamedTuple):
    slug: str
    title: str
    description: str
    category: str
    author: str
    keywords: tuple[str, ...]
    published: date
    minutes: int
    icon: str
    html: str

    @property
    def page(self) -> str:
        return f"blog-{self.slug}"


# ---------------------------------------------------------------- loading

def _text(meta: FrontMatter, key: str, default: str = "") -> str:
    value = meta.get(key, default)
    return value if isinstance(value, str) else ", ".join(value)


def _minutes(meta: FrontMatter, body: str) -> int:
    match = re.search(r"\d+", _text(meta, "reading_time").translate(_PERSIAN_DIGITS))
    return int(match.group(0)) if match else max(1, round(len(body.split()) / WORDS_PER_MINUTE))


def _drop_title(body: str) -> str:
    """The page hero shows the title, so the article's own leading `# title` line is removed."""
    return re.sub(r"\A\s*# [^\n]*\n", "", body, count=1)


def _mark_toc(html: str) -> str:
    """An h2 followed by a list of in-page links becomes the article's table of contents."""
    return _TOC.sub(r'<nav class="toc neu" aria-labelledby="\2">\1\3</nav>', html, count=1)


def _validate(meta: FrontMatter, path: Path) -> None:
    missing = [key for key in _REQUIRED if not _text(meta, key)]
    if missing:
        raise SystemExit(f"{path.name}: front matter is missing {', '.join(missing)}")
    if not _SLUG.match(_text(meta, "slug")):
        raise SystemExit(f"{path.name}: slug must use a-z, 0-9 and hyphens only")
    if _text(meta, "icon", "leaf") not in ICONS:
        raise SystemExit(f"{path.name}: unknown icon {_text(meta, 'icon')!r}; pick one from build/icons.py")


def load_article(path: Path) -> Article:
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    _validate(meta, path)
    try:
        published = date.fromisoformat(_text(meta, "date"))
    except ValueError as error:
        raise SystemExit(f"{path.name}: date must look like 2026-10-09 ({error})") from error
    keywords = meta.get("keywords", [])
    return Article(
        slug=_text(meta, "slug"),
        title=_text(meta, "title"),
        description=_text(meta, "description"),
        category=_text(meta, "category"),
        author=_text(meta, "author"),
        keywords=tuple(keywords) if isinstance(keywords, list) else (keywords,),
        published=published,
        minutes=_minutes(meta, body),
        icon=_text(meta, "icon", "leaf"),
        html=_mark_toc(render(_drop_title(body)).html),
    )


def load_articles() -> list[Article]:
    """Newest first; articles from the same day keep their file name order."""
    articles = [load_article(path) for path in sorted(BLOG_DIR.glob("*.md"))]
    slugs = [a.slug for a in articles]
    duplicates = sorted({s for s in slugs if slugs.count(s) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate article slugs: {', '.join(duplicates)}")
    return sorted(articles, key=lambda a: a.published.toordinal(), reverse=True)


ARTICLES: Final[list[Article]] = load_articles()


# ---------------------------------------------------------------- dates

def to_jalali(day: date) -> tuple[int, int, int]:
    """Gregorian to Solar Hijri (the 33-year arithmetic algorithm, exact for 1900–2100)."""
    gy, gm, gd = day.year, day.month, day.day
    month_days = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 + gd + month_days[gm - 1]
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        return jy, 1 + days // 31, 1 + days % 31
    return jy, 7 + (days - 186) // 30, 1 + (days - 186) % 30


def format_date(day: date, t: Content) -> str:
    months: list[str] = t["blog"]["months"]
    if t["blog"]["calendar"] == "jalali":
        jy, jm, jd = to_jalali(day)
        return local_digits(f"{jd} {months[jm - 1]} {jy}", t["lang"])
    if t["lang"] == "en":
        return f"{months[day.month - 1]} {day.day}, {day.year}"
    return local_digits(f"{day.day} {months[day.month - 1]} {day.year}", t["lang"])


def _meta_line(article: Article, t: Content) -> str:
    minutes = t["blog"]["minutes"].replace("{n}", local_digits(str(article.minutes), t["lang"]))
    return (
        f'<span>{icon("calendar")}<time datetime="{article.published.isoformat()}">{format_date(article.published, t)}</time></span>'
        f'<span>{icon("clock")}{e(minutes)}</span>'
    )


# ---------------------------------------------------------------- cards and pages

def _href(article: Article, t: Content) -> str:
    return f"{article.page}.html" if t["lang"] == ARTICLE_LANG else f"../{ARTICLE_LANG}/{article.page}.html"


def _card(article: Article, t: Content, heading: str = "h2") -> str:
    foreign = t["lang"] != ARTICLE_LANG
    fa = CONTENT[ARTICLE_LANG]
    body_attrs = f' lang="{ARTICLE_LANG}" dir="{fa["dir"]}"' if foreign else ""
    badge = f'<span class="post-card__badge">{e(t["blog"]["fa_badge"])}</span>' if foreign else ""
    return f"""<li class="post-card neu" data-reveal>
  <div class="post-card__top"><span class="post-card__icon neu-inset">{icon(article.icon)}</span>{badge}</div>
  <div class="post-card__body"{body_attrs}>
    <p class="post-card__cat">{e(article.category)}</p>
    <{heading} class="post-card__title"><a href="{_href(article, t)}" class="post-card__link">{e(article.title)}</a></{heading}>
    <p class="post-card__desc">{e(article.description)}</p>
  </div>
  <p class="post-card__meta">{_meta_line(article, t)}</p>
  <span class="post-card__more" aria-hidden="true">{e(t['blog']['read'])}{icon('arrow', 'icon--dir')}</span>
</li>"""


def _cards(articles: list[Article], t: Content, heading: str = "h2") -> str:
    return f'<ul class="grid grid--3 posts" role="list">{"".join(_card(a, t, heading) for a in articles)}</ul>'


def page_blog(t: Content) -> str:
    note = t["blog"]["only_fa"]
    notice = f'<p class="note blog-note" data-reveal>{icon("globe")}<span>{e(note)}</span></p>' if note else ""
    return f"""
<main id="main">
{page_hero(t, 'blog')}
<section class="section">
  <div class="container">
    {notice}
    {_cards(ARTICLES, t)}
  </div>
</section>
{cta_band(t, t['home']['cta_title'], t['home']['cta_text'])}
</main>"""


def blog_teaser(t: Content, count: int = 3) -> str:
    """Latest articles on the home page; only where the articles are in the page's language."""
    if t["lang"] != ARTICLE_LANG or not ARTICLES:
        return ""
    b = t["blog"]
    return f"""
<section class="section">
  <div class="container">
    {section_head(b['home_kicker'], b['home_title'], b['home_text'], center=True)}
    {_cards(ARTICLES[:count], t, 'h3')}
    <p class="center" data-reveal><a class="btn btn--neu" href="blog.html"><span>{e(b['all'])}</span>{icon('arrow', 'icon--dir')}</a></p>
  </div>
</section>"""


def _article_hero(article: Article, t: Content) -> str:
    return f"""
<section class="page-hero page-hero--article">
  <div class="page-hero__bubbles" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
  <div class="container page-hero__inner">
    <nav class="breadcrumb" aria-label="{e(t['ui']['breadcrumb'])}">
      <a href="index.html">{e(t['ui']['home'])}</a><span aria-hidden="true">/</span>
      <a href="blog.html">{e(t['nav']['blog'])}</a><span aria-hidden="true">/</span>
      <span aria-current="page">{e(article.category)}</span>
    </nav>
    {eyebrow(article.category)}
    <h1>{e(article.title)}</h1>
    <p class="lead">{e(article.description)}</p>
    <p class="article-meta">{_meta_line(article, t)}<span>{icon('feather')}{e(article.author)}</span></p>
  </div>
  <div class="page-hero__pipe" aria-hidden="true"><span class="page-hero__water"></span></div>
  {wave_divider()}
</section>"""


def _related(article: Article, t: Content, count: int = 3) -> str:
    others = [a for a in ARTICLES if a.slug != article.slug][:count]
    if not others:
        return ""
    b = t["blog"]
    return f"""
<section class="section section--tint">
  <div class="container">
    {section_head(b['related_kicker'], b['related_title'], center=True)}
    {_cards(others, t, 'h3')}
  </div>
</section>"""


def article_body(article: Article, t: Content) -> str:
    return f"""
<main id="main">
{_article_hero(article, t)}
<section class="section section--article">
  <div class="container">
    <article class="article prose">{article.html}</article>
  </div>
</section>
{_related(article, t)}
{cta_band(t, t['home']['cta_title'], t['home']['cta_text'])}
</main>"""


def _article_ld(article: Article, t: Content) -> str:
    ld: Content = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article.title,
        "description": article.description,
        "datePublished": article.published.isoformat(),
        "inLanguage": ARTICLE_LANG,
        "keywords": ", ".join(article.keywords),
        "articleSection": article.category,
        "author": {"@type": "Organization", "name": article.author or t["brand"]},
        "publisher": {"@type": "Organization", "name": t["brand"]},
    }
    if SITE_URL:
        ld["mainEntityOfPage"] = page_url(ARTICLE_LANG, article.page)
        ld["image"] = f"{SITE_URL}/assets/img/factory.webp"
        ld["publisher"] = {**ld["publisher"], "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/img/logo-512.png"}}
    return json.dumps(ld, ensure_ascii=False, separators=(",", ":"))


def article_info(article: Article, t: Content) -> PageInfo:
    return PageInfo(
        nav="blog",
        title=f"{article.title} | {t['brand']}",
        desc=article.description,
        og_type="article",
        langs=(ARTICLE_LANG,),
        ld=_article_ld(article, t),
        body_class="page-article",
    )

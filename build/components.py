"""Reusable HTML fragments shared by several pages."""

from __future__ import annotations

import html

from data import QUOTE_PHONES, Phone
from i18n import Content, local_digits
from icons import icon
from scene import wave_divider


def e(text: str) -> str:
    return html.escape(text, quote=True)


def phone_text(phone: Phone, lang: str) -> str:
    """Phone number in the page's digits; tel: links keep the ASCII form."""
    return local_digits(phone["display"], lang)


def phone_role(phone: Phone, t: Content) -> str:
    """Role under a number; price-inquiry numbers say so."""
    roles = t["contact"]["roles"]
    return f"{roles[phone['key']]} · {roles['quote']}" if phone["quote"] else roles[phone["key"]]


def quote_buttons(t: Content, cls: str = "btn btn--primary") -> str:
    return "".join(
        f'<a class="{cls}" href="tel:{p["tel"]}">{icon("phone")}<span dir="ltr">{phone_text(p, t["lang"])}</span></a>'
        for p in QUOTE_PHONES
    )


def img(name: str, alt: str, w: int, h: int, cls: str = "", sizes: str = "(min-width: 900px) 50vw, 100vw") -> str:
    """Responsive webp photo: <name>-sm.webp (640w) and <name>.webp (1400w)."""
    extra = f' class="{cls}"' if cls else ""
    return (
        f'<img{extra} src="../assets/img/{name}.webp" '
        f'srcset="../assets/img/{name}-sm.webp 640w, ../assets/img/{name}.webp 1400w" sizes="{sizes}" '
        f'width="{w}" height="{h}" alt="{e(alt)}" loading="lazy" decoding="async">'
    )


def photo(name: str, caption: str, w: int, h: int, icon_name: str) -> str:
    return (
        f'<figure class="photo neu">{img(name, caption, w, h, "photo__img")}'
        f'<figcaption class="photo__caption glass">{icon(icon_name)}{e(caption)}</figcaption></figure>'
    )


def eyebrow(text: str) -> str:
    return f'<p class="eyebrow">{icon("leaf")}<span>{e(text)}</span></p>'


def section_head(kicker: str, title: str, text: str = "", center: bool = False) -> str:
    cls = "section-head section-head--center" if center else "section-head"
    para = f"<p>{e(text)}</p>" if text else ""
    return f'<header class="{cls}" data-reveal>{eyebrow(kicker)}<h2>{e(title)}</h2>{para}</header>'


def chip(text: str, icon_name: str, variant: str = "neu") -> str:
    return f'<li class="chip chip--{variant}">{icon(icon_name)}{e(text)}</li>'


def icon_cards(items: list[Content], cls: str = "") -> str:
    extra = f" {cls}" if cls else ""
    return "".join(
        f'<li class="feature neu{extra}" data-reveal><span class="feature__icon neu-inset">{icon(it["icon"])}</span>'
        f'<h3>{e(it["title"])}</h3><p>{e(it["text"])}</p></li>'
        for it in items
    )


def page_hero(t: Content, page: str) -> str:
    sec = t[page]
    return f"""
<section class="page-hero">
  <div class="page-hero__bubbles" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
  <div class="container page-hero__inner">
    <nav class="breadcrumb" aria-label="{e(t['ui']['breadcrumb'])}">
      <a href="index.html">{e(t['ui']['home'])}</a><span aria-hidden="true">/</span><span aria-current="page">{e(t['nav'][page])}</span>
    </nav>
    {eyebrow(sec['eyebrow'])}
    <h1>{e(sec['title'])}</h1>
    <p class="lead">{e(sec['lead'])}</p>
  </div>
  <div class="page-hero__pipe" aria-hidden="true"><span class="page-hero__water"></span></div>
  {wave_divider()}
</section>"""


def cta_band(t: Content, title: str, text: str) -> str:
    phones = quote_buttons(t)
    return f"""
<section class="section section--tight">
  <div class="container">
    <div class="cta glass glass--water" data-reveal>
      <div class="cta__ripple" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="cta__copy"><h2>{e(title)}</h2><p>{e(text)}</p></div>
      <div class="cta__actions">{phones}<a class="btn btn--neu" href="contact.html">{icon('mail')}<span>{e(t['nav']['contact'])}</span></a></div>
    </div>
  </div>
</section>"""


def default_cta(t: Content) -> str:
    return cta_band(t, t["home"]["cta_title"], t["home"]["cta_text"])


ISO_BADGES: tuple[tuple[str, str], ...] = (
    ("iso-9001", "ISO 9001"),
    ("iso-10006", "ISO 10006"),
    ("iso-17025", "ISO/IEC 17025"),
)


def iso_badges(t: Content) -> str:
    std = (
        f'<li class="badge-card neu badge-card--std" data-reveal><span class="badge-card__icon neu-inset">{icon("shield")}</span>'
        f'<span>{e(t["quality"]["standard_title"])}</span></li>'
    )
    isos = "".join(
        f'<li class="badge-card neu" data-reveal><img src="../assets/img/{name}.webp" width="140" height="140" '
        f'alt="{label}" loading="lazy" decoding="async"><span>{label}</span></li>'
        for name, label in ISO_BADGES
    )
    return f'<ul class="badges" role="list">{std}{isos}</ul>'

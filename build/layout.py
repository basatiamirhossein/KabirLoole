"""Page shell: <head>, header, footer and the full-page render."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import NamedTuple

from components import e, phone_text
from data import (
    ASSET_VERSION, DEFAULT_LANG, EMAIL, INSTAGRAM, INSTAGRAM_URL, LANGS, PAGES, PHONES, SITE_URL, TYPEFACES,
)
from i18n import CONTENT, Content
from icons import icon, sprite, take_used
from scene import wave_divider

# Browsers refuse web fonts over file:// (opaque origin). A page opened straight from the
# folder therefore loads fonts-embedded.css, which carries the same faces as data URIs.
# Served over HTTP(S) that stylesheet is never requested.
_FILE_FONTS_SCRIPT = (
    '<script>document.documentElement.classList.add("js");'
    'if(location.protocol==="file:"){var l=document.createElement("link");l.rel="stylesheet";'
    f'l.href="../assets/css/fonts-embedded.css?v={ASSET_VERSION}";document.head.appendChild(l)}}</script>'
)


class PageInfo(NamedTuple):
    """Per-page settings; site pages build theirs from content, blog articles pass their own."""

    nav: str  # the nav item shown as current, and where the language switch goes when langs lacks a language
    title: str
    desc: str
    og_type: str = "website"
    langs: tuple[str, ...] = LANGS  # languages this exact page exists in
    ld: str = ""  # extra JSON-LD
    body_class: str = ""


def site_page_info(t: Content, page: str) -> PageInfo:
    meta = t["meta"][page]
    return PageInfo(page, meta["title"], meta["desc"], body_class=f"page-{page}")


def page_url(lang: str, page: str) -> str:
    return f"{SITE_URL}/{lang}/{page}.html"


def _seo_links(lang: str, page: str, info: PageInfo) -> str:
    if not SITE_URL:
        return ""
    alternates = ""
    if len(info.langs) > 1:
        default = DEFAULT_LANG if DEFAULT_LANG in info.langs else info.langs[0]
        alternates = "".join(f'<link rel="alternate" hreflang="{l}" href="{page_url(l, page)}">' for l in info.langs)
        alternates += f'<link rel="alternate" hreflang="x-default" href="{page_url(default, page)}">'
    return (
        f'{alternates}<link rel="canonical" href="{page_url(lang, page)}">'
        f'<meta property="og:url" content="{page_url(lang, page)}">'
        f'<meta property="og:image" content="{SITE_URL}/assets/img/factory.webp">'
    )


def _organization_ld(t: Content) -> str:
    ld: Content = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": t["brand"],
        "alternateName": ["Kabirloole", "کبیر لوله"],
        "description": t["meta"]["index"]["desc"],
        "email": EMAIL,
        "telephone": PHONES[1]["tel"],
        "sameAs": [INSTAGRAM_URL],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": t["contact"]["address"],
            "addressLocality": "Darreh Shahr",
            "addressRegion": "Ilam",
            "addressCountry": "IR",
        },
    }
    if SITE_URL:
        ld["url"] = f"{SITE_URL}/{t['lang']}/"
        ld["logo"] = f"{SITE_URL}/assets/img/logo-512.png"
    return json.dumps(ld, ensure_ascii=False, separators=(",", ":"))


def head(t: Content, page: str, info: PageInfo) -> str:
    preloads = "".join(
        f'<link rel="preload" href="../assets/fonts/{file}.woff2" as="font" type="font/woff2" crossorigin>'
        for file in TYPEFACES[t["lang"]].preload
    )
    return f"""<!doctype html>
<html lang="{t['lang']}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(info.title)}</title>
<meta name="description" content="{e(info.desc)}">
<meta name="theme-color" content="#f2efe6">
<meta name="color-scheme" content="light">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="{info.og_type}">
<meta property="og:site_name" content="{e(t['brand'])}">
<meta property="og:title" content="{e(info.title)}">
<meta property="og:description" content="{e(info.desc)}">
<meta property="og:locale" content="{t['locale']}">
{_seo_links(t['lang'], page, info)}
<link rel="icon" type="image/png" sizes="32x32" href="../assets/img/logo-32.png">
<link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
<link rel="manifest" href="../site.webmanifest">
{preloads}
<link rel="stylesheet" href="../assets/css/main.css?v={ASSET_VERSION}">
{_FILE_FONTS_SCRIPT}
<script src="../assets/js/main.js?v={ASSET_VERSION}" defer></script>
<script type="application/ld+json">{_organization_ld(t)}</script>{_extra_ld(info)}
</head>"""


def _extra_ld(info: PageInfo) -> str:
    return f'\n<script type="application/ld+json">{info.ld}</script>' if info.ld else ""


def lang_switch(t: Content, page: str, info: PageInfo, cls: str = "") -> str:
    items = "".join(
        f'<a class="lang-switch__item" href="../{l}/{page if l in info.langs else info.nav}.html" hreflang="{l}" lang="{l}" data-lang="{l}" '
        f'title="{e(CONTENT[l]["label"])}"{" aria-current=\"true\"" if l == t["lang"] else ""}>{e(CONTENT[l]["short"])}</a>'
        for l in LANGS
    )
    extra = f" {cls}" if cls else ""
    return f'<nav class="lang-switch{extra}" aria-label="{e(t["ui"]["language"])}">{items}</nav>'


def _brand(t: Content, cls: str = "") -> str:
    extra = f" {cls}" if cls else ""
    return (
        f'<a class="brand{extra}" href="index.html" aria-label="{e(t["brand"])}">'
        f'<span class="brand__mark"><img src="../assets/img/logo-192.png" width="48" height="48" alt=""></span>'
        f'<span class="brand__text"><strong>{e(t["brand"])}</strong><small>{e(t["brand_tag"])}</small></span></a>'
    )


def header(t: Content, page: str, info: PageInfo) -> str:
    current = ' aria-current="page"' if page == info.nav else ' aria-current="true"'
    links = "".join(
        f'<li><a class="nav__link" href="{p}.html"{current if p == info.nav else ""}>{e(t["nav"][p])}</a></li>'
        for p in PAGES
    )
    sales = PHONES[1]
    return f"""
<a class="skip-link" href="#main">{e(t['ui']['skip'])}</a>
<header class="site-header" data-header>
  <div class="site-header__bar container">
    {_brand(t)}
    <nav class="nav" id="site-nav" aria-label="{e(t['ui']['menu'])}" data-nav>
      <ul class="nav__list" role="list">{links}</ul>
      {lang_switch(t, page, info, 'lang-switch--drawer')}
      <a class="btn btn--primary nav__drawer-cta" href="tel:{sales['tel']}">{icon('phone')}<span dir="ltr">{phone_text(sales, t['lang'])}</span></a>
    </nav>
    <div class="site-header__actions">
      {lang_switch(t, page, info)}
      <a class="btn btn--primary btn--sm site-header__cta" href="products.html#calculator">{icon('scale')}<span>{e(t['ui']['calc'])}</span></a>
      <button class="burger" type="button" aria-controls="site-nav" aria-expanded="false" data-burger
        data-label-open="{e(t['ui']['menu'])}" data-label-close="{e(t['ui']['close'])}">
        <span class="visually-hidden" data-burger-label>{e(t['ui']['menu'])}</span>
        <span class="burger__lines" aria-hidden="true"><i></i><i></i><i></i></span>
      </button>
    </div>
  </div>
</header>
<div class="nav-backdrop" data-nav-backdrop hidden></div>"""


def footer(t: Content) -> str:
    c = t["contact"]
    links = "".join(f'<li><a href="{p}.html">{e(t["nav"][p])}</a></li>' for p in PAGES)
    phones = "".join(
        f'<li><a href="tel:{p["tel"]}">{icon("fax" if p["key"] == "fax" else "phone")}'
        f'<span><small>{e(c["roles"][p["key"]])}</small><b dir="ltr">{phone_text(p, t["lang"])}</b></span></a></li>'
        for p in PHONES
    )
    sales = PHONES[1]
    return f"""
<footer class="site-footer">
  {wave_divider('wave--footer')}
  <div class="site-footer__inner">
    <div class="container site-footer__grid">
      <section class="site-footer__about">
        {_brand(t, 'brand--footer')}
        <p>{e(t['footer']['about'])}</p>
        <a class="social" href="{INSTAGRAM_URL}" target="_blank" rel="noopener">{icon('instagram')}<span dir="ltr">@{INSTAGRAM}</span></a>
      </section>
      <nav class="site-footer__links" aria-label="{e(t['footer']['links'])}">
        <h2>{e(t['footer']['links'])}</h2>
        <ul role="list">{links}</ul>
      </nav>
      <section class="site-footer__contact">
        <h2>{e(t['footer']['contact'])}</h2>
        <ul class="contact-list" role="list">{phones}
          <li><a href="mailto:{EMAIL}">{icon('mail')}<span><small>{e(c['email_label'])}</small><b dir="ltr">{EMAIL}</b></span></a></li>
          <li><span class="contact-list__static">{icon('pin')}<span><small>{e(c['address_label'])}</small><b>{e(c['address'])}</b></span></span></li>
        </ul>
      </section>
    </div>
    <div class="container site-footer__bottom">
      <p>{e(t['footer']['rights'])}</p>
      <p class="site-footer__made">{icon('leaf')}{e(t['footer']['made'])}</p>
    </div>
  </div>
</footer>
<div class="mobile-cta" data-mobile-cta>
  <a class="btn btn--primary" href="tel:{sales['tel']}">{icon('phone')}<span>{e(t['ui']['call'])}</span></a>
  <a class="btn btn--glass" href="products.html#calculator">{icon('scale')}<span>{e(t['ui']['calc'])}</span></a>
</div>
<button class="to-top" type="button" data-to-top aria-label="{e(t['ui']['back_top'])}" hidden>{icon('chevron')}</button>"""


def render_page(lang: str, page: str, body: Callable[[Content], str], info: PageInfo | None = None) -> str:
    t = CONTENT[lang]
    info = info or site_page_info(t, page)
    take_used()
    inner = f"{header(t, page, info)}{body(t)}{footer(t)}"
    return (
        f'{head(t, page, info)}\n<body class="{info.body_class}">\n{sprite(take_used())}\n'
        f'<div class="paper" aria-hidden="true"></div>{inner}\n</body>\n</html>\n'
    )
